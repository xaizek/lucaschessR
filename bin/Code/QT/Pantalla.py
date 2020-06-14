from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code.QT import Colocacion
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTVarios
from Code.QT import WBase
from Code.QT import WInformacion


class EstadoWindow:
    def __init__(self, x):
        self.noEstado = x == QtCore.Qt.WindowNoState
        self.minimizado = x == QtCore.Qt.WindowMinimized
        self.maximizado = x == QtCore.Qt.WindowMaximized
        self.fullscreen = x == QtCore.Qt.WindowFullScreen
        self.active = x == QtCore.Qt.WindowActive


class PantallaDialog(QTVarios.WDialogo):
    signal_notify = QtCore.Signal()
    signal_routine_connected = None
    dato_notify = None

    def __init__(self, gestor, owner=None):
        self.gestor = gestor

        titulo = ""
        icono = Iconos.Aplicacion64()
        extparam = "maind"
        QTVarios.WDialogo.__init__(self, owner, titulo, icono, extparam)

        self.owner = owner

        # self.setBackgroundRole(QtGui.QPalette.Midlight)
        # self.setStyleSheet( "QToolButton { padding: 2px;}" )
        # self.setStyleSheet( "QWidget { background-color: yellow; }")
        self.base = WBase.WBase(self, gestor)

        self.siCapturas = False
        self.informacionPGN = WInformacion.InformacionPGN(self)
        self.siInformacionPGN = False
        self.informacionPGN.hide()
        self.register_splitter(self.informacionPGN.splitter, "InformacionPGN")

        self.timer = None
        self.siTrabajando = False

        self.cursorthinking = QtGui.QCursor(
            Iconos.pmThinking() if self.gestor.configuracion.x_cursor_thinking else QtCore.Qt.BlankCursor
        )
        self.onTop = False

        self.tablero = self.base.tablero
        self.tablero.dispatchSize(self.ajustaTam)
        self.tablero.permitidoResizeExterno(True)
        self.anchoAntesMaxim = None

        self.splitter = splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(self.base)
        splitter.addWidget(self.informacionPGN)

        ly = Colocacion.H().control(splitter).margen(0)

        self.setLayout(ly)

        ctrl1 = QtWidgets.QShortcut(self)
        ctrl1.setKey("Ctrl+1")
        ctrl1.activated.connect(self.pulsadoShortcutCtrl1)

        ctrlF10 = QtWidgets.QShortcut(self)
        ctrlF10.setKey("Ctrl+0")
        ctrlF10.activated.connect(self.pulsadoShortcutCtrl0)

        F11 = QtWidgets.QShortcut(self)
        F11.setKey("F11")
        F11.activated.connect(self.pulsadoShortcutF11)
        self.activadoF11 = False

        if QtWidgets.QSystemTrayIcon.isSystemTrayAvailable():
            F12 = QtWidgets.QShortcut(self)
            F12.setKey("F12")
            F12.activated.connect(self.pulsadoShortcutF12)
            self.trayIcon = None

        self.resizing = None

        self.cursor_pensado = False

    def set_notify(self, routine):
        if self.signal_routine_connected:
            self.signal_notify.disconnect(self.signal_routine_connected)
        self.signal_notify.connect(routine)
        self.signal_routine_connected = routine

    def notify(self, dato):
        self.dato_notify = dato
        self.signal_notify.emit()

    def closeEvent(self, event):  # Cierre con X
        self.tablero.cierraGuion()
        self.save_video()
        if not self.gestor.finalX0():
            event.ignore()

    def onTopWindow(self):
        self.onTop = not self.onTop
        self.muestra()

    def activateTrayIcon(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.DoubleClick:
            self.restauraTrayIcon()

    def restauraTrayIcon(self):
        self.showNormal()
        self.trayIcon.hide()

    def quitTrayIcon(self):
        self.trayIcon.hide()
        self.accept()
        self.gestor.pararMotores()

    def pulsadoShortcutF12(self):
        if not self.trayIcon:
            restoreAction = QtWidgets.QAction(Iconos.PGN(), _("Show"), self, triggered=self.restauraTrayIcon)
            quitAction = QtWidgets.QAction(Iconos.Terminar(), _("Quit"), self, triggered=self.quitTrayIcon)
            trayIconMenu = QtWidgets.QMenu(self)
            trayIconMenu.addAction(restoreAction)
            trayIconMenu.addSeparator()
            trayIconMenu.addAction(quitAction)

            self.trayIcon = QtWidgets.QSystemTrayIcon(self)
            self.trayIcon.setContextMenu(trayIconMenu)
            self.trayIcon.setIcon(Iconos.Otros())  # Aplicacion())
            self.trayIcon.activated.connect(self.activateTrayIcon)
            self.trayIcon.hide()

        if self.trayIcon:
            self.trayIcon.show()
            self.hide()

    def pulsadoShortcutF11(self):
        self.activadoF11 = not self.activadoF11
        if self.activadoF11:
            self.showFullScreen()
        else:
            self.showNormal()

    def procesosFinales(self):
        self.tablero.cierraGuion()
        self.save_video()
        self.tablero.terminar()

    def closeEvent(self, event):  # Cierre con X
        self.procesosFinales()
        if not self.gestor.finalX0():
            event.ignore()

    def ponGestor(self, gestor):
        self.gestor = gestor
        self.base.ponGestor(gestor)

    def muestra(self):
        flags = QtCore.Qt.Dialog if self.owner else QtCore.Qt.Widget
        flags |= QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowMaximizeButtonHint
        if self.onTop:
            flags |= QtCore.Qt.WindowStaysOnTopHint

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | flags)
        if self.tablero.siMaximizado():
            self.showMaximized()
        else:
            self.restore_video(siTam=False)
            self.ajustaTam()
            self.show()

        self.ponTitulo()

    def changeEvent(self, event):
        QtWidgets.QWidget.changeEvent(self, event)
        if event.type() != QtCore.QEvent.WindowStateChange:
            return

        nue = EstadoWindow(self.windowState())
        ant = EstadoWindow(event.oldState())

        ct = self.tablero.config_board

        if getattr(self.gestor, "siPresentacion", False):
            self.gestor.presentacion(False)

        if nue.fullscreen:
            self.base.tb.hide()
            self.tablero.siF11 = True
            self.antiguoAnchoPieza = 1000 if ant.maximizado else ct.anchoPieza()
            self.tablero.maximizaTam(True)
        else:
            if ant.fullscreen:
                self.base.tb.show()
                self.tablero.normalTam(self.antiguoAnchoPieza)
                self.ajustaTam()
                if self.antiguoAnchoPieza == 1000:
                    self.setWindowState(QtCore.Qt.WindowMaximized)
            elif nue.maximizado:
                self.antiguoAnchoPieza = ct.anchoPieza()
                self.tablero.maximizaTam(False)
            elif ant.maximizado:
                if not self.antiguoAnchoPieza or self.antiguoAnchoPieza == 1000:
                    self.antiguoAnchoPieza = self.tablero.calculaAnchoMXpieza()
                self.tablero.normalTam(self.antiguoAnchoPieza)
                self.ajustaTam()
                # ct.anchoPieza(self.antiguoAnchoPieza)
                # ct.guardaEnDisco()
                # self.tablero.ponAncho()
                # self.ajustaTam()

    def muestraVariantes(self, titulo):
        flags = (
            QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint
        )

        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | flags)

        self.setWindowTitle(titulo if titulo else "-")

        self.restore_video(siTam=False)
        self.ajustaTam()

        resp = self.exec_()
        self.save_video()
        return resp

    def ajustaTam(self):
        if self.isMaximized():
            if not self.tablero.siMaximizado():
                self.tablero.maximizaTam(self.activadoF11)
        else:
            n = 0
            while self.height() > self.tablero.ancho + 80:
                self.adjustSize()
                self.refresh()
                n += 1
                if n > 3:
                    break
        if hasattr(self, "capturas"):
            self.capturas.resetPZ(self.tablero)
        self.refresh()

    def ajustaTamH(self):
        if not self.isMaximized():
            for n in range(3):
                self.adjustSize()
                self.refresh()
        self.refresh()

    def ponTitulo(self):
        self.setWindowTitle(Code.lucas_chess)

    def ponRotulo1(self, rotulo):
        return self.base.ponRotulo1(rotulo)

    def ponRotulo2(self, rotulo):
        return self.base.ponRotulo2(rotulo)

    def ponRotulo3(self, rotulo):
        return self.base.ponRotulo3(rotulo)

    def alturaRotulo3(self, px):
        return self.base.alturaRotulo3(px)

    def ponWhiteBlack(self, white=None, black=None):
        self.base.ponWhiteBlack(white, black)

    def ponRevision(self, siponer):
        return
        # if siponer:
        #     self.base.lbRevision.show()
        # else:
        #     self.base.lbRevision.hide()

    def ponActivarTutor(self, siActivar):
        self.base.ponActivarTutor(siActivar)

    def pon_toolbar(self, li_acciones, separator=True, atajos=False):
        return self.base.pon_toolbar(li_acciones, separator, atajos)

    def dameToolBar(self):
        return self.base.dameToolBar()

    def ponAyudas(self, puntos, with_takeback=True):
        self.base.ponAyudas(puntos, with_takeback)

    def quitaAyudas(self, siTambienTutorAtras, with_takeback=True):
        self.base.quitaAyudas(siTambienTutorAtras, with_takeback)

    def habilitaToolbar(self, opcion, siHabilitar):
        self.base.habilitaToolbar(opcion, siHabilitar)

    def mostrarOpcionToolbar(self, opcion, siMostrar):
        self.base.mostrarOpcionToolbar(opcion, siMostrar)

    def pgnRefresh(self, is_white):
        self.base.pgnRefresh()
        self.base.pgn.gobottom(2 if is_white else 1)

    def pgnColocate(self, fil, is_white):
        col = 1 if is_white else 2
        self.base.pgn.goto(fil, col)

    def pgnPosActual(self):
        return self.base.pgn.current_position()

    def hide_pgn(self):
        self.base.pgn.hide()

    def show_pgn(self):
        self.base.pgn.show()

    def refresh(self):
        self.update()
        QTUtil.refresh_gui()

    def activaCapturas(self, siActivar=None):
        if siActivar is None:
            self.siCapturas = not self.siCapturas
        else:
            self.siCapturas = siActivar
        self.base.lb_capt_white.setVisible(self.siCapturas)
        self.base.lb_capt_black.setVisible(self.siCapturas)

    def activaInformacionPGN(self, siActivar=None):
        if siActivar is None:
            self.siInformacionPGN = not self.siInformacionPGN
        else:
            self.siInformacionPGN = siActivar
        self.informacionPGN.setVisible(self.siInformacionPGN)
        self.ajustaTamH()
        sizes = self.informacionPGN.splitter.sizes()
        for n, size in enumerate(sizes):
            if size == 0:
                sizes[n] = 100
                self.informacionPGN.splitter.setSizes(sizes)
                break

    def ponCapturas(self, dic):
        self.base.put_captures(dic)

    def ponInformacionPGN(self, game, move, opening):
        self.informacionPGN.ponJG(game, move, opening)

    def activaJuego(self, siActivar=True, siReloj=False, siAyudas=None):
        self.base.activaJuego(siActivar, siReloj, siAyudas)
        self.ajustaTamH()

    def ponDatosReloj(self, bl, rb, ng, rn):
        self.base.ponDatosReloj(bl, rb, ng, rn)

    def ponRelojBlancas(self, tm, tm2):
        self.base.ponRelojBlancas(tm, tm2)

    def ponRelojNegras(self, tm, tm2):
        self.base.ponRelojNegras(tm, tm2)

    def change_player_labels(self, bl, ng):
        self.base.change_player_labels(bl, ng)

    def start_clock(self, enlace, transicion=100):
        if self.timer is not None:
            self.timer.stop()
            del self.timer

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(enlace)
        self.timer.start(transicion)

    def stop_clock(self):
        if self.timer is not None:
            self.timer.stop()
            del self.timer
            self.timer = None

    def columnas60(self, siPoner, cNivel=None):
        if cNivel is None:
            cNivel = _("Level")
        self.base.columnas60(siPoner, cNivel)

    def pulsadoShortcutCtrl1(self):
        if self.gestor and hasattr(self.gestor, "control1"):
            self.gestor.control1()

    def pulsadoShortcutCtrl0(self):
        if self.gestor and hasattr(self.gestor, "control0"):
            self.gestor.control0()

    def soloEdicionPGN(self, fichero):
        if fichero:
            titulo = fichero
        else:
            titulo = "<<< %s >>>" % _("Temporary file")

        self.setWindowTitle(titulo)
        self.setWindowIcon(Iconos.PGN())

    def cursorFueraTablero(self):
        p = self.mapToParent(self.tablero.pos())
        p.setX(p.x() + self.tablero.ancho + 4)

        QtGui.QCursor.setPos(p)

    def pensando(self, si_pensando):
        self.refresh()
        pass
        # if si_pensando:
        #     if not self.cursor_pensado:
        #         # QtWidgets.QApplication.setOverrideCursor(self.cursorthinking)
        # else:
        #     if self.cursor_pensado:
        #         # QtWidgets.QApplication.restoreOverrideCursor()
        #         self.wbase.lbRotulo_engine_working.hode()
        #         self.ponRotulo3(None) #_("Engine working..."))
        # self.cursor_pensado = si_pensando
        # self.refresh()

    def pensando_tutor(self, si_pensando):
        if si_pensando:
            if not self.cursor_pensado:
                QtWidgets.QApplication.setOverrideCursor(self.cursorthinking)
        else:
            if self.cursor_pensado:
                QtWidgets.QApplication.restoreOverrideCursor()
        self.cursor_pensado = si_pensando
        self.refresh()
