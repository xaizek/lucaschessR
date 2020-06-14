from Code import Game
from Code import Position
from Code import Gestor
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import PantallaEntMaq
from Code.QT import PantallaSolo
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code import TrListas
from Code.QT import Voyager
from Code.Constantes import *


class GestorPartida(Gestor.Gestor):
    def inicio(self, game, siCompleta):
        self.game_type = GT_ALONE

        self.game = game
        self.reinicio = self.game.save()
        self.siCompleta = siCompleta

        self.human_is_playing = True
        self.is_human_side_white = True

        self.changed = False

        self.state = ST_PLAYING

        li = [TB_SAVE, TB_CANCEL, TB_PGN_LABELS, TB_TAKEBACK, TB_REINIT, TB_CONFIG, TB_UTILITIES]
        self.main_window.pon_toolbar(li)

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.quitaAyudas(True, False)
        self.main_window.ponRotulo1(None)
        self.main_window.ponRotulo2(None)
        self.set_dispatcher(self.mueve_humano)
        self.ponPosicion(self.game.first_position)
        self.mostrarIndicador(True)
        self.ponPiezasAbajo(game.iswhite())
        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()
        self.goto_end()

        self.dgt_setposition()

        self.ponInformacion()

        self.refresh()

        self.siguiente_jugada()

    def ponInformacion(self):
        if self.siCompleta:
            white = black = result = None
            for key, valor in self.game.li_tags:
                key = key.upper()
                if key == "WHITE":
                    white = valor
                elif key == "BLACK":
                    black = valor
                elif key == "RESULT":
                    result = valor
            self.ponRotulo1(
                "%s : <b>%s</b><br>%s : <b>%s</b>" % (_("White"), white, _("Black"), black) if white and black else ""
            )
            self.ponRotulo2("%s : <b>%s</b>" % (_("Result"), result) if result else "")

    def reiniciar(self):
        if self.changed and not QTUtil2.pregunta(self.main_window, _("You will loose all changes, are you sure?")):
            return
        p = Game.Game()
        p.restore(self.reinicio)
        self.inicio(p, self.siCompleta)

    def run_action(self, key):
        if key == TB_REINIT:
            self.reiniciar()

        elif key == TB_TAKEBACK:
            self.atras()

        elif key == TB_SAVE:
            self.main_window.accept()

        elif key == TB_CONFIG:
            self.configurarGS()

        elif key == TB_UTILITIES:
            liMasOpciones = (
                ("libros", _("Consult a book"), Iconos.Libros()),
                (None, None, None),
                ("play", _("Play current position"), Iconos.MoverJugar()),
            )

            resp = self.utilidades(liMasOpciones)
            if resp == "libros":
                liMovs = self.librosConsulta(True)
                if liMovs:
                    for x in range(len(liMovs) - 1, -1, -1):
                        from_sq, to_sq, promotion = liMovs[x]
                        self.mueve_humano(from_sq, to_sq, promotion)
            elif resp == "play":
                self.jugarPosicionActual()

        elif key == TB_PGN_LABELS:
            self.informacion()

        elif key in (TB_CANCEL, TB_END_GAME):
            self.finPartida()

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def finPartida(self):
        # Comprobamos que no haya habido cambios from_sq el ultimo grabado
        if self.changed:
            resp = QTUtil2.preguntaCancelar(self.main_window, _("Do you want to cancel changes?"), _("Yes"), _("No"))
            if not resp:
                return False

        self.main_window.reject()
        return True

    def final_x(self):
        return self.finPartida()

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.put_view()

        is_white = self.game.last_position.is_white
        self.is_human_side_white = is_white  # Compatibilidad, sino no funciona el cambio en pgn

        if self.game.is_finished():
            self.muestra_resultado()
            return

        self.ponIndicador(is_white)
        self.refresh()

        self.human_is_playing = True
        self.activaColor(is_white)

    def muestra_resultado(self):
        self.state = ST_ENDGAME
        self.disable_all()

    def mueve_humano(self, from_sq, to_sq, promotion=None):
        self.human_is_playing = True
        move = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not move:
            return False

        self.move_the_pieces(move.liMovs)

        self.add_move(move, True)

        self.siguiente_jugada()
        return True

    def add_move(self, move, siNuestra):
        self.changed = True

        self.game.add_move(move)

        self.ponFlechaSC(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

        self.dgt_setposition()

    def actualPGN(self):
        resp = ""
        st = set()
        for eti, valor in self.game.li_tags:
            etiU = eti.upper()
            if etiU in st:
                continue
            st.add(etiU)
            resp += '[%s "%s"]\n' % (eti, valor)
            if etiU == "RESULT":
                result = valor

        if not ("RESULT" in st):
            if self.resultado == RS_UNKNOWN:
                result = "*"

            elif self.resultado == RS_DRAW:
                result = "1/2-1/2"

            else:
                result = "1-0" if self.resultadoSiBlancas else "0-1"

            resp += '[Result "%s"]\n' % result

        if self.fen:
            resp += '[FEN "%s"]\n' % self.fen

        ap = self.game.opening
        if ap:
            if not ("ECO" in st):
                resp += '[ECO "%s"]\n' % ap.eco
            if not ("OPENING" in st):
                resp += '[Opening "%s"]\n' % ap.trNombre

        resp += "\n" + self.game.pgnBase() + " " + result

        return resp

    def editarEtiquetasPGN(self):
        resp = PantallaSolo.editarEtiquetasPGN(self.procesador, self.game.li_tags)
        if resp:
            self.game.li_tags = resp
            self.changed = True
            self.ponInformacion()

    def informacion(self):
        menu = QTVarios.LCMenu(self.main_window)
        f = Controles.TipoLetra(puntos=10, peso=75)
        menu.ponFuente(f)

        siOpening = False
        for key, valor in self.game.li_tags:
            trad = TrListas.pgnLabel(key)
            if trad != key:
                key = trad
            menu.opcion(key, "%s : %s" % (key, valor), Iconos.PuntoAzul())
            if key.upper() == "OPENING":
                siOpening = True

        if not siOpening:
            opening = self.game.opening
            if opening:
                menu.separador()
                nom = opening.trNombre
                ape = _("Opening")
                rotulo = nom if ape.upper() in nom.upper() else ("%s : %s" % (ape, nom))
                menu.opcion("opening", rotulo, Iconos.PuntoNaranja())

        menu.separador()
        menu.opcion("pgn", _("Edit PGN labels"), Iconos.PGN())

        resp = menu.lanza()
        if resp:
            self.editarEtiquetasPGN()

    def configurarGS(self):
        sep = (None, None, None)

        liMasOpciones = [
            ("rotacion", _("Auto-rotate board"), Iconos.JS_Rotacion()),
            sep,
            ("leerpgn", _("Read PGN"), Iconos.PGN_Importar()),
            sep,
            ("pastepgn", _("Paste PGN"), Iconos.Pegar16()),
            sep,
        ]
        if not self.siCompleta:
            liMasOpciones.extend(
                [
                    ("position", _("Edit start position"), Iconos.Datos()),
                    sep,
                    ("pasteposicion", _("Paste FEN position"), Iconos.Pegar16()),
                    sep,
                    ("voyager", _("Voyager 2"), Iconos.Voyager1()),
                ]
            )

        resp = self.configurar(liMasOpciones, siCambioTutor=True, siSonidos=True)

        if resp == "rotacion":
            self.auto_rotate = not self.auto_rotate
            is_white = self.game.last_position.is_white
            if self.auto_rotate:
                if is_white != self.tablero.is_white_bottom:
                    self.tablero.rotaTablero()

        elif resp == "position":
            ini_position = self.game.first_position
            new_position = Voyager.voyager_position(self.main_window, ini_position)
            if new_position and new_position != ini_position:
                self.game.set_position(new_position)
                self.inicio(self.game, self.siCompleta)

        elif resp == "pasteposicion":
            texto = QTUtil.traePortapapeles()
            if texto:
                cp = Position.Position()
                try:
                    cp.read_fen(str(texto))
                    self.fen = cp.fen()
                    self.posicApertura = None
                    self.reiniciar()
                except:
                    pass

        elif resp == "leerpgn":
            game = self.procesador.select_1_pgn(self.main_window)
            if game:
                if self.siCompleta and not game.siFenInicial():
                    return
                p = Game.Game()
                p.leeOtra(game)
                p.assign_opening()
                self.reinicio = p.save()
                self.reiniciar()

        elif resp == "pastepgn":
            texto = QTUtil.traePortapapeles()
            if texto:
                ok, game = Game.pgn_game(texto)
                if not ok:
                    QTUtil2.message_error(
                        self.main_window, _("The text from the clipboard does not contain a chess game in PGN format")
                    )
                    return
                if self.siCompleta and not game.siFenInicial():
                    return
                self.reinicio = game.save()
                self.reiniciar()

        elif resp == "voyager":
            ptxt = Voyager.voyagerPartida(self.main_window, self.game)
            if ptxt:
                dic = self.creaDic()
                dic["GAME"] = ptxt.save()
                dic["FEN"] = None if ptxt.siFenInicial() else ptxt.first_position.fen()
                dic["WHITEBOTTOM"] = self.tablero.is_white_bottom
                self.reiniciar(dic)

    def control_teclado(self, nkey):
        if nkey == ord("V"):  # V
            self.paste(QTUtil.traePortapapeles())

    def listHelpTeclado(self):
        return [("V", _("Paste position"))]

    def juegaRival(self):
        if not self.is_finished():
            self.pensando(True)
            rm = self.xrival.juega(nAjustado=self.xrival.nAjustarFuerza)
            self.pensando(False)
            if rm.from_sq:
                self.mueve_humano(rm.from_sq, rm.to_sq, rm.promotion)

    def cambioRival(self):
        if self.dicRival:
            dicBase = self.dicRival
        else:
            dicBase = self.configuracion.leeVariables("ENG_GESTORSOLO")

        dic = self.dicRival = PantallaEntMaq.cambioRival(
            self.main_window, self.configuracion, dicBase, siGestorSolo=True
        )

        if dic:
            for k, v in dic.items():
                self.reinicio[k] = v

            dr = dic["RIVAL"]
            rival = dr["CM"]
            r_t = dr["TIEMPO"] * 100  # Se guarda en decimas -> milesimas
            r_p = dr["PROFUNDIDAD"]
            if r_t <= 0:
                r_t = None
            if r_p <= 0:
                r_p = None
            if r_t is None and r_p is None and not dic["SITIEMPO"]:
                r_t = 1000

            nAjustarFuerza = dic["AJUSTAR"]
            self.xrival = self.procesador.creaGestorMotor(rival, r_t, r_p, nAjustarFuerza != ADJUST_BETTER)
            self.xrival.nAjustarFuerza = nAjustarFuerza

            dic["ROTULO1"] = _("Opponent") + ": <b>" + self.xrival.name
            self.ponRotulo1(dic["ROTULO1"])
            self.play_against_engine = True
            self.configuracion.escVariables("ENG_GESTORSOLO", dic)

    def tituloVentana(self):
        white = ""
        black = ""
        event = ""
        date = ""
        result = ""
        for key, valor in self.game.li_tags:
            if key.upper() == "WHITE":
                white = valor
            elif key.upper() == "BLACK":
                black = valor
            elif key.upper() == "EVENT":
                event = valor
            elif key.upper() == "DATE":
                date = valor
            elif key.upper() == "RESULT":
                result = valor
        return "%s-%s (%s, %s,%s)" % (white, black, event, date, result)

    def atras(self):
        if len(self.game):
            self.game.anulaSoloUltimoMovimiento()
            self.game.assign_opening()
            self.goto_end()
            self.state = ST_PLAYING
            self.refresh()
            self.siguiente_jugada()
