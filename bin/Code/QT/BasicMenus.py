import Code
from Code import Albums
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Grid
from Code.QT import QTVarios
from Code.QT import Iconos
from Code.QT import Delegados

from Code.Constantes import MENU_PLAY_ANY_ENGINE, MENU_PLAY_YOUNG_PLAYERS


class SaveMenu:
    def __init__(self, dic_datos, launcher, rotulo=None, icono=None):
        self.liopciones = []
        self.rotulo = rotulo
        self.icono = icono
        self.dic_data = {} if dic_datos is None else dic_datos
        self.launcher = launcher

    def opcion(self, key, rotulo, icono, is_disabled=None):
        self.liopciones.append(("opc", (key, rotulo, icono, is_disabled)))
        self.dic_data[key] = (self.launcher, rotulo, icono, is_disabled)

    def separador(self):
        self.liopciones.append(("sep", None))

    def submenu(self, rotulo, icono):
        sm = SaveMenu(self.dic_data, self.launcher, rotulo, icono)
        self.liopciones.append(("sub", sm))
        return sm

    def xmenu(self, menu):
        for tipo, datos in self.liopciones:
            if tipo == "opc":
                (key, rotulo, icono, is_disabled) = datos
                menu.opcion(key, rotulo, icono, is_disabled=is_disabled)
            elif tipo == "sep":
                menu.separador()
            elif tipo == "sub":
                sm = datos
                submenu = menu.submenu(sm.rotulo, sm.icono)
                sm.xmenu(submenu)

    def lanza(self, procesador):
        menu = QTVarios.LCMenu(procesador.main_window)
        self.xmenu(menu)
        return menu.lanza()


def menu_tools_savemenu(procesador, dic_data=None):
    savemenu = SaveMenu(dic_data, procesador.menuTools_run)

    savemenu.opcion("juega_solo", _("Create your own game"), Iconos.JuegaSolo())
    savemenu.separador()

    menu_database = savemenu.submenu(_("Databases"), Iconos.Database())
    QTVarios.menuDB(menu_database, procesador.configuracion, True, indicador_previo="dbase_R_")
    menu_database.separador()
    submenu_database = menu_database.submenu(_("Maintenance"), Iconos.DatabaseMaintenance())
    submenu_database.opcion("dbase_N", _("Create new database"), Iconos.DatabaseMas())
    submenu_database.separador()
    submenu_database.opcion("dbase_D", _("Delete a database"), Iconos.DatabaseDelete())
    if Code.isWindows:
        submenu_database.separador()
        submenu_database.opcion("dbase_M", _("Direct maintenance"), Iconos.Configurar())
    savemenu.separador()

    menu1 = savemenu.submenu(_("Openings"), Iconos.Aperturas())
    menu1.opcion("openings", _("Opening lines"), Iconos.OpeningLines())
    menu1.separador()
    menu1.opcion("aperturaspers", _("Custom openings"), Iconos.Apertura())
    savemenu.separador()

    menu1 = savemenu.submenu(_("Engines"), Iconos.Motores())
    menu1.opcion("torneos", _("Tournaments between engines"), Iconos.Torneos())
    menu1.separador()
    menu1.opcion("sts", _("STS: Strategic Test Suite"), Iconos.STS())
    menu1.separador()
    menu1.opcion("motores", _("External engines"), Iconos.Motores())
    menu1.separador()
    menu1.opcion("kibitzers", _("Kibitzers"), Iconos.Kibitzer())
    savemenu.separador()

    menu1 = savemenu.submenu(_("PGN"), Iconos.PGN())
    menu1.opcion("pgn", _("Read PGN"), Iconos.Fichero())
    menu1.separador()
    menu1.opcion("pgn_paste", _("Paste PGN"), Iconos.Pegar())
    menu1.separador()
    menu1.opcion("manual_save", _("Save positions to FNS/PGN"), Iconos.ManualSave())
    menu1.separador()
    menu1.opcion("miniatura", _("Miniature of the day"), Iconos.Miniatura())
    menu1.separador()
    savemenu.separador()

    savemenu.opcion("polyglot", _("Polyglot book factory"), Iconos.FactoryPolyglot())

    return savemenu


