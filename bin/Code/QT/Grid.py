"""
El grid es un TableView de QT.

Realiza llamadas a rutinas de la ventana donde esta ante determinados eventos, o en determinadas situaciones,
siempre que la rutina se haya definido en la ventana:

    - grid_doble_clickCabecera : ante un doble click en la cabecera, normalmente se usa para la reordenacion de la tabla por la columna pulsada.
    - grid_tecla_pulsada : al pulsarse una tecla, llama a esta rutina, para que pueda usarse por ejemplo en busquedas.
    - grid_tecla_control : al pulsarse una tecla de control, llama a esta rutina, para que pueda usarse por ejemplo en busquedas.
    - grid_doble_click : en el caso de un doble click en un registro, se hace la llamad a esta rutina
    - grid_boton_derecho : si se ha pulsado el boton derecho del raton.
    - grid_setvalue : si hay un campo editable, la llamada se produce cuando se ha cambiado el valor tras la edicion.

    - grid_color_texto : si esta definida se la llama al mostrar el texto de un campo, para determinar el color del mismo.
    - grid_color_fondo : si esta definida se la llama al mostrar el texto de un campo, para determinar el color del fondo del mismo.

"""

from PySide2 import QtCore, QtGui, QtWidgets

from Code.QT import QTUtil
import Code


