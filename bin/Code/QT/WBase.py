from PySide2 import QtCore, QtWidgets

import Code
from Code import Move
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import Tablero
from Code.Constantes import *


class WBase(QtWidgets.QWidget):
    def __init__(self, parent, gestor):
        super(WBase, self).__init__(parent)

        self.gestor = gestor

        self.configuracion = Code.configuracion

        self.procesandoEventos = None

        self.setWindowIcon(Iconos.Aplicacion64())

        self.creaToolBar()
        self.creaTablero()

        # self.creaCapturas()
        lyBI = self.creaBloqueInformacion()
        self.lyBI = lyBI

        lyT = Colocacion.V().control(self.tablero).relleno()

        self.conAtajos = True

        self.si_tutor = False
        self.num_hints = 0

        lyAI = Colocacion.H().relleno(1).otroi(lyT).otroi(lyBI).relleno(1).margen(0)
        ly = Colocacion.V().control(self.tb).relleno().otro(lyAI).relleno().margen(2)

        self.setLayout(ly)

        self.preparaColoresPGN()

        self.setAutoFillBackground(True)

    def preparaColoresPGN(self):
        self.colorMateNegativo = QTUtil.qtColorRGB(0, 0, 0)
        self.colorMatePositivo = QTUtil.qtColorRGB(159, 0, 159)
        self.colorNegativo = QTUtil.qtColorRGB(255, 0, 0)
        self.colorPositivo = QTUtil.qtColorRGB(0, 0, 255)

        self.colorBlanco = QTUtil.qtColorRGB(255, 255, 255)

    def ponGestor(self, gestor):
        self.gestor = gestor

    def creaToolBar(self):
        self.tb = QtWidgets.QToolBar("BASICO", self)
        iconsTB = self.configuracion.tipoIconos()
        self.tb.setToolButtonStyle(iconsTB)
        sz = 32 if iconsTB == QtCore.Qt.ToolButtonTextUnderIcon else 16
        self.tb.setIconSize(QtCore.QSize(sz, sz))
        style = "QToolBar {border-bottom: 1px solid gray; border-top: 1px solid gray;}"
        self.tb.setStyleSheet(style)
        # sp = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtGui, QtWidgets.QSizePolicy.Expanding)
        # self.tb.setSizePolicy(sp)
        self.tb.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tb.customContextMenuRequested.connect(self.lanzaAtajos)

        self.preparaTB()

    def preparaTB(self):
        self.dicTB = {}

        dic_opciones = {
            TB_PLAY: (_("Play"), Iconos.Libre()),
            TB_COMPETE: (_("Compete"), Iconos.NuevaPartida()),
            TB_TRAIN: (_("Train"), Iconos.Entrenamiento()),
            TB_OPTIONS: (_("Options"), Iconos.Opciones()),
            TB_INFORMATION: (_("Information"), Iconos.Informacion()),
            TB_FILE: (_("File"), Iconos.File()),
            TB_SAVE: (_("Save"), Iconos.Grabar()),
            TB_SAVE_AS: (_("Save as"), Iconos.GrabarComo()),
            TB_OPEN: (_("Open"), Iconos.Recuperar()),
            TB_RESIGN: (_("Resign"), Iconos.Abandonar()),
            TB_REINIT: (_("Reinit"), Iconos.Reiniciar()),
            TB_TAKEBACK: (_("Takeback"), Iconos.Atras()),
            TB_ADJOURN: (_("Adjourn"), Iconos.Aplazar()),
            TB_ADJOURNS: (_("Adjourns"), Iconos.Aplazamientos()),
            TB_END_GAME: (_("End game"), Iconos.FinPartida()),
            TB_CLOSE: (_("Close"), Iconos.MainMenu()),
            TB_PREVIOUS: (_("Previous"), Iconos.Anterior()),
            TB_NEXT: (_("Next"), Iconos.Siguiente()),
            TB_QUIT: (_("Quit"), Iconos.FinPartida()),
            TB_PASTE_PGN: (_("Paste PGN"), Iconos.Pegar()),
            TB_READ_PGN: (_("Read PGN"), Iconos.Fichero()),
            TB_PGN_LABELS: (_("PGN Labels"), Iconos.InformacionPGN()),
            TB_OTHER_GAME: (_("Other game"), Iconos.FicheroRepite()),
            TB_MY_GAMES: (_("My games"), Iconos.NuestroFichero()),
            TB_DRAW: (_("Draw"), Iconos.Tablas()),
            TB_BOXROOMS_PGN: (_("Boxrooms PGN"), Iconos.BoxRooms()),
            TB_END: (_("End"), Iconos.MainMenu()),
            TB_SLOW: (_("Slow"), Iconos.Pelicula_Lento()),
            TB_PAUSE: (_("Pause"), Iconos.Pelicula_Pausa()),
            TB_CONTINUE: (_("Continue"), Iconos.Pelicula_Seguir()),
            TB_FAST: (_("Fast"), Iconos.Pelicula_Rapido()),
            TB_REPEAT: (_("Repeat"), Iconos.Pelicula_Repetir()),
            TB_PGN: (_("PGN"), Iconos.Pelicula_PGN()),
            TB_HELP: (_("Help"), Iconos.AyudaGR()),
            TB_LEVEL: (_("Level"), Iconos.Jugar()),
            TB_ACCEPT: (_("Accept"), Iconos.Aceptar()),
            TB_CANCEL: (_("Cancel"), Iconos.Cancelar()),
            # TB_GAME_OF_THE_DAY: (_("Game of the day"), Iconos.LM()),
            TB_CONFIG: (_("Config"), Iconos.Configurar()),
            TB_UTILITIES: (_("Utilities"), Iconos.Utilidades()),
            TB_VARIATIONS: (_("Variations"), Iconos.VariantesG()),
            TB_TOOLS: (_("Tools"), Iconos.Tools()),
            TB_CHANGE: (_("Change"), Iconos.Cambiar()),
            TB_SHOW_TEXT: (_("Show text"), Iconos.Modificar()),
            TB_HELP_TO_MOVE: (_("Help to move"), Iconos.BotonAyuda()),
            TB_SEND: (_("Send"), Iconos.Enviar()),
            TB_STOP: (_("Play now"), Iconos.Stop()),
        }

        cf = self.gestor.configuracion
        peso = 75 if cf.x_tb_bold else 50
        puntos = cf.x_tb_fontpoints
        font = Controles.TipoLetra(puntos=puntos, peso=peso)

        for clave, (titulo, icono) in dic_opciones.items():
            accion = QtWidgets.QAction(titulo, None)
            accion.setIcon(icono)
            accion.setIconText(titulo)
            accion.setFont(font)
            accion.triggered.connect(self.run_action)
            accion.clave = clave
            self.dicTB[clave] = accion

    def lanzaAtajos(self):
        if self.conAtajos:
            self.gestor.lanza_atajos()

    def lanzaAtajosALT(self, key):
        if self.conAtajos:
            self.gestor.lanzaAtajosALT(key)

    def creaTablero(self):
        ae = QTUtil.altoEscritorio()
        mx = 64 if ae >= 750 else 48
        config_board = self.gestor.configuracion.config_board("BASE", mx)
        self.tablero = Tablero.Tablero(self, config_board)
        self.tablero.crea()
        self.tablero.setFocus()

        Delegados.generaPM(self.tablero.piezas)

    def columnas60(self, siPoner, cNivel):
        o_columns = self.pgn.o_columns
        o_columns.liColumnas[0].cabecera = cNivel if siPoner else _("N.")
        o_columns.liColumnas[1].cabecera = _("Errors") if siPoner else _("White")
        o_columns.liColumnas[2].cabecera = _("Second(s)") if siPoner else _("Black")
        o_columns.liColumnas[0].clave = "NIVEL" if siPoner else "NUMERO"
        o_columns.liColumnas[1].clave = "ERRORES" if siPoner else "BLANCAS"
        o_columns.liColumnas[2].clave = "TIEMPO" if siPoner else "NEGRAS"
        self.pgn.releerColumnas()

        self.pgn.seleccionaFilas(siPoner, False)

    def ponWhiteBlack(self, white, black):
        o_columns = self.pgn.o_columns
        o_columns.liColumnas[1].cabecera = white if white else _("White")
        o_columns.liColumnas[2].cabecera = black if black else _("Black")

    def creaBloqueInformacion(self):
        configuracion = self.gestor.configuracion
        nAnchoPgn = configuracion.x_pgn_width
        nAnchoColor = (nAnchoPgn - 52 - 24) // 2
        nAnchoLabels = max(int((nAnchoPgn - 3) // 2), 140)
        # # Pgn
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMERO", _("N."), 52, centered=True)
        si_figurines_pgn = configuracion.x_pgn_withfigurines
        o_columns.nueva(
            "BLANCAS", _("White"), nAnchoColor, edicion=Delegados.EtiquetaPGN(True if si_figurines_pgn else None)
        )
        o_columns.nueva(
            "NEGRAS", _("Black"), nAnchoColor, edicion=Delegados.EtiquetaPGN(False if si_figurines_pgn else None)
        )
        self.pgn = Grid.Grid(self, o_columns, siCabeceraMovible=False)
        self.pgn.setMinimumWidth(nAnchoPgn)
        self.pgn.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.pgn.tipoLetra(puntos=configuracion.x_pgn_fontpoints)
        self.pgn.ponAltoFila(configuracion.x_pgn_rowheight)

        # # Blancas y negras
        f = Controles.TipoLetra(puntos=configuracion.x_sizefont_infolabels + 2, peso=75)
        self.lb_player_white = Controles.LB(self).anchoFijo(nAnchoLabels).alinCentrado().ponFuente(f).ponWrap()
        style = "QWidget { border-style: groove; border-width: 2px; border-color: Gray; padding: 4px 4px 4px 4px;background-color:%s;color:%s;}"
        self.lb_player_white.setStyleSheet(style % ("white", "black"))

        self.lb_player_black = Controles.LB(self).anchoFijo(nAnchoLabels).alinCentrado().ponFuente(f).ponWrap()
        self.lb_player_black.setStyleSheet(style % ("black", "white"))

        # # Capturas
        n_alto_fijo = 2*(configuracion.x_sizefont_infolabels + 2)
        self.lb_capt_white = Controles.LB(self).anchoFijo(nAnchoLabels).ponWrap().altoFijo(n_alto_fijo)
        style = "QWidget { border-style: groove; border-width: 1px; border-color: LightGray; padding: 2px 0px 2px 0px;}"
        self.lb_capt_white.setStyleSheet(style)

        self.lb_capt_black = Controles.LB(self).anchoFijo(nAnchoLabels).ponWrap().altoFijo(n_alto_fijo)
        self.lb_capt_black.setStyleSheet(style)

        # Relojes
        f = Controles.TipoLetra("Arial Black", puntos=26, peso=75)

        def lbReloj():
            lb = (
                Controles.LB(self, "00:00")
                .ponFuente(f)
                .alinCentrado()
                .ponColorFondoN("#076C9F", "#EFEFEF")
                .anchoMinimo(nAnchoLabels)
            )
            lb.setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
            return lb

        self.lb_clock_white = lbReloj()
        self.lb_clock_black = lbReloj()

        # Revisando
        f = Controles.TipoLetra(puntos=14, peso=75)
        self.lbRevision = Controles.LB(self, _("Reviewing...")).alinCentrado().ponFuente(f).ponFondoN("#b3b3b3")

        f = Controles.TipoLetra(puntos=12)
        # Boton de tutor activo
        self.btActivarTutor = Controles.PB(self, "", rutina=self.cambiaSiActivarTutor, plano=False).ponFuente(f)

        # Rotulos de informacion
        f = Controles.TipoLetra(puntos=configuracion.x_sizefont_infolabels)
        self.lbRotulo1 = Controles.LB(self).ponWrap().ponFuente(f)
        self.lbRotulo2 = Controles.LB(self).ponWrap().ponFuente(f)
        f9 = Controles.TipoLetra(puntos=9)
        self.lbRotulo3 = Controles.LB(self).ponWrap().ponFuente(f9)
        self.lbRotulo3.setStyleSheet("*{ border: 1px solid darkgray }")
        self.lbRotulo3.altoFijo(48)

        # Lo escondemos
        self.lb_player_white.hide()
        self.lb_player_black.hide()
        self.lb_capt_white.hide()
        self.lb_capt_black.hide()
        self.lb_clock_white.hide()
        self.lb_clock_black.hide()
        self.lb_capt_white.hide()
        self.lb_capt_black.hide()
        self.pgn.hide()
        self.lbRevision.hide()
        self.btActivarTutor.hide()
        self.lbRotulo1.hide()
        self.lbRotulo2.hide()
        self.lbRotulo3.hide()

        # Layout

        # Arriba
        ly_color = Colocacion.G()
        ly_color.controlc(self.lb_player_white, 0, 0).controlc(self.lb_player_black, 0, 1)
        ly_color.controlc(self.lb_clock_white, 2, 0).controlc(self.lb_clock_black, 2, 1)

        # Abajo
        ly_capturas = Colocacion.H().control(self.lb_capt_white).control(self.lb_capt_black)

        ly_abajo = Colocacion.V()
        ly_abajo.setSizeConstraint(ly_abajo.SetFixedSize)
        ly_abajo.otro(ly_capturas)
        ly_abajo.control(self.lbRevision).control(self.btActivarTutor)
        ly_abajo.control(self.lbRotulo1).control(self.lbRotulo2).control(self.lbRotulo3)

        ly_v = Colocacion.V().otro(ly_color).control(self.pgn)
        ly_v.otro(ly_abajo)

        return ly_v

    def run_action(self):
        self.gestor.run_action(self.sender().clave)

    def pon_toolbar(self, li_acciones, separator=False, conAtajos=False):
        self.conAtajos = conAtajos

        self.tb.clear()
        last = len(li_acciones) - 1
        for n, k in enumerate(li_acciones):
            self.dicTB[k].setVisible(True)
            self.dicTB[k].setEnabled(True)
            self.tb.addAction(self.dicTB[k])
            if separator and n != last:
                self.tb.addSeparator()

        self.tb.li_acciones = li_acciones
        self.tb.update()
        QTUtil.refresh_gui()
        return self.tb

    def dameToolBar(self):
        return self.tb.li_acciones

    def habilitaToolbar(self, kopcion, siHabilitar):
        self.dicTB[kopcion].setEnabled(siHabilitar)

    def mostrarOpcionToolbar(self, kopcion, siMostrar):
        self.dicTB[kopcion].setVisible(siMostrar)

    def ponActivarTutor(self, siActivar):
        self.si_tutor = siActivar
        self.ponRotuloTutor()

    def ponRotuloTutor(self):
        if self.si_tutor:
            mens = _("Tutor enabled")
        else:
            mens = _("Tutor disabled")
        if 0 < self.num_hints < 99:
            mens += " [%d]" % self.num_hints
        self.btActivarTutor.setText(mens)

    def cambiaSiActivarTutor(self):
        self.gestor.cambiaActivarTutor()

    def grid_num_datos(self, grid):
        return self.gestor.numDatos()

    def grid_boton_izquierdo(self, grid, fila, columna):
        self.gestor.pgnMueveBase(fila, columna.clave)

    def grid_boton_derecho(self, grid, fila, columna, modificadores):
        self.gestor.pgnMueveBase(fila, columna.clave)
        self.gestor.gridRightMouse(modificadores.siShift, modificadores.siControl, modificadores.siAlt)

    def boardRightMouse(self, siShift, siControl, siAlt):
        if hasattr(self.gestor, "boardRightMouse"):
            self.gestor.boardRightMouse(siShift, siControl, siAlt)

    def grid_doble_click(self, grid, fila, columna):
        if columna.clave == "NUMERO":
            return
        self.gestor.analizaPosicion(fila, columna.clave)

    def grid_pulsada_cabecera(self, grid, columna):
        colBlancas = self.pgn.o_columns.columna(1)
        colNegras = self.pgn.o_columns.columna(2)
        nuevoTam = 0
        if colBlancas.ancho != self.pgn.columnWidth(1):
            nuevoTam = self.pgn.columnWidth(1)
        elif colNegras.ancho != self.pgn.columnWidth(2):
            nuevoTam = self.pgn.columnWidth(2)

        if nuevoTam:
            colBlancas.ancho = nuevoTam
            colNegras.ancho = nuevoTam
            self.pgn.ponAnchosColumnas()
            nAnchoPgn = nuevoTam * 2 + self.pgn.columnWidth(0) + 28
            self.pgn.setMinimumWidth(nAnchoPgn)
            QTUtil.refresh_gui()
            self.gestor.configuracion.x_pgn_width = nAnchoPgn
            self.gestor.configuracion.graba()

    def grid_tecla_control(self, grid, k, siShift, siControl, siAlt):
        self.teclaPulsada("G", k)

    def grid_wheel_event(self, ogrid, siAdelante):
        self.teclaPulsada("T", 16777236 if not siAdelante else 16777234)

    def grid_dato(self, grid, fila, oColumna):
        controlPGN = self.gestor.pgn

        col = oColumna.clave
        if col == "NUMERO":
            return controlPGN.dato(fila, col)

        move = controlPGN.soloJugada(fila, col)
        if not move:
            return self.gestor.pgn.dato(fila, col)  # GestorMate,...

        if not controlPGN.siMostrar:
            return "-"

        color = None
        info = ""
        indicadorInicial = None

        color_nag = NAG_0
        stNAGS = set(move.li_nags)
        for nag in stNAGS:
            if 0 < nag < 7:
                color_nag = nag
                break

        if move.analysis:
            mrm, pos = move.analysis
            rm = mrm.li_rm[pos]
            mate = rm.mate
            siW = move.position_before.is_white
            if mate:
                if mate == 1:
                    info = ""
                else:
                    if not siW:
                        mate = -mate
                    info = "(M%+d)" % mate
            else:
                pts = rm.puntos
                if not siW:
                    pts = -pts
                info = "(%+0.2f)" % float(pts / 100.0)

            nag, color_nag = mrm.set_nag_color(self.configuracion, rm)
            stNAGS.add(nag)

        if move.in_the_opening or len(stNAGS) > 0 or move.comment or move.variations:
            siA = move.in_the_opening
            nR = 0
            if len(stNAGS) > 0:
                nR += 1
            if move.comment:
                nR += 1
            if len(move.variations) > 0:
                nR += 1
            if siA:
                indicadorInicial = "R" if nR == 0 else "S"
            elif nR == 1:
                indicadorInicial = "V"
            elif nR > 1:
                indicadorInicial = "M"

        pgn = move.pgnFigurinesSP() if self.gestor.configuracion.x_pgn_withfigurines else move.pgn_translated()
        if color_nag:
            c = self.gestor.configuracion
            color = {
                NAG_1: c.x_color_nag1,
                NAG_2: c.x_color_nag2,
                NAG_3: c.x_color_nag3,
                NAG_4: c.x_color_nag4,
                NAG_5: c.x_color_nag5,
                NAG_6: c.x_color_nag6,
            }[color_nag]

        return pgn, color, info, indicadorInicial, stNAGS

    def grid_setvalue(self, grid, fila, oColumna, valor):
        pass

    def keyPressEvent(self, event):
        k = event.key()
        if self.conAtajos:
            if 49 <= k <= 57:
                m = int(event.modifiers())
                if (m & QtCore.Qt.AltModifier) > 0:
                    self.lanzaAtajosALT(k - 48)
                    return
        self.teclaPulsada("V", event.key())

    def tableroWheelEvent(self, tablero, siAdelante):
        self.teclaPulsada("T", 16777236 if siAdelante else 16777234)

    def teclaPulsada(self, tipo, tecla):
        if self.procesandoEventos:
            QTUtil.refresh_gui()
            return
        self.procesandoEventos = True

        dic = QTUtil2.dicTeclas()
        if tecla in dic:
            if hasattr(self.gestor, "mueveJugada"):
                self.gestor.mueveJugada(dic[tecla])
        elif tecla in (16777220, 16777221):  # intros
            fila, columna = self.pgn.current_position()
            if columna.clave != "NUMERO":
                if hasattr(self.gestor, "analizaPosicion"):
                    self.gestor.analizaPosicion(fila, columna.clave)
        else:
            if hasattr(self.gestor, "control_teclado"):
                self.gestor.control_teclado(tecla)
        self.procesandoEventos = False

    def pgnRefresh(self):
        self.pgn.refresh()

    def activaJuego(self, siActivar, siReloj, siAyudas=None):
        self.pgn.setVisible(siActivar)
        self.lbRevision.hide()
        if siAyudas is None:
            siAyudas = siActivar
        self.btActivarTutor.setVisible(siActivar)
        self.lbRotulo1.setVisible(False)
        self.lbRotulo2.setVisible(False)
        self.lbRotulo3.setVisible(False)
        self.lb_capt_white.setVisible(False)
        self.lb_capt_black.setVisible(False)

        self.lb_player_white.setVisible(siReloj)
        self.lb_player_black.setVisible(siReloj)
        self.lb_clock_white.setVisible(siReloj)
        self.lb_clock_black.setVisible(siReloj)

    def nonDistractMode(self, nonDistract):
        if nonDistract:
            for widget in nonDistract:
                widget.setVisible(True)
            nonDistract = None
        else:
            nonDistract = []
            for widget in (
                self.tb,
                self.pgn,
                self.lbRevision,
                self.btActivarTutor,
                self.lbRotulo1,
                self.lbRotulo2,
                self.lbRotulo3,
                self.lb_player_white,
                self.lb_player_black,
                self.lb_clock_white,
                self.lb_clock_black,
                self.lb_capt_white,
                self.lb_capt_black
            ):
                if widget.isVisible():
                    nonDistract.append(widget)
                    widget.setVisible(False)
        return nonDistract

    def ponDatosReloj(self, bl, rb, ng, rn):
        self.ponRelojBlancas(rb, "00:00")
        self.ponRelojNegras(rn, "00:00")
        self.change_player_labels(bl, ng)

    def change_player_labels(self, bl, ng):
        self.lb_player_white.altoMinimo(0)
        self.lb_player_black.altoMinimo(0)
        self.lb_player_white.ponTexto(bl)
        self.lb_player_black.ponTexto(ng)
        self.lb_player_white.show()
        self.lb_player_black.show()
        QTUtil.refresh_gui()

        hb = self.lb_player_white.height()
        hn = self.lb_player_black.height()
        if hb > hn:
            self.lb_player_black.altoMinimo(hb)
        elif hb < hn:
            self.lb_player_white.altoMinimo(hn)

    def put_captures(self, dic):
        d = {True: [], False: []}
        for pz, num in dic.items():
            for x in range(num):
                d[pz.isupper()].append(pz)

        def xshow(max_num, tp, li, lb):
            html = ""
            for n, pz in enumerate(reversed(li)):
                if n >= max_num:
                    html += "···"
                    break
                # html += '<img src="../Resources/IntFiles/Figs/%s%s.png">' % (tp, pz.lower())
                html += '<img src="../Resources/IntFiles/Figs/%s%s.png" width="20" height="20">' % (tp, pz.lower())
            lb.ponTexto(html)

        max_num = self.lb_capt_white.width()//23
        xshow(max_num, "b", d[True], self.lb_capt_white)
        xshow(max_num, "w", d[False], self.lb_capt_black)
        self.lb_capt_white.show()
        self.lb_capt_black.show()

    def ponAyudas(self, puntos, siQuitarAtras=True):
        self.num_hints = puntos
        self.ponRotuloTutor()

        if (puntos == 0) and siQuitarAtras:
            if TB_TAKEBACK in self.tb.li_acciones:
                self.dicTB[TB_TAKEBACK].setVisible(False)

    def quitaAyudas(self, siTambienTutorAtras, siQuitarAtras=True):
        if siTambienTutorAtras:
            self.btActivarTutor.setVisible(False)
            if siQuitarAtras and (TB_TAKEBACK in self.tb.li_acciones):
                self.dicTB[TB_TAKEBACK].setVisible(False)

    def ponRotulo1(self, rotulo):
        if rotulo:
            self.lbRotulo1.ponTexto(rotulo)
            self.lbRotulo1.show()
        else:
            self.lbRotulo1.hide()
        return self.lbRotulo1

    def ponRotulo2(self, rotulo):
        if rotulo:
            self.lbRotulo2.ponTexto(rotulo)
            self.lbRotulo2.show()
        else:
            self.lbRotulo2.hide()
        return self.lbRotulo2

    def alturaRotulo3(self, px):
        self.lbRotulo3.altoFijo(px)

    def ponRotulo3(self, rotulo):
        if rotulo is not None:
            self.lbRotulo3.ponTexto(rotulo)
            self.lbRotulo3.show()
        else:
            self.lbRotulo3.hide()
        return self.lbRotulo3

    def ponRelojBlancas(self, tm, tm2):
        if tm2 is not None:
            tm += '<br><FONT SIZE="-4">' + tm2
        self.lb_clock_white.ponTexto(tm)

    def ponRelojNegras(self, tm, tm2):
        if tm2 is not None:
            tm += '<br><FONT SIZE="-4">' + tm2
        self.lb_clock_black.ponTexto(tm)

    # def creaCapturas(self):
    #     self.capturas = WCapturas.CapturaLista(self, self.tablero)
