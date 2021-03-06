import time

from PySide2.QtCore import Qt

from Code.Tactics import Tactics
from Code import Gestor
from Code.QT import WCompetitionWithTutor
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.Constantes import *


class GestorTacticas(Gestor.Gestor):
    def inicio(self, tactic: Tactics.Tactic):
        self.reiniciando = False
        self.tactic = tactic
        self.tactic.leeDatos()
        self.tactic.work_reset_positions()
        self.is_tutor_enabled = False
        self.ayudas_iniciales = 0
        self.siCompetitivo = True
        self.reinicia()

    def reinicia(self):
        if self.reiniciando:
            return
        self.reiniciando = True

        self.pointView = self.tactic.pointView()

        self.with_automatic_jump = self.tactic.with_automatic_jump()

        self.game_obj, game_base = self.tactic.work_read_position()
        self.pos_obj = 0

        cp = self.game_obj.first_position
        is_white = cp.is_white
        if self.pointView:
            is_white = self.pointView == 1
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        if game_base:
            self.game = game_base
        else:
            self.game.set_position(cp)

        self.game_type = GT_TACTICS

        self.human_is_playing = False
        self.plays_instead_of_me_option = False

        self.main_window.ponActivarTutor(False)
        self.main_window.activaJuego(True, False, siAyudas=False)
        self.main_window.quitaAyudas(True, True)
        self.set_dispatcher(self.mueve_humano)
        self.setposition(self.game.last_position)
        self.mostrarIndicador(True)
        self.ponPiezasAbajo(is_white)

        li_opciones = [TB_CLOSE, TB_REINIT, TB_CONFIG]
        self.main_window.pon_toolbar(li_opciones)

        titulo = self.tactic.work_info(False)
        self.ponRotulo1(titulo)
        self.pgnRefresh(True)
        QTUtil.refresh_gui()

        self.dgt_setposition()

        if game_base:
            self.repiteUltimaJugada()

        self.show_label_positions()
        self.state = ST_PLAYING
        self.reiniciando = False

        self.siguiente_jugada()

    def show_label_positions(self):
        html = self.tactic.work_info_position()
        self.ponRotulo2(html)

    def put_penalization(self):
        self.tactic.work_add_error()
        self.show_label_positions()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.finPartida()

        elif key == TB_CONFIG:
            if self.with_automatic_jump:
                liMasOpciones = [("lmo_stop", _("Stop after solving"), Iconos.Stop())]
            else:
                liMasOpciones = [("lmo_jump", _("Jump to the next after solving"), Iconos.Jump())]
            resp = self.configurar(siSonidos=True, siCambioTutor=False, liMasOpciones=liMasOpciones)
            if resp in ("lmo_stop", "lmo_jump"):
                self.with_automatic_jump = resp == "lmo_jump"
                self.tactic.set_automatic_jump(self.with_automatic_jump)

        elif key == TB_REINIT:
            self.reinicia()

        elif key == TB_UTILITIES:
            self.utilidades()

        elif key == TB_NEXT:
            self.ent_siguiente()

        elif key == TB_CHANGE:
            self.cambiar()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def control_teclado(self, nkey):
        if nkey in (Qt.Key_Plus, Qt.Key_PageDown):
            if self.state == ST_ENDGAME:
                self.ent_siguiente()

    def listHelpTeclado(self):
        return [("+/%s" % _("Page Down"), _("Next position")), ("T", _("Save position in 'Selected positions' file"))]

    def ent_siguiente(self):
        if self.tactic.work_game_finished():
            self.finPartida()
        else:
            self.inicio(self.tactic)

    def finPartida(self):
        self.procesador.inicio()
        self.procesador.entrenamientos.entrenaTactica(self.tactic)

    def final_x(self):
        self.finPartida()
        return False

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.ponIndicador(is_white)
        self.refresh()

        if self.pos_obj == len(self.game_obj):
            self.end_line()
            return

        si_rival = is_white == self.is_engine_side_white

        if si_rival:
            move = self.game_obj.move(self.pos_obj)
            self.move_the_pieces(move.liMovs, True)
            self.add_move(move, False)
            self.siguiente_jugada()

        else:
            self.human_is_playing = True
            self.activaColor(is_white)
            self.ini_clock = time.time()

    def end_line(self):
        self.state = ST_ENDGAME
        self.disable_all()

        self.tactic.work_line_finished()
        if self.tactic.finished():
            self.end_training()
            return False

        if self.with_automatic_jump and not self.tactic.w_error:
            self.ent_siguiente()
        else:
            QTUtil2.mensajeTemporal(self.main_window, _("This line training is completed."), 0.7)
            li_opciones = [TB_CLOSE, TB_CONFIG, TB_UTILITIES, TB_NEXT]
            if not self.tactic.reinforcement.is_working():
                li_opciones.insert(1, TB_CHANGE)

            self.ponRotulo1(self.tactic.w_label)

            self.main_window.pon_toolbar(li_opciones)

        return True

    def mueve_humano(self, from_sq, to_sq, promotion=None):
        move = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not move:
            return False

        movimiento = move.movimiento()
        move_obj = self.game_obj.move(self.pos_obj)
        movimiento_obj = move_obj.movimiento()

        is_main = movimiento == movimiento_obj
        is_variation = False
        if not is_main:
            if len(move_obj.variations) > 0:
                li_movs = self.game_obj.variations.list_movimientos()
                is_variation = movimiento in li_movs
                if is_variation:
                    li_flechas = [(x[:2], x[2:4], False) for x in li_movs]
                    li_flechas.append((movimiento_obj[:2], movimiento_obj[2:4], True))
                    self.tablero.ponFlechasTmp(li_flechas)
            if not is_variation:
                self.put_penalization()
            self.sigueHumano()
            return False

        segundos = time.time() - self.ini_clock
        self.tactic.masSegundos(segundos)

        self.add_move(move, True)
        self.siguiente_jugada()
        return True

    def add_move(self, move, si_nuestra):
        self.game.add_move(move)

        self.pos_obj += 1

        self.ponFlechaSC(move.from_sq, move.to_sq)
        self.beepExtendido(si_nuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.tablero.setposition(move.position)
        self.refresh()

        self.dgt_setposition()

    def cambiar(self):
        if self.tactic.w_next_position >= 0:
            pos = WCompetitionWithTutor.edit_training_position(
                self.main_window,
                self.tactic.title_extended(),
                self.tactic.w_next_position,
                pos=self.tactic.w_next_position,
            )
            if pos is not None:
                self.tactic.w_next_position = pos - 1
                self.tactic.work_set_current_position(self.tactic.w_next_position)

                self.ent_siguiente()

    def end_training(self):
        self.tactic.end_training()
        mensaje = "<big>%s<br>%s</big>" % (_("Congratulations goal achieved"), _("Endgame"))
        self.mensajeEnPGN(mensaje)
        self.finPartida()
