import operator
import os
import random

from PySide2 import QtCore, QtGui, QtWidgets

import Code
from Code.Polyglots import Books
from Code.Engines import Engines
from Code.Engines import EnginesMicElo
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import FormLayout
from Code import Util


class WEngines(QTVarios.WDialogo):
    def __init__(self, owner, configuracion):

        self.lista_motores = configuracion.lista_motores_externos()
        self.configuracion = configuracion
        self.changed = False

        # Dialogo ---------------------------------------------------------------
        icono = Iconos.MotoresExternos()
        titulo = _("External engines")
        extparam = "motoresExternos"
        QTVarios.WDialogo.__init__(self, owner, titulo, icono, extparam)

        # Toolbar
        li_acciones = [
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            (_("New"), Iconos.TutorialesCrear(), self.nuevo),
            None,
            (_("Modify"), Iconos.Modificar(), self.modificar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Copy"), Iconos.Copiar(), self.copiar),
            None,
            (_("Import"), Iconos.MasDoc(), self.importar),
            None,
            (_("Up"), Iconos.Arriba(), self.arriba),
            None,
            (_("Down"), Iconos.Abajo(), self.abajo),
            None,
            (_("Command"), Iconos.Terminal(), self.command),
            None,
        ]
        tb = QTVarios.LCTB(self, li_acciones)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("ALIAS", _("Alias"), 200)
        o_columns.nueva("MOTOR", _("Engine"), 200)
        o_columns.nueva("AUTOR", _("Author"), 200)
        o_columns.nueva("INFO", _("Information"), 120)
        o_columns.nueva("ELO", "ELO", 120, centered=True)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        # n = self.grid.anchoColumnas()
        # self.grid.setFixedWidth( n + 20 )
        self.register_grid(self.grid)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid)
        self.setLayout(layout)

        self.restore_video(siTam=True)

    def grabar(self):
        li = [eng.save() for eng in self.lista_motores]
        Util.save_pickle(self.configuracion.file_external_engines(), li)
        self.configuracion.lee_motores_externos()

    def terminar(self):
        self.save_video()
        self.accept()

    def grid_num_datos(self, grid):
        return len(self.lista_motores)

    def grid_dato(self, grid, fila, oColumna):
        me = self.lista_motores[fila]
        key = oColumna.clave
        if key == "AUTOR":
            return me.autor
        elif key == "ALIAS":
            return me.clave
        elif key == "MOTOR":
            return me.name
        elif key == "INFO":
            return me.id_info.replace("\n", "-")
        elif key == "ELO":
            return str(me.elo) if me.elo else "-"

    def command(self):
        separador = FormLayout.separador
        liGen = [separador]
        liGen.append(separador)
        config = FormLayout.Fichero(_("File"), "exe", False)
        liGen.append((config, ""))

        for num in range(1, 11):
            liGen.append(("%s:" %(_("Argument %d") % num), ""))
        liGen.append(separador)
        resultado = FormLayout.fedit(liGen, title=_("Command"), parent=self, anchoMinimo=600, icon=Iconos.Terminal())
        if resultado:
            nada, resp = resultado
            command = resp[0]
            liArgs = []
            if not command or not os.path.isfile(command):
                return
            for x in range(1, len(resp)):
                arg = resp[x].strip()
                if arg:
                    liArgs.append(arg)

            um = QTUtil2.unMomento(self)
            me = Engines.Engine(path_exe=command, args=liArgs)
            li_uci = me.read_uci_options()
            um.final()
            if not li_uci:
                QTUtil2.message_bold(self, _X(_("The file %1 does not correspond to a UCI engine type."), command))
                return None

            # Editamos
            w = WEngine(self, self.lista_motores, me)
            if w.exec_():
                self.lista_motores.append(me)
                self.grid.refresh()
                self.grid.gobottom(0)
                self.grabar()

    def nuevo(self):
        me = selectEngine(self)
        if not me:
            return

        # Editamos
        w = WEngine(self, self.lista_motores, me)
        if w.exec_():
            self.lista_motores.append(me)

            self.grid.refresh()
            self.grid.gobottom(0)
            self.grabar()

    def grid_doble_click(self, grid, fil, col):
        self.modificar()

    def grid_doble_clickCabecera(self, grid, oColumna):
        key = oColumna.clave
        if key == "ALIAS":
            key = "clave"
        elif key == "MOTOR":
            key = "name"
        elif key == "ELO":
            key = "elo"
        else:
            return
        self.lista_motores.sort(key=operator.attrgetter(key))
        self.grid.refresh()
        self.grid.gotop()
        self.grabar()

    def modificar(self):
        if len(self.lista_motores):
            fila = self.grid.recno()
            if fila >= 0:
                me = self.lista_motores[fila]
                # Editamos, y graba si hace falta
                w = WEngine(self, self.lista_motores, me)
                if w.exec_():
                    self.grid.refresh()
                    self.grabar()

    def arriba(self):
        fila = self.grid.recno()
        if fila > 0:
            li = self.lista_motores
            a, b = li[fila], li[fila - 1]
            li[fila], li[fila - 1] = b, a
            self.grid.goto(fila - 1, 0)
            self.grid.refresh()
            self.grabar()

    def abajo(self):
        fila = self.grid.recno()
        li = self.lista_motores
        if fila < len(li) - 1:
            a, b = li[fila], li[fila + 1]
            li[fila], li[fila + 1] = b, a
            self.grid.goto(fila + 1, 0)
            self.grid.refresh()
            self.grabar()

    def borrar(self):
        fila = self.grid.recno()
        if fila >= 0:
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), self.lista_motores[fila].clave)):
                del self.lista_motores[fila]
                self.grid.refresh()
                self.grabar()

    def copiar(self):
        fila = self.grid.recno()
        if fila >= 0:
            me = self.lista_motores[fila].copy()
            w = WEngine(self, self.lista_motores, me)
            if w.exec_():
                self.lista_motores.nuevo(me)
                self.grid.refresh()
                self.grid.gobottom(0)
                self.grabar()

    def importar(self):
        menu = QTVarios.LCMenu(self)
        lista = Code.configuracion.comboMotores()
        nico = QTVarios.rondoPuntos()
        for name, key in lista:
            menu.opcion(key, name, nico.otro())

        resp = menu.lanza()
        if not resp:
            return

        me = Code.configuracion.buscaRival(resp)
        w = WEngine(self, self.lista_motores, me)
        if w.exec_():
            self.lista_motores.append(me)
            self.grid.refresh()
            self.grid.gobottom(0)
            self.grabar()


