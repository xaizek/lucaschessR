import time

from Code import Util
from Code.SQL import UtilSQL
from Code import Gestor
from Code import Game
from Code.QT import QTVarios
from Code.Constantes import *


class GestorAnotar(Gestor.Gestor):
    partida_objetivo = None
    total_jugadas = 0
    jugada_actual = 0
    ayudas_recibidas = 0
    errores = 0
    cancelado = False
    si_blancas_abajo = True
    si_terminar = False
    vtime = 0.0
    informacion_activable = False

    def inicio(self, partida_objetivo, si_blancas_abajo):

        self.game = Game.Game()
        self.game_type = GT_NOTE_DOWN
        self.partida_objetivo = partida_objetivo
        self.jugada_actual = -1
        self.total_jugadas = len(self.partida_objetivo)
        self.tablero.showCoordenadas(False)

        self.ayudas_recibidas = 0
        self.errores = 0
        self.cancelado = False

        self.main_window.ponActivarTutor(False)
        self.si_blancas_abajo = si_blancas_abajo
        self.ponPiezasAbajo(self.si_blancas_abajo)
        self.mostrarIndicador(True)
        self.si_terminar = False
        self.main_window.pon_toolbar((TB_CLOSE,))
        self.main_window.habilitaToolbar(TB_CLOSE, False)
        self.informacion_activable = False
        self.main_window.activaInformacionPGN(False)
        self.main_window.activaJuego(False, False, siAyudas=False)
        self.ponActivarTutor(False)
        self.quitaAyudas()
        self.put_view()
        self.ponRotulo1("")
        self.ponRotulo2("")

        self.state = ST_PLAYING

        self.disable_all()

        self.vtime = 0.0

        self.siguiente_jugada()

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return False

        self.state = ST_PLAYING

        self.jugada_actual += 1
        if self.jugada_actual >= self.total_jugadas:
            self.finalizar()
            return False

        self.ponPiezasAbajo(self.si_blancas_abajo)

        self.setposition(self.game.last_position)

        is_white = self.game.is_white()

        self.ponIndicador(is_white)
        move = self.partida_objetivo.move(self.jugada_actual)
        self.game.add_move(move)

        self.move_the_pieces(move.liMovs, True)
        self.tablero.ponFlechaSC(move.from_sq, move.to_sq)

        tm = time.time()

        w = QTVarios.ReadAnnotation(self.main_window, move.pgn_translated())
        if not w.exec_():
            self.cancelado = True
            self.finalizar()
            return False

        self.vtime += time.time() - tm
        con_ayuda, errores = w.resultado
        if con_ayuda:
            self.ayudas_recibidas += 1
        self.errores += errores

        self.refresh()

        return self.siguiente_jugada()

    def run_action(self, key):
        if key == TB_REINIT:
            self.inicio(self.partida_objetivo, self.si_blancas_abajo)

        elif key in (TB_CANCEL, TB_CLOSE):
            self.tablero.showCoordenadas(True)
            self.procesador.inicio()
            self.procesador.show_anotar()

        elif key == TB_CONFIG:
            self.configurar()

        elif key == TB_UTILITIES:
            self.utilidades()

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def final_x(self):
        self.tablero.showCoordenadas(True)
        return True

    def finalizar(self):
        self.informacion_activable = True
        self.tablero.showCoordenadas(True)
        self.main_window.activaJuego(True, False, siAyudas=False)
        self.quitaAyudas()
        self.main_window.pon_toolbar((TB_CLOSE, TB_REINIT, TB_CONFIG, TB_UTILITIES))
        if self.cancelado:
            self.game = self.partida_objetivo
        self.goto_end()
        blancas, negras, fecha, event, result = "", "", "", "", ""
        for key, value in self.partida_objetivo.li_tags:
            key = key.upper()
            if key == "WHITE":
                blancas = value
            elif key == "BLACK":
                negras = value
            elif key == "DATE":
                fecha = value
            elif key == "EVENT":
                event = value
            elif key == "RESULT":
                result = value

        self.ponRotulo1(
            "%s - %s<br> %s: <b>%s</b><br>%s: <b>%s</b><br>%s: <b>%s</b>"
            % (fecha, event, _("White"), blancas, _("Black"), negras, _("Result"), result)
        )
        numjug = self.jugada_actual
        if numjug > 0:
            self.ponRotulo2(
                '%s: <b>%d</b><br>%s: %0.2f"<br>%s: <b>%d</b><br>%s: <b>%d</b>'
                % (
                    _("Moves"),
                    numjug,
                    _("Average time"),
                    self.vtime / numjug,
                    _("Errors"),
                    self.errores,
                    _("Hints"),
                    self.ayudas_recibidas,
                )
            )
            if numjug > 2:
                db = UtilSQL.DictSQL(self.configuracion.ficheroAnotar)
                f = Util.today()
                key = "%04d-%02d-%02d %02d:%02d:%02d" % (f.year, f.month, f.day, f.hour, f.minute, f.second)
                db[key] = {
                    "PC": self.partida_objetivo,
                    "MOVES": numjug,
                    "TIME": self.vtime / numjug,
                    "HINTS": self.ayudas_recibidas,
                    "ERRORS": self.errores,
                    "COLOR": self.si_blancas_abajo,
                }
                db.close()
