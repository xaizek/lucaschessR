import os
import random
import time

import FasterCode

from Code import Analisis
from Code import AnalisisIndexes
from Code import AperturasStd
from Code import ControlPGN
from Code import Position
from Code import DGT
from Code import Move
from Code import Game
from Code.Databases import DBgames
from Code.Kibitzers import Kibitzers
from Code.QT import Histogram
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import PantallaAnalisis
from Code.QT import PantallaArbol
from Code.QT import PantallaArbolBook
from Code.QT import PantallaSavePGN
from Code.QT import PantallaTutor
from Code.QT import Pelicula
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import TabTipos
from Code import Util
import Code
from Code import XRun
from Code.Constantes import *


class Gestor:
    def __init__(self, procesador):

        self.fen = None

        self.procesador = procesador
        self.main_window = procesador.main_window
        self.tablero = procesador.tablero
        self.tablero.setAcceptDropPGNs(None)
        self.configuracion = procesador.configuracion
        self.runSound = Code.runSound

        self.state = ST_ENDGAME  # Para que siempre este definido

        self.game_type = None
        self.ayudas = None
        self.ayudas_iniciales = 0

        self.siCompetitivo = False

        self.resultado = RS_UNKNOWN

        self.categoria = None

        self.main_window.ponGestor(self)

        self.game = None
        self.new_game()

        self.listaAperturasStd = AperturasStd.ap

        self.human_is_playing = False

        self.pgn = ControlPGN.ControlPGN(self)

        self.timekeeper = Util.Timekeeper()

        self.xtutor = procesador.XTutor()
        self.xanalyzer = procesador.XAnalyzer()
        self.xrival = None

        self.rm_rival = None  # Usado por el tutor para mostrar las intenciones del rival

        self.plays_instead_of_me_option = False

        self.unMomento = self.procesador.unMomento
        self.um = None

        self.xRutinaAccionDef = None

        self.xpelicula = None

        self.main_window.ajustaTam()

        self.tablero.exePulsadoNum = self.exePulsadoNum
        self.tablero.exePulsadaLetra = self.exePulsadaLetra

        self.siRevision = True  # controla si hay mostrar el rotulo de revisando

        # Capturas
        self.capturasActivable = False

        # Informacion
        self.informacionActivable = False

        self.nonDistract = None

        # x Control del tutor
        #  asi sabemos si ha habido intento de analisis previo (por ejemplo el usuario mientras piensa decide activar el tutor)
        self.siIniAnalizaTutor = False

        self.continueTt = not self.configuracion.x_engine_notbackground

        # Atajos raton:
        self.atajosRatonDestino = None
        self.atajosRatonOrigen = None

        self.kibitzers_manager = self.procesador.kibitzers_manager
        # DGT
        self.compruebaDGT()

    def new_game(self):
        self.game = Game.Game()
        self.game.add_tag("Site", Code.lucas_chess)
        hoy = Util.today()
        self.game.add_tag("Date", "%d-%02d-%02d" % (hoy.year, hoy.month, hoy.day))

    def ponFinJuego(self):
        self.runSound.close()
        if len(self.game):
            self.state = ST_ENDGAME
            self.disable_all()
            li_options = [TB_CLOSE]
            if hasattr(self, "reiniciar"):
                li_options.append(TB_REINIT)
            li_options.append(TB_CONFIG)
            li_options.append(TB_UTILITIES)
            self.main_window.pon_toolbar(li_options)
            self.quitaAyudas()
        else:
            self.procesador.reset()

    def finGestor(self):
        # se llama from_sq procesador.inicio, antes de borrar el gestor
        self.tablero.atajosRaton = None
        if self.nonDistract:
            self.main_window.base.tb.setVisible(True)

    def atajosRatonReset(self):
        self.atajosRatonDestino = None
        self.atajosRatonOrigen = None

    def otherCandidates(self, liMoves, position, liC):
        liPlayer = []
        for mov in liMoves:
            if mov.mate():
                liPlayer.append((mov.xto(), "P#"))
            elif mov.check():
                liPlayer.append((mov.xto(), "P+"))
            elif mov.capture():
                liPlayer.append((mov.xto(), "Px"))
        oposic = position.copia()
        oposic.is_white = not position.is_white
        oposic.en_passant = ""
        siJaque = FasterCode.ischeck()
        FasterCode.set_fen(oposic.fen())
        liO = FasterCode.get_exmoves()
        liRival = []
        for n, mov in enumerate(liO):
            if not siJaque:
                if mov.mate():
                    liRival.append((mov.xto(), "R#"))
                elif mov.check():
                    liRival.append((mov.xto(), "R+"))
                elif mov.capture():
                    liPlayer.append((mov.xto(), "Rx"))
            elif mov.capture():
                liPlayer.append((mov.xto(), "Rx"))

        liC.extend(liRival)
        liC.extend(liPlayer)

    def colect_candidates(self, a1h8):
        if not hasattr(self.pgn, "move"):  # gestor60 por ejemplo
            return None
        fila, columna = self.main_window.pgnPosActual()
        pos_move, move = self.pgn.move(fila, columna.clave)
        if move:
            position = move.position
        else:
            position = self.game.first_position

        FasterCode.set_fen(position.fen())
        li = FasterCode.get_exmoves()
        if not li:
            return None

        # Se comprueba si algun movimiento puede empezar o terminar ahi
        siOrigen = siDestino = False
        for mov in li:
            from_sq = mov.xfrom()
            to_sq = mov.xto()
            if a1h8 == from_sq:
                siOrigen = True
                break
            if a1h8 == to_sq:
                siDestino = True
                break
        origen = destino = None
        if siOrigen or siDestino:
            pieza = position.squares.get(a1h8, None)
            if pieza is None:
                destino = a1h8
            elif position.is_white:
                if pieza.isupper():
                    origen = a1h8
                else:
                    destino = a1h8
            else:
                if pieza.isupper():
                    destino = a1h8
                else:
                    origen = a1h8

        liC = []
        for mov in li:
            a1 = mov.xfrom()
            h8 = mov.xto()
            siO = (origen == a1) if origen else None
            siD = (destino == h8) if destino else None

            if (siO and siD) or ((siO is None) and siD) or ((siD is None) and siO):
                t = (a1, h8)
                if not (t in liC):
                    liC.append(t)

        if origen:
            liC = [(dh[1], "C") for dh in liC]
        else:
            liC = [(dh[0], "C") for dh in liC]
        self.otherCandidates(li, position, liC)
        return liC

    def atajosRaton(self, a1h8):
        if a1h8 is None or not self.tablero.siActivasPiezas:
            self.atajosRatonReset()
            return

        num_moves, nj, fila, is_white = self.jugadaActual()
        if nj < num_moves - 1:
            self.atajosRatonReset()
            liC = self.colect_candidates(a1h8)
            self.tablero.show_candidates(liC)
            return

        position = self.game.last_position
        FasterCode.set_fen(position.fen())
        li_moves = FasterCode.get_exmoves()
        if not li_moves:
            return

        # Se comprueba si algun movimiento puede empezar o terminar ahi
        li_destinos = []
        li_origenes = []
        for mov in li_moves:
            from_sq = mov.xfrom()
            to_sq = mov.xto()
            if a1h8 == from_sq:
                li_destinos.append(to_sq)
            if a1h8 == to_sq:
                li_origenes.append(from_sq)
        if not (li_destinos or li_origenes):
            self.atajosRatonReset()
            return

        def mueve():
            self.tablero.muevePiezaTemporal(self.atajosRatonOrigen, self.atajosRatonDestino)
            if (not self.tablero.mensajero(self.atajosRatonOrigen, self.atajosRatonDestino)) and self.atajosRatonOrigen:
                self.tablero.reponPieza(self.atajosRatonOrigen)
            self.atajosRatonReset()

        def show_candidates():
            if self.configuracion.x_show_candidates:
                liC = []
                for mov in li_moves:
                    a1 = mov.xfrom()
                    h8 = mov.xto()
                    if a1 == self.atajosRatonOrigen:
                        liC.append((h8, "C"))
                if self.state != ST_PLAYING:
                    self.otherCandidates(li_moves, position, liC)
                self.tablero.show_candidates(liC)

        if not self.configuracion.x_mouse_shortcuts:
            if li_destinos:
                self.atajosRatonOrigen = a1h8
                self.atajosRatonDestino = None
                # if self.atajosRatonDestino and self.atajosRatonDestino in li_destinos:
                #     mueve()
                # else:
                #     self.atajosRatonDestino = None
                show_candidates()
                return
            elif li_origenes:
                self.atajosRatonDestino = a1h8
                if self.atajosRatonOrigen and self.atajosRatonOrigen in li_origenes:
                    mueve()
                else:
                    self.atajosRatonOrigen = None
                    self.atajosRatonDestino = None
                    show_candidates()
            return

        if li_origenes:
            self.atajosRatonDestino = a1h8
            if self.atajosRatonOrigen and self.atajosRatonOrigen in li_origenes:
                mueve()
            elif len(li_origenes) == 1:
                self.atajosRatonOrigen = li_origenes[0]
                mueve()
            else:
                show_candidates()
            return

        if li_destinos:
            self.atajosRatonOrigen = a1h8
            if self.atajosRatonDestino and self.atajosRatonDestino in li_destinos:
                mueve()
            elif len(li_destinos) == 1:
                self.atajosRatonDestino = li_destinos[0]
                mueve()
            else:
                show_candidates()
            return

    def repiteUltimaJugada(self):
        # Gestor ent tac + ent pos si hay game
        if len(self.game):
            move = self.game.last_jg()
            self.tablero.setposition(move.position_before)
            self.tablero.ponFlechaSC(move.from_sq, move.to_sq)
            QTUtil.refresh_gui()
            time.sleep(0.6)
            ant = self.configuracion.x_show_effects
            self.configuracion.x_show_effects = True
            self.move_the_pieces(move.liMovs, True)
            self.configuracion.x_show_effects = ant
            self.tablero.setposition(move.position)

    def move_the_pieces(self, liMovs, siMovTemporizado=False):
        if siMovTemporizado and self.configuracion.x_show_effects:

            rapidez = self.configuracion.x_pieces_speed * 1.0 / 100.0
            cpu = self.procesador.cpu
            cpu.reset()
            segundos = None

            # primero los movimientos
            for movim in liMovs:
                if movim[0] == "m":
                    if segundos is None:
                        from_sq, to_sq = movim[1], movim[2]
                        dc = ord(from_sq[0]) - ord(to_sq[0])
                        df = int(from_sq[1]) - int(to_sq[1])
                        # Maxima distancia = 9.9 ( 9,89... sqrt(7**2+7**2)) = 4 segundos
                        dist = (dc ** 2 + df ** 2) ** 0.5
                        segundos = 4.0 * dist / (9.9 * rapidez)
                    if self.procesador.gestor:
                        cpu.muevePieza(movim[1], movim[2], siExclusiva=False, segundos=segundos)
                    else:
                        return

            if segundos is None:
                segundos = 1.0

            # segundo los borrados
            for movim in liMovs:
                if movim[0] == "b":
                    if self.procesador.gestor:
                        n = cpu.duerme(segundos * 0.80 / rapidez)
                        cpu.borraPieza(movim[1], padre=n)
                    else:
                        return

            # tercero los cambios
            for movim in liMovs:
                if movim[0] == "c":
                    if self.procesador.gestor:
                        cpu.cambiaPieza(movim[1], movim[2], siExclusiva=True)
                    else:
                        return

            if self.procesador.gestor:
                cpu.runLineal()

        else:
            for movim in liMovs:
                if movim[0] == "b":
                    self.tablero.borraPieza(movim[1])
                elif movim[0] == "m":
                    self.tablero.muevePieza(movim[1], movim[2])
                elif movim[0] == "c":
                    self.tablero.cambiaPieza(movim[1], movim[2])

        # Aprovechamos que esta operacion se hace en cada move
        self.atajosRatonReset()

    def numDatos(self):
        return self.pgn.numDatos()

    def put_view(self):
        if not hasattr(self.pgn, "move"):  # gestor60 por ejemplo
            return
        fila, columna = self.main_window.pgnPosActual()
        pos_move, move = self.pgn.move(fila, columna.clave)

        if self.main_window.siCapturas or self.main_window.siInformacionPGN or self.kibitzers_manager.some_working():
            if move:
                dic = move.position.capturas_diferencia()
                if move.analysis:
                    mrm, pos = move.analysis
                    if pos:  # no se muestra la mejor move si es la realizada
                        rm0 = mrm.mejorMov()
                        self.tablero.ponFlechaSCvar([(rm0.from_sq, rm0.to_sq)])

            else:
                dic = self.game.last_position.capturas_diferencia()

            nomApertura = ""
            opening = self.game.opening
            if opening:
                nomApertura = opening.trNombre
            if self.main_window.siCapturas:
                self.main_window.ponCapturas(dic)
            if self.main_window.siInformacionPGN:
                if (fila == 0 and columna.clave == "NUMERO") or fila < 0:
                    self.main_window.ponInformacionPGN(self.game, None, nomApertura)
                else:
                    self.main_window.ponInformacionPGN(None, move, nomApertura)

            if self.kibitzers_manager.some_working():
                if self.si_mira_kibitzers():
                    self.mira_kibitzers(move, columna.clave)
                else:
                    self.kibitzers_manager.stop()

    def si_mira_kibitzers(self):
        return (self.state == ST_ENDGAME) or (not self.siCompetitivo)
        # self.game_type in (GT_POSITIONS, GT_AGAINST_PGN, GT_AGAINST_ENGINE, GT_TACTICS, GT_AGAINST_GM, GT_ALONE, GT_BOOK, GT_OPENINGS) or
        # (self.game_type in (GT_ELO, GT_MICELO) and ))

    def mira_kibitzers(self, move, columnaClave, only_last=False):
        if move:
            fenBase = move.position_before.fen()
            fen = fenBase if columnaClave == "NUMERO" else move.position.fen()
        else:
            fen = self.game.last_position.fen()
            fenBase = fen
        self.kibitzers_manager.put_fen(fen, fenBase, only_last)

    def ponPiezasAbajo(self, is_white):
        self.tablero.ponerPiezasAbajo(is_white)

    def quitaAyudas(self, siTambienTutorAtras=True, siQuitarAtras=True):
        self.main_window.quitaAyudas(siTambienTutorAtras, siQuitarAtras)
        self.is_tutor_enabled = False
        self.ponActivarTutor(False)

    def ponAyudas(self, ayudas, siQuitarAtras=True):
        self.main_window.ponAyudas(ayudas, siQuitarAtras)

    def pensando(self, siPensando):
        self.main_window.pensando(siPensando)

    def ponActivarTutor(self, siActivar):
        self.main_window.ponActivarTutor(siActivar)
        self.is_tutor_enabled = siActivar

    def cambiaActivarTutor(self):
        self.is_tutor_enabled = not self.is_tutor_enabled
        self.ponActivarTutor(self.is_tutor_enabled)

    def disable_all(self):
        self.tablero.disable_all()

    def activaColor(self, is_white):
        self.tablero.activaColor(is_white)

    def mostrarIndicador(self, siPoner):
        self.tablero.indicadorSC.setVisible(siPoner)

    def ponIndicador(self, is_white):
        self.tablero.ponIndicador(is_white)

    def set_dispatcher(self, funcMensajero):
        self.tablero.set_dispatcher(funcMensajero, self.atajosRaton)

    def ponFlechaSC(self, from_sq, to_sq, lipvvar=None):
        self.tablero.ponFlechaSC(from_sq, to_sq)
        self.tablero.quitaFlechas()
        if lipvvar:
            self.tablero.ponFlechaSCvar(lipvvar)

    def reponPieza(self, posic):
        self.tablero.reponPieza(posic)

    def ponRotulo1(self, mensaje):
        return self.main_window.ponRotulo1(mensaje)

    def ponRotulo2(self, mensaje):
        return self.main_window.ponRotulo2(mensaje)

    def ponRotulo3(self, mensaje):
        return self.main_window.ponRotulo3(mensaje)

    def quitaRotulo3(self):
        return self.main_window.ponRotulo3(None)

    def alturaRotulo3(self, px):
        return self.main_window.alturaRotulo3(px)

    def ponRevision(self, siPoner):
        if not self.siRevision:
            siPoner = False
        self.main_window.ponRevision(siPoner)

    def beepExtendido(self, siNuestro=False):
        if siNuestro:
            if not self.configuracion.x_sound_our:
                return
        if self.configuracion.x_sound_move:
            if len(self.game):
                move = self.game.move(-1)
                self.runSound.playLista(move.listaSonidos(), siEsperar=True)
        elif self.configuracion.x_sound_beep:
            self.runSound.playBeep()

    def beepZeitnot(self):
        self.runSound.playZeitnot()

    def beepResultadoCAMBIAR(self, resfinal):  # TOO Cambiar por beepresultado1
        if not self.configuracion.x_sound_results:
            return
        dic = {
            RS_WIN_PLAYER: "GANAMOS",
            RS_WIN_OPPONENT: "GANARIVAL",
            RS_DRAW: "TABLAS",
            RS_DRAW_REPETITION: "TABLASREPETICION",
            RS_DRAW_50: "TABLAS50",
            RS_DRAW_MATERIAL: "TABLASFALTAMATERIAL",
            RS_WIN_PLAYER_TIME: "GANAMOSTIEMPO",
            RS_WIN_OPPONENT_TIME: "GANARIVALTIEMPO",
        }
        if resfinal in dic:
            self.runSound.playClave(dic[resfinal])

    def beepResultado(self, beep):
        if beep:
            if not self.configuracion.x_sound_results:
                return
            self.runSound.playClave(beep)

    def pgnRefresh(self, is_white):
        self.main_window.pgnRefresh(is_white)

    def refresh(self):
        self.tablero.escena.update()
        self.main_window.update()
        QTUtil.refresh_gui()

    def mueveJugada(self, tipo):
        game = self.game
        if not len(game):
            return
        fila, columna = self.main_window.pgnPosActual()

        key = columna.clave
        if key == "NUMERO":
            is_white = tipo == "-"
            fila -= 1
        else:
            is_white = key != "NEGRAS"

        if_starts_with_black = game.if_starts_with_black

        lj = len(game)
        if if_starts_with_black:
            lj += 1
        ultFila = (lj - 1) / 2
        siUltBlancas = lj % 2 == 1

        if tipo == GO_BACK:
            if is_white:
                fila -= 1
            is_white = not is_white
            pos = fila * 2
            if not is_white:
                pos += 1
            if fila < 0 or (fila == 0 and pos == 0 and if_starts_with_black):
                self.ponteAlPrincipio()
                return
        elif tipo == GO_FORWARD:
            if not is_white:
                fila += 1
            is_white = not is_white
        elif tipo == GO_START:
            self.ponteAlPrincipio()
            return
        elif tipo == GO_END:
            fila = ultFila
            is_white = not game.last_position.is_white

        if fila == ultFila:
            if siUltBlancas and not is_white:
                return

        if fila < 0 or fila > ultFila:
            self.refresh()
            return
        if fila == 0 and is_white and if_starts_with_black:
            is_white = False

        self.main_window.pgnColocate(fila, is_white)
        self.pgnMueve(fila, is_white)

    def ponteEnJugada(self, numJugada):
        fila = (numJugada + 1) / 2 if self.game.if_starts_with_black else numJugada / 2
        move = self.game.move(numJugada)
        is_white = move.position_before.is_white
        self.main_window.pgnColocate(fila, is_white)
        self.pgnMueve(fila, is_white)

    def ponteAlPrincipio(self):
        self.setposition(self.game.first_position)
        self.main_window.base.pgn.goto(0, 0)
        self.main_window.base.pgnRefresh()  # No se puede usar pgnRefresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
        self.put_view()

    def ponteAlPrincipioColor(self):
        if self.game.li_moves:
            move = self.game.move(0)
            self.setposition(move.position)
            self.main_window.base.pgn.goto(0, 2 if move.position.is_white else 1)
            self.tablero.ponFlechaSC(move.from_sq, move.to_sq)
            self.main_window.base.pgnRefresh()  # No se puede usar pgnRefresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
            self.put_view()
        else:
            self.ponteAlPrincipio()

    def pgnMueve(self, fila, is_white):
        self.pgn.mueve(fila, is_white)
        self.put_view()

    def pgnMueveBase(self, fila, columna):
        if columna == "NUMERO":
            if fila == 0:
                self.ponteAlPrincipio()
                return
            else:
                fila -= 1
        self.pgn.mueve(fila, columna == "BLANCAS")
        self.put_view()

    def goto_end(self):
        if len(self.game):
            self.mueveJugada(GO_END)
        else:
            self.setposition(self.game.first_position)
            self.main_window.base.pgnRefresh()  # No se puede usar pgnRefresh, ya que se usa con gobottom en otros lados y aqui eso no funciona
        self.put_view()

    def jugadaActual(self):
        game = self.game
        fila, columna = self.main_window.pgnPosActual()
        is_white = columna.clave != "NEGRAS"
        if_starts_with_black = game.if_starts_with_black

        num_moves = len(game)
        if num_moves == 0:
            return 0, -1, -1, game.first_position.is_white
        nj = fila * 2
        if not is_white:
            nj += 1
        if if_starts_with_black:
            nj -= 1
        return num_moves, nj, fila, is_white

    def pgnInformacion(self):
        if self.informacionActivable:
            self.main_window.activaInformacionPGN()
            self.put_view()

    def quitaInformacion(self, siActivable=False):
        self.main_window.activaInformacionPGN(False)
        self.informacionActivable = siActivable

    def guardarPGN(self):
        conf = self.configuracion

        if conf.x_save_pgn:

            try:
                with open(conf.x_save_pgn, "at", encoding="utf-8", errors="ignore") as q:
                    dato = self.pgn.actual() + "\n\n"
                    q.write(dato.replace("\n", "\r\n"))
            except:
                QTUtil.ponPortapapeles(self.pgn.actual())
                QTUtil2.message_error(
                    self.main_window,
                    "%s : %s\n\n%s"
                    % (
                        _("Unable to save"),
                        conf.x_save_pgn,
                        _("It is saved in the clipboard to paste it wherever you want."),
                    ),
                )

    def guardarGanados(self, siGanado):
        conf = self.configuracion

        if siGanado:
            siSalvar = conf.x_save_won
        else:
            siSalvar = conf.x_save_lost

        if siSalvar:
            self.guardarPGN()

    def guardarNoTerminados(self):
        if len(self.game) < 2:
            return

        conf = self.configuracion

        if conf.x_save_unfinished:
            if not QTUtil2.pregunta(self.main_window, _("Do you want to save this game?")):
                return
            self.guardarPGN()

    def ponCapPorDefecto(self):
        self.capturasActivable = True
        if self.configuracion.x_captures_activate:
            self.main_window.activaCapturas(True)
            self.put_view()

    def ponInfoPorDefecto(self):
        self.informacionActivable = True
        if self.configuracion.x_info_activate:
            self.main_window.activaInformacionPGN(True)
            self.put_view()

    def ponCapInfoPorDefecto(self):
        self.ponCapPorDefecto()
        self.ponInfoPorDefecto()

    def capturas(self):
        if self.capturasActivable:
            self.main_window.activaCapturas()
            self.put_view()

    def quitaCapturas(self):
        self.main_window.activaCapturas(False)
        self.put_view()

    def nonDistractMode(self):
        self.nonDistract = self.main_window.base.nonDistractMode(self.nonDistract)
        self.main_window.ajustaTam()

    def boardRightMouse(self, siShift, siControl, siAlt):
        self.tablero.lanzaDirector()

    def gridRightMouse(self, siShift, siControl, siAlt):
        if siControl:
            self.capturas()
        elif siAlt:
            self.nonDistract = self.main_window.base.nonDistractMode(self.nonDistract)
        else:
            self.pgnInformacion()
        self.main_window.ajustaTam()

    def listado(self, tipo):
        if tipo == "pgn":
            return self.pgn.actual()
        elif tipo == "fen":
            return self.fenActivoConInicio()
        elif tipo == "fns":
            return self.game.fensActual()

    def jugadaActiva(self):
        fila, columna = self.main_window.pgnPosActual()
        is_white = columna.clave != "NEGRAS"
        pos = fila * 2
        if not is_white:
            pos += 1
        if self.game.if_starts_with_black:
            pos -= 1
        tam_lj = len(self.game)
        siUltimo = (pos + 1) >= tam_lj
        if siUltimo:
            pos = tam_lj - 1
        return pos, self.game.move(pos) if tam_lj else None

    def fenActivo(self):
        pos, move = self.jugadaActiva()
        return move.position.fen() if move else self.fenUltimo()

    def fenActivoConInicio(self):
        pos, move = self.jugadaActiva()
        if pos == 0:
            fila, columna = self.main_window.pgnPosActual()
            if columna.clave == "NUMERO":
                return self.game.first_position.fen()
        return move.position.fen() if move else self.fenUltimo()

    def fenUltimo(self):
        return self.game.fenUltimo()

    def fenPrevio(self):
        fila, columna = self.main_window.pgnPosActual()
        is_white = columna.clave != "NEGRAS"
        pos = fila * 2
        if not is_white:
            pos += 1
        if self.game.if_starts_with_black:
            pos -= 1
        tam_lj = len(self.game)
        if 0 <= pos < tam_lj:
            return self.game.move(pos).position_before.fen()
        else:
            return self.game.first_position.fen()

    def analizaTutor(self):
        self.pensando(True)
        fen = self.game.last_position.fen()
        if not self.is_finished():
            self.mrmTutor = self.xtutor.analiza(fen)
        else:
            self.mrmTutor = None
        self.pensando(False)
        return self.mrmTutor

    def cambioTutor(self):
        if PantallaTutor.cambioTutor(self.main_window, self.configuracion):
            self.procesador.cambiaXTutor()
            self.xtutor = self.procesador.XTutor()
            self.ponRotulo2(_("Tutor") + ": <b>" + self.xtutor.name)
            self.is_analyzed_by_tutor = False

            if self.game_type == GT_AGAINST_ENGINE:
                self.analizaInicio()

    def is_finished(self):
        return self.game.is_finished()

    def dameJugadaEn(self, fila, key):
        is_white = key != "NEGRAS"

        pos = fila * 2
        if not is_white:
            pos += 1
        if self.game.if_starts_with_black:
            pos -= 1
        tam_lj = len(self.game)
        if tam_lj == 0:
            return
        siUltimo = (pos + 1) >= tam_lj

        move = self.game.move(pos)
        return move, is_white, siUltimo, tam_lj, pos

    def ayudaMover(self, max_recursion):
        if not self.is_finished():
            move = Move.Move(self.game, position_before=self.game.last_position.copia())
            Analisis.show_analysis(
                self.procesador, self.xtutor, move, self.tablero.is_white_bottom, max_recursion, 0, must_save=False
            )

    def analizaPosicion(self, fila, key):
        if fila < 0:
            return

        # siShift, siControl, siAlt = QTUtil.kbdPulsado() # Antes de que analice
        move, is_white, siUltimo, tam_lj, pos_jg = self.dameJugadaEn(fila, key)
        if not move:
            return

        if self.state == ST_ENDGAME:
            max_recursion = 9999
        else:
            if not (
                self.game_type
                in [
                    GT_POSITIONS,
                    GT_AGAINST_PGN,
                    GT_AGAINST_ENGINE,
                    GT_AGAINST_GM,
                    GT_ALONE,
                    GT_BOOK,
                    GT_OPENINGS,
                    GT_TACTICS,
                ]
                or (self.game_type in [GT_ELO, GT_MICELO] and not self.siCompetitivo)
            ):
                if siUltimo or self.ayudas == 0:
                    return
                max_recursion = tam_lj - pos_jg - 3  # %#
            else:
                max_recursion = 9999
        if move.analysis is None:
            siCancelar = self.xtutor.motorTiempoJugada > 5000 or self.xtutor.motorProfundidad > 7
            me = QTUtil2.mensEspera.inicio(
                self.main_window, _("Analyzing the move...."), position="ad", siCancelar=siCancelar
            )
            if siCancelar:

                def test_me(txt):
                    return not me.cancelado()

                self.xanalyzer.ponGuiDispatch(test_me)
            mrm, pos = self.xanalyzer.analizaJugadaPartida(
                self.game, pos_jg, self.xtutor.motorTiempoJugada, self.xtutor.motorProfundidad
            )
            if siCancelar:
                if me.cancelado():
                    me.final()
                    return
            move.analysis = mrm, pos
            me.final()

        Analisis.show_analysis(self.procesador, self.xtutor, move, self.tablero.is_white_bottom, max_recursion, pos_jg)
        self.put_view()

    def analizar(self):
        Analisis.analyse_game(self)
        self.refresh()

    def borrar(self):
        separador = FormLayout.separador
        li_del = [separador]
        li_del.append(separador)
        li_del.append((_("Variations") + ":", False))
        li_del.append(separador)
        li_del.append((_("Ratings") + ":", False))
        li_del.append(separador)
        li_del.append((_("Comments") + ":", False))
        li_del.append(separador)
        li_del.append((_("Analysis") + ":", False))
        li_del.append(separador)
        li_del.append((_("All") + ":", False))
        resultado = FormLayout.fedit(li_del, title=_("Remove"), parent=self.main_window, icon=Iconos.Delete())
        if resultado:
            variations, ratings, comments, analysis, all = resultado[1]
            if all:
                variations, ratings, comments, analysis = True, True, True, True
            for move in self.game.li_moves:
                if variations:
                    move.del_variations()
                if ratings:
                    move.del_nags()
                if comments:
                    move.del_comment()
                if analysis:
                    move.del_analysis()
            self.main_window.base.pgnRefresh()
            self.refresh()

    def cambiaRival(self, nuevo):
        self.procesador.cambiaRival(nuevo)

    def pelicula(self):
        resp = Pelicula.paramPelicula(self.configuracion, self.main_window)
        if resp is None:
            return

        segundos, siInicio, siPGN = resp

        self.xpelicula = Pelicula.Pelicula(self, segundos, siInicio, siPGN)

    def ponRutinaAccionDef(self, rutina):
        self.xRutinaAccionDef = rutina

    def rutinaAccionDef(self, key):
        if self.xRutinaAccionDef:
            self.xRutinaAccionDef(key)
        elif key == TB_CLOSE:
            self.procesador.reset()
        else:
            self.procesador.run_action(key)

    def finalX0(self):
        # Se llama from_sq la main_window al pulsar X
        # Se comprueba si estamos en la pelicula
        if self.xpelicula:
            self.xpelicula.terminar()
            return False
        return self.final_x()

    def exePulsadoNum(self, siActivar, number):
        if number in [1, 8]:
            if siActivar:
                # Que move esta en el tablero
                fen = self.fenActivoConInicio()
                is_white = " w " in fen
                if number == 1:
                    siMB = is_white
                else:
                    siMB = not is_white
                self.tablero.quitaFlechas()
                if self.tablero.flechaSC:
                    self.tablero.flechaSC.hide()
                li = FasterCode.getCaptures(fen, siMB)
                for m in li:
                    d = m.from_sq()
                    h = m.to_sq()
                    self.tablero.creaFlechaMov(d, h, "c")
            else:
                self.tablero.quitaFlechas()
                if self.tablero.flechaSC:
                    self.tablero.flechaSC.show()

        elif number in [2, 7]:
            if siActivar:
                # Que move esta en el tablero
                fen = self.fenActivoConInicio()
                is_white = " w " in fen
                if number == 2:
                    siMB = is_white
                else:
                    siMB = not is_white
                if siMB != is_white:
                    fen = FasterCode.fen_other(fen)
                cp = Position.Position()
                cp.read_fen(fen)
                liMovs = cp.aura()

                self.liMarcosTmp = []
                regMarco = TabTipos.Marco()
                color = self.tablero.config_board.flechaActivoDefecto().colorinterior
                if color == -1:
                    color = self.tablero.config_board.flechaActivoDefecto().color

                st = set()
                for h8 in liMovs:
                    if not (h8 in st):
                        regMarco.a1h8 = h8 + h8
                        regMarco.siMovible = True
                        regMarco.color = color
                        regMarco.colorinterior = color
                        regMarco.opacidad = 0.5
                        marco = self.tablero.creaMarco(regMarco)
                        self.liMarcosTmp.append(marco)
                        st.add(h8)

            else:
                for marco in self.liMarcosTmp:
                    self.tablero.xremoveItem(marco)
                self.liMarcosTmp = []

    def exePulsadaLetra(self, siActivar, letra):
        if siActivar:
            dic = {
                "a": GO_START,
                "b": GO_BACK,
                "c": GO_BACK,
                "d": GO_BACK,
                "e": GO_FORWARD,
                "f": GO_FORWARD,
                "g": GO_FORWARD,
                "h": GO_END,
            }
            self.mueveJugada(dic[letra])

    def kibitzers(self, orden):
        if orden == "edit":
            self.kibitzers_manager.edit()

        else:
            nkibitzer = int(orden)
            self.kibitzers_manager.run_new(nkibitzer)
            fila, columna = self.main_window.pgnPosActual()
            pos_move, move = self.pgn.move(fila, columna.clave)
            self.mira_kibitzers(move, columna.clave, True)

    def paraHumano(self):
        self.human_is_playing = False
        self.disable_all()

    def sigueHumano(self):
        self.human_is_playing = True
        self.activaColor(self.game.last_position.is_white)

    def checkmueve_humano(self, from_sq, to_sq, promotion, with_premove=False):
        if self.human_is_playing:
            if not with_premove:
                self.paraHumano()
        else:
            self.sigueHumano()
            return None

        movimiento = from_sq + to_sq

        # Peon coronando
        if not promotion and self.game.last_position.siPeonCoronando(from_sq, to_sq):
            promotion = self.tablero.peonCoronando(self.game.last_position.is_white)
            if promotion is None:
                self.sigueHumano()
                return None
        if promotion:
            movimiento += promotion

        siBien, self.error, move = Move.dameJugada(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if siBien:
            return move
        else:
            self.sigueHumano()
            return None

    def librosConsulta(self, siEnVivo):
        w = PantallaArbolBook.PantallaArbolBook(self, siEnVivo)
        if w.exec_():
            return w.resultado
        else:
            return None

    def compruebaDGT(self):
        if self.configuracion.x_digital_board:
            if not DGT.activarSegunON_OFF(self.dgt):  # Error
                QTUtil2.message_error(self.main_window, _("Error, could not detect the %s board driver.") % self.configuracion.x_digital_board)
            else:
                self.dgt_setposition()

    def dgt(self, quien, a1h8):
        if self.tablero.mensajero and self.tablero.siActivasPiezas:
            if quien == "whiteMove":
                if not self.tablero.siActivasPiezasColor:
                    return 0
            elif quien == "blackMove":
                if self.tablero.siActivasPiezasColor:
                    return 0
            elif quien == "scan":
                QTUtil.ponPortapapeles(a1h8)
                return 1
            else:
                return 1

            if self.tablero.mensajero(a1h8[:2], a1h8[2:4], a1h8[4:]):
                return 1
            return 0

        return 1

    def setposition(self, position):
        self.tablero.setposition(position)

    def dgt_setposition(self):
        DGT.setposition(self.game)

    def juegaPorMi(self):
        if (
            self.plays_instead_of_me_option
            and self.state == ST_PLAYING
            and (self.ayudas or self.game_type in (GT_AGAINST_ENGINE, GT_ALONE, GT_POSITIONS, GT_TACTICS))
        ):
            if not self.is_finished():
                mrm = self.analizaTutor()
                rm = mrm.mejorMov()
                if rm.from_sq:
                    self.is_analyzed_by_tutor = True
                    self.mueve_humano(rm.from_sq, rm.to_sq, rm.promotion)
                    if self.ayudas:
                        self.ayudas -= 1
                        if self.ayudas:
                            self.ponAyudas(self.ayudas)
                        else:
                            self.quitaAyudas()

    def control1(self):
        self.juegaPorMi()

    def configurar(self, liMasOpciones=None, siCambioTutor=False, siSonidos=False, siBlinfold=True):
        menu = QTVarios.LCMenu(self.main_window)

        # Vista
        menuVista = menu.submenu(_("View"), Iconos.Vista())
        menuVista.opcion("vista_pgn", _("PGN information"), Iconos.InformacionPGNUno())
        menuVista.separador()
        menuVista.opcion("vista_capturas", _("Captured material"), Iconos.Capturas())
        menu.separador()

        # DGT
        dboard = self.configuracion.x_digital_board
        if dboard:
            menu.opcion("dgt", _("Disable %s board") % dboard if DGT.siON() else _("Enable %s board") % dboard, Iconos.DGT())
            menu.separador()

        # Ciega - Mostrar todas - Ocultar blancas - Ocultar negras
        if siBlinfold:
            menuCG = menu.submenu(_("Blindfold chess"), Iconos.Ojo())

            si = self.tablero.blindfold
            if si:
                ico = Iconos.Naranja()
                tit = _("Deactivate")
            else:
                ico = Iconos.Verde()
                tit = _("Activate")
            menuCG.opcion("cg_change", tit, ico)
            menuCG.separador()
            menuCG.opcion("cg_conf", _("Configuration"), Iconos.Opciones())
            menuCG.separador()
            menuCG.opcion("cg_pgn", "%s: %s" % (_("PGN"), _("Hide") if self.pgn.siMostrar else _("Show")), Iconos.PGN())

        # Sonidos
        if siSonidos:
            menu.separador()
            menu.opcion("sonido", _("Sounds"), Iconos.S_Play())

        # Cambio de tutor
        if siCambioTutor:
            menu.separador()
            menu.opcion("tutor", _("Tutor change"), Iconos.Tutor())

        menu.separador()
        menu.opcion("motores", _("External engines"), Iconos.Motores())

        # On top
        menu.separador()
        rotulo = _("Disable") if self.main_window.onTop else _("Enable")
        menu.opcion(
            "ontop",
            "%s: %s" % (rotulo, _("window on top")),
            Iconos.Bottom() if self.main_window.onTop else Iconos.Top(),
        )

        # Right mouse
        menu.separador()
        rotulo = _("Disable") if self.configuracion.x_direct_graphics else _("Enable")
        menu.opcion(
            "mouseGraphics", "%s: %s" % (rotulo, _("Live graphics with the right mouse button")), Iconos.RightMouse()
        )

        # Logs of engines
        listaGMotores = Code.list_engine_managers.listaActivos() if Code.list_engine_managers else []
        menu.separador()
        smenu = menu.submenu(_("Save engines log"), Iconos.Grabar())
        if len(listaGMotores) > 0:
            for pos, gmotor in enumerate(listaGMotores):
                ico = Iconos.Cancelar() if gmotor.ficheroLog else Iconos.PuntoVerde()
                smenu.opcion("log_%d" % pos, gmotor.name, ico)

        smenu.separador()
        if self.configuracion.x_log_engines:
            smenu.opcion("log_noall", _("Always deactivated for all engines"), Iconos.Cancelar())
        else:
            smenu.opcion("log_yesall", _("Always activated for all engines"), Iconos.Aceptar())

        menu.separador()

        # Mas Opciones
        if liMasOpciones:
            menu.separador()
            for key, rotulo, icono in liMasOpciones:
                if rotulo is None:
                    menu.separador()
                else:
                    menu.opcion(key, rotulo, icono)

        resp = menu.lanza()
        if resp:

            if liMasOpciones:
                for key, rotulo, icono in liMasOpciones:
                    if resp == key:
                        return resp

            if resp.startswith("log_"):
                resp = resp[4:]
                self.log_engines(resp)

            if resp.startswith("vista_"):
                resp = resp[6:]
                if resp == "pgn":
                    self.main_window.activaInformacionPGN()
                    self.put_view()
                elif resp == "capturas":
                    self.main_window.activaCapturas()
                    self.put_view()

            elif resp == "dgt":
                DGT.cambiarON_OFF()
                self.compruebaDGT()

            elif resp == "sonido":
                self.config_sonido()

            elif resp == "tutor":
                self.cambioTutor()

            elif resp == "motores":
                self.procesador.motoresExternos()

            elif resp == "ontop":
                self.main_window.onTopWindow()

            elif resp == "mouseGraphics":
                self.configuracion.x_direct_graphics = not self.configuracion.x_direct_graphics
                self.configuracion.graba()

            elif resp.startswith("cg_"):
                orden = resp[3:]
                if orden == "pgn":
                    self.pgn.siMostrar = not self.pgn.siMostrar
                    self.main_window.base.pgnRefresh()
                elif orden == "change":
                    x = str(self)
                    modoPosicionBlind = False
                    for tipo in ("GestorEntPos",):
                        if tipo in x:
                            modoPosicionBlind = True
                    self.tablero.blindfoldChange(modoPosicionBlind)

                elif orden == "conf":
                    self.tablero.blindfoldConfig()

        return None

    def log_engines(self, resp):
        if resp.isdigit():
            resp = int(resp)
            engine = Code.list_engine_managers.listaActivos()[resp]
            if engine.ficheroLog:
                engine.log_close()
            else:
                engine.log_open()
        else:
            listaGMotores = Code.list_engine_managers.listaActivos()
            if resp == "yesall":
                self.configuracion.x_log_engines = True
            else:
                self.configuracion.x_log_engines = False
            for gmotor in listaGMotores:
                if resp == "yesall":
                    gmotor.log_open()
                else:
                    gmotor.log_close()
            self.configuracion.graba()

    def config_sonido(self):
        separador = FormLayout.separador
        liSon = [separador]
        liSon.append(separador)
        liSon.append((_("Beep after opponent's move") + ":", self.configuracion.x_sound_beep))
        liSon.append(separador)
        liSon.append((None, _("Sound on in") + ":"))
        liSon.append((_("Results") + ":", self.configuracion.x_sound_results))
        liSon.append((_("Rival moves") + ":", self.configuracion.x_sound_move))
        liSon.append(separador)
        liSon.append((_("Activate sounds with our moves") + ":", self.configuracion.x_sound_our))
        liSon.append(separador)
        resultado = FormLayout.fedit(
            liSon, title=_("Sounds"), parent=self.main_window, anchoMinimo=250, icon=Iconos.S_Play()
        )
        if resultado:
            self.configuracion.x_sound_beep, self.configuracion.x_sound_results, self.configuracion.x_sound_move, self.configuracion.x_sound_our = resultado[
                1
            ]
            self.configuracion.graba()

    def utilidades(self, liMasOpciones=None, siArbol=True):

        menu = QTVarios.LCMenu(self.main_window)

        siJugadas = len(self.game) > 0

        # Grabar
        icoGrabar = Iconos.Grabar()
        icoFichero = Iconos.GrabarFichero()
        icoCamara = Iconos.Camara()
        icoClip = Iconos.Clipboard()

        trFichero = _("Save to a file")
        trPortapapeles = _("Copy to clipboard")

        menuSave = menu.submenu(_("Save"), icoGrabar)

        menuSave.opcion("pgnfichero", _("PGN Format"), Iconos.PGN())

        menuSave.separador()

        menuFEN = menuSave.submenu(_("FEN Format"), Iconos.Naranja())
        menuFEN.opcion("fenfichero", trFichero, icoFichero)
        menuFEN.opcion("fenportapapeles", trPortapapeles, icoClip)

        menuSave.separador()

        menuFNS = menuSave.submenu(_("List of FENs"), Iconos.InformacionPGNUno())
        menuFNS.opcion("fnsfichero", trFichero, icoFichero)
        menuFNS.opcion("fnsportapapeles", trPortapapeles, icoClip)

        menuSave.separador()

        menuSave.opcion("lcsbfichero", "%s -> %s" % (_("lcsb Format"), _("Create your own game")), Iconos.JuegaSolo())

        menuSave.separador()

        menuDB = menuSave.submenu(_("Database"), Iconos.DatabaseMas())
        QTVarios.menuDB(menuDB, self.configuracion, True)
        menuSave.separador()

        menuV = menuSave.submenu(_("Board -> Image"), icoCamara)
        menuV.opcion("volfichero", trFichero, icoFichero)
        menuV.opcion("volportapapeles", trPortapapeles, icoClip)

        menu.separador()

        # Analizar
        if siJugadas:
            if not (self.game_type in (GT_ELO, GT_MICELO) and self.siCompetitivo and self.state == ST_PLAYING):
                nAnalisis = 0
                for move in self.game.li_moves:
                    if move.analysis:
                        nAnalisis += 1
                if nAnalisis > 4:
                    submenu = menu.submenu(_("Analysis"), Iconos.Analizar())
                else:
                    submenu = menu
                submenu.opcion("analizar", _("Analyze"), Iconos.Analizar())
                if nAnalisis > 4:
                    submenu.separador()
                    submenu.opcion("analizar_grafico", _("Show graphics"), Iconos.Estadisticas())
                menu.separador()

                menu.opcion("borrar", _("Remove"), Iconos.Delete())
                menu.separador()

        # Pelicula
        if siJugadas:
            menu.opcion("pelicula", _("Replay game"), Iconos.Pelicula())
            menu.separador()

        # Kibitzers
        if self.si_mira_kibitzers():
            menu.separador()
            menuKibitzers = menu.submenu(_("Kibitzers"), Iconos.Kibitzer())

            kibitzers = Kibitzers.Kibitzers()
            for num, (name, ico) in enumerate(kibitzers.lista_menu()):
                menuKibitzers.opcion("kibitzer_%d" % num, name, ico)
            menuKibitzers.separador()
            menuKibitzers.opcion("kibitzer_edit", _("Edition"), Iconos.ModificarP())

        # Juega por mi
        if (
            self.plays_instead_of_me_option
            and self.state == ST_PLAYING
            and (self.ayudas or self.game_type in (GT_AGAINST_ENGINE, GT_ALONE, GT_POSITIONS, GT_TACTICS))
        ):
            menu.separador()
            menu.opcion("juegapormi", _("Plays instead of me") + "  [^1]", Iconos.JuegaPorMi()),

        # Arbol de movimientos
        if siArbol:
            menu.separador()
            menu.opcion("arbol", _("Moves tree"), Iconos.Arbol())

        # Mas Opciones
        if liMasOpciones:
            menu.separador()
            submenu = menu
            for key, rotulo, icono in liMasOpciones:
                if rotulo is None:
                    if icono is None:
                        # liMasOpciones.append((None, None, None))
                        submenu.separador()
                    else:
                        # liMasOpciones.append((None, None, True))  # Para salir del submenu
                        submenu = menu
                elif key is None:
                    # liMasOpciones.append((None, titulo, icono))
                    submenu = menu.submenu(rotulo, icono)

                else:
                    # liMasOpciones.append((key, titulo, icono))
                    submenu.opcion(key, rotulo, icono)

        resp = menu.lanza()

        if not resp:
            return

        if liMasOpciones:
            for key, rotulo, icono in liMasOpciones:
                if resp == key:
                    return resp

        if resp == "juegapormi":
            self.juegaPorMi()

        elif resp == "analizar":
            self.analizar()

        elif resp == "analizar_grafico":
            self.show_analysis()

        elif resp == "borrar":
            self.borrar()

        elif resp == "pelicula":
            self.pelicula()

        elif resp.startswith("kibitzer_"):
            self.kibitzers(resp[9:])

        elif resp == "arbol":
            self.arbol()

        elif resp.startswith("vol"):
            accion = resp[3:]
            if accion == "fichero":
                resp = QTUtil2.salvaFichero(
                    self.main_window,
                    _("File to save"),
                    self.configuracion.x_save_folder,
                    "%s PNG (*.png)" % _("File"),
                    False,
                )
                if resp:
                    self.tablero.salvaEnImagen(resp, "png")

            else:
                self.tablero.salvaEnImagen()

        elif resp == "lcsbfichero":
            self.salva_lcsb()

        elif resp == "pgnfichero":
            self.salvar_pgn()

        elif resp.startswith("dbf_"):
            self.salvaDB(resp[4:])

        elif resp.startswith("fen") or resp.startswith("fns"):
            extension = resp[:3]
            si_fichero = resp.endswith("fichero")
            self.salvaFEN_FNS(extension, si_fichero)

        return None

    def mensajeEnPGN(self, mens, titulo=None):
        p0 = self.main_window.base.pgn.pos()
        p = self.main_window.mapToGlobal(p0)
        QTUtil2.message(self.main_window, mens, titulo=titulo, px=p.x(), py=p.y())

    def mensaje(self, mens, titulo=None):
        QTUtil2.message_bold(self.main_window, mens, titulo)

    def show_analysis(self):
        um = self.procesador.unMomento()
        elos = self.game.calc_elos(self.configuracion)
        elosFORM = self.game.calc_elosFORM(self.configuracion)
        alm = Histogram.genHistograms(self.game)
        alm.indexesHTML, alm.indexesRAW, alm.eloW, alm.eloB, alm.eloT = AnalisisIndexes.gen_indexes(
            self.game, elos, elosFORM, alm
        )
        alm.is_white_bottom = self.tablero.is_white_bottom
        um.final()
        PantallaAnalisis.showGraph(self.main_window, self, alm, Analisis.show_analysis)

    def salvaDB(self, database):
        pgn = self.listado("pgn")
        liTags = []
        for linea in pgn.split("\n"):
            if linea.startswith("["):
                ti = linea.split('"')
                if len(ti) == 3:
                    key = ti[0][1:].strip()
                    valor = ti[1].strip()
                    liTags.append([key, valor])
            else:
                break

        pc = Game.Game(li_tags=liTags)
        pc.leeOtra(self.game)

        db = DBgames.DBgames(database)
        resp = db.inserta(pc)
        db.close()
        if resp:
            QTUtil2.message_bold(self.main_window, _("Saved"))
        else:
            QTUtil2.message_error(self.main_window, _("This game already exists."))

    def salva_lcsb(self):
        pgn = self.listado("pgn")
        dic = self.procesador.save_lcsb(self.state, self.game, pgn)
        extension = "lcsb"
        fichero = self.configuracion.x_save_lcsb
        while True:
            fichero = QTUtil2.salvaFichero(
                self.main_window,
                _("File to save"),
                fichero,
                _("File") + " %s (*.%s)" % (extension, extension),
                siConfirmarSobreescritura=True,
            )
            if fichero:
                fichero = str(fichero)
                if os.path.isfile(fichero):
                    yn = QTUtil2.preguntaCancelar(
                        self.main_window,
                        _X(_("The file %1 already exists, what do you want to do?"), fichero),
                        si=_("Overwrite"),
                        no=_("Choose another"),
                    )
                    if yn is None:
                        break
                    if not yn:
                        continue
                direc = os.path.dirname(fichero)
                if direc != self.configuracion.save_lcsb():
                    self.configuracion.save_lcsb(direc)
                    self.configuracion.graba()

                name = os.path.basename(fichero)
                if Util.save_pickle(fichero, dic):
                    QTUtil2.mensajeTemporal(self.main_window, _X(_("Saved to %1"), name), 0.8)
                    return
                else:
                    QTUtil2.message_error(self.main_window, "%s: %s" % (_("Unable to save"), name))

            break

    def salvar_pgn(self):
        w = PantallaSavePGN.WSave(self.main_window, self.game, self.configuracion)
        w.exec_()

    def salvaFEN_FNS(self, extension, siFichero):
        dato = self.listado(extension)
        if siFichero:

            resp = QTUtil2.salvaFichero(
                self.main_window,
                _("File to save"),
                self.configuracion.x_save_folder,
                _("File") + " %s (*.%s)" % (extension, extension),
                False,
            )
            if resp:
                try:

                    modo = "w"
                    if Util.exist_file(resp):
                        yn = QTUtil2.preguntaCancelar(
                            self.main_window,
                            _X(_("The file %1 already exists, what do you want to do?"), resp),
                            si=_("Append"),
                            no=_("Overwrite"),
                        )
                        if yn is None:
                            return
                        if yn:
                            modo = "a"
                            dato = "\n" * 2 + dato
                    with open(resp, modo, encoding="utf-8", errors="ignore") as q:
                        q.write(dato.replace("\n", "\r\n"))
                    QTUtil2.message_bold(self.main_window, _X(_("Saved to %1"), resp))
                    direc = os.path.dirname(resp)
                    if direc != self.configuracion.x_save_folder:
                        self.configuracion.x_save_folder = direc
                        self.configuracion.graba()
                except:
                    QTUtil.ponPortapapeles(dato)
                    QTUtil2.message_error(
                        self.main_window,
                        "%s : %s\n\n%s"
                        % (_("Unable to save"), resp, _("It is saved in the clipboard to paste it wherever you want.")),
                    )

        else:
            QTUtil.ponPortapapeles(dato)

    def arbol(self):
        num_moves, nj, fila, is_white = self.jugadaActual()
        w = PantallaArbol.PantallaArbol(self.main_window, self.game, nj, self.procesador)
        w.exec_()

    def control0(self):
        fila, columna = self.main_window.pgnPosActual()
        num_moves, nj, fila, is_white = self.jugadaActual()
        if num_moves:
            self.game.is_finished()
            if fila == 0 and columna.clave == "NUMERO":
                fen = self.game.first_position.fen()
                nj = -1
            else:
                move = self.game.move(nj)
                fen = move.position.fen()

            pgn_active = self.pgn.actual()
            pgn = ""
            for linea in pgn_active.split("\n"):
                if linea.startswith("["):
                    pgn += linea.strip()
                else:
                    break

            p = self.game.copia(nj)
            pgn += p.pgnBaseRAW()
            pgn = pgn.replace("|", "-")

            siguientes = ""
            if nj < len(self.game) - 1:
                p = self.game.copiaDesde(nj + 1)
                siguientes = p.pgnBaseRAW(p.first_position.num_moves).replace("|", "-")

            txt = "%s||%s|%s\n" % (fen, siguientes, pgn)
            QTUtil.ponPortapapeles(txt)
            QTUtil2.mensajeTemporal(
                self.main_window, _("It is saved in the clipboard to paste it wherever you want."), 2
            )

    # Para elo games + entmaq
    def tablasPlayer(self):
        siAcepta = False
        njug = len(self.game)
        if len(self.lirm_engine) >= 4 and njug > 40:
            if njug > 100:
                limite = -100
            elif njug > 60:
                limite = -150
            else:
                limite = -200
            siAcepta = True
            for rm in self.lirm_engine[-4:]:
                if rm.centipawns_abs() > limite:
                    siAcepta = False
        if siAcepta:
            self.game.last_jg().is_draw_agreement = True
            self.game.set_termination(TERMINATION_DRAW_AGREEMENT, RS_DRAW)
        else:
            QTUtil2.message_bold(self.main_window, _("Sorry, but the engine doesn't accept a draw right now."))
        self.next_test_resign = 5
        return siAcepta

    def valoraRMrival(self):
        if len(self.game) < 50 or len(self.lirm_engine) <= 5:
            return True
        if self.next_test_resign:
            self.next_test_resign -= 1
            return True

        b = random.random() ** 0.33

        # Resign
        siResign = True
        for n, rm in enumerate(self.lirm_engine[-5:]):
            if int(rm.centipawns_abs() * b) > self.resign_limit:
                siResign = False
                break
        if siResign:
            resp = QTUtil2.pregunta(self.main_window, _X(_("%1 wants to resign, do you accept it?"), self.xrival.name))
            if resp:
                self.game.resign(self.is_engine_side_white)
                self.game.set_termination(TERMINATION_RESIGN, RESULT_WIN_BLACK if self.is_engine_side_white else RESULT_WIN_WHITE)
                return False
            else:
                self.next_test_resign = 9
                return True

        # # Draw
        siDraw = True
        for rm in self.lirm_engine[-5:]:
            pts = rm.centipawns_abs()
            if (not (-250 < int(pts * b) < -100)) or pts < -250:
                siDraw = False
                break
        if siDraw:
            resp = QTUtil2.pregunta(self.main_window, _X(_("%1 proposes draw, do you accept it?"), self.xrival.name))
            if resp:
                self.game.last_jg().is_draw_agreement = True
                self.game.set_termination(TERMINATION_DRAW_AGREEMENT, RESULT_DRAW)
                return False
            else:
                self.next_test_resign = 9
                return True

        return True

    def utilidadesElo(self):
        if self.siCompetitivo:
            self.utilidades(siArbol=False)
        else:
            liMasOpciones = (("libros", _("Consult a book"), Iconos.Libros()),)

            resp = self.utilidades(liMasOpciones, siArbol=True)
            if resp == "libros":
                liMovs = self.librosConsulta(True)
                if liMovs:
                    for x in range(len(liMovs) - 1, -1, -1):
                        from_sq, to_sq, promotion = liMovs[x]
                        self.mueve_humano(from_sq, to_sq, promotion)

    def pgnInformacionMenu(self):
        menu = QTVarios.LCMenu(self.main_window)

        for key, valor in self.game.dicTags().items():
            siFecha = key.upper().endswith("DATE")
            if key.upper() == "FEN":
                continue
            if siFecha:
                valor = valor.replace(".??", "").replace(".?", "")
            valor = valor.strip("?")
            if valor:
                menu.opcion(key, "%s : %s" % (key, valor), Iconos.PuntoAzul())

        menu.lanza()

    def saveSelectedPosition(self, lineaTraining):
        # Llamado from_sq GestorEnPos and GestorEntTac, para salvar la position tras pulsar una P
        with open(self.configuracion.ficheroSelectedPositions, "at", encoding="utf-8", errors="ignore") as q:
            q.write(lineaTraining + "\n")
        QTUtil2.mensajeTemporal(
            self.main_window, _('Position saved in "%s" file.' % self.configuracion.ficheroSelectedPositions), 2
        )
        self.procesador.entrenamientos.menu = None

    def jugarPosicionActual(self):
        fila, columna = self.main_window.pgnPosActual()
        num_moves, nj, fila, is_white = self.jugadaActual()
        if num_moves:
            self.game.is_finished()
            gm = self.game.copia(nj)
            gm.set_unknown()
            if fila == 0 and columna.clave == "NUMERO":
                posicion = self.game.first_position
            else:
                move = self.game.move(nj)
                posicion = move.position
            dic = {
                "GAME": gm.save(),
                "ISWHITE": posicion.is_white
            }
            fich = Util.relative_path(self.configuracion.ficheroTemporal(".pkd"))
            Util.save_pickle(fich, dic)

            XRun.run_lucas("-play", fich)

    def showPV(self, pv, nArrows):
        if not pv:
            return True
        self.tablero.quitaFlechas()
        tipo = "mt"
        opacidad = 100
        pv = pv.strip()
        while "  " in pv:
            pv = pv.replace("  ", " ")
        lipv = pv.split(" ")
        npv = len(lipv)
        nbloques = min(npv, nArrows)
        salto = (80 - 15) * 2 / (nbloques - 1) if nbloques > 1 else 0
        cambio = max(30, salto)

        for n in range(nbloques):
            pv = lipv[n]
            self.tablero.creaFlechaMov(pv[:2], pv[2:4], tipo + str(opacidad))
            if n % 2 == 1:
                opacidad -= cambio
                cambio = salto
            tipo = "ms" if tipo == "mt" else "mt"
        return True

    def ponFlechasTutor(self, mrm, nArrows):
        self.tablero.quitaFlechas()
        if self.tablero.flechaSC:
            self.tablero.flechaSC.hide()

        rm_mejor = mrm.mejorMov()
        if not rm_mejor:
            return
        rm_peor = mrm.li_rm[-1]
        peso0 = rm_mejor.centipawns_abs()
        rango = peso0 - rm_peor.centipawns_abs()
        for n, rm in enumerate(mrm.li_rm, 1):
            peso = rm.centipawns_abs()
            factor = 1.0 - (peso0 - peso) * 1.0 / rango
            self.tablero.creaFlechaTutor(rm.from_sq, rm.to_sq, factor)
            if n >= nArrows:
                return
