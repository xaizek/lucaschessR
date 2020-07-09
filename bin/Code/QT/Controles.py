# import datetime
from PySide2 import QtCore, QtGui, QtWidgets


class ED(QtWidgets.QLineEdit):
    """
    Control de entrada de texto en una linea.
    """

    def __init__(self, parent, texto=None):
        """
        @param parent: ventana propietaria.
        @param texto: texto inicial.
        """
        if texto:
            QtWidgets.QLineEdit.__init__(self, texto, parent)
        else:
            QtWidgets.QLineEdit.__init__(self, parent)
        self.parent = parent

        self.siMayusculas = False
        self.decimales = 1

        self.menu = None

    def soloLectura(self, sino):
        self.setReadOnly(sino)
        return self

    def password(self):
        self.setEchoMode(QtWidgets.QLineEdit.Password)
        return self

    def deshabilitado(self, sino):
        self.setDisabled(sino)
        return self

    def capturaIntro(self, rutina):
        self.returnPressed.connect(rutina)
        return self

    def capturaCambiado(self, rutina):
        self.textEdited.connect(rutina)
        return self

    def ponTexto(self, texto):
        self.setText(texto)

    def texto(self):
        txt = self.text()
        return txt

    def alinCentrado(self):
        self.setAlignment(QtCore.Qt.AlignHCenter)
        return self

    def alinDerecha(self):
        self.setAlignment(QtCore.Qt.AlignRight)
        return self

    def anchoMinimo(self, px):
        self.setMinimumWidth(px)
        return self

    def anchoMaximo(self, px):
        self.setMaximumWidth(px)
        return self

    def caracteres(self, num):
        self.setMaxLength(num)
        self.numCaracteres = num
        return self

    def anchoFijo(self, px):
        self.setFixedWidth(px)
        return self

    def controlrx(self, regexpr):
        rx = QtCore.QRegExp(regexpr)
        validator = QtGui.QRegExpValidator(rx, self)
        self.setValidator(validator)
        return self

    def invalid_characters(self, c_invalid):
        def validador(x):
            for c in x:
                if c in c_invalid:
                    return False
            return True

        self.setValidator(validador)
        return self

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(self, name="", puntos=8, peso=50, siCursiva=False, siSubrayado=False, siTachado=False, txt=None):
        f = TipoLetra(name, puntos, peso, siCursiva, siSubrayado, siTachado, txt)
        self.setFont(f)
        return self

    def tipoFloat(self, valor=0.0, from_sq=0.0, to_sq=36000.0, decimales=None):
        """
        Valida los caracteres suponiendo que es un tipo decimal con unas condiciones
        @param valor: valor inicial
        @param from_sq: valor minimo
        @param to_sq: valor maximo
        @param decimales: num. decimales
        """
        if from_sq is None:
            self.setValidator(QtGui.QDoubleValidator(self))
        else:
            if decimales is None:
                decimales = self.decimales
            else:
                self.decimales = decimales
            self.setValidator(QtGui.QDoubleValidator(from_sq, to_sq, decimales, self))
        self.setAlignment(QtCore.Qt.AlignRight)
        self.ponFloat(valor)
        return self

    def ponFloat(self, valor):
        fm = "%0." + str(self.decimales) + "f"
        self.ponTexto(fm % valor)
        return self

    def textoFloat(self):
        txt = self.text()
        return round(float(txt), self.decimales) if txt else 0.0

    def tipoInt(self, valor=0):
        """
        Valida los caracteres suponiendo que es un tipo entero con unas condiciones
        @param valor: valor inicial
        """
        self.setValidator(QtGui.QIntValidator(self))
        self.setAlignment(QtCore.Qt.AlignRight)
        self.ponInt(valor)
        return self

    def ponInt(self, valor):
        self.ponTexto(str(valor))
        return self

    def textoInt(self):
        txt = self.text()
        return int(txt) if txt else 0


