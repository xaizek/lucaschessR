from PySide2 import QtWidgets, QtCore
from PySide2.QtCore import Qt

from Code import Position
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import QTVarios
from Code.QT import Tablero
import Code


class TableroKey(Tablero.Tablero):
    def keyPressEvent(self, event):
        k = event.key()
        self.main_window.tecla_pulsada(k)


class LBKey(Controles.LB):
    def keyPressEvent(self, event):
        k = event.key()
        self.parentWidget().tecla_pulsada(k)


class WInfomove(QtWidgets.QWidget):
    def __init__(self, wb_database):
        QtWidgets.QWidget.__init__(self)

        self.wb_database = wb_database
        self.movActual = None

        configuracion = Code.configuracion
        config_board = configuracion.config_board("INFOMOVE", 32)
        self.tablero = TableroKey(self, config_board)
        self.tablero.dispatchSize(self.cambiado_tablero)
        self.tablero.crea()
        self.tablero.ponerPiezasAbajo(True)
        self.tablero.disable_hard_focus()  # Para que los movimientos con el teclado from_sq grid wgames no cambien el foco
        self.cpActual = Position.Position()
        self.historia = None
        self.posHistoria = None

        self.intervalo = configuracion.x_interval_replay

        lybt, bt = QTVarios.lyBotonesMovimiento(self, "", siTiempo=True, siLibre=False, tamIcon=24)

        self.lbPGN = LBKey(self).anchoFijo(self.tablero.ancho).ponWrap()
        self.lbPGN.colocate = self.colocatePartida
        self.lbPGN.ponTipoLetra(puntos=configuracion.x_pgn_fontpoints + 2)
        self.lbPGN.setStyleSheet(
            "QLabel{ border-style: groove; border-width: 2px; border-color: LightSlateGray; padding: 2px 16px 6px 2px;}"
        )
        self.lbPGN.setOpenExternalLinks(False)

        def muestraPos(txt):
            self.colocatePartida(int(txt))

        self.lbPGN.linkActivated.connect(muestraPos)

        scroll = QtWidgets.QScrollArea()
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QtWidgets.QFrame.NoFrame)

        ly = Colocacion.V().control(self.lbPGN).relleno(1).margen(0)
        w = QtWidgets.QWidget()
        w.setLayout(ly)
        scroll.setWidget(w)

        self.siFigurines = configuracion.x_pgn_withfigurines

        self.lbOpening = Controles.LB(self).alinCentrado().anchoFijo(self.tablero.ancho).ponWrap()
        self.lbOpening.ponTipoLetra(puntos=10, peso=200)
        lyO = Colocacion.H().relleno().control(self.lbOpening).relleno()

        lya = Colocacion.H().relleno().control(scroll).relleno()

        layout = Colocacion.G()
        layout.controlc(self.tablero, 0, 0)
        layout.otroc(lybt, 1, 0)
        layout.otro(lyO, 2, 0)
        layout.otro(lya, 3, 0)
        self.setLayout(layout)

        self.usoNormal = True

        self.siReloj = False

    def cambiado_tablero(self):
        self.lbPGN.anchoFijo(self.tablero.ancho)
        self.lbOpening.anchoFijo(self.tablero.ancho)

    def process_toolbar(self):
        getattr(self, self.sender().clave)()

    def modoNormal(self):
        self.usoNormal = True
        self.MoverFinal()

    def modoPartida(self, game, move):
        self.usoNormal = False
        self.game = game
        if game.opening:
            txt = game.opening.trNombre
            if game.pending_opening:
                txt += " ..."
            self.lbOpening.ponTexto(txt)
        else:
            self.lbOpening.ponTexto("")
        self.colocatePartida(move)

    def modoFEN(self, game, fen, move):
        self.usoNormal = False
        self.game = game
        self.lbOpening.ponTexto(fen)
        self.colocatePartida(move)

    def colocate(self, pos):
        if not self.historia:
            self.tablero.activaColor(True)
            return
        lh = len(self.historia) - 1
        if pos >= lh:
            self.siReloj = False
            pos = lh
        if pos < 0:
            return self.MoverInicio()

        self.posHistoria = pos

        move = self.historia[self.posHistoria]
        self.cpActual.read_fen(move.fen())
        self.tablero.ponPosicion(self.cpActual)
        pv = move.pv()
        if pv:
            self.tablero.ponFlechaSC(pv[:2], pv[2:4])

        if self.posHistoria != lh:
            self.tablero.disable_all()
        else:
            self.tablero.activaColor(self.cpActual.is_white)

        nh = len(self.historia)
        li = []
        for x in range(1, nh):
            uno = self.historia[x]
            xp = uno.pgnNum()
            if x > 1:
                if ".." in xp:
                    xp = xp.split("...")[1]
            if x == self.posHistoria:
                xp = '<span style="color:blue">%s</span>' % xp
            li.append(xp)
        pgn = " ".join(li)
        self.lbPGN.ponTexto(pgn)

    def colocatePartida(self, pos):
        if not len(self.game):
            self.lbPGN.ponTexto("")
            self.tablero.ponPosicion(self.game.first_position)
            return
        lh = len(self.game) - 1
        if pos >= lh:
            self.siReloj = False
            pos = lh

        p = self.game

        numJugada = p.primeraJugada()
        pgn = ""
        style_number = "color:teal; font-weight: bold;"
        style_moves = "color:black;"
        style_select = "color:navy;font-weight: bold;"
        if p.if_starts_with_black:
            pgn += '<span style="%s">%d...</span>' % (style_number, numJugada)
            numJugada += 1
            salta = 1
        else:
            salta = 0
        for n, move in enumerate(p.li_moves):
            if n % 2 == salta:
                pgn += '<span style="%s">%d.</span>' % (style_number, numJugada)
                numJugada += 1

            xp = move.pgn_html(self.siFigurines)
            if n == pos:
                xp = '<span style="%s">%s</span>' % (style_select, xp)
            else:
                xp = '<span style="%s">%s</span>' % (style_moves, xp)

            pgn += '<a href="%d" style="text-decoration:none;">%s</a> ' % (n, xp)

        self.lbPGN.ponTexto(pgn)

        self.pos_move = pos

        if pos < 0:
            self.tablero.ponPosicion(self.game.first_position)
            return

        move = self.game.move(self.pos_move)
        position = move.position

        self.tablero.ponPosicion(position)
        self.tablero.ponFlechaSC(move.from_sq, move.to_sq)

        self.tablero.disable_all()

    def tecla_pulsada(self, k):
        if k in (Qt.Key_Left, Qt.Key_Up):
            self.MoverAtras()
        elif k in (Qt.Key_Right, Qt.Key_Down):
            self.MoverAdelante()
        elif k == Qt.Key_Home:
            self.MoverInicio()
        elif k == Qt.Key_End:
            self.MoverFinal()

    def MoverInicio(self):
        if self.usoNormal:
            self.posHistoria = -1
            position = Position.Position().set_pos_initial()
        else:
            # self.colocatePartida(-1)
            self.pos_move = -1
            position = self.game.first_position
        self.tablero.ponPosicion(position)

    def MoverAtras(self):
        if self.usoNormal:
            self.colocate(self.posHistoria - 1)
        else:
            self.colocatePartida(self.pos_move - 1)

    def MoverAdelante(self):
        if self.usoNormal:
            self.colocate(self.posHistoria + 1)
        else:
            self.colocatePartida(self.pos_move + 1)

    def MoverFinal(self):
        if self.usoNormal:
            self.colocate(len(self.historia) - 1)
        else:
            self.colocatePartida(99999)

    def MoverTiempo(self):
        if self.siReloj:
            self.siReloj = False
        else:
            self.siReloj = True
            self.MoverInicio()
            self.lanzaReloj()

    def toolbar_rightmouse(self):
        configuracion = Code.configuracion
        QTVarios.change_interval(self, configuracion)
        self.intervalo = configuracion.x_interval_replay

    def lanzaReloj(self):
        if self.siReloj:
            self.MoverAdelante()
            QtCore.QTimer.singleShot(self.intervalo, self.lanzaReloj)