def menu_tools(procesador):
    savemenu = menu_tools_savemenu(procesador)
    return savemenu.lanza(procesador)


def menuplay_youngs(menu1):
    for name, trans, ico in QTVarios.list_irina():
        menu1.opcion(("person", name), trans, ico)
    menu1.separador()

    menu2 = menu1.submenu(_("Albums of animals"), Iconos.Penguin())
    albumes = Albums.AlbumesAnimales()
    dic = albumes.list_menu()
    anterior = None
    for animal in dic:
        is_disabled = False
        if anterior and not dic[anterior]:
            is_disabled = True
        menu2.opcion(("animales", animal), _F(animal), Iconos.icono(animal), is_disabled=is_disabled)
        anterior = animal
    menu1.separador()

    menu2 = menu1.submenu(_("Albums of vehicles"), Iconos.Wheel())
    albumes = Albums.AlbumesVehicles()
    dic = albumes.list_menu()
    anterior = None
    for character in dic:
        is_disabled = False
        if anterior and not dic[anterior]:
            is_disabled = True
        menu2.opcion(("vehicles", character), _F(character), Iconos.icono(character), is_disabled=is_disabled)
        anterior = character


def menuplay_savemenu(procesador, dic_data=None):
    savemenu = SaveMenu(dic_data, procesador.menuPlay_run)

    savemenu.opcion(("free", None), _("Play against an engine"), Iconos.Libre())
    savemenu.separador()

    # Principiantes ----------------------------------------------------------------------------------------
    menu1 = savemenu.submenu(_("Opponents for young players"), Iconos.RivalesMP())
    menuplay_youngs(menu1)

    return savemenu


def menuplay(procesador, extended=False):
    if not extended:
        configuracion = procesador.configuracion
        opcion = configuracion.x_menu_play
        if opcion == MENU_PLAY_ANY_ENGINE:
            return "free", None
        elif opcion == MENU_PLAY_YOUNG_PLAYERS:
            menu = QTVarios.LCMenu(procesador.main_window)
            menuplay_youngs(menu)
            return menu.lanza()

    savemenu = menuplay_savemenu(procesador)
    return savemenu.lanza(procesador)


def menucompete_savemenu(procesador, dic_data=None):
    savemenu = SaveMenu(dic_data, procesador.menucompete_run)
    savemenu.opcion(("competition", None), _("Competition with tutor"), Iconos.NuevaPartida())
    savemenu.separador()

    submenu = savemenu.submenu(_("Elo-Rating"), Iconos.Elo())
    submenu.opcion(("lucaselo", 0), "%s (%d)" % (_("Lucas-Elo"), procesador.configuracion.x_elo), Iconos.Elo())
    submenu.separador()
    submenu.opcion(("micelo", 0), "%s (%d)" % (_("Tourney-Elo"), procesador.configuracion.x_michelo), Iconos.EloTimed())
    submenu.separador()
    fics = procesador.configuracion.x_fics
    menuf = submenu.submenu("%s (%d)" % (_("Fics-Elo"), fics), Iconos.Fics())
    rp = QTVarios.rondoPuntos()
    for elo in range(900, 2800, 100):
        if (elo == 900) or (0 <= (elo + 99 - fics) <= 400 or 0 <= (fics - elo) <= 400):
            menuf.opcion(("fics", elo / 100), "%d-%d" % (elo, elo + 99), rp.otro())
    submenu.separador()
    fide = procesador.configuracion.x_fide
    menuf = submenu.submenu("%s (%d)" % (_("Fide-Elo"), fide), Iconos.Fide())
    for elo in range(1500, 2700, 100):
        if (elo == 1500) or (0 <= (elo + 99 - fide) <= 400 or 0 <= (fide - elo) <= 400):
            menuf.opcion(("fide", elo / 100), "%d-%d" % (elo, elo + 99), rp.otro())
    lichess = procesador.configuracion.x_lichess
    submenu.separador()
    menuf = submenu.submenu("%s (%d)" % (_("Lichess-Elo"), lichess), Iconos.Lichess())
    rp = QTVarios.rondoPuntos()
    for elo in range(800, 2700, 100):
        if (elo == 800) or (0 <= (elo + 99 - lichess) <= 400 or 0 <= (lichess - elo) <= 400):
            menuf.opcion(("lichess", elo / 100), "%d-%d" % (elo, elo + 99), rp.otro())
    savemenu.separador()
    submenu = savemenu.submenu(_("Singular moves"), Iconos.Singular())
    submenu.opcion(("strenght101", 0), _("Calculate your strength"), Iconos.Strength())
    submenu.separador()
    submenu.opcion(("challenge101", 0), _("Challenge 101"), Iconos.Wheel())

    return savemenu


