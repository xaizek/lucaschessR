import copy
import os

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
from Code.QT import Tablero
from Code import Util
import Code


class WTV_Marker(QtWidgets.QDialog):
    def __init__(self, owner, regMarker, xml=None, name=None):

        QtWidgets.QDialog.__init__(self, owner)

        self.setWindowTitle(_("Marker"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.configuracion = Code.configuracion

        if regMarker is None:
            regMarker = TabVisual.PMarker()
            regMarker.xml = xml
            if name:
                regMarker.name = name

        li_acciones = [
            (_("Save"), Iconos.Aceptar(), self.grabar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
        ]
        tb = Controles.TBrutina(self, li_acciones)

        # Tablero
        config_board = owner.tablero.config_board
        self.tablero = Tablero.Tablero(self, config_board, siDirector=False)
        self.tablero.crea()
        self.tablero.copiaPosicionDe(owner.tablero)

        # Datos generales
        liGen = []

        # name del svg que se usara en los menus del tutorial
        config = FormLayout.Editbox(_("Name"), ancho=120)
        liGen.append((config, regMarker.name))

        # ( "opacidad", "n", 1.0 ),
        config = FormLayout.Dial(_("Degree of transparency"), 0, 99)
        liGen.append((config, 100 - int(regMarker.opacidad * 100)))

        # ( "psize", "n", 100 ),
        config = FormLayout.Spinbox(_("Size") + " %", 1, 1600, 50)
        liGen.append((config, regMarker.psize))

        # ( "poscelda", "n", 1 ),
        li = (
            ("%s-%s" % (_("Top"), _("Left")), 0),
            ("%s-%s" % (_("Top"), _("Right")), 1),
            ("%s-%s" % (_("Bottom"), _("Left")), 2),
            ("%s-%s" % (_("Bottom"), _("Right")), 3),
        )
        config = FormLayout.Combobox(_("Position in the square"), li)
        liGen.append((config, regMarker.poscelda))

        # orden
        config = FormLayout.Combobox(_("Order concerning other items"), QTUtil2.listaOrdenes())
        liGen.append((config, regMarker.position.orden))

        self.form = FormLayout.FormWidget(liGen, dispatch=self.cambios)

        # Layout
        layout = Colocacion.H().control(self.form).relleno().control(self.tablero)
        layout1 = Colocacion.V().control(tb).otro(layout)
        self.setLayout(layout1)

        # Ejemplos
        liMovs = ["b4c4", "e2e2", "e4g7"]
        self.liEjemplos = []
        for a1h8 in liMovs:
            regMarker.a1h8 = a1h8
            regMarker.siMovible = True
            marker = self.tablero.creaMarker(regMarker, siEditando=True)
            self.liEjemplos.append(marker)

    def cambios(self):
        if hasattr(self, "form"):
            li = self.form.get()
            for n, marker in enumerate(self.liEjemplos):
                regMarker = marker.bloqueDatos
                regMarker.name = li[0]
                regMarker.opacidad = (100.0 - float(li[1])) / 100.0
                regMarker.psize = li[2]
                regMarker.poscelda = li[3]
                regMarker.position.orden = li[4]
                marker.setOpacity(regMarker.opacidad)
                marker.setZValue(regMarker.position.orden)
                marker.update()
            self.tablero.escena.update()
            QTUtil.refresh_gui()

    def grabar(self):
        regMarker = self.liEjemplos[0].bloqueDatos
        name = regMarker.name.strip()
        if name == "":
            QTUtil2.message_error(self, _("Name missing"))
            return

        pm = self.liEjemplos[0].pixmapX()
        bf = QtCore.QBuffer()
        pm.save(bf, "PNG")
        regMarker.png = str(bf.buffer())

        self.regMarker = regMarker
        self.accept()


class WTV_Markers(QTVarios.WDialogo):
    def __init__(self, owner, listaMarkers, dbMarkers):

        titulo = _("Markers")
        icono = Iconos.Markers()
        extparam = "markers"
        QTVarios.WDialogo.__init__(self, owner, titulo, icono, extparam)

        self.owner = owner

        flb = Controles.TipoLetra(puntos=8)

        self.configuracion = Code.configuracion
        self.liPMarkers = listaMarkers
        self.dbMarkers = dbMarkers

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMERO", _("N."), 60, centered=True)
        o_columns.nueva("NOMBRE", _("Name"), 256)

        self.grid = Grid.Grid(self, o_columns, xid="M", siSelecFilas=True)

        li_acciones = [
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("New"), Iconos.Nuevo(), self.mas),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Modify"), Iconos.Modificar(), self.modificar),
            None,
            (_("Copy"), Iconos.Copiar(), self.copiar),
            None,
            (_("Up"), Iconos.Arriba(), self.arriba),
            None,
            (_("Down"), Iconos.Abajo(), self.abajo),
            None,
        ]
        tb = Controles.TBrutina(self, li_acciones)
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

        self.grid.gotop()
        self.grid.setFocus()

    def closeEvent(self, event):
        self.save_video()

    def terminar(self):
        self.save_video()
        self.close()

    def grid_num_datos(self, grid):
        return len(self.liPMarkers)

    def grid_dato(self, grid, fila, oColumna):
        key = oColumna.clave
        if key == "NUMERO":
            return str(fila + 1)
        elif key == "NOMBRE":
            return self.liPMarkers[fila].name

    def grid_doble_click(self, grid, fila, oColumna):
        self.modificar()

    def grid_cambiado_registro(self, grid, fila, oColumna):
        if fila >= 0:
            regMarker = self.liPMarkers[fila]
            self.tablero.borraMovibles()
            # Ejemplos
            liMovs = ["g4h3", "e2e4", "d6f4"]
            for a1h8 in liMovs:
                regMarker.a1h8 = a1h8
                regMarker.siMovible = True
                self.tablero.creaMarker(regMarker, siEditando=True)
            self.tablero.escena.update()

    def mas(self):

        menu = QTVarios.LCMenu(self)

        def miraDir(submenu, base, dr):
            if base:
                pathCarpeta = base + dr + "/"
                smenu = submenu.submenu(dr, Iconos.Carpeta())
            else:
                pathCarpeta = dr + "/"
                smenu = submenu
            li = []
            for fich in os.listdir(pathCarpeta):
                pathFich = pathCarpeta + fich
                if os.path.isdir(pathFich):
                    miraDir(smenu, pathCarpeta, fich)
                elif pathFich.lower().endswith(".svg"):
                    li.append((pathFich, fich))

            for pathFich, fich in li:
                ico = QTVarios.fsvg2ico(pathFich, 32)
                if ico:
                    smenu.opcion(pathFich, fich[:-4], ico)

        miraDir(menu, "", "imgs")

        menu.separador()

        menu.opcion("@", _X(_("To seek %1 file"), "Marker"), Iconos.Fichero())

        resp = menu.lanza()

        if resp is None:
            return

        if resp == "@":
            fichero = QTUtil2.leeFichero(self, "imgs", "svg", titulo=_("Image"))
            if not fichero:
                return
        else:
            fichero = resp
        with open(fichero, "rt", encoding="utf-8", errors="ignore") as f:
            contenido = f.read()
        name = os.path.basename(fichero)[:-4]
        w = WTV_Marker(self, None, xml=contenido, name=name)
        if w.exec_():
            regMarker = w.regMarker
            regMarker.id = Util.new_id()
            regMarker.ordenVista = (self.liPMarkers[-1].ordenVista + 1) if self.liPMarkers else 1
            self.dbMarkers[regMarker.id] = regMarker
            self.liPMarkers.append(regMarker)
            self.grid.refresh()
            self.grid.gobottom()
            self.grid.setFocus()

    def borrar(self):
        fila = self.grid.recno()
        if fila >= 0:
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), self.liPMarkers[fila].name)):
                regMarker = self.liPMarkers[fila]
                nid = regMarker.id
                del self.liPMarkers[fila]
                del self.dbMarkers[nid]
                self.grid.refresh()
                self.grid.setFocus()

    def modificar(self):
        fila = self.grid.recno()
        if fila >= 0:
            w = WTV_Marker(self, self.liPMarkers[fila])
            if w.exec_():
                regMarker = w.regMarker
                xid = regMarker.id
                self.liPMarkers[fila] = regMarker
                self.dbMarkers[xid] = regMarker
                self.grid.refresh()
                self.grid.setFocus()
                self.grid_cambiado_registro(self.grid, fila, None)

    def copiar(self):
        fila = self.grid.recno()
        if fila >= 0:
            regMarker = copy.deepcopy(self.liPMarkers[fila])
            n = 1

            def siEstaNombre(name):
                for rf in self.liPMarkers:
                    if rf.name == name:
                        return True
                return False

            name = "%s-%d" % (regMarker.name, n)
            while siEstaNombre(name):
                n += 1
                name = "%s-%d" % (regMarker.name, n)
            regMarker.name = name
            regMarker.id = Util.new_id()
            regMarker.ordenVista = self.liPMarkers[-1].ordenVista + 1
            self.dbMarkers[regMarker.id] = regMarker
            self.liPMarkers.append(regMarker)
            self.grid.refresh()
            self.grid.setFocus()

    def intercambia(self, fila1, fila2):
        regMarker1, regMarker2 = self.liPMarkers[fila1], self.liPMarkers[fila2]
        regMarker1.ordenVista, regMarker2.ordenVista = regMarker2.ordenVista, regMarker1.ordenVista
        self.dbMarkers[regMarker1.id] = regMarker1
        self.dbMarkers[regMarker2.id] = regMarker2
        self.liPMarkers[fila1], self.liPMarkers[fila2] = self.liPMarkers[fila1], self.liPMarkers[fila2]
        self.grid.goto(fila2, 0)
        self.grid.refresh()
        self.grid.setFocus()

    def arriba(self):
        fila = self.grid.recno()
        if fila > 0:
            self.intercambia(fila, fila - 1)

    def abajo(self):
        fila = self.grid.recno()
        if 0 <= fila < (len(self.liPMarkers) - 1):
            self.intercambia(fila, fila + 1)
