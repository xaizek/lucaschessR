import copy

from PySide2 import QtCore, QtWidgets

from Code.Constantes import FEN_INITIAL
from Code import AperturasStd
from Code import Move
from Code import Game
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import Tablero
from Code import Util
import Code
from Code import Variantes


class WAperturas(QTVarios.WDialogo):
    def __init__(self, owner, configuracion, bloqueApertura):
        icono = Iconos.Apertura()
        titulo = _("Select an opening")
        extparam = "selectOpening"
        QTVarios.WDialogo.__init__(self, owner, titulo, icono, extparam)

        # Variables--------------------------------------------------------------------------
        self.apStd = AperturasStd.apTrain
        self.configuracion = configuracion
        self.game = Game.Game()
        self.bloqueApertura = bloqueApertura
        self.liActivas = []

        # Tablero
        config_board = configuracion.config_board("APERTURAS", 32)
        self.tablero = Tablero.Tablero(self, config_board)
        self.tablero.crea()
        self.tablero.set_dispatcher(self.mueve_humano)

        # Current pgn
        self.lbPGN = Controles.LB(self, "").ponWrap().ponTipoLetra(puntos=10, peso=75)

        # Movimiento
        self.is_moving_time = False

        lyBM, tbBM = QTVarios.lyBotonesMovimiento(self, "", siLibre=False, tamIcon=24)
        self.tbBM = tbBM

        # Tool bar
        tb = Controles.TBrutina(self)
        tb.new(_("Accept"), Iconos.Aceptar(), self.aceptar)
        tb.new(_("Cancel"), Iconos.Cancelar(), self.cancelar)
        tb.new(_("Reinit"), Iconos.Reiniciar(), self.resetPartida)
        tb.new(_("Takeback"), Iconos.Atras(), self.atras)
        tb.new(_("Remove"), Iconos.Borrar(), self.borrar)

        # Lista Aperturas
        o_columns = Columnas.ListaColumnas()
        dicTipos = {"b": Iconos.pmSun(), "n": Iconos.pmPuntoAzul(), "l": Iconos.pmNaranja()}
        o_columns.nueva("TIPO", "", 24, edicion=Delegados.PmIconosBMT(dicIconos=dicTipos))
        o_columns.nueva("OPENING", _("Possible continuation"), 480)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, altoFila=32)
        self.register_grid(self.grid)

        # # Derecha
        lyD = Colocacion.V().control(tb).control(self.grid)
        gbDerecha = Controles.GB(self, "", lyD)

        # # Izquierda
        lyI = Colocacion.V().control(self.tablero).otro(lyBM).control(self.lbPGN)
        gbIzquierda = Controles.GB(self, "", lyI)

        splitter = QtWidgets.QSplitter(self)
        splitter.addWidget(gbIzquierda)
        splitter.addWidget(gbDerecha)
        self.register_splitter(splitter, "splitter")

        # Completo
        ly = Colocacion.H().control(splitter).margen(3)
        self.setLayout(ly)

        self.ponActivas()
        self.resetPartida()
        self.actualizaPosicion()

        dic = {"_SIZE_": "916,444", "SP_splitter": [356, 548]}
        self.restore_video(dicDef=dic)

    def mueve_humano(self, from_sq, to_sq, promotion=None):
        self.tablero.disable_all()

        movimiento = from_sq + to_sq

        position = self.game.move(self.posCurrent).position if self.posCurrent >= 0 else self.game.last_position

        # Peon coronando
        if not promotion and position.siPeonCoronando(from_sq, to_sq):
            promotion = self.tablero.peonCoronando(position.is_white)
            if promotion is None:
                self.sigueHumano()
                return False
        if promotion:
            movimiento += promotion

        siBien, mens, move = Move.dameJugada(self.game, position, from_sq, to_sq, promotion)
        if siBien:
            self.nuevaJugada(move)
        else:
            self.actualizaPosicion()

    def grid_num_datos(self, grid):
        return len(self.liActivas)

    def grid_dato(self, grid, fila, oColumna):
        key = oColumna.clave
        ap = self.liActivas[fila]
        if key == "TIPO":
            return "b" if ap.siBasic else "n"
        else:
            return ap.name + "\n" + ap.pgn

    def grid_doble_click(self, grid, fila, columna):
        if -1 < fila < len(self.liActivas):
            ap = self.liActivas[fila]
            self.game.set_position()
            self.game.read_pv(ap.a1h8)
            self.ponActivas()

    def nuevaJugada(self, move):
        self.posCurrent += 1
        if self.posCurrent < len(self.game):
            self.game.li_moves = self.game.li_moves[: self.posCurrent]
        self.game.add_move(move)
        self.ponActivas()

    def ponActivas(self):
        li = self.apStd.list_possible_openings(self.game, True)
        if li:
            li = sorted(li, key=lambda ap: ("A" if ap.siBasic else "Z") + ap.pgn)
        else:
            li = []
        self.liActivas = li

        self.tablero.setposition(self.game.last_position)

        self.game.assign_opening()
        txt = self.game.pgn_translated()
        if self.game.opening:
            txt = '<span style="color:gray;">%s</span><br>%s' % (self.game.opening.name, txt)

        self.lbPGN.ponTexto(txt)
        self.posCurrent = len(self.game) - 1

        self.actualizaPosicion()
        self.grid.refresh()
        self.grid.gotop()

        w = self.width()
        self.adjustSize()
        if self.width() != w:
            self.resize(w, self.height())

    def actualizaPosicion(self):
        if self.posCurrent > -1:
            move = self.game.move(self.posCurrent)
            position = move.position
        else:
            position = self.game.first_position
            move = None

        self.tablero.setposition(position)
        self.tablero.activaColor(position.is_white)
        if move:
            self.tablero.ponFlechaSC(move.from_sq, move.to_sq)

    def resetPartida(self):
        self.game.set_position()
        if self.bloqueApertura:
            self.game.read_pv(self.bloqueApertura.a1h8)
        self.ponActivas()
        self.mueve(siFinal=True)

    def terminar(self):
        self.is_moving_time = False
        self.save_video()

    def closeEvent(self, event):
        self.terminar()

    def aceptar(self):
        self.terminar()
        self.accept()

    def cancelar(self):
        self.terminar()
        self.reject()

    def atras(self):
        self.game.anulaSoloUltimoMovimiento()
        self.ponActivas()

    def borrar(self):
        self.game.set_position()
        self.ponActivas()

    def process_toolbar(self):
        accion = self.sender().clave
        if accion == "MoverAdelante":
            self.mueve(nSaltar=1)
        elif accion == "MoverAtras":
            self.mueve(nSaltar=-1)
        elif accion == "MoverInicio":
            self.mueve(siInicio=True)
        elif accion == "MoverFinal":
            self.mueve(siFinal=True)
        elif accion == "MoverTiempo":
            self.move_timed()

    def mueve(self, siInicio=False, nSaltar=0, siFinal=False):
        num_moves = len(self.game)
        if nSaltar:
            pos = self.posCurrent + nSaltar
            if 0 <= pos < num_moves:
                self.posCurrent = pos
            else:
                return
        elif siInicio:
            self.posCurrent = -1
        elif siFinal:
            self.posCurrent = num_moves - 1
        else:
            return
        self.actualizaPosicion()

    def move_timed(self):
        if self.is_moving_time:
            self.is_moving_time = False

        else:
            self.is_moving_time = True
            self.mueve(siInicio=True)
            QtCore.QTimer.singleShot(1000, self.siguienteTiempo)

    def siguienteTiempo(self):
        if self.is_moving_time:
            if self.posCurrent < len(self.game) - 1:
                self.mueve(nSaltar=1)
                QtCore.QTimer.singleShot(2500, self.siguienteTiempo)
            else:
                self.is_moving_time = False

    def resultado(self):
        if len(self.game) == 0:
            return None
        ap = self.game.opening
        if ap is None:
            ap = AperturasStd.AperturasStd(_("Unknown"))
            ap.a1h8 = self.game.pv()
        else:
            if not self.game.last_jg().in_the_opening:
                p = Game.Game()
                p.read_pv(ap.a1h8)
                ap.a1h8 = self.game.pv()
                ap.trNombre += " + %s" % (self.game.pgn_translated()[len(p.pgn_translated()) + 1:],)

        ap.pgn = self.game.pgn_translated()
        return ap


