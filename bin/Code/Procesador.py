import os
import random
import sys
import webbrowser

import Code
from Code import Util
from Code import AperturasStd
from Code import Routes
from Code import Update
from Code.Engines import EngineManager, WEngines, PlayAgainstEngine, GestorPlayAgainstEngine
from Code.Constantes import *
from Code import Albums
from Code import CPU
from Code import Configuracion

# Added by GON
from Code import DGT
# ------------

from Code import Position
from Code import Trainings
from Code import GestorAlbum
from Code import GestorElo
from Code import GestorEntPos
from Code import GestorEverest
from Code import GestorFideFics
from Code import GestorMateMap
from Code import GestorMicElo
from Code import GestorCompeticion
from Code import GestorOpeningLines
from Code import GestorPerson
from Code import GestorRoutes
from Code import GestorSingularM
from Code import GestorSolo
from Code import GestorPartida
from Code import Presentacion
from Code import GestorWashing
from Code import GestorPlayGame
from Code import GestorAnotar
from Code import Adjourns
from Code.QT import WCompetitionWithTutor, BasicMenus
from Code.QT import Iconos
from Code.QT import About
from Code.QT import Pantalla
from Code.QT import PantallaAlbumes
from Code.QT import PantallaAnotar
from Code.Openings import PantallaOpenings, PantallaOpeningLine, PantallaOpeningLines, OpeningLines
from Code.QT import PantallaBMT
from Code.QT import PantallaColores
from Code.QT import PantallaConfig
from Code.QT import PantallaEverest
from Code.QT import PantallaRoutes
from Code.QT import PantallaSTS
from Code.Sound import PantallaSonido
from Code.QT import PantallaSingularM
from Code.QT import PantallaUsuarios
from Code.QT import PantallaWashing
from Code.QT import PantallaWorkMap
from Code.QT import PantallaPlayGame
from Code.QT import Piezas
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.Databases import PantallaDatabase, WDB_Games, DBgames
from Code.QT import PantallaManualSave
from Code.Kibitzers import KibitzersManager
from Code.Tournaments import WTournaments
from Code.Polyglots import WFactory
from Code.Polyglots import WPolyglot
from Code.Endings import WEndingsGTB


