import os
import shutil
import time

from PySide2 import QtWidgets, QtCore

from Code import Analisis
from Code import Game
from Code.Databases import DBgames, WDB_Utils
from Code import TrListas
from Code import Util
from Code import AperturasStd
from Code.SQL import UtilSQL
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import Iconos
from Code.Polyglots import PolyglotImports
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import PantallaSavePGN
from Code.QT import PantallaAnalisisParam
from Code.QT import GridEditCols
from Code.QT import Delegados
from Code.QT import PantallaPlayGame


class WGames(QtWidgets.QWidget):
    def __init__(self, procesador, wb_database, dbGames, wsummary, si_select):
        QtWidgets.QWidget.__init__(self)

        self.wb_database = wb_database
        self.dbGames = dbGames  # <--setdbGames
        self.procesador = procesador
        self.configuracion = procesador.configuracion

        self.wsummary = wsummary
        self.infoMove = None  # <-- setInfoMove
        self.summaryActivo = None  # movimiento activo en summary
        self.numJugada = 0  # Se usa para indicarla al mostrar el pgn en infoMove

        self.si_select = si_select

        self.terminado = False  # singleShot

        self.ap = AperturasStd.ap

        self.liFiltro = []
        self.where = None

        self.last_opening = None

        # Grid
        o_columns = self.lista_columnas()
        self.grid = Grid.Grid(self, o_columns, siSelecFilas=True, siSeleccionMultiple=True, xid="wgames")

        # Status bar
        self.status = QtWidgets.QStatusBar(self)
        self.status.setFixedHeight(22)

        # ToolBar
        if si_select:
            liAccionesWork = [
                (_("Accept"), Iconos.Aceptar(), wb_database.tw_aceptar),
                None,
                (_("Cancel"), Iconos.Cancelar(), wb_database.tw_cancelar),
                None,
                (_("First"), Iconos.Inicio(), self.tw_gotop),
                None,
                (_("Last"), Iconos.Final(), self.tw_gobottom),
                None,
                (_("Filter"), Iconos.Filtrar(), self.tw_filtrar),
                None,
            ]
        else:
            liAccionesWork = [
                (_("Close"), Iconos.MainMenu(), wb_database.tw_terminar),
                None,
                (_("Edit"), Iconos.Modificar(), self.tw_editar),
                None,
                (_("New"), Iconos.Nuevo(), self.tw_nuevo, _("Add a new game")),
                None,
                (_("Filter"), Iconos.Filtrar(), self.tw_filtrar),
                None,
                (_("First"), Iconos.Inicio(), self.tw_gotop),
                None,
                (_("Last"), Iconos.Final(), self.tw_gobottom),
                None,
                (_("Up"), Iconos.Arriba(), self.tw_up),
                None,
                (_("Down"), Iconos.Abajo(), self.tw_down),
                None,
                (_("Remove"), Iconos.Borrar(), self.tw_borrar),
                None,
                (_("Config"), Iconos.Configurar(), self.tw_configure),
                None,
                (_("Utilities"), Iconos.Utilidades(), self.tw_utilities),
                None,
                (_("Import"), Iconos.Import8(), self.tw_import),
                None,
                (_("Export"), Iconos.Export8(), self.tw_export),
                None,
                (_("Train"), Iconos.TrainStatic(), self.tw_train),
                None,

            ]

        self.tbWork = QTVarios.LCTB(self, liAccionesWork)

        lyTB = Colocacion.H().control(self.tbWork)

        layout = Colocacion.V().otro(lyTB).control(self.grid).control(self.status).margen(1)

        self.setLayout(layout)

    def tw_train(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(self.tw_play_against, _("Play against a game"), Iconos.Law())
        if self.dbGames.has_positions():
            menu.separador()
            menu.opcion(self.tw_uti_tactic, _("Create tactics training"), Iconos.Tacticas())
        resp = menu.lanza()
        if resp:
            resp()

    def tw_play_against(self):
        li = self.grid.recnosSeleccionados()
        if li:
            recno = li[0]
            game = self.dbGames.leePartidaRecno(recno)
            h = hash(game.xpv())
            dbPlay = PantallaPlayGame.DBPlayGame(self.configuracion.file_play_game())
            recplay = dbPlay.recnoHash(h)
            if recplay is None:
                reg = {"GAME": game.save()}
                dbPlay.appendHash(h, reg)
                recplay = dbPlay.recnoHash(h)
            dbPlay.close()

            self.wb_database.tw_terminar()
            self.procesador.play_game_show(recplay)

    def lista_columnas(self):
        dcabs = self.dbGames.recuperaConfig("dcabs", DBgames.drots.copy())
        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("__num__", _("N."), 60, centered=True)
        li_tags = self.dbGames.li_tags()
        st100 = {"Event", "Site", "White", "Black"}
        for tag in li_tags:
            rotulo = TrListas.pgnLabel(tag)
            if rotulo == tag:
                rotulo = dcabs.get(rotulo, rotulo)
            centered = not (tag in ("Event", "Site"))
            ancho = 100 if tag in st100 else 80
            o_columns.nueva(tag, rotulo, ancho, centered=centered)
        o_columns.nueva("rowid", _("Row ID"), 60, centered=True)
        return o_columns

    def rehaz_columnas(self):
        li_tags = self.dbGames.li_tags()
        o_columns = self.grid.o_columns
        si_cambios = False

        li_remove = []
        for n, col in enumerate(o_columns.liColumnas):
            clave = col.clave
            if not (clave in li_tags) and not (clave in ("__num__", "rowid")):
                li_remove.append(n)
        if li_remove:
            si_cambios = True
            li_remove.sort(reverse=True)
            for n in li_remove:
                del o_columns.liColumnas[n]

        dcabs = self.dbGames.recuperaConfig("dcabs", DBgames.drots.copy())
        st100 = {"Event", "Site", "White", "Black"}
        stActual = {col.clave for col in self.grid.o_columns.liColumnas}
        for tag in li_tags:
            if not (tag in stActual):
                rotulo = TrListas.pgnLabel(tag)
                if rotulo == tag:
                    rotulo = dcabs.get(rotulo, rotulo)
                o_columns.nueva(tag, rotulo, 100 if tag in st100 else 70, centered=not (tag in ("Event", "Site")))
                si_cambios = True

        if si_cambios:
            self.dbGames.reset_cache()
            self.grid.releerColumnas()

    def setdbGames(self, dbGames):
        self.dbGames = dbGames

    def setInfoMove(self, infoMove):
        self.infoMove = infoMove
        self.graphicBoardReset()

    def updateStatus(self):
        if self.terminado:
            return
        if not self.summaryActivo:
            txt = ""
        else:
            game = self.summaryActivo.get("game", Game.Game())
            nj = len(game)
            if nj > 1:
                p = game.copia(nj - 2)
                txt = "%s | " % p.pgnBaseRAW()
            else:
                txt = ""
            siPte = self.dbGames.siFaltanRegistrosPorLeer()
            if not siPte:
                recs = self.dbGames.reccount()
                if recs:
                    txt += "%s: %d" % (_("Games"), recs)
            if self.where:
                txt += " | %s: %s" % (_("Filter"), self.where)
            if siPte:
                QtCore.QTimer.singleShot(1000, self.updateStatus)

        self.status.showMessage(txt, 0)

    def grid_num_datos(self, grid):
        return self.dbGames.reccount()

    def grid_dato(self, grid, nfila, ocol):
        key = ocol.clave
        if key == "__num__":
            return str(nfila + 1)
        elif key == "rowid":
            return str(self.dbGames.getROWID(nfila))
        elif key == "__opening__":
            xpv = self.dbGames.field(nfila, "XPV")
            if xpv[0] != "|":
                return self.ap.xpv(xpv)
            return ""
        return self.dbGames.field(nfila, key)

    def grid_doble_click(self, grid, fil, col):
        if self.si_select:
            self.wb_database.tw_aceptar()
        else:
            self.tw_editar()

    def grid_doble_clickCabecera(self, grid, col):
        liOrden = self.dbGames.dameOrden()
        key = col.clave
        if key in ("__num__"):
            return
        if key == "opening":
            key = "XPV"
        siEsta = False
        for n, (cl, tp) in enumerate(liOrden):
            if cl == key:
                siEsta = True
                if tp == "ASC":
                    liOrden[n] = (key, "DESC")
                    col.cabecera = col.antigua + "-"
                    if n:
                        del liOrden[n]
                        liOrden.insert(0, (key, "DESC"))

                elif tp == "DESC":
                    del liOrden[n]
                    col.cabecera = col.cabecera[:-1]
                break
        if not siEsta:
            liOrden.insert(0, (key, "ASC"))
            col.antigua = col.cabecera
            col.cabecera = col.antigua + "+"
        self.dbGames.ponOrden(liOrden)
        self.grid.refresh()
        self.updateStatus()

    def grid_tecla_control(self, grid, k, siShift, siControl, siAlt):
        if k in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return):
            self.tw_editar()
        elif k in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Right):
            self.infoMove.tecla_pulsada(k)
            fila, col = self.grid.posActualN()
            if QtCore.Qt.Key_Right:
                if col > 0:
                    col -= 1
            elif QtCore.Qt.Key_Left:
                if col < len(self.grid.columnas().liColumnas) - 1:
                    col += 1
            self.grid.goto(fila, col)
        elif k == QtCore.Qt.Key_Home:
            self.tw_gotop()
        elif k == QtCore.Qt.Key_End:
            self.tw_gobottom()

    def closeEvent(self, event):
        self.tw_terminar()

    def tw_terminar(self):
        self.terminado = True
        self.dbGames.close()

    def actualiza(self, siObligatorio=False):
        def pvSummary(summary):
            if summary is None:
                return ""
            lipv = summary.get("pv", "").split(" ")
            return " ".join(lipv[:-1])

        if self.wsummary:
            summaryActivo = self.wsummary.movActivo()
            if siObligatorio or pvSummary(self.summaryActivo) != pvSummary(summaryActivo) or self.liFiltro:
                self.where = None
                self.summaryActivo = summaryActivo
                pv = ""
                if self.summaryActivo:
                    pv = self.summaryActivo.get("pv")
                    if pv:
                        lipv = pv.split(" ")
                        pv = " ".join(lipv[:-1])
                    else:
                        pv = ""
                self.dbGames.filterPV(pv)
                self.updateStatus()
                self.numJugada = pv.count(" ")
                self.grid.refresh()
                self.grid.gotop()
        else:
            if siObligatorio or self.liFiltro:
                self.where = None
                self.dbGames.filterPV("")
                self.updateStatus()
                self.grid.refresh()
                self.grid.gotop()

        recno = self.grid.recno()
        if recno >= 0:
            self.grid_cambiado_registro(None, recno, None)

    def grid_cambiado_registro(self, grid, fila, oCol):
        if self.grid_num_datos(grid) > fila >= 0:
            self.setFocus()
            self.grid.setFocus()
            fen, pv = self.dbGames.damePV(fila)
            if fen:
                p = Game.Game(fen=fen)
                p.read_pv(pv)
                p.is_finished()
                self.infoMove.modoFEN(p, fen, -1)
            else:
                p = Game.Game()
                p.read_pv(pv)
                p.assign_opening()
                p.is_finished()
                self.infoMove.modoPartida(p, 0)

    def tw_gobottom(self):
        self.grid.gobottom()

    def tw_gotop(self):
        self.grid.gotop()

    def tw_up(self):
        fila = self.grid.recno()
        filaNueva = self.dbGames.intercambia(fila, True)
        if filaNueva is not None:
            self.grid.goto(filaNueva, 0)
            self.grid.refresh()

    def tw_down(self):
        fila = self.grid.recno()
        filaNueva = self.dbGames.intercambia(fila, False)
        if filaNueva is not None:
            self.grid.goto(filaNueva, 0)
            self.grid.refresh()

    def editar(self, recno, game):
        game = self.procesador.gestorPartida(self, game, not self.dbGames.allows_positions, self.infoMove.tablero)
        if game:
            resp = self.dbGames.guardaPartidaRecno(recno, game)
            if resp.ok:
                if not resp.changed:
                    return

                if resp.summary_changed:
                    self.wsummary.rehazActual()

                if resp.inserted:
                    self.updateStatus()

                if recno is None:
                    self.grid.gobottom()
                else:
                    self.grid.goto(recno, 0)
                    self.grid_cambiado_registro(self, recno, None)
                self.rehaz_columnas()
                self.grid.refresh()

            else:
                QTUtil2.message_error(self, resp.mens_error)

    def tw_nuevo(self):
        recno = None
        pc = self.dbGames.blankPartida()
        self.editar(recno, pc)

    def tw_editar(self):
        game, recno = self.current_game()
        if game:
            self.editar(recno, game)
        elif recno is not None:
            QTUtil2.message_bold(self, _("This game is wrong and can not be edited"))

    def current_game(self):
        li = self.grid.recnosSeleccionados()
        if li:
            recno = li[0]
            game = self.dbGames.leePartidaRecno(recno)
        else:
            recno = None
            game = None
        return game, recno

    def tw_filtrar(self):
        xpv = None
        if self.summaryActivo and "pv" in self.summaryActivo:
            li = self.summaryActivo["pv"].split(" ")
            if len(li) > 1:
                xpv = " ".join(li[:-1])

        def refresh():
            self.grid.refresh()
            self.grid.gotop()
            self.updateStatus()
            self.grid_cambiado_registro(None, 0, 0)

        def standard():
            w = WDB_Utils.WFiltrar(self, self.grid.o_columns, self.liFiltro, self.dbGames.nom_fichero)
            if w.exec_():
                self.liFiltro = w.liFiltro

                self.where = w.where()
                self.dbGames.filterPV(xpv, self.where)
                refresh()

        def raw_sql():
            w = WDB_Utils.WFiltrarRaw(self, self.grid.o_columns, self.where)
            if w.exec_():
                self.where = w.where
                self.dbGames.filterPV(xpv, self.where)
                refresh()

        def opening():
            me = QTUtil2.unMomento(self)
            import Code.Openings.PantallaOpenings as PantallaAperturas

            w = PantallaAperturas.WAperturas(self, self.configuracion, self.last_opening)
            me.final()
            if w.exec_():
                self.last_opening = ap = w.resultado()
                pv = getattr(ap, "a1h8", "")
                self.dbGames.filterPV(pv)
                self.numJugada = pv.count(" ")
                refresh()

        def remove_filter():
            self.dbGames.filterPV("")
            self.where = None
            self.summaryActivo["game"] = Game.Game()
            self.wsummary.inicio()
            refresh()

        menu = QTVarios.LCMenu(self)
        menu.opcion(standard, _("Standard"), Iconos.Filtrar())
        menu.separador()
        menu.opcion(raw_sql, _("Advanced"), Iconos.SQL_RAW())
        menu.separador()
        menu.opcion(opening, _("Opening"), Iconos.Apertura())
        if self.dbGames.filter is not None and self.dbGames.filter:
            menu.separador()
            menu.opcion(remove_filter, _("Remove filter"), Iconos.Cancelar())

        resp = menu.lanza()
        if resp:
            resp()

    def tw_borrar(self):
        li = self.grid.recnosSeleccionados()
        if li:
            if not QTUtil2.pregunta(self, _("Do you want to delete all selected records?")):
                return

            um = QTUtil2.unMomento(self)

            self.dbGames.borrarLista(li)
            self.summaryActivo["games"] -= len(li)
            self.grid.refresh()
            self.updateStatus()

            self.wsummary.reset()

            um.final()

    def tw_import(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(self.tw_importar_PGN, _("From a PGN file"), Iconos.FichPGN())
        menu.separador()
        menu.opcion(self.tw_importar_DB, _("From other database"), Iconos.Database())
        menu.separador()
        # menu.opcion(self.tw_importar_lcsb, _("From a lcsb file"), Iconos.JuegaSolo())
        # menu.separador()

        resp = menu.lanza()
        if resp:
            resp()

    def tw_export(self):
        li_all = range(self.dbGames.reccount())
        if not li_all:
            return None
        li_sel = self.grid.recnosSeleccionados()

        menu = QTVarios.LCMenu(self)

        submenu = menu.submenu(_("To a PGN file"), Iconos.FichPGN())
        submenu.opcion((self.tw_exportar_pgn, False), _("All registers"), Iconos.PuntoVerde())
        if li_sel:
            submenu.separador()
            submenu.opcion(
                (self.tw_exportar_pgn, True), "%s [%d]" % (_("Only selected"), len(li_sel)), Iconos.PuntoAzul()
            )

        menu.separador()
        submenu = menu.submenu(_("To other database"), Iconos.Database())
        submenu.opcion((self.tw_exportar_db, li_all), _("All registers"), Iconos.PuntoVerde())
        if li_sel:
            submenu.separador()
            submenu.opcion(
                (self.tw_exportar_db, li_sel), "%s [%d]" % (_("Only selected"), len(li_sel)), Iconos.PuntoAzul()
            )

        resp = menu.lanza()
        if resp:
            funcion, lista = resp
            funcion(lista)

    def tw_configure(self):
        menu = QTVarios.LCMenu(self)

        menu.opcion(self.tw_options, _("Database options"), Iconos.Opciones())
        menu.separador()

        menu.opcion(self.tw_tags, _("Tags"), Iconos.Tags())
        menu.separador()

        submenu = menu.submenu(_("Appearance"), Iconos.Appearance())

        dico = {True: Iconos.Aceptar(), False: Iconos.PuntoRojo()}
        submenu.opcion(self.tw_resize_columns, _("Resize all columns to contents"), Iconos.ResizeAll())
        submenu.separador()
        submenu.opcion(self.tw_edit_columns, _("Configure the columns"), Iconos.EditColumns())
        submenu.separador()

        si_show = self.dbGames.recuperaConfig("GRAPHICS_SHOW_ALLWAYS", False)
        si_graphics_specific = self.dbGames.recuperaConfig("GRAPHICS_SPECIFIC", False)
        menu1 = submenu.submenu(_("Graphic elements (Director)"), Iconos.Script())
        menu2 = menu1.submenu(_("Show allways"), Iconos.PuntoAzul())
        menu2.opcion(self.tw_dir_show_yes, _("Yes"), dico[si_show])
        menu2.separador()
        menu2.opcion(self.tw_dir_show_no, _("No"), dico[not si_show])
        menu1.separador()
        menu2 = menu1.submenu(_("Specific to this database"), Iconos.PuntoAzul())
        menu2.opcion(self.tw_locale_yes, _("Yes"), dico[si_graphics_specific])
        menu2.separador()
        menu2.opcion(self.tw_locale_no, _("No"), dico[not si_graphics_specific])
        menu.separador()

        resp = menu.lanza()
        if resp:
            resp()

    def tw_options(self):
        dic_data = modify_database(self, self.configuracion, self.dbGames)
        if dic_data is None:
            return

        # Comprobamos depth
        new_depth = dic_data["SUMMARY_DEPTH"]
        if new_depth != self.dbGames.depthStat():
            self.wsummary.reindexar(new_depth)
            self.dbGames.guardaConfig("SUMMARY_DEPTH", new_depth)

        # Si ha cambiado la localización, se cierra, se mueve y se reabre en la nueva
        new_path = dic_data["FILEPATH"]
        old_path = self.dbGames.nom_fichero
        if not Util.same_path(new_path, old_path):
            self.dbGames.close()
            self.configuracion.set_last_database(new_path)
            shutil.move(old_path, new_path)
            shutil.move(old_path + ".st1", new_path + ".st1")
            self.wb_database.reinit_sinsalvar()  # para que no cree de nuevo al salvar configuración

    def tw_tags(self):
        w = WTags(self, self.dbGames)
        if w.exec_():
            dic_cambios = w.dic_cambios

            dcabs = self.dbGames.recuperaConfig("dcabs", {})
            reinit = False

            # Primero CREATE
            for dic in dic_cambios["CREATE"]:
                self.dbGames.add_column(dic["KEY"])
                dcabs[dic["KEY"]] = dic["LABEL"]
                reinit = True

            # Segundo FILL
            li_field_value = []
            for dic in dic_cambios["FILL"]:
                li_field_value.append((dic["KEY"], dic["VALUE"]))
            if li_field_value:
                self.dbGames.fill(li_field_value)

            # Tercero RENAME_LBL
            for dic in dic_cambios["RENAME"]:
                dcabs[dic["KEY"]] = dic["LABEL"]

            self.dbGames.guardaConfig("dcabs", dcabs)

            # Cuarto REMOVE
            lir = dic_cambios["REMOVE"]
            if len(lir) > 0:
                um = QTUtil2.unMomento(self, _("Working..."))
                lista = [x["KEY"] for x in lir]
                self.dbGames.remove_columns(lista)
                reinit = True
                um.final()

            if reinit:
                self.wb_database.reinit_sinsalvar()  # para que no cree de nuevo al salvar configuración

            else:
                self.dbGames.reset_cache()
                self.grid.refresh()

    def tw_edit_columns(self):
        w = GridEditCols.EditCols(self.grid, self.configuracion, "columns_database")
        if w.exec_():
            self.grid.releerColumnas()

    def readVarsConfig(self):
        showAllways = self.dbGames.recuperaConfig("GRAPHICS_SHOW_ALLWAYS")
        specific = self.dbGames.recuperaConfig("GRAPHICS_SPECIFIC")
        return showAllways, specific

    def graphicBoardReset(self):
        showAllways, specific = self.readVarsConfig()
        fichGraphic = self.dbGames.nom_fichero if specific else None
        self.infoMove.tablero.dbVisual_setFichero(fichGraphic)
        self.infoMove.tablero.dbVisual_setShowAllways(showAllways)

    def tw_dir_show_yes(self):
        self.dbGames.guardaConfig("GRAPHICS_SHOW_ALLWAYS", True)
        self.graphicBoardReset()

    def tw_dir_show_no(self):
        self.dbGames.guardaConfig("GRAPHICS_SHOW_ALLWAYS", False)
        self.graphicBoardReset()

    def tw_locale_yes(self):
        self.dbGames.guardaConfig("GRAPHICS_SPECIFIC", True)
        self.graphicBoardReset()

    def tw_locale_no(self):
        self.dbGames.guardaConfig("GRAPHICS_SPECIFIC", False)
        self.graphicBoardReset()

    def tw_resize_columns(self):
        um = QTUtil2.unMomento(self, _("Resizing"))
        self.grid.resizeColumnsToContents()
        um.final()

    def tw_utilities(self):
        menu = QTVarios.LCMenu(self)
        menu.opcion(self.tw_massive_analysis, _("Mass analysis"), Iconos.Analizar())
        menu.separador()
        menu.opcion(self.tw_polyglot, _("Create a polyglot book"), Iconos.Book())
        menu.separador()
        menu.opcion(self.tw_pack, _("Pack database"), Iconos.Pack())
        resp = menu.lanza()
        if resp:
            resp()

    def tw_uti_tactic(self):

        def rutinaDatos(recno):
            dic = {}
            for clave in self.dbGames.li_fields:
                dic[clave] = self.dbGames.field(recno, clave)
            p = self.dbGames.leePartidaRecno(recno)
            dic["PGN"] = p.pgn()
            dic["PLIES"] = len(p)
            return dic

        liRegistros = self.grid.recnosSeleccionados()
        if len(liRegistros) < 2:
            liRegistros = range(self.dbGames.reccount())

        WDB_Utils.crearTactic(self.procesador, self, liRegistros, rutinaDatos)

    def tw_pack(self):
        um = QTUtil2.unMomento(self)
        self.dbGames.pack()
        um.final()

    def tw_massive_analysis(self):
        liSeleccionadas = self.grid.recnosSeleccionados()
        nSeleccionadas = len(liSeleccionadas)

        alm = PantallaAnalisisParam.paramAnalisisMasivo(self, self.configuracion, nSeleccionadas > 1, siDatabase=True)
        if alm:

            if alm.siVariosSeleccionados:
                nregs = nSeleccionadas
            else:
                nregs = self.dbGames.reccount()

            tmpBP = QTUtil2.BarraProgreso2(self, _("Mass analysis"), formato2="%p%")
            tmpBP.ponTotal(1, nregs)
            tmpBP.ponRotulo(1, _("Game"))
            tmpBP.ponRotulo(2, _("Moves"))
            tmpBP.mostrar()

            ap = Analisis.AnalizaPartida(self.procesador, alm, True)

            for n in range(nregs):

                if tmpBP.is_canceled():
                    break

                tmpBP.pon(1, n + 1)

                if alm.siVariosSeleccionados:
                    n = liSeleccionadas[n]

                game = self.dbGames.leePartidaRecno(n)
                self.grid.goto(n, 0)

                ap.xprocesa(game, tmpBP)

                self.dbGames.guardaPartidaRecno(n, game)

            if not tmpBP.is_canceled():
                ap.terminar(True)

                liCreados = []
                liNoCreados = []

                if alm.tacticblunders:
                    if ap.siTacticBlunders:
                        liCreados.append(alm.tacticblunders)
                    else:
                        liNoCreados.append(alm.tacticblunders)

                for x in (alm.pgnblunders, alm.fnsbrilliancies, alm.pgnbrilliancies):
                    if x:
                        if Util.exist_file(x):
                            liCreados.append(x)
                        else:
                            liNoCreados.append(x)

                if alm.bmtblunders:
                    if ap.si_bmt_blunders:
                        liCreados.append(alm.bmtblunders)
                    else:
                        liNoCreados.append(alm.bmtblunders)
                if alm.bmtbrilliancies:
                    if ap.si_bmt_brilliancies:
                        liCreados.append(alm.bmtbrilliancies)
                    else:
                        liNoCreados.append(alm.bmtbrilliancies)
                if liCreados:
                    WDB_Utils.mensajeEntrenamientos(self, liCreados, liNoCreados)

            else:
                ap.terminar(False)

            tmpBP.cerrar()

    def tw_polyglot(self):
        titulo = self.dbGames.get_name() + ".bin"
        resp = PolyglotImports.export_polyglot_config(self, self.configuracion, titulo)
        if resp is None:
            return
        path_bin, uniform = resp
        resp = PolyglotImports.import_polyglot_config(self, self.configuracion, os.path.basename(path_bin))
        if resp is None:
            return
        plies, st_side, st_results, ru, min_games, min_score, calc_weight, save_score = resp
        db = UtilSQL.DictBig()

        def fsum(keymove, pt):
            num, pts = db.get(keymove, (0, 0))
            num += 1
            pts += pt
            db[keymove] = num, pts

        dltmp = PolyglotImports.ImportarPGNDB(self, titulo)
        dltmp.show()

        ok = PolyglotImports.add_db(self.dbGames, plies, st_results, st_side, ru, time.time, 1.2, dltmp.dispatch, fsum)
        dltmp.close()

        if ok:
            PolyglotImports.create_bin_from_dbbig(self, path_bin, db, min_games, min_score, calc_weight, save_score)

    def tw_exportar_db(self, lista):
        dbpath = QTVarios.select_db(self, self.configuracion, False, True)
        if not dbpath:
            return
        if dbpath == ":n":
            dbpath = new_database(self, self.configuracion)
            if dbpath is None:
                return

        dlTmp = QTVarios.ImportarFicheroDB(self)
        dlTmp.ponExportados()
        dlTmp.show()

        dbn = DBgames.DBgames(dbpath)
        if dbn.allows_duplicates:
            dlTmp.hide_duplicates()
        dbn.appendDB(self.dbGames, lista, dlTmp)

    def tw_exportar_pgn(self, only_selected):
        w = PantallaSavePGN.WSaveVarios(self, self.configuracion)
        if w.exec_():
            ws = PantallaSavePGN.FileSavePGN(self, w.dic_result)
            if ws.open():
                sp = "\r\n" if ws.crlf else "\n"
                pb = QTUtil2.BarraProgreso1(self, _("Saving..."), formato1="%p%")
                pb.mostrar()
                if only_selected:
                    li_sel = self.grid.recnosSeleccionados()
                else:
                    li_sel = list(range(self.dbGames.reccount()))
                pb.ponTotal(len(li_sel))
                for n, recno in enumerate(li_sel):
                    pb.pon(n)
                    pgn, result = self.dbGames.leePGNRecno(recno, sp)
                    if pb.is_canceled():
                        break
                    if n > 0 or not ws.is_new:
                        ws.write(sp + sp)
                    if result in ("*", "1-0", "0-1", "1/2-1/2"):
                        if not pgn.endswith(result):
                            pgn += " " + result
                    ws.write(pgn + sp)

                pb.close()
                ws.close()

    def tw_importar_PGN(self):
        files = QTVarios.select_pgns(self)
        if not files:
            return None

        dlTmp = QTVarios.ImportarFicheroPGN(self)
        if self.dbGames.allows_duplicates:
            dlTmp.hide_duplicates()
        dlTmp.show()
        self.dbGames.leerPGNs(files, dlTmp)

        self.rehaz_columnas()
        self.actualiza(True)
        if self.wsummary:
            self.wsummary.reset()

    def tw_importar_DB(self):
        path = QTVarios.select_db(self, self.configuracion, False, False)
        if not path:
            return None

        dlTmp = QTVarios.ImportarFicheroDB(self)
        if self.dbGames.allows_duplicates:
            dlTmp.hide_duplicates()
        dlTmp.show()

        dbn = DBgames.DBgames(path)
        self.dbGames.appendDB(dbn, range(dbn.all_reccount()), dlTmp)

        self.rehaz_columnas()
        self.actualiza(True)
        if self.wsummary:
            self.wsummary.reset()


class WOptionsDatabase(QtWidgets.QDialog):
    def __init__(self, owner, configuracion, dic_data):
        super(WOptionsDatabase, self).__init__(owner)

        self.new = len(dic_data) == 0

        self.dic_data = dic_data
        self.dic_data_resp = None

        def d_str(key):
            return dic_data.get(key, "")

        def d_true(key):
            return dic_data.get(key, True)

        def d_false(key):
            return dic_data.get(key, False)

        title = _("New database") if len(dic_data) == 0 else "%s: %s" % (_("Database"), d_str("NAME"))
        self.setWindowTitle(title)
        self.setWindowIcon(Iconos.DatabaseMas())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self.configuracion = configuracion
        self.resultado = None

        valid_rx = r'^[^<>:;,?"*|/\\]+'

        lb_name = Controles.LB2P(self, _("Name"))
        self.ed_name = Controles.ED(self, d_str("NAME")).controlrx(valid_rx)

        ly_name = Colocacion.H().control(lb_name).control(self.ed_name)

        folder = os.path.dirname(Util.relative_path(d_str("FILEPATH")))
        folder = folder[len(configuracion.folder_databases()):]
        if folder.strip():
            folder = folder.strip(os.sep)
            li = folder.split(os.sep)
            nli = len(li)
            group = li[0]
            subgroup1 = li[1] if nli > 1 else ""
            subgroup2 = li[2] if nli > 2 else ""
        else:
            group = ""
            subgroup1 = ""
            subgroup2 = ""

        lb_group = Controles.LB2P(self, _("Group"))
        self.ed_group = Controles.ED(self, group).controlrx(valid_rx)
        self.bt_group = (
            Controles.PB(self, "", self.mira_group).ponIcono(Iconos.BuscarC(), 16).ponToolTip(_("Group lists"))
        )
        ly_group = (
            Colocacion.H().control(lb_group).control(self.ed_group).espacio(-10).control(self.bt_group).relleno(1)
        )

        lb_subgroup_l1 = Controles.LB2P(self, _("Subgroup"))
        self.ed_subgroup_l1 = Controles.ED(self, subgroup1).controlrx(valid_rx)
        self.bt_subgroup_l1 = (
            Controles.PB(self, "", self.mira_subgroup_l1).ponIcono(Iconos.BuscarC(), 16).ponToolTip(_("Group lists"))
        )
        ly_subgroup_l1 = (
            Colocacion.H()
            .espacio(40)
            .control(lb_subgroup_l1)
            .control(self.ed_subgroup_l1)
            .espacio(-10)
            .control(self.bt_subgroup_l1)
            .relleno(1)
        )

        lb_subgroup_l2 = Controles.LB2P(self, "%s → %s" % (_("Subgroup"), _("Subgroup")))
        self.ed_subgroup_l2 = Controles.ED(self, subgroup2).controlrx(valid_rx)
        self.bt_subgroup_l2 = (
            Controles.PB(self, "", self.mira_subgroup_l2).ponIcono(Iconos.BuscarC(), 16).ponToolTip(_("Group lists"))
        )
        ly_subgroup_l2 = (
            Colocacion.H()
            .espacio(40)
            .control(lb_subgroup_l2)
            .control(self.ed_subgroup_l2)
            .espacio(-10)
            .control(self.bt_subgroup_l2)
            .relleno(1)
        )

        x1 = -8
        ly_group = Colocacion.V().otro(ly_group).espacio(x1).otro(ly_subgroup_l1).espacio(x1).otro(ly_subgroup_l2)

        gb_group = Controles.GB(self, "%s (%s)" % (_("Group"), "optional"), ly_group)

        lb_summary = Controles.LB2P(self, _("Summary depth (0=disable)"))
        self.sb_summary = Controles.SB(self, dic_data.get("SUMMARY_DEPTH", 12), 0, 999)
        ly_summary = Colocacion.H().control(lb_summary).control(self.sb_summary).relleno(1)

        self.external_folder = d_str("EXTERNAL_FOLDER")
        lb_external = Controles.LB2P(self, _("Store in an external folder"))
        self.bt_external = Controles.PB(self, self.external_folder, self.select_external, False)
        self.bt_external.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        )
        ly_external = Colocacion.H().control(lb_external).control(self.bt_external)

        self.chb_complete = Controles.CHB(self, _("Allow complete games"), d_true("ALLOWS_COMPLETE_GAMES"))
        self.chb_positions = Controles.CHB(self, _("Allow positions"), d_true("ALLOWS_POSITIONS"))
        self.chb_duplicate = Controles.CHB(self, _("Allow duplicates"), d_false("ALLOWS_DUPLICATES"))
        self.chb_zeromoves = Controles.CHB(self, _("Allow without moves"), d_false("ALLOWS_ZERO_MOVES"))
        ly_res = (
            Colocacion.V()
            .controlc(self.chb_complete)
            .controlc(self.chb_positions)
            .controlc(self.chb_duplicate)
            .controlc(self.chb_zeromoves)
        )

        gb_restrictions = Controles.GB(self, _("Import restrictions"), ly_res)

        li_acciones = [
            (_("Save"), Iconos.Aceptar(), self.save),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
        ]
        self.tb = QTVarios.LCTB(self, li_acciones)

        x0 = 16

        layout = Colocacion.V().control(self.tb).espacio(x0)
        layout.otro(ly_name).espacio(x0).control(gb_group).espacio(x0)
        layout.otro(ly_summary).espacio(x0)
        layout.otro(ly_external).espacio(x0)
        layout.control(gb_restrictions)
        layout.margen(9)

        self.setLayout(layout)

        self.ed_name.setFocus()

    def select_external(self):
        folder = QTUtil2.leeCarpeta(self, self.external_folder, _("Use an external folder"))
        if folder:
            folder = os.path.realpath(folder)
            default = os.path.realpath(self.configuracion.folder_databases())
            if folder.startswith(default):
                QTUtil2.message_error(
                    self, "%s:\n%s\n\n%s" % (_("The folder must be outside the default folder"), default, folder)
                )
                return
            self.external_folder = folder

        self.bt_external.ponTexto(self.external_folder)

    def menu_groups(self, carpeta):
        if Util.exist_folder(carpeta):
            with os.scandir(carpeta) as it:
                li = [entry.name for entry in it if entry.is_dir()]
            if li:
                rondo = QTVarios.rondoPuntos()
                menu = QTVarios.LCMenu(self)
                for direc in li:
                    menu.opcion(direc, direc, rondo.otro())
                return menu.lanza()

    def mira_group(self):
        resp = self.menu_groups(self.configuracion.folder_databases())
        if resp:
            self.ed_group.ponTexto(resp)

    def mira_subgroup_l1(self):
        group = self.ed_group.texto().strip()
        if group:
            carpeta = os.path.join(self.configuracion.folder_databases(), group)
            resp = self.menu_groups(carpeta)
            if resp:
                self.ed_subgroup_l1.ponTexto(resp)

    def mira_subgroup_l2(self):
        group = self.ed_group.texto().strip()
        if group:
            subgroup = self.ed_subgroup_l1.texto().strip()
            if subgroup:
                carpeta = os.path.join(self.configuracion.folder_databases(), group, subgroup)
                resp = self.menu_groups(carpeta)
                if resp:
                    self.ed_subgroup_l2.ponTexto(resp)

    def save(self):
        name = self.ed_name.texto().strip()
        if not name:
            QTUtil2.message_error(self, _("You must indicate a name"))
            return

        folder = self.configuracion.folder_databases()
        group = self.ed_group.texto()
        if group:
            folder = os.path.join(folder, group)
            subgroup_l1 = self.ed_subgroup_l1.texto()
            if subgroup_l1:
                folder = os.path.join(folder, subgroup_l1)
                subgroup_l2 = self.ed_subgroup_l2.texto()
                if subgroup_l2:
                    folder = os.path.join(folder, subgroup_l2)
        if not Util.exist_folder(folder):
            try:
                os.makedirs(folder, True)
            except:
                QTUtil2.message_error(self, "%s\n%s" % (_("Unable to create folder"), folder))
                return

        filename = "%s.lcdb" % name
        if self.external_folder:
            filepath = os.path.join(self.external_folder, filename)
        else:
            filepath = os.path.join(folder, filename)

        test_exist = self.new
        if not self.new:
            previous = self.dic_data["FILEPATH"]
            test_exist = not Util.same_path(previous, filepath)

        if test_exist and Util.exist_file(filepath):
            QTUtil2.message_error(self, "%s\n%s" % (_("This database already exists."), filepath))
            return

        if self.external_folder:
            file = os.path.join(folder, "%s.lcdblink" % name)
            with open(file, "wt") as q:
                q.write(filepath)
        else:
            file = filepath

        self.dic_data_resp = {
            "ALLOWS_DUPLICATES": self.chb_duplicate.valor(),
            "ALLOWS_POSITIONS": self.chb_positions.valor(),
            "ALLOWS_COMPLETE_GAMES": self.chb_complete.valor(),
            "ALLOWS_ZERO_MOVES": self.chb_zeromoves.valor(),
            "SUMMARY_DEPTH": self.sb_summary.valor(),
        }

        db = DBgames.DBgames(filepath)
        for key, value in self.dic_data_resp.items():
            db.guardaConfig(key, value)
        db.close()

        self.dic_data_resp["FILEPATH"] = file
        self.dic_data_resp["EXTERNAL_FOLDER"] = self.external_folder

        self.accept()