class WEngine(QtWidgets.QDialog):
    def __init__(self, wParent, listaMotores, engine, siTorneo=False):

        super(WEngine, self).__init__(wParent)

        self.setWindowTitle(engine.version)
        self.setWindowIcon(Iconos.Motor())
        self.setWindowFlags(
            QtCore.Qt.WindowCloseButtonHint
            | QtCore.Qt.Dialog
            | QtCore.Qt.WindowTitleHint
            | QtCore.Qt.WindowMinimizeButtonHint
            | QtCore.Qt.WindowMaximizeButtonHint
        )

        scrollArea = wgen_options_engine(self, engine)

        self.motorExterno = engine
        self.liMotores = listaMotores
        self.siTorneo = siTorneo

        # Toolbar
        tb = QTUtil2.tbAcceptCancel(self)

        lbAlias = Controles.LB2P(self, _("Alias"))
        self.edAlias = Controles.ED(self, engine.clave).anchoMinimo(360)

        lbNombre = Controles.LB2P(self, _("Name"))
        self.edNombre = Controles.ED(self, engine.name).anchoMinimo(360)

        lbInfo = Controles.LB(self, _("Information") + ": ")
        self.emInfo = Controles.EM(self, engine.id_info, siHTML=False).anchoMinimo(360).altoFijo(60)

        lbElo = Controles.LB(self, "ELO: ")
        self.sbElo = Controles.SB(self, engine.elo, 0, 4000)

        lbExe = Controles.LB(self, "%s: %s" % (_("File"), Util.relative_path(engine.path_exe)))

        if siTorneo:
            lbDepth = Controles.LB(self, _("Maximum depth") + ": ")
            self.sbDepth = Controles.SB(self, engine.max_depth, 0, 50)

            lbTime = Controles.LB(self, _("Maximum seconds to think") + ": ")
            self.sbTime = Controles.SB(self, engine.max_time, 0, 9999)

            lbBook = Controles.LB(self, _("Opening book") + ": ")
            fvar = Code.configuracion.ficheroBooks
            self.listaLibros = Books.ListaLibros()
            self.listaLibros.restore_pickle(fvar)
            # # Comprobamos que todos esten accesibles
            self.listaLibros.comprueba()
            li = [(x.name, x.path) for x in self.listaLibros.lista]
            li.insert(0, ("* " + _("None"), "-"))
            li.insert(0, ("* " + _("Default"), "*"))
            self.cbBooks = Controles.CB(self, li, engine.book)
            btNuevoBook = Controles.PB(self, "", self.nuevoBook, plano=False).ponIcono(Iconos.Nuevo(), tamIcon=16)
            # # Respuesta rival
            li = (
                (_("Uniform random"), "au"),
                (_("Proportional random"), "ap"),
                (_("Always the highest percentage"), "mp"),
            )
            self.cbBooksRR = QTUtil2.comboBoxLB(self, li, engine.bookRR)
            lyBook = (
                Colocacion.H()
                .control(lbBook)
                .control(self.cbBooks)
                .control(self.cbBooksRR)
                .control(btNuevoBook)
                .relleno()
            )
            lyDT = (
                Colocacion.H()
                .control(lbDepth)
                .control(self.sbDepth)
                .espacio(40)
                .control(lbTime)
                .control(self.sbTime)
                .relleno()
            )
            lyTorneo = Colocacion.V().otro(lyDT).otro(lyBook)

        # Layout
        ly = Colocacion.G()
        ly.controld(lbAlias, 0, 0).control(self.edAlias, 0, 1)
        ly.controld(lbNombre, 1, 0).control(self.edNombre, 1, 1)
        ly.controld(lbInfo, 2, 0).control(self.emInfo, 2, 1)
        ly.controld(lbElo, 3, 0).control(self.sbElo, 3, 1)
        ly.control(lbExe, 4, 0, 1, 2)

        if siTorneo:
            ly.otro(lyTorneo, 5, 0, 1, 2)

        layout = Colocacion.V().control(tb).espacio(30).otro(ly).control(scrollArea)
        self.setLayout(layout)

        self.edAlias.setFocus()

    def nuevoBook(self):
        fbin = QTUtil2.leeFichero(self, self.listaLibros.path, "bin", titulo=_("Polyglot book"))
        if fbin:
            self.listaLibros.path = os.path.dirname(fbin)
            name = os.path.basename(fbin)[:-4]
            b = Books.Libro("P", name, fbin, False)
            self.listaLibros.nuevo(b)
            fvar = Code.configuracion.ficheroBooks
            self.listaLibros.save_pickle(fvar)
            li = [(x.name, x.path) for x in self.listaLibros.lista]
            li.insert(0, ("* " + _("Engine book"), "-"))
            li.insert(0, ("* " + _("Default"), "*"))
            self.cbBooks.rehacer(li, b.path)

    def aceptar(self):
        alias = self.edAlias.texto().strip()
        if not alias:
            QTUtil2.message_error(self, _("You have not indicated any alias"))
            return

        # Comprobamos que no se repita el alias
        for engine in self.liMotores:
            if (self.motorExterno != engine) and (engine.clave == alias):
                QTUtil2.message_error(
                    self,
                    _(
                        "There is already another engine with the same alias, the alias must change in order to have both."
                    ),
                )
                return
        self.motorExterno.clave = alias
        name = self.edNombre.texto().strip()
        self.motorExterno.name = name if name else alias
        self.motorExterno.id_info = self.emInfo.texto()
        self.motorExterno.elo = self.sbElo.valor()

        if self.siTorneo:
            self.motorExterno.depth = self.sbDepth.valor()
            self.motorExterno.time = self.sbTime.valor()
            pbook = self.cbBooks.valor()
            self.motorExterno.book = pbook
            self.motorExterno.bookRR = self.cbBooksRR.valor()

        # Grabamos opciones
        wsave_options_engine(self.motorExterno)

        self.accept()


