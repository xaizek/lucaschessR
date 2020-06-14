import copy

from PySide2 import QtCore, QtWidgets

from Code import TabVisual
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import TabTipos
from Code.QT import Tablero
from Code import Util
import Code


class WTV_Marco(QtWidgets.QDialog):
    def __init__(self, owner, regMarco):

        QtWidgets.QDialog.__init__(self, owner)

        self.setWindowTitle(_("Box"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        if not regMarco:
            regMarco = TabVisual.PMarco()

        li_acciones = [(_("Save"), Iconos.Aceptar(), "grabar"), None, (_("Cancel"), Iconos.Cancelar(), "reject"), None]
        tb = Controles.TB(self, li_acciones)

        # Tablero
        config_board = owner.tablero.config_board
        self.tablero = Tablero.Tablero(self, config_board, siDirector=False)
        self.tablero.crea()
        self.tablero.copiaPosicionDe(owner.tablero)

        # Datos generales
        liGen = []

        # name del marco que se usara en los menus del tutorial
        config = FormLayout.Editbox(_("Name"), ancho=120)
        liGen.append((config, regMarco.name))

        # ( "tipo", "n", Qt.SolidLine ), #1=SolidLine, 2=DashLine, 3=DotLine, 4=DashDotLine, 5=DashDotDotLine
        config = FormLayout.Combobox(_("Line Type"), QTUtil2.tiposDeLineas())
        liGen.append((config, regMarco.tipo))

        # ( "color", "n", 0 ),
        config = FormLayout.Colorbox(_("Color"), 80, 20)
        liGen.append((config, regMarco.color))

        # ( "colorinterior", "n", -1 ),
        config = FormLayout.Colorbox(_("Internal color"), 80, 20, siChecked=True)
        liGen.append((config, regMarco.colorinterior))

        # ( "opacidad", "n", 1.0 ),
        config = FormLayout.Dial(_("Degree of transparency"), 0, 99)
        liGen.append((config, 100 - int(regMarco.opacidad * 100)))

        # ( "grosor", "n", 1 ), # ancho del trazo
        config = FormLayout.Spinbox(_("Thickness"), 1, 20, 50)
        liGen.append((config, regMarco.grosor))

        # ( "redEsquina", "n", 0 ),
        config = FormLayout.Spinbox(_("Rounded corners"), 0, 100, 50)
        liGen.append((config, regMarco.redEsquina))

        # orden
        config = FormLayout.Combobox(_("Order concerning other items"), QTUtil2.listaOrdenes())
        liGen.append((config, regMarco.position.orden))

        self.form = FormLayout.FormWidget(liGen, dispatch=self.cambios)

        # Layout
        layout = Colocacion.H().control(self.form).relleno().control(self.tablero)
        layout1 = Colocacion.V().control(tb).otro(layout)
        self.setLayout(layout1)

        # Ejemplos
        liMovs = ["b4c4", "e2e2", "e4g7"]
        self.liEjemplos = []
        for a1h8 in liMovs:
            regMarco.a1h8 = a1h8
            regMarco.siMovible = True
            marco = self.tablero.creaMarco(regMarco)
            self.liEjemplos.append(marco)

    def process_toolbar(self):
        accion = self.sender().clave
        eval("self.%s()" % accion)

    def cambios(self):
        if hasattr(self, "form"):
            li = self.form.get()
            for n, marco in enumerate(self.liEjemplos):
                regMarco = marco.bloqueDatos
                regMarco.name = li[0]
                regMarco.tipo = li[1]
                regMarco.color = li[2]
                regMarco.colorinterior = li[3]
                # regMarco.colorinterior2 = li[]
                regMarco.opacidad = (100.0 - float(li[4])) / 100.0
                regMarco.grosor = li[5]
                regMarco.redEsquina = li[6]
                regMarco.position.orden = li[7]
                marco.setOpacity(regMarco.opacidad)
                marco.setZValue(regMarco.position.orden)
                marco.update()
            self.tablero.escena.update()
            QTUtil.refresh_gui()

    def grabar(self):
        regMarco = self.liEjemplos[0].bloqueDatos
        name = regMarco.name.strip()
        if name == "":
            QTUtil2.message_error(self, _("Name missing"))
            return

        self.regMarco = regMarco
        pm = self.liEjemplos[0].pixmap()
        bf = QtCore.QBuffer()
        pm.save(bf, "PNG")
        self.regMarco.png = str(bf.buffer())

        self.accept()


class WTV_Marcos(QTVarios.WDialogo):
    def __init__(self, owner, listaMarcos, dbMarcos):

        titulo = _("Boxes")
        icono = Iconos.Marcos()
        extparam = "marcos"
        QTVarios.WDialogo.__init__(self, owner, titulo, icono, extparam)

        self.owner = owner

        flb = Controles.TipoLetra(puntos=8)

        self.liPMarcos = listaMarcos
        self.configuracion = Code.configuracion

        self.dbMarcos = dbMarcos

        self.liPMarcos = owner.listaMarcos()

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMERO", _("N."), 60, centered=True)
        o_columns.nueva("NOMBRE", _("Name"), 256)

        self.grid = Grid.Grid(self, o_columns, xid="M", siSelecFilas=True)

        li_acciones = [
            (_("Close"), Iconos.MainMenu(), "terminar"),
            None,
            (_("New"), Iconos.Nuevo(), "mas"),
            None,
            (_("Remove"), Iconos.Borrar(), "borrar"),
            None,
            (_("Modify"), Iconos.Modificar(), "modificar"),
            None,
            (_("Copy"), Iconos.Copiar(), "copiar"),
            None,
            (_("Up"), Iconos.Arriba(), "arriba"),
            None,
            (_("Down"), Iconos.Abajo(), "abajo"),
            None,
        ]
        tb = Controles.TB(self, li_acciones)
        tb.setFont(flb)

        ly = Colocacion.V().control(tb).control(self.grid)

        # Tablero
        config_board = owner.tablero.config_board
        self.tablero = Tablero.Tablero(self, config_board, siDirector=False)
        self.tablero.crea()
        self.tablero.copiaPosicionDe(owner.tablero)

        # Layout
        layout = Colocacion.H().otro(ly).control(self.tablero)
        self.setLayout(layout)

        self.register_grid(self.grid)
        self.restore_video()

        # Ejemplos
        liMovs = ["b4c4", "e2e2", "e4g7"]
        self.liEjemplos = []
        regMarco = TabTipos.Marco()
        for a1h8 in liMovs:
            regMarco.a1h8 = a1h8
            regMarco.siMovible = True
            marco = self.tablero.creaMarco(regMarco)
            self.liEjemplos.append(marco)

        self.grid.gotop()
        self.grid.setFocus()

    def closeEvent(self, event):
        self.save_video()

    def terminar(self):
        self.save_video()
        self.close()

    def grid_num_datos(self, grid):
        return len(self.liPMarcos)

    def grid_dato(self, grid, fila, oColumna):
        key = oColumna.clave
        if key == "NUMERO":
            return str(fila + 1)
        elif key == "NOMBRE":
            return self.liPMarcos[fila].name

    def grid_doble_click(self, grid, fila, oColumna):
        self.modificar()

    def grid_cambiado_registro(self, grid, fila, oColumna):
        if fila >= 0:
            regMarco = self.liPMarcos[fila]
            for ejemplo in self.liEjemplos:
                a1h8 = ejemplo.bloqueDatos.a1h8
                bd = copy.deepcopy(regMarco)
                bd.a1h8 = a1h8
                bd.anchoCasilla = self.tablero.anchoCasilla
                ejemplo.bloqueDatos = bd
                ejemplo.reset()
            self.tablero.escena.update()

    def process_toolbar(self):
        accion = self.sender().clave
        eval("self.%s()" % accion)

    def mas(self):
        w = WTV_Marco(self, None)
        if w.exec_():
            regMarco = w.regMarco
            regMarco.id = Util.new_id()
            regMarco.ordenVista = (self.liPMarcos[-1].ordenVista + 1) if self.liPMarcos else 1
            self.dbMarcos[regMarco.id] = regMarco
            self.liPMarcos.append(regMarco)
            self.grid.refresh()
            self.grid.gobottom()
            self.grid.setFocus()

    def borrar(self):
        fila = self.grid.recno()
        if fila >= 0:
            if QTUtil2.pregunta(self, _X(_("Delete box %1?"), self.liPMarcos[fila].name)):
                regMarco = self.liPMarcos[fila]
                xid = regMarco.id
                del self.dbMarcos[xid]
                del self.liPMarcos[fila]
                self.grid.refresh()
                self.grid.setFocus()

    def modificar(self):
        fila = self.grid.recno()
        if fila >= 0:
            w = WTV_Marco(self, self.liPMarcos[fila])
            if w.exec_():
                regMarco = w.regMarco
                xid = regMarco.id
                self.liPMarcos[fila] = regMarco
                self.dbMarcos[xid] = regMarco
                self.grid.refresh()
                self.grid.setFocus()
                self.grid_cambiado_registro(self.grid, fila, None)

    def copiar(self):
        fila = self.grid.recno()
        if fila >= 0:
            regMarco = copy.deepcopy(self.liPMarcos[fila])

            def siEstaNombre(name):
                for rf in self.liPMarcos:
                    if rf.name == name:
                        return True
                return False

            n = 1
            name = "%s-%d" % (regMarco.name, n)
            while siEstaNombre(name):
                n += 1
                name = "%s-%d" % (regMarco.name, n)
            regMarco.name = name
            regMarco.id = Util.new_id()
            regMarco.ordenVista = self.liPMarcos[-1].ordenVista + 1
            self.dbMarcos[regMarco.id] = regMarco
            self.liPMarcos.append(regMarco)
            self.grid.refresh()
            self.grid.setFocus()

    def intercambia(self, fila1, fila2):
        regMarco1, regMarco2 = self.liPMarcos[fila1], self.liPMarcos[fila2]
        regMarco1.ordenVista, regMarco2.ordenVista = regMarco2.ordenVista, regMarco1.ordenVista
        self.dbMarcos[regMarco1.id] = regMarco1
        self.dbMarcos[regMarco2.id] = regMarco2
        self.liPMarcos[fila1], self.liPMarcos[fila2] = self.liPMarcos[fila1], self.liPMarcos[fila2]
        self.grid.goto(fila2, 0)
        self.grid.refresh()
        self.grid.setFocus()

    def arriba(self):
        fila = self.grid.recno()
        if fila > 0:
            self.intercambia(fila, fila - 1)

    def abajo(self):
        fila = self.grid.recno()
        if 0 <= fila < (len(self.liPMarcos) - 1):
            self.intercambia(fila, fila + 1)