def menucompete(procesador):
    savemenu = menucompete_savemenu(procesador)
    return savemenu.lanza(procesador)


class WAtajos(QTVarios.WDialogo):
    def __init__(self, procesador, dic_data):
        entrenamientos = procesador.entrenamientos
        entrenamientos.comprueba()
        self.entrenamientos = entrenamientos
        self.procesador = procesador
        self.li_favoritos = self.procesador.configuracion.get_favoritos()
        self.dic_data = dic_data

        QTVarios.WDialogo.__init__(self, self.procesador.main_window, _("Shortcuts"), Iconos.Atajos(), "atajos")

        li_acciones = [
            (_("Close"), Iconos.MainMenu(), self.terminar),
            None,
            ("+" + _("Play"), Iconos.Libre(), self.masplay),
            ("+" + _("Train"), Iconos.Entrenamiento(), self.masentrenamiento),
            ("+" + _("Compete"), Iconos.NuevaPartida(), self.mascompete),
            ("+" + _("Tools"), Iconos.Tools(), self.mastools),
            None,
            (_("Remove"), Iconos.Borrar(), self.borrar),
            None,
            (_("Up"), Iconos.Arriba(), self.arriba),
            (_("Down"), Iconos.Abajo(), self.abajo),
            None,
        ]
        tb = Controles.TBrutina(self, li_acciones, puntos=procesador.configuracion.x_tb_fontpoints)

        # Lista
        o_columnas = Columnas.ListaColumnas()
        o_columnas.nueva("OPCION", _("Option"), 300)
        o_columnas.nueva("LABEL", _("Label"), 300, edicion=Delegados.LineaTextoUTF8(siPassword=False))

        self.grid = Grid.Grid(self, o_columnas, siSelecFilas=True, siEditable=True)
        self.grid.setMinimumWidth(self.grid.anchoColumnas() + 20)
        f = Controles.TipoLetra(puntos=10, peso=75)
        self.grid.ponFuente(f)

        # Layout
        layout = Colocacion.V().control(tb).control(self.grid).relleno().margen(3)
        self.setLayout(layout)

        self.restore_video(siTam=True)

        self.grid.gotop()

    def terminar(self):
        self.save_video()
        self.accept()

    def masplay(self):
        self.nuevo(menuplay(self.procesador, extended=True))

    def mascompete(self):
        self.nuevo(menucompete(self.procesador))

    def masentrenamiento(self):
        self.nuevo(self.entrenamientos.menu.lanza())

    def mastools(self):
        self.nuevo(menu_tools(self.procesador))

    def grid_num_datos(self, grid):
        return len(self.li_favoritos)

    def grid_dato(self, grid, fila, oColumna):
        dic = self.li_favoritos[fila]
        opcion = dic["OPCION"]
        if opcion in self.dic_data:
            menu_run, name, icono, is_disabled = self.dic_data[opcion]
        else:
            name = "???"
        return dic.get("LABEL", name) if oColumna.clave == "LABEL" else name

    def grid_setvalue(self, grid, fila, oColumna, valor):  # ? necesario al haber delegados
        dic = self.li_favoritos[fila]
        dato = self.dic_data.get(dic["OPCION"], None)
        if dato is not None:
            if valor:
                dic["LABEL"] = valor.strip()
            else:
                if "LABEL" in dic:
                    del dic["LABEL"]

            self.graba(fila)

    def graba(self, fila):
        self.procesador.configuracion.save_favoritos(self.li_favoritos)
        self.grid.refresh()
        if fila >= len(self.li_favoritos):
            fila = len(self.li_favoritos) - 1
        self.grid.goto(fila, 0)

    def nuevo(self, resp):
        if resp:
            resp = {"OPCION": resp}
            fila = self.grid.recno()
            tam = len(self.li_favoritos)
            if fila < tam - 1:
                fila += 1
                self.li_favoritos.insert(0, resp)
            else:
                self.li_favoritos.append(resp)
                fila = len(self.li_favoritos) - 1
            self.graba(fila)

    def borrar(self):
        fila = self.grid.recno()
        if fila >= 0:
            del self.li_favoritos[fila]
            self.graba(fila)

    def arriba(self):
        fila = self.grid.recno()
        if fila >= 1:
            self.li_favoritos[fila], self.li_favoritos[fila - 1] = self.li_favoritos[fila - 1], self.li_favoritos[fila]
            self.graba(fila - 1)

    def abajo(self):
        fila = self.grid.recno()
        if fila < len(self.li_favoritos) - 1:
            self.li_favoritos[fila], self.li_favoritos[fila + 1] = self.li_favoritos[fila + 1], self.li_favoritos[fila]
            self.graba(fila + 1)