def wgen_options_engine(owner, engine):
    fil = 0
    col = 0
    layout = Colocacion.G()
    for opcion in engine.li_uci_options_editable():
        tipo = opcion.tipo
        lb = Controles.LB(owner, opcion.name + ":").alinDerecha()
        if tipo == "spin":
            control = QTUtil2.spinBoxLB(
                owner, opcion.valor, opcion.minimo, opcion.maximo, maxTam=50 if opcion.maximo < 1000 else 80
            )
            lb.ponTexto("%s [%d-%d] :" % (opcion.name, opcion.minimo, opcion.maximo))
        elif tipo == "check":
            control = Controles.CHB(owner, " ", opcion.valor)
        elif tipo == "combo":
            liVars = []
            for var in opcion.li_vars:
                liVars.append((var, var))
            control = Controles.CB(owner, liVars, opcion.valor)
        elif tipo == "string":
            control = Controles.ED(owner, opcion.valor)
        # elif tipo == "button":
        #     control = Controles.CHB(owner, " ", opcion.valor)

        layout.controld(lb, fil, col).control(control, fil, col + 1)
        col += 2
        if col > 2:
            fil += 1
            col = 0
        opcion.control = control

    w = QtWidgets.QWidget(owner)
    w.setLayout(layout)
    scrollArea = QtWidgets.QScrollArea()
    scrollArea.setBackgroundRole(QtGui.QPalette.Light)
    scrollArea.setWidget(w)
    scrollArea.setWidgetResizable(True)

    return scrollArea