class SB(QtWidgets.QSpinBox):
    """
    SpinBox: Entrada de numeros enteros, con control de incremento o reduccion
    """

    def __init__(self, parent, valor, from_sq, to_sq):
        """
        @param valor: valor inicial
        @param from_sq: limite inferior
        @param to_sq: limite superior
        """
        QtWidgets.QSpinBox.__init__(self, parent)
        self.setRange(from_sq, to_sq)
        self.setSingleStep(1)
        self.setValue(int(valor))

    def tamMaximo(self, px):
        self.setFixedWidth(px)
        return self

    def valor(self):
        return self.value()

    def ponValor(self, valor):
        self.setValue(int(valor) if valor else 0)

    def capturaCambiado(self, rutina):
        self.valueChanged.connect(rutina)
        return self

    def ponFuente(self, font):
        self.setFont(font)
        return self


class CB(QtWidgets.QComboBox):
    """
    ComboBox : entrada de una lista de opciones = etiqueta,clave[,icono]
    """

    def __init__(self, parent, li_options, valorInicial):
        """
        @param li_options: lista de (etiqueta,clave)
        @param valorInicial: valor inicial
        """
        QtWidgets.QComboBox.__init__(self, parent)
        self.rehacer(li_options, valorInicial)

    def valor(self):
        return self.itemData(self.currentIndex())

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def rehacer(self, li_options, valorInicial):
        self.li_options = li_options
        self.clear()
        nindex = 0
        for n, opcion in enumerate(li_options):
            if len(opcion) == 2:
                etiqueta, clave = opcion
                self.addItem(etiqueta, clave)
            else:
                etiqueta, clave, icono = opcion
                self.addItem(icono, etiqueta, clave)
            if clave == valorInicial:
                nindex = n
        self.setCurrentIndex(nindex)

    def ponValor(self, valor):
        for n, opcion in enumerate(self.li_options):
            clave = opcion[1]
            if clave == valor:
                self.setCurrentIndex(n)
                break

    def ponAncho(self, px):
        r = self.geometry()
        r.setWidth(px)
        self.setGeometry(r)
        return self

    def ponAnchoFijo(self, px):
        self.setFixedWidth(px)
        return self

    def ponAnchoMinimo(self):
        self.setSizeAdjustPolicy(self.AdjustToMinimumContentsLengthWithIcon)
        return self

    def capturaCambiado(self, rutina):
        self.currentIndexChanged.connect(rutina)
        return self


class CHB(QtWidgets.QCheckBox):
    """
    CheckBox : entrada de una campo seleccionable
    """

    def __init__(self, parent, etiqueta, valorInicial):
        """
        @param etiqueta: rotulo mostrado
        @param valorInicial: valor inicial : True/False
        """
        QtWidgets.QCheckBox.__init__(self, etiqueta, parent)
        self.setChecked(valorInicial)

    def ponValor(self, si):
        self.setChecked(si)
        return self

    def valor(self):
        return self.isChecked()

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def capturaCambiado(self, owner, rutina):
        self.clicked.connect(rutina)
        return self

    def anchoFijo(self, px):
        self.setFixedWidth(px)
        return self


