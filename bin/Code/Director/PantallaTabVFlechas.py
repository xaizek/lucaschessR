import copy

from PySide2 import QtCore, QtWidgets

import Code
from Code.Director import TabVisual
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
from Code.QT import TabFlechas
from Code import Util


def tiposDestino():
    li = ((_("To center"), "c"), (_("To closest point"), "m"))
    return li


class WTV_Flecha(QtWidgets.QDialog):
    def __init__(self, owner, regFlecha, siNombre):

        QtWidgets.QDialog.__init__(self, owner)

        self.setWindowTitle(_("Arrow"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.siNombre = siNombre

        if regFlecha is None:
            regFlecha = TabVisual.PFlecha()

        li_acciones = [(_("Save"), Iconos.Aceptar(), "grabar"), None, (_("Cancel"), Iconos.Cancelar(), "reject"), None]
        tb = Controles.TB(self, li_acciones)

        # Tablero
        config_board = owner.tablero.config_board.copia(owner.tablero.config_board.id())
        config_board.anchoPieza(32)
        self.tablero = Tablero.Tablero(self, config_board, siDirector=False)
        self.tablero.crea()
        self.tablero.copiaPosicionDe(owner.tablero)

        # Datos generales
        liGen = []

        if siNombre:
            # name de la arrow que se usara en los menus del tutorial
            config = FormLayout.Editbox(_("Name"), ancho=120)
            liGen.append((config, regFlecha.name))

        # ( "forma", "t", "a" ), # a = abierta -> , c = cerrada la cabeza, p = poligono cuadrado,
        liFormas = (
            (_("Opened"), "a"),
            (_("Head closed"), "c"),
            (_("Polygon  1"), "1"),
            (_("Polygon  2"), "2"),
            (_("Polygon  3"), "3"),
        )
        config = FormLayout.Combobox(_("Form"), liFormas)
        liGen.append((config, regFlecha.forma))

        # ( "tipo", "n", Qt.SolidLine ), #1=SolidLine, 2=DashLine, 3=DotLine, 4=DashDotLine, 5=DashDotDotLine
        config = FormLayout.Combobox(_("Line Type"), QTUtil2.tiposDeLineas())
        liGen.append((config, regFlecha.tipo))

        # liGen.append( (None,None) )

        # ( "color", "n", 0 ),
        config = FormLayout.Colorbox(_("Color"), 80, 20)
        liGen.append((config, regFlecha.color))

        # ( "colorinterior", "n", -1 ), # si es cerrada
        config = FormLayout.Colorbox(_("Internal color"), 80, 20, siChecked=True)
        liGen.append((config, regFlecha.colorinterior))

        # ( "opacidad", "n", 1.0 ),
        config = FormLayout.Dial(_("Degree of transparency"), 0, 99)
        liGen.append((config, 100 - int(regFlecha.opacidad * 100)))

        # liGen.append( (None,None) )

        # ( "redondeos", "l", False ),
        liGen.append((_("Rounded edges"), regFlecha.redondeos))

        # ( "grosor", "n", 1 ), # ancho del trazo
        config = FormLayout.Spinbox(_("Thickness"), 1, 20, 50)
        liGen.append((config, regFlecha.grosor))

        # liGen.append( (None,None) )

        # ( "altocabeza", "n", 1 ), # altura de la cabeza
        config = FormLayout.Spinbox(_("Head height"), 0, 100, 50)
        liGen.append((config, regFlecha.altocabeza))

        # ( "ancho", "n", 10 ), # ancho de la base de la arrow si es un poligono
        config = FormLayout.Spinbox(_("Base width"), 1, 100, 50)
        liGen.append((config, regFlecha.ancho))

        # ( "vuelo", "n", 5 ), # vuelo de la arrow respecto al ancho de la base
        config = FormLayout.Spinbox(_("Additional width of the base of the head"), 1, 100, 50)
        liGen.append((config, regFlecha.vuelo))

        # ( "descuelgue", "n", 2 ), # vuelo hacia arriba
        config = FormLayout.Spinbox(_("Height of the base angle of the head"), -100, 100, 50)
        liGen.append((config, regFlecha.descuelgue))

        # liGen.append( (None,None) )

        # ( "destino", "t", "c" ), # c = centro, m = minimo
        config = FormLayout.Combobox(_("Target position"), tiposDestino())
        liGen.append((config, regFlecha.destino))

        # liGen.append( (None,None) )

        # orden
        config = FormLayout.Combobox(_("Order concerning other items"), QTUtil2.listaOrdenes())
        liGen.append((config, regFlecha.position.orden))

        self.form = FormLayout.FormWidget(liGen, dispatch=self.cambios)

        # Layout
        layout = Colocacion.H().control(self.form).relleno().control(self.tablero)
        layout1 = Colocacion.V().control(tb).otro(layout)
        self.setLayout(layout1)

        # Ejemplos
        self.tablero.borraMovibles()
        liMovs = ["d2d6", "a8h8", "h5b7"]
        self.liEjemplos = []
        for a1h8 in liMovs:
            regFlecha.a1h8 = a1h8
            regFlecha.siMovible = True
            arrow = self.tablero.creaFlecha(regFlecha)
            self.liEjemplos.append(arrow)

    def process_toolbar(self):
        accion = self.sender().clave
        eval("self.%s()" % accion)

    def cambios(self):
        if hasattr(self, "form"):
            li = self.form.get()
            n = 1 if self.siNombre else 0
            for arrow in self.liEjemplos:
                regFlecha = arrow.bloqueDatos
                if self.siNombre:
                    regFlecha.name = li[0]
                regFlecha.forma = li[n]
                regFlecha.tipo = li[n + 1]
                regFlecha.color = li[n + 2]
                regFlecha.colorinterior = li[n + 3]
                # regFlecha.colorinterior2 = li[4]
                regFlecha.opacidad = (100.0 - float(li[n + 4])) / 100.0
                regFlecha.redondeos = li[n + 5]
                regFlecha.grosor = li[n + 6]
                regFlecha.altocabeza = li[n + 7]
                regFlecha.ancho = li[n + 8]
                regFlecha.vuelo = li[n + 9]
                regFlecha.descuelgue = li[n + 10]
                regFlecha.destino = li[n + 11]
                regFlecha.position.orden = li[n + 12]
                arrow.posicion2xy()  # posible cambio en destino
                arrow.setOpacity(regFlecha.opacidad)
                arrow.setZValue(regFlecha.position.orden)
            self.tablero.escena.update()
            QTUtil.refresh_gui()

    def grabar(self):
        regFlecha = self.liEjemplos[0].bloqueDatos
        if self.siNombre:
            name = regFlecha.name.strip()
            if name == "":
                QTUtil2.message_error(self, _("Name missing"))
                return

        bf = regFlecha
        p = bf.position
        p.x = 0
        p.y = 16
        p.ancho = 32
        p.alto = 16

        pm = TabFlechas.pixmapArrow(bf, 32, 32)
        buf = QtCore.QBuffer()
        pm.save(buf, "PNG")
        regFlecha.png = bytes(buf.buffer())
        self.regFlecha = regFlecha
        self.accept()


class WTV_Flechas(QTVarios.WDialogo):
    def __init__(self, owner, list_arrows, dbFlechas):

        titulo = _("Arrows")
        icono = Iconos.Flechas()
        extparam = "flechas"
        QTVarios.WDialogo.__init__(self, owner, titulo, icono, extparam)

        self.owner = owner

        flb = Controles.TipoLetra(puntos=8)

        self.configuracion = Code.configuracion

        self.dbFlechas = dbFlechas

        self.liPFlechas = owner.list_arrows()

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMERO", _("N."), 60, centered=True)
        o_columns.nueva("NOMBRE", _("Name"), 256)

        self.grid = Grid.Grid(self, o_columns, xid="F", siSelecFilas=True)

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
        liMovs = ["d2d6", "a8h8", "h5b7"]
        self.liEjemplos = []
        regFlecha = TabTipos.Flecha()
        for a1h8 in liMovs:
            regFlecha.a1h8 = a1h8
            regFlecha.siMovible = True
            arrow = self.tablero.creaFlecha(regFlecha)
            self.liEjemplos.append(arrow)

        self.grid.gotop()
        self.grid.setFocus()

    def closeEvent(self, event):
        self.save_video()

    def terminar(self):
        self.save_video()
        self.close()

    def grid_num_datos(self, grid):
        return len(self.liPFlechas)

    def grid_dato(self, grid, fila, oColumna):
        key = oColumna.clave
        if key == "NUMERO":
            return str(fila + 1)
        elif key == "NOMBRE":
            return self.liPFlechas[fila].name

        return len(self.liPFlechas)

    def grid_doble_click(self, grid, fila, oColumna):
        self.modificar()

    def grid_cambiado_registro(self, grid, fila, oColumna):
        if fila >= 0:
            regFlecha = self.liPFlechas[fila]
            for ejemplo in self.liEjemplos:
                a1h8 = ejemplo.bloqueDatos.a1h8
                bd = copy.deepcopy(regFlecha)
                bd.a1h8 = a1h8
                bd.anchoCasilla = self.tablero.anchoCasilla
                ejemplo.bloqueDatos = bd
                ejemplo.reset()
            self.tablero.escena.update()

    def process_toolbar(self):
        accion = self.sender().clave
        eval("self.%s()" % accion)

    def mas(self):
        w = WTV_Flecha(self, None, True)
        if w.exec_():
            regFlecha = w.regFlecha
            regFlecha.id = Util.str_id()
            regFlecha.ordenVista = (self.liPFlechas[-1].ordenVista + 1) if self.liPFlechas else 1
            self.dbFlechas[regFlecha.id] = regFlecha.save_dic()
            self.liPFlechas.append(regFlecha)
            self.grid.refresh()
            self.grid.gobottom()
            self.grid.setFocus()

    def borrar(self):
        fila = self.grid.recno()
        if fila >= 0:
            if QTUtil2.pregunta(self, _X(_("Delete the arrow %1?"), self.liPFlechas[fila].name)):
                regFlecha = self.liPFlechas[fila]
                str_id = regFlecha.id
                del self.dbFlechas[str_id]
                del self.liPFlechas[fila]
                self.grid.refresh()
                self.grid.setFocus()

    def modificar(self):
        fila = self.grid.recno()
        if fila >= 0:
            w = WTV_Flecha(self, self.liPFlechas[fila], True)
            if w.exec_():
                regFlecha = w.regFlecha
                str_id = regFlecha.id
                self.liPFlechas[fila] = regFlecha
                self.dbFlechas[str_id] = regFlecha.save_dic()
                self.grid.refresh()
                self.grid.setFocus()
                self.grid_cambiado_registro(self.grid, fila, None)

    def copiar(self):
        fila = self.grid.recno()
        if fila >= 0:
            regFlecha = copy.deepcopy(self.liPFlechas[fila])

            def siEstaNombre(name):
                for rf in self.liPFlechas:
                    if rf.name == name:
                        return True
                return False

            n = 1
            name = "%s-%d" % (regFlecha.name, n)
            while siEstaNombre(name):
                n += 1
                name = "%s-%d" % (regFlecha.name, n)
            regFlecha.name = name
            regFlecha.id = Util.str_id()
            regFlecha.ordenVista = self.liPFlechas[-1].ordenVista + 1
            self.dbFlechas[regFlecha.id] = regFlecha.save_dic()
            self.liPFlechas.append(regFlecha)
            self.grid.refresh()
            self.grid.setFocus()

    def intercambia(self, fila1, fila2):
        regFlecha1, regFlecha2 = self.liPFlechas[fila1], self.liPFlechas[fila2]
        regFlecha1.ordenVista, regFlecha2.ordenVista = regFlecha2.ordenVista, regFlecha1.ordenVista
        self.dbFlechas[regFlecha1.id] = regFlecha1.save_dic()
        self.dbFlechas[regFlecha2.id] = regFlecha2.save_dic()
        self.liPFlechas[fila1], self.liPFlechas[fila2] = self.liPFlechas[fila1], self.liPFlechas[fila2]
        self.grid.goto(fila2, 0)
        self.grid.refresh()
        self.grid.setFocus()

    def arriba(self):
        fila = self.grid.recno()
        if fila > 0:
            self.intercambia(fila, fila - 1)

    def abajo(self):
        fila = self.grid.recno()
        if 0 <= fila < (len(self.liPFlechas) - 1):
            self.intercambia(fila, fila + 1)