def wsave_options_engine(engine):
    liUCI = engine.liUCI = []
    for opcion in engine.li_uci_options_editable():
        tipo = opcion.tipo
        control = opcion.control
        if tipo == "spin":
            valor = control.value()
        elif tipo == "check":
            valor = control.isChecked()
        elif tipo == "combo":
            valor = control.valor()
        elif tipo == "string":
            valor = control.texto()
        else:
            valor = True
        # elif tipo == "button":
        #     valor = control.isChecked()
        if valor != opcion.valor:
            liUCI.append((opcion.name, valor))
            opcion.valor = valor
        if opcion.name == "MultiPV":
            engine.maxMultiPV = opcion.maximo


def selectEngine(wowner):
    """
    :param wowner: window
    :return: MotorExterno / None=error
    """
    # Pedimos el ejecutable
    folderEngines = Code.configuracion.leeVariables("FOLDER_ENGINES")
    exeMotor = QTUtil2.leeFichero(
        wowner, folderEngines if folderEngines else ".", "%s EXE (*.exe)" % _("File"), _("Engine")
    )
    if not exeMotor:
        return None
    folderEngines = Util.dirRelativo(os.path.dirname(exeMotor))
    Code.configuracion.escVariables("FOLDER_ENGINES", folderEngines)

    # Leemos el UCI
    um = QTUtil2.unMomento(wowner)
    me = Engines.read_engine_uci(exeMotor)
    um.final()
    if not me:
        QTUtil2.message_bold(wowner, _X(_("The file %1 does not correspond to a UCI engine type."), exeMotor))
        return None
    return me