class LB(QtWidgets.QLabel):
    """
    Etiquetas de texto.
    """

    def __init__(self, parent, texto=None):
        """
        @param texto: texto inicial.
        """
        if texto:
            QtWidgets.QLabel.__init__(self, texto, parent)
        else:
            QtWidgets.QLabel.__init__(self, parent)

        self.setOpenExternalLinks(True)
        self.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction | QtCore.Qt.TextSelectableByMouse)

    def ponTexto(self, texto):
        self.setText(texto)

    def texto(self):
        return self.text()

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(self, name="", puntos=8, peso=50, siCursiva=False, siSubrayado=False, siTachado=False, txt=None):
        f = TipoLetra(name, puntos, peso, siCursiva, siSubrayado, siTachado, txt)
        self.setFont(f)
        return self

    def alinCentrado(self):
        self.setAlignment(QtCore.Qt.AlignCenter)
        return self

    def alinDerecha(self):
        self.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        return self

    def anchoMaximo(self, px):
        self.setMaximumWidth(px)
        return self

    def anchoFijo(self, px):
        self.setFixedWidth(px)
        return self

    def anchoMinimo(self, px):
        self.setMinimumWidth(px)
        return self

    def altoMinimo(self, px):
        self.setMinimumHeight(px)
        return self

    def altoFijo(self, px):
        self.setFixedHeight(px)
        return self

    def ponAlto(self, px):
        rec = self.geometry()
        rec.setHeight(px)
        self.setGeometry(rec)
        return self

    def alineaY(self, otroLB):
        rec = self.geometry()
        rec.setY(otroLB.geometry().y())
        self.setGeometry(rec)
        return self

    def ponImagen(self, pm):
        self.setPixmap(pm)
        return self

    def ponFondo(self, color):
        return self.ponFondoN(color.name())

    def ponFondoN(self, color):
        self.setStyleSheet("QWidget { background-color: %s }" % color)
        return self

    def put_color(self, color):
        return self.ponColorN(color.name())

    def ponColorN(self, color):
        self.setStyleSheet("QWidget { color: %s }" % color)
        return self

    def ponColorFondoN(self, color, fondo):
        self.setStyleSheet("QWidget { color: %s; background-color: %s}" % (color, fondo))
        return self

    def ponWrap(self):
        self.setWordWrap(True)
        return self

    def ponAncho(self, px):
        r = self.geometry()
        r.setWidth(px)
        self.setGeometry(r)
        return self


def LB2P(parent, texto):
    return LB(parent, texto + ": ")


class PB(QtWidgets.QPushButton):
    """
    Boton.
    """

    def __init__(self, parent, texto, rutina=None, plano=True):
        """
        @param parent: ventana propietaria, necesario para conectar una rutina.
        @param texto: etiqueta inicial.
        @param rutina: rutina a la que se conecta el boton.
        """
        QtWidgets.QPushButton.__init__(self, texto, parent)
        self.wParent = parent
        self.setFlat(plano)
        if rutina:
            self.conectar(rutina)

    def ponIcono(self, icono, tamIcon=16):
        self.setIcon(icono)
        self.setIconSize(QtCore.QSize(tamIcon, tamIcon))
        return self

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(self, name="", puntos=8, peso=50, siCursiva=False, siSubrayado=False, siTachado=False, txt=None):
        f = TipoLetra(name, puntos, peso, siCursiva, siSubrayado, siTachado, txt)
        self.setFont(f)
        return self

    def anchoFijo(self, px):
        self.setFixedWidth(px)
        return self

    def altoFijo(self, px):
        self.setFixedHeight(px)
        return self

    def cuadrado(self, px):
        self.setFixedSize(px, px)
        return self

    def anchoMinimo(self, px):
        self.setMinimumWidth(px)
        return self

    def conectar(self, rutina):
        self.clicked.connect(rutina)
        return self

    def ponFondo(self, txtFondo):
        self.setStyleSheet("QWidget { background: %s }" % txtFondo)
        return self

    def ponFondoN(self, ncolor):
        self.setStyleSheet("QWidget { background-color: %d }" % ncolor)
        return self

    def ponPlano(self, siPlano):
        self.setFlat(siPlano)
        return self

    def ponToolTip(self, txt):
        self.setToolTip(txt)
        return self

    def ponTexto(self, txt):
        self.setText(txt)


class RB(QtWidgets.QRadioButton):
    """
    RadioButton: lista de alternativas
    """

    def __init__(self, wParent, texto, rutina=None):
        QtWidgets.QRadioButton.__init__(self, texto, wParent)
        if rutina:
            self.clicked.connect(rutina)

    def activa(self, siActivar=True):
        self.setChecked(siActivar)
        return self


