from PySide2 import QtCore

from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import Tablero
import Code
from Code.Constantes import *


class PantallaTutor(QTVarios.WDialogo):
    def __init__(self, gestor, tutor, siRival, siAperturas, is_white, siPuntos):
        titulo = _("Analyzing your move")
        icono = Iconos.Tutor()
        extparam = "tutor"
        QTVarios.WDialogo.__init__(self, gestor.main_window, titulo, icono, extparam)

        self.tutor = tutor
        self.gestor0 = gestor.gestor
        self.respLibro = None
        self.siElegidaApertura = False

        self.x_tutor_view = gestor.procesador.configuracion.x_tutor_view

        # ~ self.setStyleSheet("QDialog,QGroupBox { background: #f0f0f0; }")

        f = Controles.TipoLetra(puntos=12, peso=75)
        flb = Controles.TipoLetra(puntos=10)
        flba = Controles.TipoLetra(puntos=8)

        ae = QTUtil.anchoEscritorio()
        mx = 32 if ae > 1000 else 20
        config_board = Code.configuracion.config_board("TUTOR", mx)

        # Tableros

        def creaTablero(name, si=True, siLibre=True, siMas=False):
            if not si:
                return None, None, None
            tablero = Tablero.Tablero(self, config_board)
            tablero.crea()
            tablero.ponerPiezasAbajo(is_white)
            lytb, tb = QTVarios.lyBotonesMovimiento(self, name, siLibre, siMas=siMas)
            return tablero, lytb, tb

        self.tableroTutor, lytbTutor, self.tbTutor = creaTablero("tutor")
        self.tableroUsuario, lytbUsuario, self.tbUsuario = creaTablero("user")
        self.tableroRival, lytbRival, self.tbRival = creaTablero("rival", siRival)
        self.tableroApertura, lytbApertura, self.tbApertura = creaTablero("opening", siAperturas, siLibre=False)
        tutor.ponTablerosGUI(self.tableroTutor, self.tableroUsuario, self.tableroRival, self.tableroApertura)

        # Puntuaciones
        self.lbTutorPuntuacion = Controles.LB(self).alinCentrado().ponFuente(flb)
        self.lbUsuarioPuntuacion = Controles.LB(self).alinCentrado().ponFuente(flb)
        if siRival:
            self.lbRivalPuntuacion = Controles.LB(self).alinCentrado().ponFuente(flb)

        # Aperturas
        if siAperturas:
            li_options = self.tutor.opcionesAperturas()
            self.cbAperturas = Controles.CB(self, li_options, 0)
            self.cbAperturas.setFont(flba)
            self.connect(self.cbAperturas, QtCore.SIGNAL("currentIndexChanged(int)"), self.tutor.cambiarApertura)

        # RM
        liRM = []
        for n, uno in enumerate(tutor.list_rm):
            liRM.append((uno[1], n))

        self.cbRM, self.lbRM = QTUtil2.comboBoxLB(self, liRM, liRM[0][1], _("Moves analyzed"))
        self.connect(self.cbRM, QtCore.SIGNAL("currentIndexChanged (int)"), tutor.cambiadoRM)
        lyRM = Colocacion.H().control(self.lbRM).control(self.cbRM)

        lyTutor = Colocacion.V().relleno().control(self.lbTutorPuntuacion).relleno()
        gbTutor = Controles.GB(self, _("Tutor's suggestion"), lyTutor).ponFuente(f).alinCentrado()
        if siPuntos:
            gbTutor.conectar(self.elegirTutor)
            self.lbTutorPuntuacion.setEnabled(True)

        lyUsuario = Colocacion.V().relleno().control(self.lbUsuarioPuntuacion).relleno()
        gbUsuario = (
            Controles.GB(self, _("Your move"), lyUsuario).ponFuente(f).alinCentrado().conectar(self.elegirUsuario)
        )
        self.lbUsuarioPuntuacion.setEnabled(True)
        btLibros = Controles.PB(self, _("Consult a book"), self.consultaLibro).ponPlano(False)

        if siRival:
            lyRival = Colocacion.V().relleno().control(self.lbRivalPuntuacion).relleno()
            gbRival = Controles.GB(self, _("Opponent's prediction"), lyRival).ponFuente(f).alinCentrado()

        if siAperturas:
            lyAperturas = Colocacion.V().relleno().control(self.cbAperturas).relleno()
            gbAperturas = Controles.GB(self, _("Opening"), lyAperturas).alinCentrado().ponFuente(f)
            if siPuntos:
                gbAperturas.conectar(self.elegirApertura)
            self.cbAperturas.setEnabled(True)
            self.tutor.cambiarApertura(0)

        dicVista = {
            POS_TUTOR_HORIZONTAL: ((0, 1), (0, 2)),
            POS_TUTOR_HORIZONTAL_2_1: ((0, 1), (4, 0)),
            POS_TUTOR_HORIZONTAL_1_2: ((4, 0), (4, 1)),
            POS_TUTOR_VERTICAL: ((4, 0), (8, 0)),
        }

        usu, riv = dicVista[self.x_tutor_view]

        fu, cu = usu
        fr, cr = riv

        layout = Colocacion.G()
        layout.controlc(gbTutor, 0, 0).controlc(self.tableroTutor, 1, 0).otro(lytbTutor, 2, 0).otroc(lyRM, 3, 0)
        layout.controlc(gbUsuario, fu, cu).controlc(self.tableroUsuario, fu + 1, cu).otro(
            lytbUsuario, fu + 2, cu
        ).controlc(btLibros, fu + 3, cu)
        if siRival:
            layout.controlc(gbRival, fr, cr).controlc(self.tableroRival, fr + 1, cr).otro(lytbRival, fr + 2, cr)
        elif siAperturas:
            layout.controlc(gbAperturas, fr, cr).controlc(self.tableroApertura, fr + 1, cr).otro(
                lytbApertura, fr + 2, cr
            )

        layout.margen(8)

        self.setLayout(layout)

        self.restore_video(siTam=False)

    def process_toolbar(self):
        self.exeTB(self.sender().clave)

    def exeTB(self, accion):
        x = accion.index("Mover")
        quien = accion[:x]
        que = accion[x + 5 :]
        self.tutor.mueve(quien, que)

    # def cambioTablero(self):
    #     self.tableroUsuario.crea()
    #     if self.tableroRival:
    #         self.tableroRival.crea()
    #     if self.tableroApertura:
    #         self.tableroApertura.crea()

    def tableroWheelEvent(self, tablero, siAdelante):
        for t in ["Tutor", "Usuario", "Rival", "Apertura"]:
            if eval("self.tablero%s == tablero" % t):
                self.exeTB(t.lower() + "Mover" + ("Adelante" if siAdelante else "Atras"))
                return

    def consultaLibro(self):
        liMovs = self.gestor0.librosConsulta(True)
        if liMovs:
            self.respLibro = liMovs[-1]
            self.save_video()
            self.accept()

    def elegirTutor(self):
        self.save_video()
        self.accept()

    def elegirApertura(self):
        self.siElegidaApertura = True
        self.save_video()
        self.accept()

    def elegirUsuario(self):
        self.save_video()
        self.reject()

    def ponPuntuacionUsuario(self, txt):
        self.lbUsuarioPuntuacion.setText(txt)

    def ponPuntuacionTutor(self, txt):
        self.lbTutorPuntuacion.setText(txt)

    def ponPuntuacionRival(self, txt):
        self.lbRivalPuntuacion.setText(txt)

    def start_clock(self, funcion):
        if not hasattr(self, "timer"):
            self.timer = QtCore.QTimer(self)
            self.connect(self.timer, QtCore.SIGNAL("timeout()"), funcion)
        self.timer.start(1000)

    def stop_clock(self):
        if hasattr(self, "timer"):
            self.timer.stop()
            delattr(self, "timer")