def new_database(owner, configuracion):
    dic_data = {}
    w = WOptionsDatabase(owner, configuracion, dic_data)
    if w.exec_():
        return w.dic_data_resp["FILEPATH"]
    else:
        return None


def modify_database(owner, configuracion, db):
    dic_data = {
        "NAME": db.get_name(),
        "FILEPATH": db.nom_fichero,
        "EXTERNAL_FOLDER": db.external_folder,
        "SUMMARY_DEPTH": db.depthStat(),
        "ALLOWS_DUPLICATES": db.recuperaConfig("ALLOWS_DUPLICATES", False),
        "ALLOWS_POSITIONS": db.recuperaConfig("ALLOWS_POSITIONS", True),
        "ALLOWS_COMPLETE_GAMES": db.recuperaConfig("ALLOWS_COMPLETE_GAMES", True),
        "ALLOWS_ZERO_MOVES": db.recuperaConfig("ALLOWS_ZERO_MOVES", False),
    }
    w = WOptionsDatabase(owner, configuracion, dic_data)
    if w.exec_():
        return w.dic_data_resp
    else:
        return None


class WTags(QTVarios.WDialogo):
    def __init__(self, owner, dbgames: [DBgames.DBgames]):
        QTVarios.WDialogo.__init__(self, owner, _("Tags"), Iconos.Tags(), "tagsedition")
        self.dbgames = dbgames
        self.dic_cambios = None

        dcabs = dbgames.recuperaConfig("dcabs", {})
        li_basetags = dbgames.li_tags()
        if li_basetags[0] == "PLYCOUNT":
            del li_basetags[0]

        self.li_data = []
        for tag in li_basetags:
            dic = {
                "KEY": tag,
                "LABEL": dcabs.get(tag, Util.primera_mayuscula(tag)),
                "ACTION": "-",
                "VALUE": "",
                "NEW": False,
            }
            dic["PREV_LABEL"] = dic["KEY"]
            self.li_data.append(dic)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("KEY", _("Key"), 80, centered=True)
        o_columns.nueva("LABEL", _("PGN Label"), 80, centered=True, edicion=Delegados.LineaTexto(rx="[A-Za-z_0-9]*"))

        self.fill_column = _("Fill column with value")
        self.remove_column = _("Remove column")
        self.nothing = "-"
        self.li_actions = [self.nothing, self.fill_column, self.remove_column]
        o_columns.nueva("ACTION", _("Action"), 80, centered=True, edicion=Delegados.ComboBox(self.li_actions))
        o_columns.nueva("VALUE", self.fill_column, 200, edicion=Delegados.LineaTextoUTF8())
        self.gtags = Grid.Grid(self, o_columns, siEditable=True)

        li_acciones = (
            (_("Save"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
            (_("New"), Iconos.Nuevo(), self.new),
            None,
        )
        tb = QTVarios.LCTB(self, li_acciones)

        ly = Colocacion.V().control(tb).control(self.gtags).margen(4)

        self.setLayout(ly)

        self.register_grid(self.gtags)
        self.restore_video(anchoDefecto=self.gtags.anchoColumnas() + 20, altoDefecto=400)

        self.gtags.gotop()

    def grid_num_datos(self, grid):
        return len(self.li_data)

    def grid_dato(self, grid, fila, ocol):
        return self.li_data[fila][ocol.clave]

    def grid_setvalue(self, grid, fila, oColumna, value):
        clave = oColumna.clave
        dic = self.li_data[fila]
        value = value.strip()
        if clave == "VALUE" and value:
            dic["ACTION"] = self.fill_column
        elif clave == "ACTION" and value != self.fill_column:
            dic["VALUE"] = ""
        elif clave == "LABEL":
            new = dic["NEW"]
            if new:
                newkey = value.upper()
                for xfila, xdic in enumerate(self.li_data):
                    if xfila != fila:
                        if xdic["KEY"] == newkey or xdic["PREV_LABEL"] == newkey:
                            QTUtil2.message_error(self, _("This tag is repeated"))
                            return
                dic["KEY"] = newkey
                dic["PREV_LABEL"] = newkey
            else:
                if len(value) == 0:
                    return
        dic[clave] = value
        self.gtags.refresh()

    def aceptar(self):
        dic_cambios = {"CREATE": [], "RENAME": [], "FILL": [], "REMOVE": []}
        for dic in self.li_data:
            if dic["NEW"]:
                key = dic["KEY"]
                if len(key) == 0 or dic["ACTION"] == self.remove_column:
                    continue
                dic_cambios["CREATE"].append(dic)
            elif dic["LABEL"] != dic["PREV_LABEL"]:
                dic_cambios["RENAME"].append(dic)
            if dic["ACTION"] == self.remove_column:
                dic_cambios["REMOVE"].append(dic)
            elif dic["ACTION"] == self.fill_column:
                dic_cambios["FILL"].append(dic)

        self.dic_cambios = dic_cambios
        self.accept()

    def new(self):
        dic = {"KEY": "", "PREV_LABEL": "", "LABEL": "", "ACTION": "-", "VALUE": "", "NEW": True}
        self.li_data.append(dic)
        self.gtags.refresh()
