import copy
import time

from PySide2 import QtCore

from Code import Apertura
from Code import Everest
from Code import Gestor
from Code.QT import PantallaJuicio
from Code.QT import QTUtil2
from Code.Constantes import *


class GestorEverest(Gestor.Gestor):
    def inicio(self, recno):

        self.expedition = Everest.Expedition(self.configuracion, recno)
        self.expedition.run()

        self.dic_analysis = {}

        self.siCompetitivo = True
        self.resultado = None
        self.human_is_playing = False
        self.analysis = None
        self.comment = None
        self.siAnalizando = False
        self.is_human_side_white = self.expedition.is_white
        self.is_engine_side_white = not self.expedition.is_white
        self.partidaObj = self.expedition.game
        self.game.set_tags(self.partidaObj.li_tags)
        self.numJugadasObj = self.partidaObj.num_moves()
        self.posJugadaObj = 0
        self.nombreObj = self.expedition.name

        self.xanalyzer.maximizaMultiPV()

        self.puntos = 0
        self.vtime = 0.0

        self.book = Apertura.AperturaPol(999)

        self.main_window.pon_toolbar((TB_CANCEL, TB_REINIT, TB_CONFIG))

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.quitaAyudas(True, True)

        self.set_dispatcher(self.mueve_humano)
        self.setposition(self.game.last_position)
        self.ponPiezasAbajo(self.is_human_side_white)
        self.mostrarIndicador(True)
        self.ponRotulo1(self.expedition.label())
        self.ponRotulo2("")

        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()
        self.dgt_setposition()

        self.state = ST_PLAYING
        self.siguiente_jugada()

    def ponPuntos(self):
        self.ponRotulo2("%s : <b>%d</b>" % (_("Points"), self.puntos))

    def run_action(self, key):
        if key == TB_CANCEL:
            self.cancelar()

        elif key == TB_REINIT:
            if not QTUtil2.pregunta(self.main_window, _("Restart the game?")):
                return
            change_game = self.restart(False)
            if change_game:
                self.terminar()
            else:
                self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True)

        elif key == TB_UTILITIES:
            self.utilidadesElo()

        elif key == TB_CLOSE:
            self.terminar()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def final_x(self):
        return self.cancelar()

    def cancelar(self):
        if self.posJugadaObj > 1 and self.state == ST_PLAYING:
            self.restart(False)
        self.terminar()
        return False

    def terminar(self):
        self.analizaTerminar()
        self.terminaNoContinuo()
        self.procesador.inicio()
        self.procesador.showEverest(self.expedition.recno)

    def reiniciar(self):
        self.game.set_position()
        self.posJugadaObj = 0
        self.puntos = 0
        self.ponPuntos()
        self.vtime = 0.0
        self.book = Apertura.AperturaPol(999)
        self.state = ST_PLAYING
        self.tablero.setposition(self.game.first_position)
        self.pgnRefresh(True)
        self.dgt_setposition()
        self.analizaFinal()
        self.terminaNoContinuo()

        self.ponRotulo1(self.expedition.label())
        self.ponPuntos()
        self.siguiente_jugada()

    def restart(self, lost_points):
        self.terminaNoContinuo()
        change_game = self.expedition.add_try(False, self.vtime, self.puntos)
        self.vtime = 0.0
        licoment = []
        if lost_points:
            licoment.append(_("You have exceeded the limit of lost points."))

        if change_game:
            licoment.append(_("You have exceeded the limit of tries, you will fall back to the previous."))
        elif lost_points:
            licoment.append(_("You must repeat the game from beginning."))
        if licoment:
            comment = "\n".join(licoment)
            w = PantallaJuicio.MensajeF(self.main_window, comment)
            w.mostrar()
        return change_game

    def analizaInicio(self):
        if not self.is_finished():
            self.xanalyzer.ac_inicio(self.game)
            self.siAnalizando = True

    def analizaMinimo(self, minTime):
        self.mrm = copy.deepcopy(self.xanalyzer.ac_minimo(minTime, False))
        return self.mrm

    def analizaEstado(self):
        self.xanalyzer.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xanalyzer.ac_estado())
        return self.mrm

    def analizaFinal(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xanalyzer.ac_final(-1)

    def analizaTerminar(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xanalyzer.terminar()

    def analizaNoContinuo(self):
        self.tiempoNoContinuo += 500
        if self.tiempoNoContinuo >= 5000:
            self.analizaMinimo(5)
            self.analizaFinal()
            self.pendienteNoContinuo = False
        else:
            QtCore.QTimer.singleShot(500, self.analizaNoContinuo)

    def analizaNoContinuoFinal(self):
        if self.tiempoNoContinuo < 5000:
            um = QTUtil2.analizando(self.main_window)
            self.analizaMinimo(5000)
            um.final()

    def terminaNoContinuo(self):
        if not self.continueTt:
            self.tiempoNoContinuo = 99999
            self.pendienteNoContinuo = False

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return

        if self.puntos < -self.expedition.tolerance:
            self.restart(True)
            self.state = ST_ENDGAME
            self.main_window.pon_toolbar((TB_CLOSE, TB_REINIT, TB_CONFIG, TB_UTILITIES))
            return
            # if change_game:
            #     self.terminar()
            #     return
            # self.reiniciar()

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()
        is_white = self.game.last_position.is_white

        num_moves = len(self.game)
        if num_moves >= self.numJugadasObj:
            self.put_result()
            return

        siRival = is_white == self.is_engine_side_white
        self.ponIndicador(is_white)

        # self.refresh()

        if siRival:
            self.add_move(False)
            self.siguiente_jugada()

        else:
            self.human_is_playing = True
            self.pensando(True)
            self.analizaInicio()
            self.activaColor(is_white)
            self.pensando(False)
            self.iniTiempo = time.time()
            if not self.continueTt:
                QtCore.QTimer.singleShot(1000, self.analizaNoContinuo)
                self.tiempoNoContinuo = 0
                self.pendienteNoContinuo = True

    def mueve_humano(self, from_sq, to_sq, promotion=""):
        jgUsu = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not jgUsu:
            return False

        self.vtime += time.time() - self.iniTiempo

        jgObj = self.partidaObj.move(self.posJugadaObj)
        fen = self.fenUltimo()

        siAnalizaJuez = True
        if self.book:
            siBookUsu = self.book.check_human(fen, from_sq, to_sq)
            siBookObj = self.book.check_human(fen, jgObj.from_sq, jgObj.to_sq)
            if siBookUsu and siBookObj:
                if jgObj.movimiento() != jgUsu.movimiento():
                    bmove = _("book move")
                    comment = "%s: %s %s<br>%s: %s %s" % (
                        self.nombreObj,
                        jgObj.pgn_translated(),
                        bmove,
                        self.configuracion.x_player,
                        jgUsu.pgn_translated(),
                        bmove,
                    )
                    w = PantallaJuicio.MensajeF(self.main_window, comment)
                    w.mostrar()
                siAnalizaJuez = False
            else:
                siAnalizaJuez = True
                if not siBookObj:
                    self.book = None

        analisis = None
        comment = None

        if siAnalizaJuez:
            position = self.game.last_position
            saved = fen in self.dic_analysis
            if saved:
                rmObj, posObj, analisis, mrm = self.dic_analysis[fen]
            else:
                if self.continueTt:
                    um = QTUtil2.analizando(self.main_window)
                    mrm = self.analizaMinimo(5000) if self.continueTt else self.mrm
                    um.final()
                else:
                    self.analizaNoContinuoFinal()
                    mrm = self.mrm
                rmObj, posObj = mrm.buscaRM(jgObj.movimiento())
                analisis = mrm, posObj
                self.dic_analysis[fen] = [rmObj, posObj, analisis, mrm]

            rmUsu, posUsu = mrm.buscaRM(jgUsu.movimiento())
            if rmUsu is None:
                um = QTUtil2.analizando(self.main_window)
                self.analizaFinal()
                rmUsu = self.xanalyzer.valora(position, from_sq, to_sq, promotion)
                mrm.agregaRM(rmUsu)
                self.analizaInicio()
                um.final()

            w = PantallaJuicio.WJuicio(
                self, self.xanalyzer, self.nombreObj, position, mrm, rmObj, rmUsu, analisis, siCompetitivo=False
            )
            w.exec_()

            if not saved:
                analisis = w.analysis
                self.dic_analysis[fen][2] = analisis

            dpts = w.difPuntos()
            self.puntos += dpts
            self.ponPuntos()

            if posUsu != posObj:
                comentarioUsu = " %s" % (rmUsu.abrTexto())
                comentarioObj = " %s" % (rmObj.abrTexto())

                comentarioPuntos = "%s = %d %+d %+d = %d" % (
                    _("Points"),
                    self.puntos - dpts,
                    rmUsu.centipawns_abs(),
                    -rmObj.centipawns_abs(),
                    self.puntos,
                )
                comment = "%s: %s %s\n%s: %s %s\n%s" % (
                    self.nombreObj,
                    jgObj.pgn_translated(),
                    comentarioObj,
                    self.configuracion.x_player,
                    jgUsu.pgn_translated(),
                    comentarioUsu,
                    comentarioPuntos,
                )
        if not self.continueTt:
            self.terminaNoContinuo()

        self.analizaFinal()

        self.add_move(True, analisis, comment)

        self.siguiente_jugada()
        return True

    def add_move(self, siNuestra, analisis=None, comment=None):
        move = self.partidaObj.move(self.posJugadaObj)
        self.posJugadaObj += 1
        if analisis:
            move.analysis = analisis
        if comment:
            move.comment = comment

        self.game.add_move(move)
        self.move_the_pieces(move.liMovs, True)
        self.tablero.setposition(move.position)
        self.ponFlechaSC(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)

        self.dgt_setposition()

    def put_result(self):
        self.analizaTerminar()
        self.disable_all()
        self.human_is_playing = False

        self.state = ST_ENDGAME

        mensaje = _("Congratulations you have passed this game.")
        self.expedition.add_try(True, self.vtime, self.puntos)

        self.mensajeEnPGN(mensaje)

        self.terminar()