class WSelectEngineElo(QTVarios.WDialogo):
    def __init__(self, gestor, elo, titulo, icono, tipo):
        QTVarios.WDialogo.__init__(self, gestor.main_window, titulo, icono, tipo.lower())

        self.siMicElo = tipo == "MICELO"
        self.siMicPer = tipo == "MICPER"
        self.siMic = self.siMicElo or self.siMicPer

        self.gestor = gestor

        self.colorNoJugable = QTUtil.qtColorRGB(241, 226, 226)
        self.colorMenor = QTUtil.qtColorRGB(245, 245, 245)
        self.colorMayor = None
        self.elo = elo
        self.tipo = tipo

        # Toolbar
        li_acciones = [
            (_("Choose"), Iconos.Aceptar(), self.elegir),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("Random opponent"), Iconos.FAQ(), self.selectRandom),
            None,
        ]
        if self.siMicElo:
            li_acciones.append((_("Reset"), Iconos.Reiniciar(), self.reset))
            li_acciones.append(None)

        self.tb = QTVarios.LCTB(self, li_acciones)

        self.liMotores = self.gestor.list_engines(elo)
        self.liMotoresActivos = self.liMotores

        liFiltro = (
            ("---", None),
            (">=", ">"),
            ("<=", "<"),
            ("+-100", "100"),
            ("+-200", "200"),
            ("+-400", "400"),
            ("+-800", "800"),
        )

        self.cbElo = Controles.CB(self, liFiltro, None).capturaCambiado(self.filtrar)

        minimo = 9999
        maximo = 0
        for mt in self.liMotores:
            if mt.siJugable:
                if mt.elo < minimo:
                    minimo = mt.elo
                if mt.elo > maximo:
                    maximo = mt.elo
        self.sbElo, lbElo = QTUtil2.spinBoxLB(self, elo, minimo, maximo, maxTam=50, etiqueta=_("Elo"))
        self.sbElo.capturaCambiado(self.filtrar)

        if self.siMic:
            liCaract = []
            st = set()
            for mt in self.liMotores:
                mt.liCaract = li = mt.id_info.split("\n")
                mt.txtCaract = ", ".join([_F(x) for x in li])
                for x in li:
                    if not (x in st):
                        st.add(x)
                        liCaract.append((_F(x), x))
            liCaract.sort(key=lambda x: x[1])
            liCaract.insert(0, ("---", None))
            self.cbCaract = Controles.CB(self, liCaract, None).capturaCambiado(self.filtrar)

        ly = Colocacion.H().control(lbElo).control(self.cbElo).control(self.sbElo)
        if self.siMic:
            ly.control(self.cbCaract)
        ly.relleno(1)
        gbRandom = Controles.GB(self, "", ly)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMERO", _("N."), 35, centered=True)
        o_columns.nueva("MOTOR", _("Name"), 140)
        o_columns.nueva("ELO", _("Elo"), 60, siDerecha=True)
        if not self.siMicPer:
            o_columns.nueva("GANA", _("Win"), 80, centered=True)
            o_columns.nueva("TABLAS", _("Draw"), 80, centered=True)
            o_columns.nueva("PIERDE", _("Lost"), 80, centered=True)
        if self.siMic:
            o_columns.nueva("INFO", _("Information"), 300, centered=True)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, siCabeceraMovible=False, altoFila=24)
        n = self.grid.anchoColumnas()
        self.grid.setMinimumWidth(n + 20)
        self.register_grid(self.grid)

        f = Controles.TipoLetra(puntos=9)
        self.grid.ponFuente(f)

        self.grid.gotop()

        # Layout
        lyH = Colocacion.H().control(self.tb).control(gbRandom)
        layout = Colocacion.V().otro(lyH).control(self.grid).margen(3)
        self.setLayout(layout)

        self.filtrar()

        self.restore_video()

    def removeReset(self):
        self.tb.setAccionVisible(self.reset, False)

    def filtrar(self):
        cb = self.cbElo.valor()
        elo = self.sbElo.valor()
        if cb is None:
            self.liMotoresActivos = self.liMotores
            self.sbElo.setDisabled(True)
        else:
            self.sbElo.setDisabled(False)
            if cb == ">":
                self.liMotoresActivos = [x for x in self.liMotores if x.elo >= elo]
            elif cb == "<":
                self.liMotoresActivos = [x for x in self.liMotores if x.elo <= elo]
            elif cb in ("100", "200", "400", "800"):
                mx = int(cb)
                self.liMotoresActivos = [x for x in self.liMotores if abs(x.elo - elo) <= mx]
        if self.siMic:
            cc = self.cbCaract.valor()
            if cc:
                self.liMotoresActivos = [mt for mt in self.liMotoresActivos if cc in mt.liCaract]
        self.grid.refresh()

    def reset(self):
        if not QTUtil2.pregunta(self, _("Are you sure you want to set the original elo of all engines?")):
            return

        self.gestor.configuracion.escVariables("DicMicElos", {})
        self.cancelar()

    def cancelar(self):
        self.resultado = None
        self.save_video()
        self.reject()

    def elegir(self):
        f = self.grid.recno()
        mt = self.liMotoresActivos[f]
        if mt.siJugable:
            self.resultado = mt
            self.save_video()
            self.accept()
        else:
            QTUtil.beep()

    def selectRandom(self):
        li = []
        for mt in self.liMotoresActivos:
            if mt.siJugable:
                li.append(mt)
        if li:
            n = random.randint(0, len(li) - 1)
            self.resultado = li[n]
            self.save_video()
            self.accept()
        else:
            QTUtil2.message_error(self, _("There is not a playable engine between these values"))

    def grid_doble_click(self, grid, fila, oColumna):
        self.elegir()

    def grid_num_datos(self, grid):
        return len(self.liMotoresActivos)

    def grid_wheel_event(self, quien, siAdelante):
        n = len(self.liMotoresActivos)
        f, c = self.grid.posActualN()
        f += -1 if siAdelante else +1
        if 0 <= f < n:
            self.grid.goto(f, c)

    def grid_color_fondo(self, grid, fila, oColumna):
        mt = self.liMotoresActivos[fila]
        if mt.siOut:
            return self.colorNoJugable
        else:
            return self.colorMenor if mt.elo < self.elo else self.colorMayor

    def grid_dato(self, grid, fila, oColumna):
        mt = self.liMotoresActivos[fila]
        key = oColumna.clave
        if key == "NUMERO":
            valor = "%2d" % mt.number
        elif key == "MOTOR":
            valor = " " + mt.alias
        elif key == "ELO":
            valor = "%d " % mt.elo
        elif key == "INFO":
            valor = mt.txtCaract
        else:
            if not mt.siJugable:
                return "x"
            if key == "GANA":
                pts = mt.pgana
            elif key == "TABLAS":
                pts = mt.ptablas
            elif key == "PIERDE":
                pts = mt.ppierde

            valor = "%+d" % pts

        return valor


def select_engine_elo(gestor, elo):
    titulo = _("Lucas-Elo") + ". " + _("Choose the opponent")
    icono = Iconos.Elo()
    w = WSelectEngineElo(gestor, elo, titulo, icono, "ELO")
    if w.exec_():
        return w.resultado
    else:
        return None


def select_engine_micelo(gestor, elo):
    titulo = _("Club players competition") + ". " + _("Choose the opponent")
    icono = Iconos.EloTimed()
    w = WSelectEngineElo(gestor, elo, titulo, icono, "MICELO")
    if w.exec_():
        return w.resultado
    else:
        return None


def select_engine_entmaq(main_window):
    titulo = _("Choose the opponent")
    icono = Iconos.EloTimed()

    class GestorTmp:
        def __init__(self):
            self.main_window = main_window
            self.configuracion = Code.configuracion

        def list_engines(self, elo):
            li = EnginesMicElo.all_engines()
            numX = len(li)
            for num, mt in enumerate(li):
                mt.siJugable = True
                mt.siOut = False
                mt.number = numX - num
            return li

    w = WSelectEngineElo(GestorTmp(), 1600, titulo, icono, "MICPER")
    if w.exec_():
        return w.resultado
    else:
        return None