class GB(QtWidgets.QGroupBox):
    """
    GroupBox: Recuadro para agrupamiento de controles
    """

    def __init__(self, wParent, texto, layout):
        QtWidgets.QGroupBox.__init__(self, texto, wParent)
        self.setLayout(layout)
        self.wParent = wParent

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(self, name="", puntos=8, peso=50, siCursiva=False, siSubrayado=False, siTachado=False, txt=None):
        f = TipoLetra(name, puntos, peso, siCursiva, siSubrayado, siTachado, txt)
        self.setFont(f)
        return self

    def alinCentrado(self):
        self.setAlignment(QtCore.Qt.AlignHCenter)
        return self

    def conectar(self, rutina):
        self.setCheckable(True)
        self.setChecked(False)
        self.clicked.connect(rutina)
        return self

    def ponTexto(self, texto):
        self.setTitle(texto)
        return self


class EM(QtWidgets.QTextEdit):
    """
    Control de entrada de texto en varias lineas.
    """

    def __init__(self, parent, texto=None, siHTML=True):
        """
        @param texto: texto inicial.
        """
        QtWidgets.QTextEdit.__init__(self, parent)
        self.parent = parent

        self.menu = None  # menu de contexto
        self.rutinaDobleClick = None

        self.setAcceptRichText(siHTML)

        if texto:
            if siHTML:
                self.setText(texto)
            else:
                self.insertPlainText(texto)

    def ponHtml(self, texto):
        self.setHtml(texto)
        return self

    def insertarHtml(self, texto):
        self.insertHtml(texto)
        return self

    def insertarTexto(self, texto):
        self.insertPlainText(texto)
        return self

    def soloLectura(self):
        self.setReadOnly(True)
        return self

    def texto(self):
        return self.toPlainText()

    def ponTexto(self, txt):
        self.setText("")
        self.insertarTexto(txt)

    def html(self):
        return self.toHtml()

    def ponAncho(self, px):
        r = self.geometry()
        r.setWidth(px)
        self.setGeometry(r)
        return self

    def anchoMinimo(self, px):
        self.setMinimumWidth(px)
        return self

    def altoMinimo(self, px):
        self.setMinimumHeight(px)
        return self

    def altoFijo(self, px):
        self.setFixedHeight(px)
        return self

    def anchoFijo(self, px):
        self.setFixedWidth(px)
        return self

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(self, name="", puntos=8, peso=50, siCursiva=False, siSubrayado=False, siTachado=False, txt=None):
        f = TipoLetra(name, puntos, peso, siCursiva, siSubrayado, siTachado, txt)
        self.setFont(f)
        return self

    def ponWrap(self, siPoner):
        self.setWordWrapMode(QtGui.QTextOption.WordWrap if siPoner else QtGui.QTextOption.NoWrap)
        return self

    def capturaCambios(self, rutina):
        self.textChanged.connect(rutina)
        return self

    def capturaDobleClick(self, rutina):
        self.rutinaDobleClick = rutina
        return self

    def mouseDoubleClickEvent(self, event):
        if self.rutinaDobleClick:
            self.rutinaDobleClick(event)

    def position(self):
        return self.textCursor().position()


