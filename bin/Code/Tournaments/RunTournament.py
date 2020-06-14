from PySide2 import QtWidgets

import Code
from Code import Configuracion, AperturasStd
from Code.QT import Piezas
from Code.Tournaments import WTournamentRun


def run(user, file_tournament, file_work):
    # sys.stderr = Util.Log("./bug.tournaments")

    app = QtWidgets.QApplication([])

    configuracion = Configuracion.Configuracion(user)
    configuracion.lee()
    configuracion.leeConfTableros()
    configuracion.releeTRA()
    Code.configuracion = configuracion
    AperturasStd.reset()
    Code.todasPiezas = Piezas.TodasPiezas()

    app.setStyle(QtWidgets.QStyleFactory.create(configuracion.x_style))
    QtWidgets.QApplication.setPalette(QtWidgets.QApplication.style().standardPalette())

    w = WTournamentRun.WTournamentRun(file_tournament, file_work)
    w.show()
    w.busca_trabajo()

    # app.exec_()