class EntrenamientoApertura(QTVarios.WDialogo):
    def __init__(self, owner, listaAperturasStd, dic_data):
        icono = Iconos.Apertura()
        titulo = _("Learn openings by repetition")
        extparam = "opentrainingE"
        QTVarios.WDialogo.__init__(self, owner, titulo, icono, extparam)

        name = dic_data.get("NOMBRE", "")
        self.listaAperturasStd = listaAperturasStd
        self.liBloques = self.leeBloques(dic_data.get("LISTA", []))

        # Toolbar
        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            None,
            (_("Add"), Iconos.Nuevo(), self.nueva),
            None,
            (_("Modify"), Iconos.Modificar(), self.modificar),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
        ]
        tb = Controles.TBrutina(self, li_acciones)

        lbNombre = Controles.LB(self, _("Name") + ": ")
        self.edNombre = Controles.ED(self, name)

        lyNombre = Colocacion.H().control(lbNombre).control(self.edNombre)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NOMBRE", _("Name"), 240)
        o_columns.nueva("PGN", _("Moves"), 360)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        n = self.grid.anchoColumnas()
        self.grid.setMinimumWidth(n + 20)
        self.register_grid(self.grid)
        self.grid.gotop()

        layout = Colocacion.V().control(tb).otro(lyNombre).control(self.grid)

        self.setLayout(layout)
        self.restore_video()

    def grid_num_datos(self, grid):
        return len(self.liBloques)

    def grid_dato(self, grid, fila, oColumna):
        key = oColumna.clave
        bloque = self.liBloques[fila]
        if key == "NOMBRE":
            return bloque.trNombre
        return bloque.pgn

    def grid_doble_click(self, grid, fil, col):
        self.modificar()

    def leeBloques(self, liPV):
        li = []
        for pv in liPV:
            p = Game.Game()
            p.read_pv(pv)
            p.assign_opening()
            ap = p.opening
            if ap is None:
                ap = AperturasStd.AperturasStd(_("Unknown"))
                ap.a1h8 = pv
            else:
                ap.a1h8 = pv
                ap.pgn = ap.pgn.replace(". ", ".")
                nap = len(ap.pgn)
                pgn_translated = p.pgn_translated()
                if len(pgn_translated) > nap:
                    ap.trNombre += " + %s" % (pgn_translated[nap + 1:],)
            ap.pgn = p.pgn_translated()
            li.append(ap)
        return li

    def nueva(self):
        bloque = self.editar(None)
        if bloque:
            self.liBloques.append(bloque)
            if not self.edNombre.texto().strip():
                self.edNombre.ponTexto(bloque.trNombre)
            self.grid.refresh()
            self.grid.gobottom()

    def modificar(self):
        fila = self.grid.recno()
        if fila >= 0:
            bloque = self.liBloques[fila]
            bloque = self.editar(bloque)
            if bloque:
                self.liBloques[fila] = bloque
                self.grid.refresh()

    def editar(self, bloque):
        me = QTUtil2.unMomento(self)
        w = WAperturas(self, Code.configuracion, bloque)
        me.final()
        if w.exec_():
            return w.resultado()
        return None

    def borrar(self):
        fila = self.grid.recno()
        if fila >= 0:
            bloque = self.liBloques[fila]
            if QTUtil2.pregunta(self, _X(_("Delete %1?"), bloque.trNombre)):
                del self.liBloques[fila]
                self.grid.refresh()

    def aceptar(self):
        if not self.liBloques:
            QTUtil2.message_error(self, _("you have not indicated any opening"))
            return

        self.name = self.edNombre.texto().strip()
        if not self.name:
            if len(self.liBloques) == 1:
                self.name = self.liBloques[0].trNombre
            else:
                QTUtil2.message_error(self, _("Not indicated the name of training"))
                return

        self.accept()

    def cancelar(self):
        self.reject()

    def listaPV(self):
        li = []
        for bloque in self.liBloques:
            li.append(bloque.a1h8)
        return li