class Procesador:
    user = None
    li_opciones_inicio = None
    configuracion = None
    gestor = None
    version = None

    def __init__(self):
        if Code.list_engine_managers is None:
            Code.list_engine_managers = EngineManager.ListEngineManagers()

        self.web = "https://lucaschess.pythonanywhere.com"
        self.blog = "https://lucaschess.blogspot.com"
        self.github = "https://github.com/lukasmonk/lucaschessR"

    def start_with_user(self, user):
        self.user = user

        self.li_opciones_inicio = [
            TB_QUIT,
            TB_PLAY,
            TB_TRAIN,
            TB_COMPETE,
            TB_TOOLS,
            TB_OPTIONS,
            TB_INFORMATION,
        ]  # Lo incluimos aqui porque sino no lo lee, en caso de aplazada

        self.configuracion = Configuracion.Configuracion(user)
        self.configuracion.start()
        Code.configuracion = self.configuracion
        Code.procesador = self
        AperturasStd.reset()

        # Tras crear configuración miramos si hay adjourns
        self.test_opcion_adjourns()

        Code.todasPiezas = Piezas.TodasPiezas()

        self.gestor = None

        self.siPrimeraVez = True
        self.siPresentacion = False  # si esta funcionando la presentacion

        self.posicionInicial = Position.Position()
        self.posicionInicial.set_pos_initial()

        self.xrival = None
        self.xtutor = None  # creaTutor lo usa asi que hay que definirlo antes
        self.xanalyzer = (
            None
        )  # cuando se juega GestorEntMaq y el tutor danzando a toda maquina, se necesita otro diferente

        self.replay = None
        self.replayBeep = None

    def test_opcion_adjourns(self):
        must_adjourn = len(Adjourns.Adjourns()) > 0
        if TB_ADJOURNS in self.li_opciones_inicio:
            if not must_adjourn:
                pos = self.li_opciones_inicio.index(TB_ADJOURNS)
                del self.li_opciones_inicio[pos]
        else:
            if must_adjourn:
                self.li_opciones_inicio.insert(1, TB_ADJOURNS)

    def set_version(self, version):
        self.version = version

    def iniciar_gui(self):
        if len(sys.argv) > 1:
            comando = sys.argv[1]
            if comando.lower().endswith(".pgn"):
                self.main_window = None
                self.read_pgn(comando)
                return

        self.main_window = Pantalla.PantallaDialog(self)
        self.main_window.ponGestor(self)  # antes que muestra
        self.main_window.muestra()
        self.kibitzers_manager = KibitzersManager.Manager(self)

        self.tablero = self.main_window.tablero

        self.entrenamientos = Trainings.Entrenamientos(self)

        if self.configuracion.x_check_for_update:
            Update.test_update(self.version, self)

        if self.configuracion.siAplazada:
            aplazamiento = self.configuracion.aplazamiento
            self.juegaAplazada(aplazamiento)
        else:
            if len(sys.argv) > 1:
                comando = sys.argv[1]
                comandoL = comando.lower()
                if comandoL.endswith(".pgn"):
                    aplazamiento = {}
                    aplazamiento["TIPOJUEGO"] = GT_AGAINST_PGN
                    aplazamiento["ISWHITE"] = True  # Compatibilidad
                    self.juegaAplazada(aplazamiento)
                    return
                elif comandoL.endswith(".lcsb"):
                    aplazamiento = {}
                    aplazamiento["TIPOJUEGO"] = GT_ALONE
                    aplazamiento["ISWHITE"] = True  # Compatibilidad
                    self.juegaAplazada(aplazamiento)
                    return
                elif comandoL.endswith(".lcdb"):
                    self.externDatabase(comando)
                    return
                elif comandoL.endswith(".bmt"):
                    self.inicio()
                    self.externBMT(comando)
                    return
                elif comando == "-play":
                    fich_tmp = sys.argv[2]
                    self.juegaExterno(fich_tmp)
                    return

            else:
                self.inicio()

    def reset(self):
        self.main_window.activaCapturas(False)
        self.main_window.activaInformacionPGN(False)
        if self.gestor:
            self.gestor.finGestor()
            self.gestor = None
        self.main_window.ponGestor(self)  # Necesario, no borrar
        self.tablero.indicadorSC.setVisible(False)
        self.tablero.blindfoldQuitar()
        self.test_opcion_adjourns()
        self.main_window.pon_toolbar(self.li_opciones_inicio, atajos=True)
        self.main_window.activaJuego(False, False)
        self.tablero.exePulsadoNum = None
        self.tablero.setposition(self.posicionInicial)
        self.tablero.borraMovibles()
        self.tablero.quitaFlechas()
        self.main_window.ajustaTam()
        self.main_window.ponTitulo()
        self.pararMotores()

    def inicio(self):
        Code.runSound.close()
        if self.gestor:
            del self.gestor
            self.gestor = None
        self.configuracion.limpiaTemporal()
        self.reset()
        if self.configuracion.siPrimeraVez:
            self.cambiaconfigurationPrimeraVez()
            self.configuracion.siPrimeraVez = False
            self.main_window.ponTitulo()
        if self.siPrimeraVez:
            self.siPrimeraVez = False
            self.cpu = CPU.CPU(self.main_window)
            self.presentacion()
        self.kibitzers_manager.stop()

    def presentacion(self, siEmpezar=True):
        self.siPresentacion = siEmpezar
        if not siEmpezar:
            self.cpu.stop()
            self.tablero.ponerPiezasAbajo(True)
            self.tablero.activaMenuVisual(True)
            self.tablero.setposition(self.posicionInicial)
            self.tablero.setToolTip("")
            self.tablero.bloqueaRotacion(False)

        else:
            self.tablero.bloqueaRotacion(True)
            self.tablero.setToolTip("")
            self.tablero.activaMenuVisual(True)
            Presentacion.GestorChallenge101(self)

    def juegaAplazada(self, aplazamiento):
        self.cpu = CPU.CPU(self.main_window)

        tipoJuego = aplazamiento["TIPOJUEGO"]
        is_white = aplazamiento["ISWHITE"]

        if tipoJuego == GT_COMPETITION_WITH_TUTOR:
            categoria = self.configuracion.rival.categorias.segun_clave(aplazamiento["CATEGORIA"])
            nivel = aplazamiento["NIVEL"]
            puntos = aplazamiento["PUNTOS"]
            self.gestor = GestorCompeticion.GestorCompeticion(self)
            self.gestor.inicio(categoria, nivel, is_white, puntos, aplazamiento)
        elif tipoJuego == GT_AGAINST_ENGINE:
            if aplazamiento["MODO"] == "Basic":
                self.entrenaMaquina(None, aplazamiento)
            else:
                self.playPersonAplazada(aplazamiento)
        elif tipoJuego == GT_ELO:
            self.gestor = GestorElo.GestorElo(self)
            self.gestor.inicio(None, aplazamiento)
        elif tipoJuego == GT_MICELO:
            self.gestor = GestorMicElo.GestorMicElo(self)
            self.gestor.inicio(None, 0, 0, aplazamiento)
        elif tipoJuego == GT_ALBUM:
            self.gestor = GestorAlbum.GestorAlbum(self)
            self.gestor.inicio(None, None, aplazamiento)
        elif tipoJuego == GT_AGAINST_PGN:
            self.read_pgn(sys.argv[1])
        elif tipoJuego in (GT_FICS, GT_FIDE, GT_LICHESS):
            self.gestor = GestorFideFics.GestorFideFics(self)
            self.gestor.selecciona(tipoJuego)
            self.gestor.inicio(aplazamiento["IDGAME"], aplazamiento=aplazamiento)

    def XTutor(self):
        if self.xtutor is None or not self.xtutor.activo:
            self.creaXTutor()
        return self.xtutor

    def creaXTutor(self):
        xtutor = EngineManager.EngineManager(self, self.configuracion.tutor)
        xtutor.name += "(%s)" % _("tutor")
        xtutor.opciones(self.configuracion.x_tutor_mstime, self.configuracion.x_tutor_depth, True)
        if self.configuracion.x_tutor_multipv == 0:
            xtutor.maximizaMultiPV()
        else:
            xtutor.setMultiPV(self.configuracion.x_tutor_multipv)

        self.xtutor = xtutor

    def cambiaXTutor(self):
        if self.xtutor:
            self.xtutor.terminar()
        self.creaXTutor()
        self.cambiaXAnalyzer()

    def XAnalyzer(self):
        if self.xanalyzer is None or not self.xanalyzer.activo:
            self.creaXAnalyzer()
        return self.xanalyzer

    def creaXAnalyzer(self):
        xanalyzer = EngineManager.EngineManager(self, self.configuracion.tutor)
        xanalyzer.name += "(%s)" % _("analyzer")
        xanalyzer.opciones(self.configuracion.x_tutor_mstime, self.configuracion.x_tutor_depth, True)
        if self.configuracion.x_tutor_multipv == 0:
            xanalyzer.maximizaMultiPV()
        else:
            xanalyzer.setMultiPV(self.configuracion.x_tutor_multipv)

        self.xanalyzer = xanalyzer
        Code.xanalyzer = xanalyzer

    def cambiaXAnalyzer(self):
        if self.xanalyzer:
            self.xanalyzer.terminar()
        self.creaXAnalyzer()

    def creaGestorMotor(self, confMotor, vtime, nivel, siMultiPV=False, priority=None):
        xgestor = EngineManager.EngineManager(self, confMotor)
        xgestor.opciones(vtime, nivel, siMultiPV)
        xgestor.setPriority(priority)
        return xgestor

    def pararMotores(self):
        Code.list_engine_managers.close_all()

    # Added by GON
    def closeEboard(self):
        if Code.dgt:
            DGT.close()
    # ------------        

    def cambiaRival(self, nuevo):
        """
        Llamado from_sq DatosNueva, cuando elegimos otro engine para jugar.
        """
        self.configuracion.rival = self.configuracion.buscaRival(nuevo)
        self.configuracion.graba()

    def menuplay(self):
        resp = BasicMenus.menuplay(self)
        if resp:
            self.menuPlay_run(resp)

    def menuPlay_run(self, resp):
        tipo, rival = resp
        if tipo == "free":
            self.libre()

        elif tipo == "person":
            self.playPerson(rival)

        elif tipo == "animales":
            self.albumAnimales(rival)

        elif tipo == "vehicles":
            self.albumVehicles(rival)

    def playPersonAplazada(self, aplazamiento):
        self.gestor = GestorPerson.GestorPerson(self)
        self.gestor.inicio(None, aplazamiento=aplazamiento)

    def playPerson(self, rival):
        uno = QTVarios.blancasNegrasTiempo(self.main_window)
        if not uno:
            return
        is_white, siTiempo, minutos, segundos, fastmoves = uno
        if is_white is None:
            return

        dic = {}
        dic["ISWHITE"] = is_white
        dic["RIVAL"] = rival

        dic["SITIEMPO"] = siTiempo and minutos > 0
        dic["MINUTOS"] = minutos
        dic["SEGUNDOS"] = segundos

        dic["FASTMOVES"] = fastmoves

        self.gestor = GestorPerson.GestorPerson(self)
        self.gestor.inicio(dic)

    def reabrirAlbum(self, album):
        tipo, name = album.claveDB.split("_")
        if tipo == "animales":
            self.albumAnimales(name)
        elif tipo == "vehicles":
            self.albumVehicles(name)

    def albumAnimales(self, animal):
        albumes = Albums.AlbumesAnimales()
        album = albumes.get_album(animal)
        album.test_finished()
        cromo, siRebuild = PantallaAlbumes.eligeCromo(self.main_window, self, album)
        if cromo is None:
            if siRebuild:
                albumes.reset(animal)
                self.albumAnimales(animal)
            return

        self.gestor = GestorAlbum.GestorAlbum(self)
        self.gestor.inicio(album, cromo)

    def albumVehicles(self, character):
        albumes = Albums.AlbumesVehicles()
        album = albumes.get_album(character)
        album.test_finished()
        cromo, siRebuild = PantallaAlbumes.eligeCromo(self.main_window, self, album)
        if cromo is None:
            if siRebuild:
                albumes.reset(character)
                self.albumVehicles(character)
            return

        self.gestor = GestorAlbum.GestorAlbum(self)
        self.gestor.inicio(album, cromo)

    def menucompete(self):
        resp = BasicMenus.menucompete(self)
        if resp:
            self.menucompete_run(resp)

    def menucompete_run(self, resp):
        tipo, rival = resp
        if tipo == "competition":
            self.competicion()

        elif tipo == "lucaselo":
            self.lucaselo()

        elif tipo == "micelo":
            self.micelo()

        elif tipo == "fics":
            self.ficselo(rival)

        elif tipo == "fide":
            self.fideelo(rival)

        elif tipo == "lichess":
            self.lichesselo(rival)

        elif tipo == "challenge101":
            Presentacion.GestorChallenge101(self)

        elif tipo == "strenght101":
            self.strenght101()

    def strenght101(self):
        w = PantallaSingularM.WSingularM(self.main_window, self.configuracion)
        if w.exec_():
            self.gestor = GestorSingularM.GestorSingularM(self)
            self.gestor.inicio(w.sm)

    def lucaselo(self):
        self.gestor = GestorElo.GestorElo(self)
        resp = WEngines.select_engine_elo(self.gestor, self.configuracion.eloActivo())
        if resp:
            self.gestor.inicio(resp)

    def micelo(self):
        self.gestor = GestorMicElo.GestorMicElo(self)
        resp = WEngines.select_engine_micelo(self.gestor, self.configuracion.miceloActivo())
        if resp:
            respT = QTVarios.vtime(self.main_window, minMinutos=3, minSegundos=0, maxMinutos=999, maxSegundos=999)
            if respT:
                minutos, segundos = respT
                self.gestor.inicio(resp, minutos, segundos)

    def ficselo(self, nivel):
        self.gestor = GestorFideFics.GestorFideFics(self)
        self.gestor.selecciona(GT_FICS)
        xid = self.gestor.elige_juego(nivel)
        self.gestor.inicio(xid)

    def fideelo(self, nivel):
        self.gestor = GestorFideFics.GestorFideFics(self)
        self.gestor.selecciona(GT_FIDE)
        xid = self.gestor.elige_juego(nivel)
        self.gestor.inicio(xid)

    def lichesselo(self, nivel):
        self.gestor = GestorFideFics.GestorFideFics(self)
        self.gestor.selecciona(GT_LICHESS)
        xid = self.gestor.elige_juego(nivel)
        self.gestor.inicio(xid)

    def run_action(self, key):
        if self.siPresentacion:
            self.presentacion(False)

        if key == TB_QUIT:
            if hasattr(self, "cpu"):
                self.cpu.stop()
            self.main_window.procesosFinales()
            self.main_window.accept()

        elif key == TB_PLAY:
            self.menuplay()

        elif key == TB_COMPETE:
            self.menucompete()

        elif key == TB_TRAIN:
            self.entrenamientos.lanza()

        elif key == TB_OPTIONS:
            self.opciones()

        elif key == TB_TOOLS:
            self.menu_tools()

        elif key == TB_INFORMATION:
            self.informacion()

        elif key == TB_ADJOURNS:
            self.adjourns()

    def adjourns(self):
        menu = QTVarios.LCMenu(self.main_window)
        li_adjourns = Adjourns.Adjourns().list_menu()
        for key, label, tp in li_adjourns:
            menu.opcion((True, key, tp), label, Iconos.PuntoMagenta())
            menu.addSeparator()
        menu.addSeparator()
        mr = menu.submenu(_("Remove"), Iconos.Borrar())
        for key, label, tp in li_adjourns:
            mr.opcion((False, key, tp), label, Iconos.Delete())

        resp = menu.lanza()
        if resp:
            si_run, key, tp = resp
            if si_run:
                dic = Adjourns.Adjourns().get(key)
                Adjourns.Adjourns().remove(key)
                if tp == GT_AGAINST_ENGINE:
                    self.gestor = GestorPlayAgainstEngine.GestorPlayAgainstEngine(self)
                    self.gestor.run_adjourn(dic)
                elif tp == GT_ALBUM:
                    self.gestor = GestorAlbum.GestorAlbum(self)
                    self.gestor.run_adjourn(dic)
                elif tp == GT_COMPETITION_WITH_TUTOR:
                    self.gestor = GestorCompeticion.GestorCompeticion(self)
                    self.gestor.run_adjourn(dic)
                elif tp == GT_ELO:
                    self.gestor = GestorElo.GestorElo(self)
                    self.gestor.run_adjourn(dic)
                elif tp in (GT_FIDE, GT_FICS, GT_LICHESS):
                    self.gestor = GestorFideFics.GestorFideFics(self)
                    self.gestor.selecciona(tp)
                    self.gestor.run_adjourn(dic)
                return

            else:
                Adjourns.Adjourns().remove(key)

            self.test_opcion_adjourns()
            self.main_window.pon_toolbar(self.li_opciones_inicio, atajos=True)

    def lanza_atajos(self):
        BasicMenus.atajos(self)

    def lanzaAtajosALT(self, key):
        BasicMenus.atajosALT(self, key)

    def opciones(self):
        menu = QTVarios.LCMenu(self.main_window)

        menu.opcion(self.cambiaconfiguration, _("Configuration"), Iconos.Opciones())
        menu.separador()

        menu1 = menu.submenu(_("Colors"), Iconos.Colores())
        menu1.opcion(self.editaColoresTablero, _("Main board"), Iconos.EditarColores())
        menu1.separador()
        menu1.opcion(self.cambiaColores, _("General"), Iconos.Vista())
        menu.separador()

        menu.opcion(self.sonidos, _("Custom sounds"), Iconos.SoundTool())
        menu.separador()
        menu.opcion(self.setPassword, _("Set password"), Iconos.Password())

        if self.configuracion.is_main:
            menu.separador()
            menu.opcion(self.usuarios, _("Usuarios"), Iconos.Usuarios())
            menu.separador()

            menu1 = menu.submenu(_("User data folder"), Iconos.Carpeta())
            menu1.opcion(self.folder_change, _("Change the folder"), Iconos.FolderChange())
            if not Configuracion.is_default_folder():
                menu1.separador()
                menu1.opcion(self.folder_default, _("Set the default"), Iconos.Defecto())

        resp = menu.lanza()
        if resp:
            if isinstance(resp, tuple):
                resp[0](resp[1])
            else:
                resp()

    def cambiaconfiguration(self):
        if PantallaConfig.opciones(self.main_window, self.configuracion):
            self.configuracion.graba()
            self.reiniciar()

    def editaColoresTablero(self):
        w = PantallaColores.WColores(self.tablero)
        w.exec_()

    def cambiaColores(self):
        if PantallaColores.cambiaColores(self.main_window, self.configuracion):
            self.reiniciar()

    def sonidos(self):
        w = PantallaSonido.WSonidos(self)
        w.exec_()

    def folder_change(self):
        carpeta = QTUtil2.leeCarpeta(
            self.main_window,
            self.configuracion.carpeta,
            _("Change the folder where all data is saved") + "\n" + _("Be careful please"),
        )
        if carpeta:
            if os.path.isdir(carpeta):
                self.configuracion.changeActiveFolder(carpeta)
                self.reiniciar()

    def folder_default(self):
        self.configuracion.changeActiveFolder(None)
        self.reiniciar()

    def reiniciar(self):
        self.main_window.accept()
        QTUtil.salirAplicacion(OUT_REINIT)

    def cambiaconfigurationPrimeraVez(self):
        if PantallaConfig.opcionesPrimeraVez(self.main_window, self.configuracion):
            self.configuracion.graba()

    def motoresExternos(self):
        w = WEngines.WEngines(self.main_window, self.configuracion)
        w.exec_()

    def aperturaspers(self):
        w = PantallaOpenings.AperturasPersonales(self)
        w.exec_()

    def usuarios(self):
        PantallaUsuarios.editaUsuarios(self)

    def setPassword(self):
        PantallaUsuarios.setPassword(self)

    def trainingMap(self, mapa):
        resp = PantallaWorkMap.train_map(self, mapa)
        if resp:
            self.gestor = GestorMateMap.GestorMateMap(self)
            self.gestor.inicio(resp)

    def menu_tools(self):
        resp = BasicMenus.menu_tools(self)
        if resp:
            self.menuTools_run(resp)

    def menuTools_run(self, resp):
        if resp == "pgn":
            self.visorPGN()

        elif resp == "miniatura":
            self.miniatura()

        elif resp == "polyglot":
            self.polyglot_factory()

        elif resp == "pgn_paste":
            self.pgn_paste()

        elif resp == "juega_solo":
            self.jugarSolo()

        elif resp == "torneos":
            self.torneos()
        elif resp == "motores":
            self.motoresExternos()
        elif resp == "sts":
            self.sts()
        elif resp == "kibitzers":
            self.kibitzers_manager.edit()

        elif resp == "manual_save":
            self.manual_save()

        elif resp.startswith("dbase_"):
            comando = resp[6:]
            accion = comando[0]  # R = read database,  N = create new, D = delete
            valor = comando[2:]
            self.database(accion, valor)

        elif resp == "aperturaspers":
            self.aperturaspers()
        elif resp == "openings":
            self.openings()

    def openings(self):
        dicline = PantallaOpeningLines.openingLines(self)
        if dicline:
            if "TRAIN" in dicline:
                resp = "tr_%s" % dicline["TRAIN"]
            else:
                resp = PantallaOpeningLine.study(self, dicline["file"])
            if resp is None:
                self.openings()
            else:
                pathFichero = os.path.join(self.configuracion.folder_openings(), dicline["file"])
                if resp == "tr_sequential":
                    self.openingsTrainingSequential(pathFichero)
                elif resp == "tr_static":
                    self.openingsTrainingStatic(pathFichero)
                elif resp == "tr_positions":
                    self.openingsTrainingPositions(pathFichero)
                elif resp == "tr_engines":
                    self.openingsTrainingEngines(pathFichero)

    def openingsTrainingSequential(self, pathFichero):
        self.gestor = GestorOpeningLines.GestorOpeningLines(self)
        self.gestor.inicio(pathFichero, "sequential", 0)

    def openingsTrainingEngines(self, pathFichero):
        self.gestor = GestorOpeningLines.GestorOpeningEngines(self)
        self.gestor.inicio(pathFichero)

    def openingsTrainingStatic(self, pathFichero):
        dbop = OpeningLines.Opening(pathFichero)
        num_linea = PantallaOpeningLines.selectLine(self, dbop)
        dbop.close()
        if num_linea is not None:
            self.gestor = GestorOpeningLines.GestorOpeningLines(self)
            self.gestor.inicio(pathFichero, "static", num_linea)
        else:
            self.openings()

    def openingsTrainingPositions(self, pathFichero):
        self.gestor = GestorOpeningLines.GestorOpeningLinesPositions(self)
        self.gestor.inicio(pathFichero)

    def externBMT(self, fichero):
        self.configuracion.ficheroBMT = fichero
        PantallaBMT.pantallaBMT(self)

    def anotar(self, game, siblancasabajo):
        self.gestor = GestorAnotar.GestorAnotar(self)
        self.gestor.inicio(game, siblancasabajo)

    def show_anotar(self):
        w = PantallaAnotar.WAnotar(self)
        if w.exec_():
            pc, siblancasabajo = w.resultado
            if pc is None:
                pc = DBgames.get_random_game()
            self.anotar(pc, siblancasabajo)

    def externDatabase(self, fichero):
        self.configuracion.ficheroDBgames = fichero
        self.database(fichero)
        self.run_action(TB_QUIT)

    def database(self, accion, dbpath, temporary=False):
        if accion == "M":
            if Code.isWindows:
                os.startfile(self.configuracion.folder_databases())
            return

        if accion == "N":
            dbpath = WDB_Games.new_database(self.main_window, self.configuracion)
            if dbpath is None:
                return
            accion = "R"

        if accion == "D":
            resp = QTVarios.select_db(self.main_window, self.configuracion, True, False)
            if resp:
                if QTUtil2.pregunta(self.main_window, "%s\n%s" % (_("Do you want to remove ?"), resp)):
                    Util.remove_file(resp)
                    Util.remove_file(resp + ".st1")
            return

        if accion == "R":
            self.configuracion.set_last_database(Util.relative_path(dbpath))
            w = PantallaDatabase.WBDatabase(self.main_window, self, dbpath, temporary, False)
            if self.main_window:
                if w.exec_():
                    if w.reiniciar:
                        self.database("R", self.configuracion.get_last_database())
            else:
                w.show()

    def manual_save(self):
        PantallaManualSave.manual_save(self)

    def torneos(self):
        WTournaments.tournaments(self.main_window)
        # xjugar =
        # while xjugar:
        #     nombre_torneo, liNumGames = xjugar
        #     self.gestor = GestorTorneo.GestorTorneo(self)
        #     self.gestor.inicio(nombre_torneo, liNumGames)
        #     self.inicio()
        #     xjugar = PantallaTorneos.unTorneo(self.main_window, nombre_torneo)
        # self.reiniciar()

    def sts(self):
        PantallaSTS.sts(self, self.main_window)

    def libre(self):
        dic = PlayAgainstEngine.play_against_engine(self, _("Play against an engine"))
        if dic:
            self.entrenaMaquina(dic)

    def entrenaMaquina(self, dic):
        # self.game_type = GT_AGAINST_ENGINE
        # self.state = ST_PLAYING
        self.gestor = GestorPlayAgainstEngine.GestorPlayAgainstEngine(self)
        side = dic["SIDE"]
        if side == "R":
            side = "B" if random.randint(1, 2) == 1 else "N"
        dic["ISWHITE"] = side == "B"
        self.gestor.inicio(dic)

    def read_pgn(self, fichero_pgn):
        fichero_pgn = os.path.abspath(fichero_pgn)
        cfecha_pgn = str(os.path.getmtime(fichero_pgn))
        cdir = self.configuracion.folder_databases_pgn()

        file_db = os.path.join(cdir, os.path.basename(fichero_pgn)[:-4] + ".lcdb")

        if Util.exist_file(file_db):
            create = False
            db = DBgames.DBgames(file_db)
            cfecha_pgn_ant = db.recuperaConfig("PGN_DATE")
            fichero_pgn_ant = db.recuperaConfig("PGN_FILE")
            db.close()
            if cfecha_pgn != cfecha_pgn_ant or fichero_pgn_ant != fichero_pgn:
                create = True
                Util.remove_file(file_db)
        else:
            create = True

        if create:
            db = DBgames.DBgames(file_db)
            dlTmp = QTVarios.ImportarFicheroPGN(self.main_window)
            dlTmp.show()
            db.leerPGNs([fichero_pgn], dlTmp=dlTmp)
            db.guardaConfig("PGN_DATE", cfecha_pgn)
            db.guardaConfig("PGN_FILE", fichero_pgn)
            db.close()
            dlTmp.close()

        self.database("R", file_db, temporary=True)

    def visorPGN(self):
        path = QTVarios.select_pgn(self.main_window)
        if path:
            self.read_pgn(path)

    def select_1_pgn(self, wparent=None):
        wparent = self.main_window if wparent is None else wparent
        path = QTVarios.select_pgn(wparent)
        if path:
            fichero_pgn = os.path.abspath(path)
            cfecha_pgn = str(os.path.getmtime(fichero_pgn))
            cdir = self.configuracion.folder_databases_pgn()

            file_db = os.path.join(cdir, os.path.basename(fichero_pgn)[:-4] + ".lcdb")

            if Util.exist_file(file_db):
                create = False
                db = DBgames.DBgames(file_db)
                cfecha_pgn_ant = db.recuperaConfig("PGN_DATE")
                fichero_pgn_ant = db.recuperaConfig("PGN_FILE")
                db.close()
                if cfecha_pgn != cfecha_pgn_ant or fichero_pgn_ant != fichero_pgn:
                    create = True
                    Util.remove_file(file_db)
            else:
                create = True

            if create:
                db = DBgames.DBgames(file_db)
                dlTmp = QTVarios.ImportarFicheroPGN(wparent)
                dlTmp.show()
                db.leerPGNs([fichero_pgn], dlTmp=dlTmp)
                db.guardaConfig("PGN_DATE", cfecha_pgn)
                db.guardaConfig("PGN_FILE", fichero_pgn)
                db.close()
                dlTmp.close()

            w = PantallaDatabase.WBDatabase(self.main_window, self, file_db, True, True)
            if w.exec_():
                return w.game

        return None

    def pgn_paste(self):
        path = self.configuracion.ficheroTemporal("lcdb")
        texto = QTUtil.traePortapapeles()
        if texto:
            with open(path, "wb") as q:
                q.write(texto)
            self.read_pgn(path)

    def miniatura(self):
        file_miniatures = Code.path_resource("IntFiles", "Miniatures.lcdb")
        db = DBgames.DBgames(file_miniatures)
        db.all_reccount()
        num_game = random.randint(0, db.reccount() - 1)
        game = db.leePartidaRecno(num_game)
        db.close()
        dic = {"GAME": game.save()}
        gestor = GestorSolo.GestorSolo(self)
        gestor.inicio(dic)

    def polyglot_factory(self):
        resp = WFactory.polyglots_factory(self)
        if resp:
            w = WPolyglot.WPolyglot(self.main_window, self.configuracion, resp)
            w.exec_()
            self.polyglot_factory()

    def juegaExterno(self, fich_tmp):
        dic_sended = Util.restore_pickle(fich_tmp)
        fich = Util.relative_path(self.configuracion.ficheroTemporal(".pkd"))

        dic = PlayAgainstEngine.play_position(self, _("Play a position"), dic_sended["ISWHITE"])
        if dic is None:
            self.run_action(TB_QUIT)
        else:
            side = dic["SIDE"]
            if side == "R":
                side = "B" if random.randint(1, 2) == 1 else "N"
            dic["ISWHITE"] = side == "B"
            self.gestor = GestorPlayAgainstEngine.GestorPlayAgainstEngine(self)
            self.gestor.play_position(dic, dic_sended["GAME"])

    def jugarSolo(self):
        self.gestor = GestorSolo.GestorSolo(self)
        self.gestor.inicio()

    def entrenaPos(self, position, nPosiciones, titentreno, liEntrenamientos, entreno, jump):
        # self.game_type = GT_POSITIONS
        # self.state = ST_PLAYING
        self.gestor = GestorEntPos.GestorEntPos(self)
        self.gestor.set_training(entreno)
        self.gestor.inicio(position, nPosiciones, titentreno, liEntrenamientos, is_automatic_jump=jump)

    def playRoute(self, route):
        if route.state == Routes.BETWEEN:
            self.gestor = GestorRoutes.GestorRoutesTactics(self)
            # self.state = ST_PLAYING
            # self.game_type = GT_POSITIONS
            self.gestor.inicio(route)
        elif route.state == Routes.ENDING:
            self.gestor = GestorRoutes.GestorRoutesEndings(self)
            # self.state = ST_PLAYING
            # self.game_type = GT_POSITIONS
            self.gestor.inicio(route)
        elif route.state == Routes.PLAYING:
            self.gestor = GestorRoutes.GestorRoutesPlay(self)
            # self.state = ST_PLAYING
            # self.game_type = GT_AGAINST_ENGINE
            self.gestor.inicio(route)

    def showRoute(self):
        PantallaRoutes.train_train(self)

    def playEverest(self, recno):
        self.gestor = GestorEverest.GestorEverest(self)
        # self.state = ST_PLAYING
        # self.game_type = GT_AGAINST_ENGINE
        self.gestor.inicio(recno)

    def showEverest(self, recno):
        if PantallaEverest.show_expedition(self.main_window, self.configuracion, recno):
            self.playEverest(recno)

    def play_game(self):
        w = PantallaPlayGame.WPlayGameBase(self)
        if w.exec_():
            recno = w.recno
            if recno is not None:
                is_white = w.is_white
                self.gestor = GestorPlayGame.GestorPlayGame(self)
                self.gestor.inicio(recno, is_white)

    def play_game_show(self, recno):
        db = PantallaPlayGame.DBPlayGame(self.configuracion.file_play_game())
        w = PantallaPlayGame.WPlay1(self.main_window, self.configuracion, db, recno)
        if w.exec_():
            if w.recno is not None:
                is_white = w.is_white
                self.gestor = GestorPlayGame.GestorPlayGame(self)
                self.gestor.inicio(w.recno, is_white)
        db.close()

    def showTurnOnLigths(self, name):
        self.entrenamientos.turn_on_lights(name)

    def playWashing(self):
        GestorWashing.gestorWashing(self)

    def showWashing(self):
        if PantallaWashing.pantallaWashing(self):
            self.playWashing()

    def informacion(self):
        resp = BasicMenus.menuInformacion(self)
        if resp:
            self.informacion_run(resp)

    def informacion_run(self, resp):
        if resp == "acercade":
            self.acercade()
        elif resp == "docs":
            webbrowser.open("%s/docs" % self.web)
        elif resp == "blog":
            webbrowser.open(self.blog)
        elif resp.startswith("http"):
            webbrowser.open(resp)
        elif resp == "web":
            webbrowser.open("%s/index?lang=%s" % (self.web, self.configuracion.translator()))
        elif resp == "mail":
            webbrowser.open("mailto:lukasmonk@gmail.com")

        elif resp == "actualiza":
            self.actualiza()

    def adTitulo(self):
        return "<b>" + Code.lucas_chess + "</b><br>" + _X(_("version %1"), self.version)

    def adPie(self):
        return (
            "<hr><br><b>%s</b>" % _("Author")
            + ': <a href="mailto:lukasmonk@gmail.com">Lucas Monge</a> -'
            + ' <a href="%s">%s</a></a>' % (self.web, self.web)
            + '(%s <a href="http://www.gnu.org/copyleft/gpl.html"> GPL</a>).<br>' % _("License")
        )

    def acercade(self):
        w = About.WAbout(self)
        w.exec_()

    def actualiza(self):
        if Update.update(self.version, self.main_window):
            self.reiniciar()

    def unMomento(self, mensaje=None):
        return QTUtil2.mensEspera.inicio(
            self.main_window, mensaje if mensaje else _("One moment please..."), position="ad"
        )

    def numDatos(self):
        return 0

    def competicion(self):
        opciones = WCompetitionWithTutor.datos(self.main_window, self.configuracion, self)
        if opciones:
            # self.game_type = GT_COMPETITION_WITH_TUTOR
            categorias, categoria, nivel, is_white, puntos = opciones

            self.gestor = GestorCompeticion.GestorCompeticion(self)
            self.gestor.inicio(categorias, categoria, nivel, is_white, puntos)

    def final_x(self):
        return True

    def finalX0(self):
        return True

    def clonVariantes(self, wpantalla, xtutor=None, siCompetitivo=False):
        return ProcesadorVariantes(
            wpantalla, xtutor, siCompetitivo=siCompetitivo, kibitzers_manager=self.kibitzers_manager
        )

    def gestorUnPGN(self, wpantalla, pgn, jugadaInicial=None, must_save=True):
        clonProcesador = ProcesadorVariantes(
            wpantalla, self.xtutor, siCompetitivo=False, kibitzers_manager=self.kibitzers_manager
        )

        clonProcesador.gestor = GestorSolo.GestorSolo(clonProcesador)
        clonProcesador.gestor.inicio(pgn=pgn, jugadaInicial=jugadaInicial, must_save=must_save)

        clonProcesador.main_window.muestraVariantes(clonProcesador.gestor.tituloVentanaPGN())

        return getattr(clonProcesador, "valorPGN", (None, None, None))

    def gestorPartida(self, wpantalla, game, siCompleta, tableroFather):
        clonProcesador = ProcesadorVariantes(
            wpantalla, self.xtutor, siCompetitivo=False, kibitzers_manager=self.kibitzers_manager
        )
        clonProcesador.gestor = GestorPartida.GestorPartida(clonProcesador)
        clonProcesador.gestor.inicio(game, siCompleta)

        tablero = clonProcesador.main_window.tablero
        if tableroFather:
            tablero.dbVisual_setFichero(tableroFather.dbVisual.fichero)
            tablero.dbVisual_setShowAllways(tableroFather.dbVisual.showAllways)

        resp = clonProcesador.main_window.muestraVariantes(clonProcesador.gestor.tituloVentana())
        if tableroFather:
            tableroFather.dbVisual_setFichero(tableroFather.dbVisual.fichero)
            tableroFather.dbVisual_setShowAllways(tableroFather.dbVisual.showAllways())

        if resp:
            return clonProcesador.gestor.game
        else:
            return None

    def save_lcsb(self, estado, game, pgn):
        dic = GestorSolo.pgn_lcsb(estado, pgn)
        dic["GAME"] = game.save()
        return dic

    def selectOneFNS(self, owner=None):
        if owner is None:
            owner = self.main_window
        return Trainings.selectOneFNS(owner, self)

    def gaviota_endings(self):
        WEndingsGTB.train_gtb(self)


class ProcesadorVariantes(Procesador):
    def __init__(self, wpantalla, xtutor, siCompetitivo=False, kibitzers_manager=None):

        self.kibitzers_manager = kibitzers_manager
        self.siCompetitivo = siCompetitivo

        self.configuracion = Code.configuracion

        self.li_opciones_inicio = [
            TB_QUIT,
            TB_PLAY,
            TB_TRAIN,
            TB_COMPETE,
            TB_TOOLS,
            TB_OPTIONS,
            TB_INFORMATION,
        ]  # Lo incluimos aqui porque sino no lo lee, en caso de aplazada

        self.siPresentacion = False

        self.main_window = Pantalla.PantallaDialog(self, wpantalla)
        self.main_window.ponGestor(self)

        self.tablero = self.main_window.tablero

        self.xtutor = xtutor
        self.xrival = None
        self.xanalyzer = None

        self.replayBeep = None

        self.posicionInicial = None

        self.cpu = CPU.CPU(self.main_window)
