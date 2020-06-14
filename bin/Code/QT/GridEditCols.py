from PySide2 import QtCore, QtGui, QtWidgets

from Code.QT import QTVarios
from Code.QT import Iconos
from Code.QT import Grid
from Code.QT import Columnas
from Code.QT import Colocacion
from Code.QT import FormLayout
from Code.QT import QTUtil2
from Code.QT import Delegados


class EditCols(QtWidgets.QDialog):
    def __init__(self, grid_owner, configuracion, work):
        QtWidgets.QDialog.__init__(self, grid_owner)
        self.setWindowTitle(_("Edit columns"))
        self.setWindowIcon(Iconos.EditColumns())

        self.grid_owner = grid_owner
        self.o_columnas_base = grid_owner.columnas()
        self.o_columnas = self.o_columnas_base.clone()

        self.configuracion = configuracion
        self.work = work

        li_options = [
            (_("Save"), Iconos.GrabarFichero(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
            (_("Up"), Iconos.Arriba(), self.tw_up),
            (_("Down"), Iconos.Abajo(), self.tw_down),
            None,
            (_("Configurations"), Iconos.Configurar(), self.configurations),
            None,
        ]
        tb = QTVarios.LCTB(self, li_options)

        # Grid
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("SIMOSTRAR", "", 20, siChecked=True)
        o_columns.nueva("CLAVE", _("Key"), 80, centered=True)
        o_columns.nueva("CABECERA", _("Title"), 150, edicion=Delegados.LineaTexto())
        o_columns.nueva("ANCHO", _("Width"), 60, edicion=Delegados.LineaTexto(siEntero=True), siDerecha=True)

        self.liAlin = [_("Left"), _("Center"), _("Right")]
        o_columns.nueva("ALINEACION", _("Alignment"), 100, centered=True, edicion=Delegados.ComboBox(self.liAlin))
        o_columns.nueva("CTEXTO", _("Foreground"), 80, centered=True)
        o_columns.nueva("CFONDO", _("Background"), 80, centered=True)
        self.grid = Grid.Grid(self, o_columns, siEditable=True)

        layout = Colocacion.V().control(tb).control(self.grid).margen(3)
        self.setLayout(layout)

        self.resize(self.grid.anchoColumnas() + 48, 360)
        self.grid.goto(0, 1)

    def tw_up(self):
        pos = self.grid.recno()
        if pos > 0:
            lic = self.o_columnas.liColumnas
            lic[pos], lic[pos - 1] = lic[pos - 1], lic[pos]
            for n, col in enumerate(lic):
                col.position = n

            self.grid.goto(pos - 1, 1)
            self.grid.refresh()

    def tw_down(self):
        pos = self.grid.recno()
        lic = self.o_columnas.liColumnas
        if pos < len(lic) - 1:
            lic[pos], lic[pos + 1] = lic[pos + 1], lic[pos]
            self.grid.goto(pos + 1, 1)
            self.grid.refresh()
            for n, col in enumerate(lic):
                col.position = n

    def configurations(self):
        dic_conf = self.configuracion.leeVariables(self.work)
        menu = QTVarios.LCMenu(self)
        submenu = menu.submenu(_("Save"), Iconos.ManualSave())
        submenu.opcion("save_name", _("Save with name"), Iconos.Grabar())
        submenu.separador()
        submenu.opcion("save_default", _("Save as default"), Iconos.Defecto())
        menu.separador()
        menu.opcion("reinit", _("Reinit"), Iconos.Reiniciar())
        menu.separador()
        if dic_conf:
            menu.setToolTip(_("To choose: <b>left button</b> <br>To erase: <b>right button</b>"))
            for name in dic_conf:
                menu.opcion(name, name, Iconos.PuntoAzul())

        resp = menu.lanza()
        if resp is None:
            return

        elif resp == "save_name":
            form = FormLayout.FormLayout(self, _("Name"), Iconos.Opciones(), anchoMinimo=240)
            form.separador()

            form.edit(_("Name"), "")

            resultado = form.run()
            if resultado:
                accion, resp = resultado
                name = resp[0].strip()
                if name:
                    dic_current = self.o_columnas.save_dic(self.grid_owner)
                    dic_conf[name] = dic_current
                    self.configuracion.escVariables(self.work, dic_conf)

        elif resp == "save_default":
            key = "databases_columns_default"
            dic_current = self.o_columnas.save_dic(self.grid_owner)
            self.configuracion.escVariables(key, dic_current)

        elif resp == "reinit":
            dic_current = self.o_columnas_base.save_dic(self.grid_owner)
            self.o_columnas.restore_dic(dic_current)
            self.o_columnas.liColumnas.sort(key=lambda x: x.position)
            self.grid.refresh()

        else:
            if menu.siDer:
                if QTUtil2.pregunta(self, _X(_("Delete %1?"), resp)):
                    del dic_conf[resp]
                    self.configuracion.escVariables(self.work, dic_conf)
            else:
                dic_current = dic_conf[resp]
                self.o_columnas.restore_dic(dic_current, self.grid_owner)
                self.o_columnas.liColumnas.sort(key=lambda x: x.position)
                self.grid.refresh()

    def aceptar(self):
        self.grid_owner.o_columns = self.o_columnas
        self.accept()

    def grid_num_datos(self, grid):
        return len(self.o_columnas.liColumnas)

    def grid_dato(self, grid, fila, oColumna):
        columna = self.o_columnas.liColumnas[fila]
        clave = oColumna.clave
        if clave == "SIMOSTRAR":
            return columna.siMostrar
        elif clave == "CLAVE":
            return columna.clave
        elif clave == "CABECERA":
            return columna.cabecera
        elif clave == "ALINEACION":
            pos = "icd".find(columna.alineacion)
            return self.liAlin[pos]
        elif clave == "ANCHO":
            return str(columna.ancho)

        return _("Test")

    def grid_setvalue(self, grid, fila, oColumna, value):
        columna = self.o_columnas.liColumnas[fila]
        clave = oColumna.clave
        if clave == "SIMOSTRAR":
            columna.siMostrar = not columna.siMostrar
        elif clave == "CABECERA":
            columna.cabecera = value
        elif clave == "ALINEACION":
            pos = self.liAlin.index(value)
            columna.alineacion = "icd"[pos]
        elif clave == "ANCHO":
            ancho = int(value) if value else 0
            if ancho > 0:
                columna.ancho = ancho

    def grid_color_texto(self, grid, fila, col):
        columna = self.o_columnas.liColumnas[fila]
        if col.clave in ("CTEXTO", "CFONDO"):
            color = columna.rgbTexto
            return None if color == -1 else QtGui.QBrush(QtGui.QColor(color))
        return None

    def grid_color_fondo(self, grid, fila, col):
        columna = self.o_columnas.liColumnas[fila]
        if col.clave in ("CTEXTO", "CFONDO"):
            color = columna.rgbFondo
            return None if color == -1 else QtGui.QBrush(QtGui.QColor(color))
        return None

    def grid_doble_click(self, grid, fila, columna):
        clave = columna.clave
        columna = self.o_columnas.liColumnas[fila]
        if clave in ["CTEXTO", "CFONDO"]:
            siTexto = clave == "CTEXTO"
            if siTexto:
                negro = QtCore.Qt.black
                rgb = columna.rgbTexto
                color = negro if rgb == -1 else QtGui.QColor(rgb)
                color = QtWidgets.QColorDialog.getColor(color, self)
                if color.isValid():
                    columna.rgbTexto = -1 if color == negro else color.rgb()
            else:
                blanco = QtCore.Qt.white
                rgb = columna.rgbFondo
                color = blanco if rgb == -1 else QtGui.QColor(rgb)
                color = QtWidgets.QColorDialog.getColor(color, self)
                if color.isValid():
                    columna.rgbFondo = -1 if color == blanco else color.rgb()
            columna.ponQT()

    def grid_boton_derecho(self, grid, fila, col, modif):
        clave = col.clave
        col = self.o_columnas.liColumnas[fila]
        if clave in ["CTEXTO", "CFONDO"]:
            siTexto = clave == "CTEXTO"
            if siTexto:
                col.rgbTexto = -1
            else:
                col.rgbFondo = -1
            col.ponQT()