def atajos(procesador):
    procesador.entrenamientos.comprueba()
    dic_data = procesador.entrenamientos.dicMenu
    menuplay_savemenu(procesador, dic_data)
    menucompete_savemenu(procesador, dic_data)
    menu_tools_savemenu(procesador, dic_data)
    li_favoritos = procesador.configuracion.get_favoritos()

    menu = QTVarios.LCMenu(procesador.main_window)
    nx = 1
    for dic in li_favoritos:
        key = dic["OPCION"]
        if key in dic_data:
            launcher, rotulo, icono, is_disabled = dic_data[key]
            label = dic.get("LABEL", rotulo)
            if nx <= 9:
                label += "  [%s-%d]" % (_("Alt"), nx)
            menu.opcion(key, label, icono, is_disabled)
            nx += 1
            menu.separador()
    menu.separador()
    menu.opcion("ed_atajos", _("Add new shortcuts"), Iconos.Mas())
    resp = menu.lanza()
    if resp == "ed_atajos":
        w = WAtajos(procesador, dic_data)
        w.exec_()
    elif resp is not None and resp in dic_data:
        launcher, rotulo, icono, is_disabled = dic_data[resp]
        launcher(resp)


def atajosALT(procesador, num):
    procesador.entrenamientos.comprueba()
    dic_data = procesador.entrenamientos.dicMenu
    menuplay_savemenu(procesador, dic_data)
    menucompete_savemenu(procesador, dic_data)
    menu_tools_savemenu(procesador, dic_data)
    li_favoritos = procesador.configuracion.get_favoritos()

    nx = 1
    for dic in li_favoritos:
        key = dic["OPCION"]
        if key in dic_data:
            launcher, rotulo, icono, is_disabled = dic_data[key]
            if nx == num:
                launcher(key)
                return
            nx += 1


def menuInformacion(procesador):
    menu = QTVarios.LCMenu(procesador.main_window)

    menu.opcion("docs", _("Documents"), Iconos.Ayuda())
    menu.separador()
    menu.opcion("web", _("Homepage"), Iconos.Web())
    menu.separador()
    menu.opcion("blog", "Fresh news", Iconos.Blog())
    menu.separador()
    menu.opcion("mail", _("Contact") + " (%s)" % "lukasmonk@gmail.com", Iconos.Mail())
    menu.separador()
    if procesador.configuracion.is_main:
        menu.opcion("actualiza", _("Search for updates"), Iconos.Actualiza())
        menu.separador()

    menu.opcion("acercade", _("About"), Iconos.Aplicacion64())

    return menu.lanza()