class ControlGrid(QtCore.QAbstractTableModel):
    """
    Modelo de datos asociado al grid, y que realiza todo el trabajo asignado por QT.
    """

    def __init__(self, grid, wParent, oColumnasR):
        """
        @param tableView:
        @param oColumnasR: ListaColumnas con la configuracion de todas las columnas visualizables.
        """
        QtCore.QAbstractTableModel.__init__(self, wParent)
        self.grid = grid
        self.wParent = wParent
        self.siOrden = False
        self.hh = grid.horizontalHeader()
        self.siColorTexto = hasattr(self.wParent, "grid_color_texto")
        self.siColorFondo = hasattr(self.wParent, "grid_color_fondo")
        self.siAlineacion = hasattr(self.wParent, "grid_alineacion")
        self.font = grid.font()
        self.siBold = hasattr(self.wParent, "grid_bold")
        if self.siBold:
            self.bfont = QtGui.QFont(self.font)
            self.bfont.setWeight(75)

        self.oColumnasR = oColumnasR

    def rowCount(self, parent):
        """
        Llamada interna, solicitando el number de registros.
        """
        self.numDatos = self.wParent.grid_num_datos(self.grid)
        return self.numDatos

    def refresh(self):
        """
        Si hay un cambio del number de registros, la llamada a esta rutina actualiza la visualizacion.
        """
        # self.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
        self.layoutAboutToBeChanged.emit()
        ant_ndatos = self.numDatos
        nue_ndatos = self.wParent.grid_num_datos(self.grid)
        if ant_ndatos != nue_ndatos:
            if ant_ndatos < nue_ndatos:
                self.insertRows(ant_ndatos, nue_ndatos - ant_ndatos)
            else:
                self.removeRows(nue_ndatos, ant_ndatos - nue_ndatos)
            self.numDatos = nue_ndatos

        ant_ncols = self.numCols
        nue_ncols = self.oColumnasR.numColumnas()
        if ant_ncols != nue_ncols:
            if ant_ncols < nue_ncols:
                self.insertColumns(0, nue_ncols - ant_ncols)
            else:
                self.removeColumns(nue_ncols, ant_ncols - nue_ncols)

        self.layoutChanged.emit()

    def columnCount(self, parent):
        """
        Llamada interna, solicitando el number de columnas.
        """
        self.numCols = self.oColumnasR.numColumnas()
        return self.numCols

    def data(self, index, role):
        """
        Llamada interna, solicitando informacion que ha de tener/contener el campo actual.
        """
        if not index.isValid():
            return None

        columna = self.oColumnasR.columna(index.column())

        if role == QtCore.Qt.TextAlignmentRole:
            if self.siAlineacion:
                resp = self.wParent.grid_alineacion(self.grid, index.row(), columna)
                if resp:
                    return columna.QTalineacion(resp)
            return columna.qtAlineacion
        elif role == QtCore.Qt.BackgroundRole:
            if self.siColorFondo:
                resp = self.wParent.grid_color_fondo(self.grid, index.row(), columna)
                if resp:
                    return resp
            return columna.qtColorFondo
        elif role == QtCore.Qt.TextColorRole:
            if self.siColorTexto:
                resp = self.wParent.grid_color_texto(self.grid, index.row(), columna)
                if resp:
                    return resp
            return columna.qtColorTexto
        elif self.siBold and role == QtCore.Qt.FontRole:
            if self.wParent.grid_bold(self.grid, index.row(), columna):
                return self.bfont
            return None

        if role == QtCore.Qt.DisplayRole:
            return self.wParent.grid_dato(self.grid, index.row(), columna)

        return None

    def getAlineacion(self, index):
        columna = self.oColumnasR.columna(index.column())
        return self.wParent.grid_alineacion(self.grid, index.row(), columna)

    def getFondo(self, index):
        columna = self.oColumnasR.columna(index.column())
        return self.wParent.grid_color_fondo(self.grid, index.row(), columna)

    def flags(self, index):
        """
        Llamada interna, solicitando mas informacion sobre las carcateristicas del campo actual.
        """
        if not index.isValid():
            return QtCore.Qt.ItemIsEnabled

        flag = QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
        columna = self.oColumnasR.columna(index.column())
        if columna.siEditable:
            flag |= QtCore.Qt.ItemIsEditable

        if columna.siChecked:
            flag |= QtCore.Qt.ItemIsUserCheckable
        return flag

    def setData(self, index, valor, role=QtCore.Qt.EditRole):
        """
        Tras producirse la edicion de un campo en un registro se llama a esta rutina para cambiar el valor en el origen de los datos.
        Se lanza grid_setvalue en la ventana propietaria.
        """
        if not index.isValid():
            return None
        if role == QtCore.Qt.EditRole or role == QtCore.Qt.CheckStateRole:
            columna = self.oColumnasR.columna(index.column())
            nfila = index.row()
            self.wParent.grid_setvalue(self.grid, nfila, columna, valor)
            index2 = self.createIndex(nfila, 1)
            # self.emit(QtCore.SIGNAL('dataChanged(const QModelIndex &,const QModelIndex &)'), index2, index2)
            self.dataChanged.emit(index2, index2)

        return True

    def headerData(self, col, orientation, role):
        """
        Llamada interna, para determinar el texto de las cabeceras de las columnas.
        """
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            columna = self.oColumnasR.columna(col)
            return columna.cabecera
        # elif orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
        #     return str(col+1)
        return None


class Cabecera(QtWidgets.QHeaderView):
    """
    Se crea esta clase para poder implementar el doble click en la cabecera.
    """

    def __init__(self, tvParent, siCabeceraMovible):
        QtWidgets.QHeaderView.__init__(self, QtCore.Qt.Horizontal)
        self.setSectionsMovable(siCabeceraMovible)
        self.setSectionsClickable(True)
        self.tvParent = tvParent

    def mouseDoubleClickEvent(self, event):
        numColumna = self.logicalIndexAt(event.x(), event.y())
        self.tvParent.dobleClickCabecera(numColumna)
        return QtWidgets.QHeaderView.mouseDoubleClickEvent(self, event)

    def mouseReleaseEvent(self, event):
        QtWidgets.QHeaderView.mouseReleaseEvent(self, event)
        numColumna = self.logicalIndexAt(event.x(), event.y())
        self.tvParent.mouseCabecera(numColumna)


