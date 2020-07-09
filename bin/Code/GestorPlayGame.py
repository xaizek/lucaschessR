import copy
import time

from Code import Util
from Code import Apertura
from Code import Game
from Code import Gestor
from Code.QT import PantallaJuicio
from Code.QT import QTUtil2
from Code.QT import PantallaPlayGame
from Code.Constantes import *


class GestorPlayGame(Gestor.Gestor):
    def inicio(self, recno, is_white):

        db = PantallaPlayGame.DBPlayGame(self.configuracion.file_play_game())
        reg = db.leeRegistro(recno)
        partidaObj = Game.Game()
        partidaObj.restore(reg["GAME"])
        nombreObj = partidaObj.get_tag("WHITE" if is_white else "BLACK")
        rotulo = db.rotulo(recno)
        db.close()

        self.recno = recno
        self.resultado = None
        self.human_is_playing = False
        self.analysis = None
        self.comment = None
        self.siAnalizando = False
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white
        self.numJugadasObj = partidaObj.num_moves()
        self.partidaObj = partidaObj
        self.posJugadaObj = 0
        self.nombreObj = nombreObj

        self.siSave = False
        self.minTiempo = 5000

        self.xanalyzer.maximizaMultiPV()

        self.puntosMax = 0
        self.puntos = 0
        self.vtime = 0.0

        self.book = Apertura.AperturaPol(999)

        self.main_window.pon_toolbar((TB_CANCEL, TB_REINIT, TB_CONFIG, TB_UTILITIES))

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.quitaAyudas(True, True)

        self.set_dispatcher(self.mueve_humano)
        self.setposition(self.game.last_position)
        self.ponPiezasAbajo(self.is_human_side_white)
        self.mostrarIndicador(True)
        self.ponRotulo1(rotulo)
        self.ponRotulo2("")

        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()
        self.dgt_setposition()

        self.state = ST_PLAYING
        self.siguiente_jugada()

    def ponPuntos(self):
        self.ponRotulo2("%s : <b>%d (%d)</b>" % (_("Points"), self.puntos, -self.puntosMax))

    def run_action(self, key):
        if key == TB_CLOSE:
            self.procesador.inicio()
            self.procesador.play_game_show(self.recno)

        elif key == TB_CANCEL:
            self.cancelar()

        elif key == TB_REINIT:
            self.reiniciar(True)

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True)

        elif key == TB_UTILITIES:
            self.utilidadesElo()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def final_x(self):
        return self.cancelar()

    def cancelar(self):
        self.puntos = -999
        self.analizaTerminar()
        self.procesador.inicio()
        return False

    def reiniciar(self, siPregunta):
        if siPregunta:
            if not QTUtil2.pregunta(self.main_window, _("Restart the game?")):
                return

        self.game.set_position()
        self.posJugadaObj = 0
        self.puntos = 0
        self.puntosMax = 0
        self.ponPuntos()
        self.vtime = 0.0
        self.book = Apertura.AperturaPol(999)
        self.state = ST_PLAYING
        self.tablero.setposition(self.game.first_position)
        self.pgnRefresh(True)
        self.dgt_setposition()
        self.analizaFinal()

        self.siguiente_jugada()

    def validoMRM(self, pvUsu, pvObj, mrmActual):
        move = self.partidaObj.move(self.posJugadaObj)
        if move.analysis:
            mrm, pos = move.analysis
            msAnalisis = mrm.getTime()
            if msAnalisis > self.minTiempo:
                if mrmActual.getTime() > msAnalisis and mrmActual.contiene(pvUsu) and mrmActual.contiene(pvObj):
                    return None
                if mrm.contiene(pvObj) and mrm.contiene(pvUsu):
                    return mrm
        return None

    def analizaInicio(self):
        if not self.is_finished():
            self.xanalyzer.ac_inicio(self.game)
            self.siAnalizando = True

    def analizaMinimo(self, pvUsu, pvObj):
        mrmActual = self.xanalyzer.ac_estado()
        mrm = self.validoMRM(pvUsu, pvObj, mrmActual)
        if mrm:
            return mrm
        self.mrm = copy.deepcopy(self.xanalyzer.ac_minimo(self.minTiempo, False))
        return self.mrm

    def analizaEstado(self):
        self.xanalyzer.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xanalyzer.ac_estado())
        return self.mrm

    def analizaFinal(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xanalyzer.ac_final(-1)
            self.siSave = True

    def analizaTerminar(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xanalyzer.terminar()

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return

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

        self.refresh()

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

    def mueve_humano(self, from_sq, to_sq, promotion=""):
        jgUsu = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not jgUsu:
            return False

        self.vtime += time.time() - self.iniTiempo

        jgObj = self.partidaObj.move(self.posJugadaObj)

        siAnalizaJuez = True
        if self.book:
            fen = self.fenUltimo()
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
            um = QTUtil2.analizando(self.main_window)
            pvUsu = jgUsu.movimiento()
            pvObj = jgObj.movimiento()
            mrm = self.analizaMinimo(pvUsu, pvObj)
            position = self.game.last_position

            rmUsu, nada = mrm.buscaRM(pvUsu)
            rmObj, posObj = mrm.buscaRM(pvObj)

            analisis = mrm, posObj
            um.final()

            w = PantallaJuicio.WJuicio(self, self.xanalyzer, self.nombreObj, position, mrm, rmObj, rmUsu, analisis)
            w.exec_()

            analisis = w.analysis
            if w.siAnalisisCambiado:
                self.siSave = True
            dpts = w.difPuntos()
            self.puntos += dpts

            dptsMax = w.difPuntosMax()
            self.puntosMax += dptsMax

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
            self.ponPuntos()

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
        self.refresh()

        self.dgt_setposition()

    def put_result(self):
        self.analizaTerminar()
        self.disable_all()
        self.human_is_playing = False

        self.state = ST_ENDGAME

        if self.puntos < 0:
            mensaje = _("Unfortunately you have lost.")
            quien = RS_WIN_OPPONENT
        else:
            mensaje = _("Congratulations you have won.")
            quien = RS_WIN_PLAYER

        self.beepResultadoCAMBIAR(quien)

        self.mensajeEnPGN(mensaje)
        self.ponFinJuego()
        self.guardar()

    def guardar(self):
        db = PantallaPlayGame.DBPlayGame(self.configuracion.file_play_game())
        reg = db.leeRegistro(self.recno)

        dicIntento = {
            "DATE": Util.today(),
            "COLOR": "w" if self.is_human_side_white else "b",
            "POINTS": self.puntos,
            "POINTSMAX": self.puntosMax,
            "TIME": self.vtime,
        }

        if not ("LIINTENTOS" in reg):
            reg["LIINTENTOS"] = []
        reg["LIINTENTOS"].insert(0, dicIntento)

        if self.siSave:
            reg["GAME"] = self.partidaObj.save()
            self.siSave = False

        db.cambiaRegistro(self.recno, reg)

        db.close()