class AperturasPersonales(QTVarios.WDialogo):
    def __init__(self, procesador, owner=None):

        self.procesador = procesador
        self.ficheroDatos = procesador.configuracion.file_pers_openings()
        self.lista = self.leer()

        if owner is None:
            owner = procesador.main_window
        icono = Iconos.Apertura()
        titulo = _("Custom openings")
        extparam = "customopen"
        QTVarios.WDialogo.__init__(self, owner, titulo, icono, extparam)

        # Toolbar
        tb = Controles.TBrutina(self)
        tb.new(_("Close"), Iconos.MainMenu(), self.terminar)
        tb.new(_("New"), Iconos.TutorialesCrear(), self.nuevo)
        tb.new(_("Modify"), Iconos.Modificar(), self.modificar)
        tb.new(_("Remove"), Iconos.Borrar(), self.borrar)
        tb.new(_("Copy"), Iconos.Copiar(), self.copiar)
        tb.new(_("Up"), Iconos.Arriba(), self.arriba)
        tb.new(_("Down"), Iconos.Abajo(), self.abajo)

        # Lista
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NOMBRE", _("Name"), 240)
        o_columns.nueva("ECO", "ECO", 70, centered=True)
        o_columns.nueva("PGN", "PGN", 280)
        o_columns.nueva("ESTANDAR", _("Add to standard list"), 120, centered=True)

        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True)
        n = self.grid.anchoColumnas()
        self.grid.setMinimumWidth(n + 20)
        self.register_grid(self.grid)
        self.grid.gotop()

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).margen(8)
        self.setLayout(layout)

        self.restore_video(siTam=True)

        self.dicPGNSP = {}

    def terminar(self):
        self.save_video()
        self.reject()
        return

    def grid_num_datos(self, grid):
        return len(self.lista)

    def grid_dato(self, grid, fila, oColumna):
        key = oColumna.clave
        reg = self.lista[fila]
        if key == "ESTANDAR":
            return _("Yes") if reg["ESTANDAR"] else _("No")
        elif key == "PGN":
            pgn = reg["PGN"]
            if not (pgn in self.dicPGNSP):
                p = Game.Game()
                p.read_pv(reg["A1H8"])
                self.dicPGNSP[pgn] = p.pgn_translated()
            return self.dicPGNSP[pgn]
        return reg[key]

    def grid_doble_click(self, grid, fil, col):
        self.editar(fil)

    def grid_doble_clickCabecera(self, grid, oColumna):
        key = oColumna.clave

        li = sorted(self.lista, key=lambda x: x[key].upper())

        self.lista = li

        self.grid.refresh()
        self.grid.gotop()

        self.grabar()

    def editar(self, fila):

        if fila is None:
            name = ""
            eco = ""
            pgn = ""
            estandar = True
            titulo = _("New opening")

        else:
            reg = self.lista[fila]

            name = reg["NOMBRE"]
            eco = reg["ECO"]
            pgn = reg["PGN"]
            estandar = reg["ESTANDAR"]

            titulo = name

        # Datos
        liGen = [(None, None)]
        liGen.append((_("Name") + ":", name))
        config = FormLayout.Editbox("ECO", ancho=30, rx="[A-Z, a-z][0-9][0-9]")
        liGen.append((config, eco))
        liGen.append((_("Add to standard list") + ":", estandar))

        # Editamos
        resultado = FormLayout.fedit(liGen, title=titulo, parent=self, anchoMinimo=460, icon=Iconos.Apertura())
        if resultado is None:
            return

        accion, liResp = resultado
        name = liResp[0].strip()
        if not name:
            return
        eco = liResp[1].upper()
        estandar = liResp[2]

        fen = FEN_INITIAL

        self.procesador.procesador = self.procesador  # ya que editaVariante espera un gestor

        if pgn:
            ok, game = Game.pgn_game(pgn)
            if not ok:
                game = Game.Game()
        else:
            game = Game.Game()

        resp = Variantes.editaVariante(self.procesador, game, titulo=name, is_white_bottom=True)

        if resp:
            game = resp

            reg = {}
            reg["NOMBRE"] = name
            reg["ECO"] = eco
            reg["PGN"] = game.pgnBaseRAW()
            reg["A1H8"] = game.pv()
            reg["ESTANDAR"] = estandar

            if fila is None:
                self.lista.append(reg)
                self.grid.refresh()
                self.grabar()
            else:
                self.lista[fila] = reg
            self.grid.refresh()
            self.grabar()

    def nuevo(self):
        self.editar(None)

    def modificar(self):
        recno = self.grid.recno()
        if recno >= 0:
            self.editar(recno)

    def borrar(self):
        fila = self.grid.recno()
        if fila >= 0:
            if QTUtil2.pregunta(self, _X(_("Do you want to delete the opening %1?"), self.lista[fila]["NOMBRE"])):
                del self.lista[fila]
                self.grid.refresh()
                self.grabar()

    def copiar(self):
        fila = self.grid.recno()
        if fila >= 0:
            reg = self.lista[fila]
            nreg = copy.deepcopy(reg)
            self.lista.append(nreg)
            self.grid.refresh()
            self.grabar()

    def leer(self):
        lista = Util.restore_pickle(self.ficheroDatos)
        if lista is None:
            lista = []

        return lista

    def grabar(self):
        Util.save_pickle(self.ficheroDatos, self.lista)

    def arriba(self):
        fila = self.grid.recno()
        if fila > 0:
            self.lista[fila - 1], self.lista[fila] = self.lista[fila], self.lista[fila - 1]
            self.grid.goto(fila - 1, 0)
            self.grid.refresh()
            self.grid.setFocus()
            self.grabar()

    def abajo(self):
        fila = self.grid.recno()
        if 0 <= fila < (len(self.lista) - 1):
            self.lista[fila + 1], self.lista[fila] = self.lista[fila], self.lista[fila + 1]
            self.grid.goto(fila + 1, 0)
            self.grid.refresh()
            self.grid.setFocus()
            self.grabar()