def cambioTutor(parent, configuracion):
    liGen = [(None, None)]

    # # Tutor
    liGen.append((_("Engine") + ":", configuracion.ayudaCambioTutor()))

    # # Decimas de segundo a pensar el tutor
    liGen.append((_("Duration of engine analysis (secs)") + ":", float(configuracion.x_tutor_mstime / 1000.0)))
    liDepths = [("--", 0)]
    for x in range(1, 51):
        liDepths.append((str(x), x))
    config = FormLayout.Combobox(_("Depth"), liDepths)
    liGen.append((config, configuracion.x_tutor_depth))

    li = [(_("Maximum"), 0)]
    for x in (1, 3, 5, 10, 15, 20, 30, 40, 50, 75, 100, 150, 200):
        li.append((str(x), x))
    config = FormLayout.Combobox(_("Number of moves evaluated by engine(MultiPV)"), li)
    liGen.append((config, configuracion.x_tutor_multipv))

    liGen.append((None, _("Sensitivity")))
    liGen.append(
        (FormLayout.Spinbox(_("Minimum difference in centipawns"), 0, 1000, 70), configuracion.x_tutor_difpoints)
    )
    liGen.append((FormLayout.Spinbox(_("Minimum difference in %"), 0, 1000, 70), configuracion.x_tutor_difporc))

    # Editamos
    resultado = FormLayout.fedit(liGen, title=_("Tutor change"), parent=parent, anchoMinimo=460, icon=Iconos.Opciones())

    if resultado:
        claveMotor, vtime, depth, multiPV, difpts, difporc = resultado[1]
        configuracion.tutor = configuracion.buscaTutor(claveMotor)
        configuracion.x_tutor_mstime = int(vtime * 1000)
        configuracion.x_tutor_depth = depth
        configuracion.x_tutor_multipv = multiPV
        configuracion.x_tutor_difpoints = difpts
        configuracion.x_tutor_difporc = difporc
        configuracion.graba()
        return True
    else:
        return False