class Menu(QtWidgets.QMenu):
    """
    Menu popup.

    Ejemplo::

        menu = Controles.Menu(window)

        menu.opcion( "op1", "Primera opcion", icono )
        menu.separador()
        menu.opcion( "op2", "Segunda opcion", icono1 )
        menu.separador()

        menu1 = menu.submenu( "Submenu", icono2 )
        menu1.opcion( "op3_1", "opcion 1", icono3 )
        menu1.separador()
        menu1.opcion( "op3_2", "opcion 2", icono3 )
        menu1.separador()

        resp = menu.lanza()

        if resp:
            if resp == "op1":
                ..........

            elif resp == "op2":
                ................
    """

    def __init__(self, parent, titulo=None, icono=None, is_disabled=False, puntos=None, siBold=True):

        self.parent = parent
        QtWidgets.QMenu.__init__(self, parent)

        if titulo:
            self.setTitle(titulo)
        if icono:
            self.setIcon(icono)

        if is_disabled:
            self.setDisabled(True)

        if puntos:
            tl = TipoLetra(puntos=puntos, peso=75) if siBold else TipoLetra(puntos=puntos)
            self.setFont(tl)

        app = QtWidgets.QApplication.instance()
        style = app.style().metaObject().className()
        self.si_separadores = style != "QFusionStyle"

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(self, name="", puntos=8, peso=50, siCursiva=False, siSubrayado=False, siTachado=False, txt=None):
        f = TipoLetra(name, puntos, peso, siCursiva, siSubrayado, siTachado, txt)
        self.setFont(f)
        return self

    def opcion(self, clave, rotulo, icono=None, is_disabled=False, tipoLetra=None, siChecked=False):
        if icono:
            accion = QtWidgets.QAction(icono, rotulo, self)
        else:
            accion = QtWidgets.QAction(rotulo, self)
        accion.clave = clave
        if is_disabled:
            accion.setDisabled(True)
        if tipoLetra:
            accion.setFont(tipoLetra)
        if siChecked is not None:
            accion.setCheckable(True)
            accion.setChecked(siChecked)

        self.addAction(accion)
        return accion

    def submenu(self, rotulo, icono=None, is_disabled=False):
        menu = Menu(self, rotulo, icono, is_disabled)
        menu.setFont(self.font())
        self.addMenu(menu)
        return menu

    def mousePressEvent(self, event):
        self.siIzq = event.button() == QtCore.Qt.LeftButton
        self.siDer = event.button() == QtCore.Qt.RightButton
        resp = QtWidgets.QMenu.mousePressEvent(self, event)
        return resp

    def separador(self):
        if self.si_separadores:
            self.addSeparator()

    def lanza(self):
        QtCore.QCoreApplication.processEvents()
        QtWidgets.QApplication.processEvents()
        resp = self.exec_(QtGui.QCursor.pos())
        if resp:
            return resp.clave
        else:
            return None


class TB(QtWidgets.QToolBar):
    """
    Crea una barra de tareas simple.

    @param li_acciones: lista de acciones, en forma de tupla = titulo, icono, clave
    @param siTexto: si muestra texto
    @param tamIcon: tama_o del icono
    @param rutina: rutina que se llama al pulsar una opcion. Por defecto sera parent.process_toolbar().
        Y la clave enviada se obtiene de self.sender().clave
    """

    def __init__(self, parent, li_acciones, siTexto=True, tamIcon=32, rutina=None, puntos=None, background=None):

        QtWidgets.QToolBar.__init__(self, "BASICO", parent)

        self.setIconSize(QtCore.QSize(tamIcon, tamIcon))

        self.parent = parent

        self.rutina = parent.process_toolbar if rutina is None else rutina

        if siTexto:
            self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        self.f = TipoLetra(puntos=puntos) if puntos else None

        if background:
            self.setStyleSheet("QWidget { background: %s }" % background)

        self.ponAcciones(li_acciones)

    def ponAcciones(self, li_acciones):
        self.dicTB = {}
        lista = []
        for datos in li_acciones:
            if datos:
                if type(datos) == int:
                    self.addWidget(LB("").anchoFijo(datos))
                else:
                    titulo, icono, clave = datos
                    accion = QtWidgets.QAction(titulo, self.parent)
                    accion.setIcon(icono)
                    accion.setIconText(titulo)
                    accion.triggered.connect(self.rutina)
                    accion.clave = clave
                    if self.f:
                        accion.setFont(self.f)
                    lista.append(accion)
                    self.addAction(accion)
                    self.dicTB[clave] = accion
            else:
                self.addSeparator()
        self.li_acciones = lista

    def reset(self, li_acciones):
        self.clear()
        self.ponAcciones(li_acciones)
        self.update()

    def vertical(self):
        self.setOrientation(QtCore.Qt.Vertical)
        return self

    def setAccionVisible(self, key, value):
        for accion in self.li_acciones:
            if accion.clave == key:
                accion.setVisible(value)

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.RightButton:
            if hasattr(self.parent, "toolbar_rightmouse"):
                self.parent.toolbar_rightmouse()
                return
        QtWidgets.QToolBar.mousePressEvent(self, event)


