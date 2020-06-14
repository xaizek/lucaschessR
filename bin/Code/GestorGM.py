import copy
import random

import Code
from Code import Apertura
from Code import GM
from Code import Gestor
from Code import Move
from Code.QT import PantallaGM
from Code.QT import PantallaJuicio
from Code.QT import QTUtil2
from Code import Util
from Code.SQL import UtilSQL
from Code.Constantes import *


class GestorGM(Gestor.Gestor):
    def inicio(self, record):

        self.game_type = GT_AGAINST_GM

        self.ayudas = 9999  # Para que analice sin problemas

        self.puntos = 0

        self.record = record

        self.gm = record.gm
        self.is_white = record.is_white
        self.modo = record.modo
        self.siJuez = record.siJuez
        self.showevals = record.showevals
        self.engine = record.engine
        self.vtime = record.vtime
        self.depth = record.depth
        self.multiPV = record.multiPV
        self.mostrar = record.mostrar
        self.jugContrario = record.jugContrario
        self.jugInicial = record.jugInicial
        self.partidaElegida = record.partidaElegida
        self.bypassBook = record.bypassBook
        self.opening = record.opening
        self.onBypassBook = True if self.bypassBook else False
        if self.onBypassBook:
            self.bypassBook.polyglot()
        self.onApertura = True if self.opening else False

        self.siAnalizando = False

        if self.siJuez:
            self.puntos = 0
            tutor = self.configuracion.buscaRival(self.engine)
            t_t = self.vtime * 100
            self.xtutor = self.procesador.creaGestorMotor(tutor, t_t, self.depth)
            self.xtutor.actMultiPV(self.multiPV)
            self.analysis = None

        self.book = Apertura.AperturaPol(999)

        self.pensando(True)

        default = Code.path_resource("GM")
        carpeta = default if self.modo == "estandar" else self.configuracion.dirPersonalTraining
        self.motorGM = GM.GM(carpeta, self.gm)
        self.motorGM.colorFilter(self.is_white)
        if self.partidaElegida is not None:
            self.motorGM.ponPartidaElegida(self.partidaElegida)

        self.is_human_side_white = self.is_white
        self.is_engine_side_white = not self.is_white
        self.pensando(False)

        self.main_window.pon_toolbar((TB_CLOSE, TB_REINIT, TB_CONFIG, TB_UTILITIES))
        self.main_window.activaJuego(True, False)
        self.set_dispatcher(self.mueve_humano)
        self.ponPosicion(self.game.last_position)
        self.mostrarIndicador(True)
        self.quitaAyudas()
        self.ponPiezasAbajo(self.is_white)
        dic = GM.dic_gm()
        self.nombreGM = dic[self.gm.lower()] if self.modo == "estandar" else self.gm
        rot = _("Grandmaster")
        rotulo1 = rot + ": <b>%s</b>" if self.modo == "estandar" else "<b>%s</b>"
        self.ponRotulo1(rotulo1 % self.nombreGM)

        self.nombreRival = ""
        self.textoPuntuacion = ""
        self.ponRotuloSecundario()
        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()

        self.state = ST_PLAYING

        self.dgt_setposition()

        self.siguiente_jugada()

    def ponRotuloSecundario(self):
        self.ponRotulo2(self.nombreRival + "<br><br>" + self.textoPuntuacion)

    def run_action(self, key):

        if key == TB_CLOSE:
            self.finPartida()

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True)

        elif key == TB_UTILITIES:
            self.utilidades()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def final_x(self):
        if self.state == ST_ENDGAME:
            return True
        return self.finPartida()

    def finPartida(self):
        self.analizaTerminar()
        siJugadas = len(self.game) > 0
        if siJugadas and self.state != ST_ENDGAME:
            self.game.set_unknown()
            self.ponFinJuego()
        self.procesador.inicio()

        return False

    def reiniciar(self):
        if QTUtil2.pregunta(self.main_window, _("Restart the game?")):
            self.analizaTerminar()
            self.game.set_position()
            self.inicio(self.record)

    def analizaInicio(self):
        if not self.is_finished():
            self.xtutor.ac_inicio(self.game)
            self.siAnalizando = True

    def analizaEstado(self):
        self.xtutor.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xtutor.ac_estado())
        return self.mrm

    def analizaMinimo(self, minTime):
        self.mrm = copy.deepcopy(self.xtutor.ac_minimo(minTime, False))
        return self.mrm

    def analizaFinal(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xtutor.ac_final(-1)

    def siguiente_jugada(self):
        self.analizaTerminar()
        self.disable_all()

        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        if (len(self.game) > 0) and self.motorGM.isFinished():
            self.put_result()
            return

        self.ponIndicador(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white

        if self.jugInicial > 1:
            siJugInicial = (len(self.game) / 2 + 1) <= self.jugInicial
        else:
            siJugInicial = False

        liAlternativas = self.motorGM.alternativas()
        nliAlternativas = len(liAlternativas)

        # Movimiento automatico
        if siJugInicial or self.onApertura or self.onBypassBook:
            siBuscar = True
            if self.onApertura:
                liPV = self.opening.a1h8.split(" ")
                nj = len(self.game)
                if len(liPV) > nj:
                    move = liPV[nj]
                    if move in liAlternativas:
                        siBuscar = False
                    else:
                        self.onApertura = False
                else:
                    self.onApertura = False

            if siBuscar:
                if self.onBypassBook:
                    li_moves = self.bypassBook.miraListaJugadas(self.fenUltimo())
                    liN = []
                    for from_sq, to_sq, promotion, pgn, peso in li_moves:
                        move = from_sq + to_sq + promotion
                        if move in liAlternativas:
                            liN.append(move)
                    if liN:
                        siBuscar = False
                        nliAlternativas = len(liN)
                        if nliAlternativas > 1:
                            pos = random.randint(0, nliAlternativas - 1)
                            move = liN[pos]
                        else:
                            move = liN[0]
                    else:
                        self.onBypassBook = None

            if siBuscar:
                if siJugInicial:
                    siBuscar = False
                    if nliAlternativas > 1:
                        pos = random.randint(0, nliAlternativas - 1)
                        move = liAlternativas[pos]
                    elif nliAlternativas == 1:
                        move = liAlternativas[0]

            if not siBuscar:
                self.mueve_rival(move)
                self.siguiente_jugada()
                return

        if siRival:
            if nliAlternativas > 1:
                if self.jugContrario:
                    li_moves = self.motorGM.dameJugadasTXT(self.game.last_position, False)
                    from_sq, to_sq, promotion = PantallaGM.eligeJugada(self, li_moves, False)
                    move = from_sq + to_sq + promotion
                else:
                    pos = random.randint(0, nliAlternativas - 1)
                    move = liAlternativas[pos]
            else:
                move = liAlternativas[0]

            self.mueve_rival(move)
            self.siguiente_jugada()

        else:
            self.human_is_playing = True
            self.pensando(True)
            self.analizaInicio()
            self.activaColor(is_white)
            self.pensando(False)

    def analizaTerminar(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xtutor.terminar()

    def mueve_humano(self, from_sq, to_sq, promotion=None):
        jgUsu = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not jgUsu:
            return False

        movimiento = jgUsu.movimiento()
        position = self.game.last_position
        isValid = self.motorGM.isValidMove(movimiento)
        analisis = None

        if not isValid:
            self.tablero.ponPosicion(position)
            self.tablero.activaColor(self.is_human_side_white)
            li_moves = self.motorGM.dameJugadasTXT(position, True)
            desdeGM, hastaGM, coronacionGM = PantallaGM.eligeJugada(self, li_moves, True)
            siAnalizaJuez = self.siJuez
            if siAnalizaJuez:
                if self.book:
                    fen = self.fenUltimo()
                    siH = self.book.check_human(fen, from_sq, to_sq)
                    siGM = self.book.check_human(fen, desdeGM, hastaGM)
                    if siGM and siH:
                        siAnalizaJuez = False
                    else:
                        self.book = False
        else:
            siAnalizaJuez = (
                self.siJuez and self.mostrar is None
            )  # None es ver siempre False no ver nunca True ver si diferentes
            if len(movimiento) == 5:
                promotion = movimiento[4].lower()
            desdeGM, hastaGM, coronacionGM = from_sq, to_sq, promotion

        siBien, mens, jgGM = Move.dameJugada(self.game, position, desdeGM, hastaGM, coronacionGM)
        movGM = jgGM.pgn_translated()
        movUsu = jgUsu.pgn_translated()

        if siAnalizaJuez:
            um = QTUtil2.analizando(self.main_window)
            mrm = self.analizaMinimo(self.vtime * 100)

            rmUsu, nada = mrm.buscaRM(jgUsu.movimiento())
            if rmUsu is None:
                um = QTUtil2.analizando(self.main_window)
                self.analizaFinal()
                rmUsu = self.xtutor.valora(position, from_sq, to_sq, promotion)
                mrm.agregaRM(rmUsu)
                self.analizaInicio()
                um.final()

            rmGM, pos_gm = mrm.buscaRM(jgGM.movimiento())
            if rmGM is None:
                self.analizaFinal()
                rmGM = self.xtutor.valora(position, desdeGM, hastaGM, coronacionGM)
                pos_gm = mrm.agregaRM(rmGM)
                self.analizaInicio()

            um.final()

            analisis = mrm, pos_gm
            dpts = rmUsu.centipawns_abs() - rmGM.centipawns_abs()

            if self.mostrar is None or ((self.mostrar is True) and not isValid):
                w = PantallaJuicio.WJuicio(
                    self,
                    self.xtutor,
                    self.nombreGM,
                    position,
                    mrm,
                    rmGM,
                    rmUsu,
                    analisis,
                    siCompetitivo=not self.showevals,
                )
                w.exec_()

                rm, pos_gm = w.analysis[0].buscaRM(jgGM.movimiento())
                analisis = w.analysis[0], pos_gm

                dpts = w.difPuntos()

            self.puntos += dpts

            comentario0 = "<b>%s</b> : %s = %s<br>" % (self.configuracion.x_player, movUsu, rmUsu.texto())
            comentario0 += "<b>%s</b> : %s = %s<br>" % (self.nombreGM, movGM, rmGM.texto())
            comentario1 = "<br><b>%s</b> = %+d<br>" % (_("Difference"), dpts)
            comentario2 = "<b>%s</b> = %+d<br>" % (_("Points accumulated"), self.puntos)
            self.textoPuntuacion = comentario2
            self.ponRotuloSecundario()

            if not isValid:
                jgGM.comment = (
                    (comentario0 + comentario1 + comentario2)
                    .replace("<b>", "")
                    .replace("</b>", "")
                    .replace("<br>", "\n")
                )

        self.analizaFinal()

        self.move_the_pieces(jgGM.liMovs)

        jgGM.analysis = analisis
        self.add_move(jgGM, True)
        self.error = ""
        self.siguiente_jugada()
        return True

    def analizaPosicion(self, fila, key):
        if self.state != ST_ENDGAME:
            return
        Gestor.Gestor.analizaPosicion(self, fila, key)

    def mueve_rival(self, move):
        from_sq = move[:2]
        to_sq = move[2:4]
        promotion = move[4:]

        siBien, mens, move = Move.dameJugada(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if siBien:
            self.error = ""

            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)

            return True
        else:
            self.error = mens
            return False

    def add_move(self, move, siNuestra):
        self.game.add_move(move)
        self.game.comprueba()

        self.ponFlechaSC(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        txt = self.motorGM.rotuloPartidaSiUnica(siGM=self.modo == "estandar")
        if txt:
            self.nombreRival = txt
        self.ponRotuloSecundario()

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

        self.motorGM.play(move.movimiento())

        self.dgt_setposition()

    def put_result(self):
        self.state = ST_ENDGAME
        self.tablero.disable_all()

        mensaje = _("Game ended")

        txt, porc, txtResumen = self.motorGM.resultado(self.game)
        mensaje += "<br><br>" + txt
        if self.siJuez:
            mensaje += "<br><br><b>%s</b> = %+d<br>" % (_("Points accumulated"), self.puntos)

        self.mensajeEnPGN(mensaje)

        dbHisto = UtilSQL.DictSQL(self.configuracion.ficheroGMhisto)

        gmK = "P_%s" % self.gm if self.modo == "personal" else self.gm

        dic = {}
        dic["FECHA"] = Util.today()
        dic["PUNTOS"] = self.puntos
        dic["PACIERTOS"] = porc
        dic["JUEZ"] = self.engine
        dic["TIEMPO"] = self.vtime
        dic["RESUMEN"] = txtResumen

        liHisto = dbHisto[gmK]
        if liHisto is None:
            liHisto = []
        liHisto.insert(0, dic)
        dbHisto[gmK] = liHisto
        dbHisto.pack()
        dbHisto.close()
