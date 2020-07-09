import FasterCode
from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code import Position
from Code.Polyglots import Books
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import Piezas
from Code.QT import QTUtil
from Code.QT import QTVarios
from Code.QT import Tablero
from Code.QT import Delegados
from Code.QT import Voyager


class WPolyglot(QtWidgets.QDialog):
    def __init__(self, cpu):
        QtWidgets.QDialog.__init__(self)

        self.cpu = cpu

        dicVideo = self.cpu.dic_video
        if not dicVideo:
            dicVideo = {}

        self.siTop = dicVideo.get("SITOP", True)
        self.siShowTablero = dicVideo.get("SHOW_TABLERO", True)
        self.position = Position.Position()

        self.fen = ""
        self.siPlay = True
        self.li_moves = []
        self.history = []

        self.setWindowTitle(cpu.titulo)
        self.setWindowIcon(Iconos.Book())

        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
        )

        self.setBackgroundRole(QtGui.QPalette.Light)

        Code.configuracion = cpu.configuracion

        Code.todasPiezas = Piezas.TodasPiezas()
        config_board = cpu.configuracion.config_board("kib" + cpu.kibitzer.huella, 24)
        self.tablero = Tablero.Tablero(self, config_board)
        self.tablero.crea()
        self.tablero.set_dispatcher(self.mensajero)
        Delegados.generaPM(self.tablero.piezas)

        self.book = Books.Libro("P", cpu.kibitzer.name, cpu.kibitzer.path_exe, True)
        self.book.polyglot()

        self.siFigurines = cpu.configuracion.x_pgn_withfigurines

        o_columns = Columnas.ListaColumnas()
        delegado = Delegados.EtiquetaPOS(True, siLineas=False) if self.siFigurines else None
        o_columns.nueva("MOVE", _("Move"), 80, centered=True, edicion=delegado)
        o_columns.nueva("PORC", "%", 60, centered=True)
        o_columns.nueva("WEIGHT", _("Weight"), 80, siDerecha=True)
        self.grid_moves = Grid.Grid(self, o_columns, dicVideo=dicVideo, siSelecFilas=True)

        li_acciones = (
            (_("Quit"), Iconos.Kibitzer_Terminar(), self.terminar),
            (_("Continue"), Iconos.Kibitzer_Continuar(), self.play),
            (_("Pause"), Iconos.Kibitzer_Pausa(), self.pause),
            (_("Takeback"), Iconos.Atras(), self.takeback),
            (_("Manual position"), Iconos.Voyager(), self.set_position),
            (_("Show/hide board"), Iconos.Tablero(), self.config_board),
            ("%s: %s" % (_("Enable"), _("window on top")), Iconos.Top(), self.windowTop),
            ("%s: %s" % (_("Disable"), _("window on top")), Iconos.Bottom(), self.windowBottom),
        )
        self.tb = Controles.TBrutina(self, li_acciones, siTexto=False, tamIcon=16)
        self.tb.setAccionVisible(self.play, False)

        ly1 = Colocacion.H().control(self.tb)
        ly2 = Colocacion.V().otro(ly1).control(self.grid_moves)

        layout = Colocacion.H().control(self.tablero).otro(ly2)
        self.setLayout(layout)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.cpu.compruebaInput)
        self.timer.start(200)

        if not self.siShowTablero:
            self.tablero.hide()
        self.restore_video(dicVideo)
        self.ponFlags()

    def grid_doble_click(self, grid, fila, oColumna):
        if 0 <= fila < len(self.li_moves):
            FasterCode.set_fen(self.fen)
            alm = self.li_moves[fila]
            FasterCode.make_move(alm.pv)
            self.pon_fen_hist(FasterCode.get_fen())

    def grid_boton_derecho(self, grid, fila, columna, modificadores):
        if len(self.history) > 0:
            fila, fen = self.history[-1]
            self.history = self.history[:-1]
            self.ponFen(fen)
            self.grid_moves.goto(fila, 0)

    def grid_cambiado_registro(self, grid, fila, oColumna):
        self.ponFlecha(fila)

    def ponFlecha(self, fila):
        if -1 < fila < len(self.li_moves):
            alm = self.li_moves[fila]
            self.tablero.ponFlechaSC(alm.from_sq, alm.to_sq)

    def ponFlags(self):
        flags = self.windowFlags()
        if self.siTop:
            flags |= QtCore.Qt.WindowStaysOnTopHint
        else:
            flags &= ~QtCore.Qt.WindowStaysOnTopHint
        flags |= QtCore.Qt.WindowCloseButtonHint
        self.setWindowFlags(flags)
        self.tb.setAccionVisible(self.windowTop, not self.siTop)
        self.tb.setAccionVisible(self.windowBottom, self.siTop)
        self.show()

    def windowTop(self):
        self.siTop = True
        self.ponFlags()

    def windowBottom(self):
        self.siTop = False
        self.ponFlags()

    def terminar(self):
        self.finalizar()
        self.accept()

    def pause(self):
        self.siPlay = False
        self.tb.setPosVisible(1, True)
        self.tb.setPosVisible(2, False)

    def play(self):
        self.siPlay = True
        self.tb.setPosVisible(1, False)
        self.tb.setPosVisible(2, True)
        self.ponFen(self.fen)

    def stop(self):
        pass

    def grid_num_datos(self, grid):
        return len(self.li_moves)

    def grid_dato(self, grid, fila, oColumna):
        alm = self.li_moves[fila]

        # alm = Util.Record()
        # alm.from_sq, alm.to_sq, alm.promotion = pv[:2], pv[2:4], pv[4:]
        # alm.pgn = position.pgn_translated(alm.from_sq, alm.to_sq, alm.promotion)
        # alm.pgnRaw = position.pgn(alm.from_sq, alm.to_sq, alm.promotion)
        # alm.fen = fen
        # alm.porc = "%0.02f%%" % (w * 100.0 / total,) if total else ""
        # alm.weight = w

        key = oColumna.clave
        if key == "MOVE":
            if self.siFigurines:
                is_white = " w " in alm.fen
                return alm.pgnRaw, is_white, None, None, None, None, False, True
            else:
                return alm.pgn
        elif key == "PORC":
            return alm.porc
        elif key == "WEIGHT":
            return "%d" % alm.weight

    def closeEvent(self, event):
        self.finalizar()

    def siAnalizar(self):
        siW = " w " in self.fen
        if not self.siPlay or (siW and (not self.is_white)) or ((not siW) and (not self.siNegras)):
            return False
        return True

    def color(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion("blancas", _("White"), Iconos.PuntoNaranja())
        menu.opcion("negras", _("Black"), Iconos.PuntoNegro())
        menu.opcion("blancasnegras", "%s + %s" % (_("White"), _("Black")), Iconos.PuntoVerde())
        resp = menu.lanza()
        if resp:
            self.siNegras = True
            self.is_white = True
            if resp == "blancas":
                self.siNegras = False
            elif resp == "negras":
                self.is_white = False
            if self.siAnalizar():
                self.ponFen(self.fen)

    def finalizar(self):
        self.save_video()

    def save_video(self):
        dic = {}

        pos = self.pos()
        dic["_POSICION_"] = "%d,%d" % (pos.x(), pos.y())

        tam = self.size()
        dic["_SIZE_"] = "%d,%d" % (tam.width(), tam.height())

        dic["SHOW_TABLERO"] = self.siShowTablero

        dic["SITOP"] = self.siTop

        self.cpu.save_video(dic)

    def restore_video(self, dicVideo):
        if dicVideo:
            wE, hE = QTUtil.tamEscritorio()
            x, y = dicVideo["_POSICION_"].split(",")
            x = int(x)
            y = int(y)
            if not (0 <= x <= (wE - 50)):
                x = 0
            if not (0 <= y <= (hE - 50)):
                y = 0
            self.move(x, y)
            if not ("_SIZE_" in dicVideo):
                w, h = self.width(), self.height()
                for k in dicVideo:
                    if k.startswith("_TAMA"):
                        w, h = dicVideo[k].split(",")
            else:
                w, h = dicVideo["_SIZE_"].split(",")
            w = int(w)
            h = int(h)
            if w > wE:
                w = wE
            elif w < 20:
                w = 20
            if h > hE:
                h = hE
            elif h < 20:
                h = 20
            self.resize(w, h)

    def config_board(self):
        self.siShowTablero = not self.siShowTablero
        self.tablero.setVisible(self.siShowTablero)
        self.save_video()

    def takeback(self):
        if len(self.history) > 1:
            fen = self.history.pop()
            if fen == self.fen and self.history:
                fen = self.history.pop()
            self.pon_fen_hist(fen)

    def set_position(self):
        cp = Position.Position()
        cp.read_fen(self.fen)
        resp = Voyager.voyager_position(self, cp)
        if resp is not None:
            self.ponFen(resp.fen())

    def ponFen(self, fen):
        self.history = []
        self.pon_fen_hist(fen)

    def pon_fen_hist(self, fen):
        if not self.history or self.history[-1] != fen:
            self.history.append(fen)
        self.position = Position.Position()
        self.position.read_fen(fen)
        self.fen = fen

        if self.siPlay:
            self.siW = self.position.is_white
            self.tablero.setposition(self.position)
            self.tablero.activaColor(self.siW)
            self.li_moves = self.book.almListaJugadas(fen)
            self.grid_moves.gotop()
            self.grid_moves.refresh()
            self.ponFlecha(0)

    def mensajero(self, from_sq, to_sq, promocion=""):
        FasterCode.set_fen(self.fen)
        if FasterCode.make_move(from_sq + to_sq + promocion):
            self.fen = FasterCode.get_fen()
            self.pon_fen_hist(self.fen)