class TBrutina(QtWidgets.QToolBar):
    """
    Crea una barra de tareas simple.

    @param li_acciones: lista de acciones, en forma de tupla = titulo, icono, clave
    @param siTexto: si muestra texto
    @param tamIcon: tama_o del icono
    @param rutina: rutina que se llama al pulsar una opcion. Por defecto sera parent.process_toolbar().
        Y la clave enviada se obtiene de self.sender().clave
    """

    def __init__(self, parent, li_acciones=None, siTexto=True, tamIcon=None, puntos=None, background=None, style=None):

        QtWidgets.QToolBar.__init__(self, "BASICO", parent)

        if style:
            self.setToolButtonStyle(style)
            if style != QtCore.Qt.ToolButtonTextUnderIcon and tamIcon is None:
                tamIcon = 16
        elif siTexto:
            self.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        tam = 32 if tamIcon is None else tamIcon
        self.setIconSize(QtCore.QSize(tam, tam))

        self.parent = parent

        self.f = TipoLetra(puntos=puntos) if puntos else None

        if background:
            self.setStyleSheet("QWidget { background: %s }" % background)

        if li_acciones:
            self.ponAcciones(li_acciones)

        else:
            self.dicTB = {}
            self.li_acciones = []

    def new(self, titulo, icono, clave, sep=True, toolTip=None):
        accion = QtWidgets.QAction(titulo, self.parent)
        accion.setIcon(icono)
        accion.setIconText(titulo)
        if toolTip:
            accion.setToolTip(toolTip)
        accion.triggered.connect(clave)
        if self.f:
            accion.setFont(self.f)
        self.li_acciones.append(accion)
        self.addAction(accion)
        self.dicTB[clave] = accion
        if sep:
            self.addSeparator()

    def ponAcciones(self, liAcc):
        self.dicTB = {}
        self.li_acciones = []
        for datos in liAcc:
            if datos:
                if type(datos) == int:
                    self.addWidget(LB("").anchoFijo(datos))
                elif len(datos) == 3:
                    titulo, icono, clave = datos
                    self.new(titulo, icono, clave, False)
                else:
                    titulo, icono, clave, toolTip = datos
                    self.new(titulo, icono, clave, False, toolTip=toolTip)
            else:
                self.addSeparator()

    def reset(self, li_acciones):
        self.clear()
        self.ponAcciones(li_acciones)
        self.update()

    def vertical(self):
        self.setOrientation(QtCore.Qt.Vertical)
        return self

    def setPosVisible(self, pos, value):
        self.li_acciones[pos].setVisible(value)

    def setAccionVisible(self, key, value):
        accion = self.dicTB.get(key, None)
        if accion:
            accion.setVisible(value)


class TipoLetra(QtGui.QFont):
    def __init__(self, name="", puntos=8, peso=50, siCursiva=False, siSubrayado=False, siTachado=False, txt=None):
        QtGui.QFont.__init__(self)
        if txt is None:
            cursiva = 1 if siCursiva else 0
            subrayado = 1 if siSubrayado else 0
            tachado = 1 if siTachado else 0
            if not name:
                name = self.defaultFamily()
            txt = "%s,%d,-1,5,%d,%d,%d,%d,0,0" % (name, puntos, peso, cursiva, subrayado, tachado)
        self.fromString(txt)


