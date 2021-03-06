from PySide2 import QtWidgets, QtCore

from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTVarios
from Code.Databases import WDB_Games, WDB_Summary, WDB_Players, WDB_InfoMove, DBgames


class WBDatabase(QTVarios.WDialogo):
    def __init__(self, wParent, procesador, file_database, temporary, si_select):
        self.temporary = temporary
        icono = Iconos.Database()
        extparam = "databases"
        titulo = _("Temporary database") if self.temporary else _("Database")
        QTVarios.WDialogo.__init__(self, wParent, titulo, icono, extparam)
        self.owner = wParent

        self.procesador = procesador
        self.configuracion = procesador.configuracion

        self.reiniciar = False  # lo usamos para cambiar de database

        self.dbGames = DBgames.DBgames(file_database)

        dicVideo = self.restore_dicvideo()

        siSummary = not si_select

        self.wplayer = WDB_Players.WPlayer(procesador, self, self.dbGames)
        self.wplayer_active = False

        if siSummary:
            self.wsummary = WDB_Summary.WSummary(procesador, self, self.dbGames, siMoves=False)
            self.register_grid(self.wsummary.grid)

        else:
            self.wsummary = None

        self.wgames = WDB_Games.WGames(procesador, self, self.dbGames, self.wsummary, si_select)

        self.ultFocus = None

        self.tab = Controles.Tab()
        self.tab.nuevaTab(self.wgames, _("Games"))
        if siSummary:
            self.tab.nuevaTab(self.wsummary, _("Summary"))
            self.tab.dispatchChange(self.tabChanged)
        if not si_select:
            self.tab.nuevaTab(self.wplayer, _("Players"))
        self.tab.ponTipoLetra(puntos=procesador.configuracion.x_tb_fontpoints)

        if self.owner and not self.temporary:
            liAccionesWork = [
                (_("Select other"), Iconos.Database(), self.tw_select_other),
                # (_("Create new"), Iconos.DatabaseMas(), self.tw_create_new),
            ]
            self.tbWork = QTVarios.LCTB(self, liAccionesWork, tamIcon=20)
            self.tbWork.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
            self.tab.setCornerWidget(self.tbWork)

        w = QtWidgets.QWidget(self)
        layoutv = Colocacion.V().control(self.tab).margen(4)
        w.setLayout(layoutv)

        self.infoMove = WDB_InfoMove.WInfomove(self)

        self.splitter = splitter = QtWidgets.QSplitter()
        splitter.addWidget(w)
        splitter.addWidget(self.infoMove)

        layout = Colocacion.H().control(splitter).margen(0)
        self.setLayout(layout)

        self.restore_video(anchoDefecto=1200, altoDefecto=600)
        if not dicVideo:
            dicVideo = {"SPLITTER": [800, 380], "TREE_1": 25, "TREE_2": 25, "TREE_3": 50, "TREE_4": 661}

        if not ("SPLITTER" in dicVideo):
            ancho = self.width()
            ancho_tablero = self.infoMove.tablero.width()
            sz = [ancho - ancho_tablero, ancho_tablero]
        else:
            sz = dicVideo["SPLITTER"]
        self.splitter.setSizes(sz)

        dic_grid = self.dbGames.recuperaConfig("dic_grid")
        if not dic_grid:
            key = "databases_columns_default"
            dic_grid = self.configuracion.leeVariables(key)
        if dic_grid:
            self.wgames.grid.restore_video(dic_grid)
            self.wgames.grid.releerColumnas()

        self.inicializa()

    def closeEvent(self, event):
        self.tw_terminar()

    def tw_terminar(self):
        self.wgames.tw_terminar()
        self.salvar()
        self.accept()

    def tw_aceptar(self):
        self.game, recno = self.wgames.current_game()
        self.dbGames.close()
        if self.game:
            self.accept()
        else:
            self.reject()

    def tw_cancelar(self):
        self.dbGames.close()
        self.game = None
        self.reject()

    def tw_select_other(self):
        resp = QTVarios.select_db(self, self.configuracion, False, True)
        if resp:
            if resp == ":n":
                dbpath = WDB_Games.new_database(self, self.configuracion)
                if dbpath is not None:
                    self.configuracion.set_last_database(dbpath)
                    self.reinit()
            else:
                self.configuracion.set_last_database(resp)
                self.reinit()

    def listaGamesSelected(self, no1=False):
        return self.wgames.listaSelected(no1)

    def tabChanged(self, ntab):
        QtWidgets.QApplication.processEvents()
        tablero = self.infoMove.tablero
        tablero.disable_all()
        if ntab == 0:
            self.wgames.actualiza()
        else:
            self.wsummary.gridActualiza()

    def inicializa(self):
        self.setWindowTitle(self.dbGames.rotulo())
        self.wgames.setdbGames(self.dbGames)
        self.wgames.setInfoMove(self.infoMove)
        self.wplayer.setInfoMove(self.infoMove)
        self.wplayer.setdbGames(self.dbGames)
        if self.wsummary:
            self.wsummary.setInfoMove(self.infoMove)
            self.wsummary.setdbGames(self.dbGames)
            self.wsummary.actualizaPV("")
        self.wgames.actualiza(True)
        if self.temporary:
            self.wgames.adjustSize()

    def salvar(self):
        dic_extended = {"SPLITTER": self.splitter.sizes()}

        self.save_video(dic_extended)

        dic = {}
        self.wgames.grid.save_video(dic)
        self.dbGames.guardaConfig("dic_grid", dic)

    def reinit(self):
        self.salvar()
        self.dbGames.close()
        self.reiniciar = True
        self.accept()

    def reinit_sinsalvar(self):
        self.dbGames.close()
        self.reiniciar = True
        self.accept()
