import time

from PySide2 import QtCore, QtGui

import FasterCode

import Code
from Code.QT import Colocacion, Controles, Iconos, QTUtil, QTVarios, Tablero, QTUtil2


class WRunCounts(QTVarios.WDialogo):
    def __init__(self, owner, db_counts, count):

        QTVarios.WDialogo.__init__(self, owner, _("Count moves"), Iconos.Count(), "runcounts")

        self.configuracion = Code.configuracion
        self.count = count
        self.db_counts = db_counts

        conf_board = self.configuracion.config_board("RUNCOUNTS", 64)

        self.board = Tablero.TableroEstaticoMensaje(self, conf_board, None)
        self.board.crea()

        # Rotulo informacion
        self.lb_info_game = Controles.LB(
            self, self.count.game.titulo("DATE", "EVENT", "WHITE", "BLACK", "RESULT")
        ).ponTipoLetra(puntos=self.configuracion.x_pgn_fontpoints)

        # Movimientos
        self.ed_moves = Controles.ED(self, "").ponTipoLetra(puntos=32)
        self.ed_moves.setValidator(QtGui.QIntValidator(self.ed_moves))
        self.ed_moves.setAlignment(QtCore.Qt.AlignRight)
        self.ed_moves.anchoFijo(72)

        ly = Colocacion.H().relleno().control(self.ed_moves).relleno()

        self.gb_counts = Controles.GB(self, _("Number of moves"), ly).ponFuente(Controles.TipoLetra(puntos=10, peso=75))

        self.lb_result = Controles.LB(self).ponTipoLetra(puntos=10, peso=500).anchoFijo(254).altoFijo(32).ponWrap()
        self.lb_info = (
            Controles.LB(self).ponTipoLetra(puntos=14, peso=500).anchoFijo(254).ponColorFondoN("white", "#496075").alinCentrado()
        )

        # Botones
        li_acciones = (
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("Begin"), Iconos.Empezar(), self.begin),
            (_("Check"), Iconos.Check(), self.check),
            (_("Continue"), Iconos.Pelicula_Seguir(), self.seguir),
        )
        self.tb = QTVarios.LCTB(self, li_acciones, style=QtCore.Qt.ToolButtonTextBesideIcon, tamIcon=32)
        self.show_tb(self.terminar, self.begin)

        ly_right = (
            Colocacion.V()
            .control(self.tb)
            .controlc(self.lb_info)
            .relleno()
            .control(self.gb_counts)
            .relleno()
            .control(self.lb_result)
            .relleno()
        )

        ly_center = Colocacion.H().control(self.board).otro(ly_right)

        ly = Colocacion.V().otro(ly_center).control(self.lb_info_game).margen(3)

        self.setLayout(ly)

        self.restore_video()
        self.adjustSize()

        # Tiempo
        self.time_base = time.time()

        self.gb_counts.setDisabled(True)

        self.pon_info_posic()
        self.set_position()

    def set_position(self):
        self.move_base = self.count.game.move(self.count.current_posmove)
        self.move_obj = self.count.game.move(self.count.current_posmove + self.count.current_depth)
        self.board.ponPosicion(self.move_base.position_before)
        self.ed_moves.setFocus()

    def pon_info_posic(self):
        self.lb_info.ponTexto(
            "%d+%d / %d"
            % (self.count.current_posmove + 1, self.count.current_depth, len(self.count.game), )
        )

    def closeEvent(self, event):
        self.save_video()
        event.accept()

    def terminar(self):
        self.save_video()
        self.reject()

    def show_tb(self, *lista):
        for opc in self.tb.dicTB:
            self.tb.setAccionVisible(opc, opc in lista)
        QTUtil.refresh_gui()

    def begin(self):
        self.seguir()

    def seguir(self):
        self.set_position()
        self.lb_result.ponTexto("")
        self.ed_moves.ponTexto("")

        self.show_tb()

        # Mostramos los movimientos según depth
        depth = self.count.current_depth
        if depth:
            for x in range(depth):
                move = self.count.game.move(self.count.current_posmove + x)
                txt = move.pgnBaseSP()
                self.board.pon_texto(txt, 0.9)
                QTUtil.refresh_gui()
                dif = depth - x
                factor = 1.0 - dif * 0.1
                if factor < 0.5:
                    factor = 0.5

                time.sleep(2.6*factor*factor)
                self.board.pon_texto("", 0)
                QTUtil.refresh_gui()

        # Ponemos el toolbar
        self.show_tb(self.check, self.terminar)

        # Activamos capturas
        self.gb_counts.setEnabled(True)

        # Marcamos el tiempo
        self.time_base = time.time()

        self.ed_moves.setFocus()

    def check(self):
        tiempo = time.time() - self.time_base

        position_obj = self.move_obj.position_before
        moves = FasterCode.get_exmoves_fen(position_obj.fen())

        num_moves_calculated = int(self.ed_moves.texto())

        if num_moves_calculated == len(moves):
            self.count.current_depth += 1
            if (self.count.current_posmove + self.count.current_depth) >= len(self.count.game):
                QTUtil2.message(self, _("Training finished"))
                self.db_counts.change_count(self.count)
                self.terminar()
                return
            self.lb_result.ponTexto("%s (%d)" % (_("Right, go to the next level of depth"), self.count.current_depth))
            self.lb_result.ponColorN("green")

        else:
            if self.count.current_depth >= 1:
                self.count.current_posmove += self.count.current_depth - 1
                if self.count.current_posmove < 0:
                    self.count.current_posmove = 0
                self.count.current_depth = 0
                self.lb_result.ponTexto(
                    "%s (%d)" % (_("Wrong, you advance to the last position solved"), self.count.current_posmove + 1)
                )
                self.lb_result.ponColorN("red")
            else:
                self.lb_result.ponTexto(_("Wrong, you must repeat this position"))
                self.lb_result.ponColorN("red")
            self.board.ponPosicion(position_obj)
            for x in moves:
                self.board.creaFlechaTmp(x.xfrom(), x.xto(), False)


        self.db_counts.change_count_capture(self.count)
        self.pon_info_posic()
        self.show_tb(self.terminar, self.seguir)