class Tab(QtWidgets.QTabWidget):
    def nuevaTab(self, widget, texto, pos=None):
        if pos is None:
            self.addTab(widget, texto)
        else:
            self.insertTab(pos, widget, texto)

    def current_position(self):
        return self.currentIndex()

    def ponValor(self, cual, valor):
        self.setTabText(cual, valor)

    def activa(self, cual):
        self.setCurrentIndex(cual)

    def setposition(self, pos):
        rpos = self.North
        if pos == "S":
            rpos = self.South
        elif pos == "E":
            rpos = self.East
        elif pos == "W":
            rpos = self.West
        self.setTabPosition(rpos)
        return self

    def ponIcono(self, pos, icono):
        self.setTabIcon(pos, icono)

    def ponFuente(self, f):
        self.setFont(f)
        return self

    def ponTipoLetra(self, name="", puntos=8, peso=50, siCursiva=False, siSubrayado=False, siTachado=False, txt=None):
        f = TipoLetra(name, puntos, peso, siCursiva, siSubrayado, siTachado, txt)
        self.setFont(f)
        return self

    def dispatchChange(self, dispatch):
        self.currentChanged.connect(dispatch)

        # def formaTriangular( self ):
        # self.setTabShape(self.Triangular)


class SL(QtWidgets.QSlider):
    def __init__(self, parent, minimo, maximo, nvalor, dispatch, tick=10, step=1):
        QtWidgets.QSlider.__init__(self, QtCore.Qt.Horizontal, parent)

        self.setMinimum(minimo)
        self.setMaximum(maximo)

        self.dispatch = dispatch
        if tick:
            self.setTickPosition(QtWidgets.QSlider.TicksBelow)
            self.setTickInterval(tick)
        self.setSingleStep(step)

        self.setValue(nvalor)

        self.valueChanged.connect(self.movido)

    def ponValor(self, nvalor):
        self.setValue(nvalor)
        return self

    def movido(self, valor):
        if self.dispatch:
            self.dispatch()

    def valor(self):
        return self.value()

    def ponAncho(self, px):
        self.setFixedWidth(px)
        return self

    # class PRB(QtWidgets.QProgressBar):
    # def __init__(self, minimo, maximo):
    # QtWidgets.QProgressBar.__init__(self)
    # self.setMinimum(minimo)
    # self.setMaximum(maximo)

    # def ponFormatoValor(self):
    # self.setFormat("%v")
    # return self

    # class Fecha(QtWidgets.QDateTimeEdit):
    # def __init__(self, fecha=None):
    # QtWidgets.QDateTimeEdit.__init__(self)

    # self.setDisplayFormat("dd-MM-yyyy")

    # self.setCalendarPopup(True)
    # calendar = QtWidgets.QCalendarWidget()
    # calendar.setFirstDayOfWeek(QtCore.Qt.Monday)
    # calendar.setGridVisible(True)
    # self.setCalendarWidget(calendar)

    # if fecha:
    # self.ponFecha(fecha)

    # def fecha2date(self, fecha):
    # date = QtCore.QDate()
    # date.setDate(fecha.year, fecha.month, fecha.day)
    # return date

    # def ponFecha(self, fecha):
    # self.setDate(self.fecha2date(fecha))
    # return self

    # def fecha(self):
    # date = self.date()
    # fecha = datetime.date(date.year(), date.month(), date.day())
    # return fecha

    # def minima(self, fecha):
    # previa = self.date()
    # fecha = self.fecha2date(fecha)

    # if previa < fecha:
    # self.ponFecha(fecha)

    # self.setMinimumDate(fecha)
    # return self

    # def maxima(self, fecha):
    # previa = self.date()
    # fecha = self.fecha2date(fecha)
    # if previa > fecha:
    # self.ponFecha(fecha)

    # self.setMaximumDate(fecha)
    # return self