class CabeceraHeight(Cabecera):
    def __init__(self, tvParent, siCabeceraMovible, height):
        Cabecera.__init__(self, tvParent, siCabeceraMovible)
        self.height = height

    def sizeHint(self):
        baseSize = Cabecera.sizeHint(self)
        baseSize.setHeight(self.height)
        return baseSize


class Grid(QtWidgets.QTableView):
    """
    Implementa un TableView, en base a la configuracion de una lista de columnas.
    """

    def __init__(
        self,
        wParent,
        o_columns,
        dicVideo=None,
        altoFila=20,
        siSelecFilas=False,
        siSeleccionMultiple=False,
        siLineas=True,
        siEditable=False,
        siCabeceraMovible=True,
        xid=None,
        background="",
        siCabeceraVisible=True,
        altoCabecera=None,
    ):
        """
        @param wParent: ventana propietaria
        @param o_columns: configuracion de las columnas.
        @param altoFila: altura de todas las filas.
        """

        assert wParent is not None

        self.starting = True

        QtWidgets.QTableView.__init__(self)

        configuracion = Code.configuracion

        p = self.palette()
        p.setBrush(
            QtGui.QPalette.Active,
            QtGui.QPalette.Highlight,
            QtGui.QBrush(QtGui.QColor(configuracion.pgn_selbackground())),
        )
        self.setPalette(p)

        self.wParent = wParent
        self.id = xid

        self.o_columns = o_columns
        if dicVideo:
            self.restore_video(dicVideo)
        self.oColumnasR = self.o_columns.columnasMostrables()  # Necesario tras recuperar video

        self.cg = ControlGrid(self, wParent, self.oColumnasR)

        self.setModel(self.cg)
        self.setShowGrid(siLineas)
        self.setWordWrap(False)
        self.setTextElideMode(QtCore.Qt.ElideNone)

        if background == "":
            self.setStyleSheet("QTableView {background: %s;}" % QTUtil.backgroundGUI())
        elif background is not None:
            self.setStyleSheet("QTableView {background: %s;}" % background)

        if configuracion.x_pgn_headerbackground:
            self.setStyleSheet("QHeaderView::section { background-color:%s }" % configuracion.pgn_headerbackground())

        self.coloresAlternados()

        if altoCabecera:
            hh = CabeceraHeight(self, siCabeceraMovible, altoCabecera)
        else:
            hh = Cabecera(self, siCabeceraMovible)
        self.setHorizontalHeader(hh)
        if not siCabeceraVisible:
            hh.setVisible(False)

        vh = self.verticalHeader()
        vh.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        vh.setDefaultSectionSize(altoFila)
        vh.setVisible(False)

        self.seleccionaFilas(siSelecFilas, siSeleccionMultiple)

        self.ponAnchosColumnas()  # es necesario llamarlo from_sq aqui

        self.siEditable = siEditable
        self.starting = False

    def buscaCabecera(self, clave):
        return self.o_columns.buscaColumna(clave)

    def coloresAlternados(self):
        self.setAlternatingRowColors(True)

    def seleccionaFilas(self, siSelecFilas, siSeleccionMultiple):
        sel = QtWidgets.QAbstractItemView.SelectRows if siSelecFilas else QtWidgets.QAbstractItemView.SelectItems
        if siSeleccionMultiple:
            selMode = QtWidgets.QAbstractItemView.ExtendedSelection
        else:
            selMode = QtWidgets.QAbstractItemView.SingleSelection
        self.setSelectionMode(selMode)
        self.setSelectionBehavior(sel)

    def releerColumnas(self):
        """
        Cuando se cambia la configuracion de las columnas, se vuelven a releer y se indican al control de datos.
        """
        self.oColumnasR = self.o_columns.columnasMostrables()
        self.cg.oColumnasR = self.oColumnasR
        self.cg.refresh()
        self.ponAnchosColumnas()

    def ponAnchosColumnas(self):
        for numCol, columna in enumerate(self.oColumnasR.liColumnas):
            self.setColumnWidth(numCol, columna.ancho)
            if columna.edicion and columna.siMostrar:
                self.setItemDelegateForColumn(numCol, columna.edicion)

    def keyPressEvent(self, event):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        cada tecla pulsada, llamando a la rutina correspondiente si existe (grid_tecla_pulsada/grid_tecla_control)
        """
        k = event.key()
        m = int(event.modifiers())
        siShift = (m & QtCore.Qt.ShiftModifier) > 0
        siControl = (m & QtCore.Qt.ControlModifier) > 0
        siAlt = (m & QtCore.Qt.AltModifier) > 0
        if hasattr(self.wParent, "grid_tecla_pulsada"):
            if not (siControl or siAlt) and k < 256:
                self.wParent.grid_tecla_pulsada(self, event.text())
        if hasattr(self.wParent, "grid_tecla_control"):
            self.wParent.grid_tecla_control(self, k, siShift, siControl, siAlt)

    def selectionChanged(self, uno, dos):
        if self.starting:
            return
        if hasattr(self.wParent, "grid_cambiado_registro"):
            fil, columna = self.current_position()
            self.wParent.grid_cambiado_registro(self, fil, columna)
        self.refresh()

    def wheelEvent(self, event):
        if hasattr(self.wParent, "grid_wheel_event"):
            self.wParent.grid_wheel_event(self, event.angleDelta().y() > 0)
        else:
            QtWidgets.QTableView.wheelEvent(self, event)

    def mouseDoubleClickEvent(self, event):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        cada doble click, llamando a la rutina correspondiente si existe (grid_doble_click)
        con el number de fila y el objeto columna como argumentos
        """
        if self.siEditable:
            QtWidgets.QTableView.mouseDoubleClickEvent(self, event)
        if hasattr(self.wParent, "grid_doble_click") and event.button() == 1:
            fil, columna = self.current_position()
            self.wParent.grid_doble_click(self, fil, columna)

    def mousePressEvent(self, event):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        cada pulsacion del boton derecho, llamando a la rutina correspondiente si existe (grid_boton_derecho)
        """
        QtWidgets.QTableView.mousePressEvent(self, event)
        button = event.button()
        fil, col = self.current_position()
        if fil < 0:
            return
        if button == 2:
            if hasattr(self.wParent, "grid_boton_derecho"):

                class Vacia:
                    pass

                modif = Vacia()
                m = int(event.modifiers())
                modif.siShift = (m & QtCore.Qt.ShiftModifier) > 0
                modif.siControl = (m & QtCore.Qt.ControlModifier) > 0
                modif.siAlt = (m & QtCore.Qt.AltModifier) > 0
                self.wParent.grid_boton_derecho(self, fil, col, modif)
        elif button == 1:
            if fil < 0:
                return
            if col.siChecked:
                value = self.wParent.grid_dato(self, fil, col)
                self.wParent.grid_setvalue(self, fil, col, not value)
                self.refresh()
            elif hasattr(self.wParent, "grid_boton_izquierdo"):
                self.wParent.grid_boton_izquierdo(self, fil, col)

    def dobleClickCabecera(self, numColumna):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        los doble clicks sobre la cabecera , normalmente para cambiar el orden de la columna,
        llamando a la rutina correspondiente si existe (grid_doble_clickCabecera) y con el
        argumento del objeto columna
        """
        if hasattr(self.wParent, "grid_doble_clickCabecera"):
            self.wParent.grid_doble_clickCabecera(self, self.oColumnasR.columna(numColumna))

    def mouseCabecera(self, numColumna):
        """
        Se gestiona este evento, ante la posibilidad de que la ventana quiera controlar,
        los doble clicks sobre la cabecera , normalmente para cambiar el orden de la columna,
        llamando a la rutina correspondiente si existe (grid_doble_clickCabecera) y con el
        argumento del objeto columna
        """
        if hasattr(self.wParent, "grid_pulsada_cabecera"):
            self.wParent.grid_pulsada_cabecera(self, self.oColumnasR.columna(numColumna))

    def save_video(self, dic):
        """
        Guarda en el diccionario de video la configuracion actual de todas las columnas

        @param dic: diccionario de video donde se guarda la configuracion de las columnas
        """
        liClaves = []
        for n, columna in enumerate(self.oColumnasR.liColumnas):
            columna.ancho = self.columnWidth(n)
            columna.position = self.columnViewportPosition(n)
            columna.guardarConf(dic, self)
            liClaves.append(columna.clave)

        # Las que no se muestran
        for columna in self.o_columns.liColumnas:
            if not (columna.clave in liClaves):
                columna.guardarConf(dic, self)

    def restore_video(self, dic):
        for columna in self.o_columns.liColumnas:
            columna.recuperarConf(dic, self)

        self.o_columns.liColumnas.sort(key=lambda x: x.position)

    def columnas(self):
        for n, columna in enumerate(self.oColumnasR.liColumnas):
            columna.ancho = self.columnWidth(n)
            columna.position = self.columnViewportPosition(n)
        self.o_columns.liColumnas.sort(key=lambda x: x.position)
        return self.o_columns

    def anchoColumnas(self):
        """
        Calcula el ancho que corresponde a todas las columnas mostradas.
        """
        ancho = 0
        for n, columna in enumerate(self.oColumnasR.liColumnas):
            ancho += columna.ancho
        return ancho

    def fixMinWidth(self):
        nAncho = self.anchoColumnas() + 24
        self.setMinimumWidth(nAncho)
        return nAncho

    def recno(self):
        """
        Devuelve la fila actual.
        """
        n = self.currentIndex().row()
        nX = self.cg.numDatos - 1
        return n if n <= nX else nX

    def reccount(self):
        return self.cg.numDatos

    def recnosSeleccionados(self):
        li = []
        for x in self.selectionModel().selectedIndexes():
            li.append(x.row())

        return list(set(li))

    def goto(self, fila, col):
        """
        Se situa en una position determinada.
        """
        elem = self.cg.createIndex(fila, col)
        self.setCurrentIndex(elem)
        self.scrollTo(elem)

    def gotop(self):
        """
        Se situa al principio del grid.
        """
        if self.cg.numDatos > 0:
            self.goto(0, 0)

    def gobottom(self, col=0):
        """
        Se situa en el ultimo registro del frid.
        """
        if self.cg.numDatos > 0:
            self.goto(self.cg.numDatos - 1, col)

    def refresh(self):
        """
        Hace un refresco de la visualizacion del grid, ante algun cambio en el contenido.
        """
        self.cg.refresh()

    def current_position(self):
        """
        Devuelve la position actual.

        @return: tupla con ( num fila, objeto columna )
        """
        columna = self.oColumnasR.columna(self.currentIndex().column())
        return self.recno(), columna

    def posActualN(self):
        """
        Devuelve la position actual.

        @return: tupla con ( num fila, num  columna )
        """
        return self.recno(), self.currentIndex().column()

    def tipoLetra(self, name="", puntos=8, peso=50, siCursiva=False, siSubrayado=False, siTachado=False, txt=None):
        font = QtGui.QFont()
        if txt is None:
            cursiva = 1 if siCursiva else 0
            subrayado = 1 if siSubrayado else 0
            tachado = 1 if siTachado else 0
            if not name:
                name = font.defaultFamily()
            txt = "%s,%d,-1,5,%d,%d,%d,%d,0,0" % (name, puntos, peso, cursiva, subrayado, tachado)
        font.fromString(txt)
        self.ponFuente(font)

    def ponFuente(self, font):
        self.setFont(font)
        hh = self.horizontalHeader()
        hh.setFont(font)

    def ponAltoFila(self, altoFila):
        vh = self.verticalHeader()
        vh.setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        vh.setDefaultSectionSize(altoFila)
        vh.setVisible(False)
