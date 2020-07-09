from Code import Apertura
from Code.Engines import GestorPlayAgainstEngine
from Code.QT import Iconos
from Code import Util
from Code.Constantes import *


class GestorPerson(GestorPlayAgainstEngine.GestorPlayAgainstEngine):
    def inicio(self, dic_var):
        self.base_inicio(dic_var)
        self.siguiente_jugada()

    def base_inicio(self, dic_var):
        self.reinicio = dic_var

        self.cache = dic_var.get("cache", {})

        self.game_type = GT_AGAINST_CHILD_ENGINE

        self.human_is_playing = False
        self.plays_instead_of_me_option = True
        self.state = ST_PLAYING

        self.summary = {}  # numJugada : "a"ccepted, "s"ame, "r"ejected, dif points, time used
        self.with_summary = dic_var.get("SUMMARY", False)

        is_white = dic_var["ISWHITE"]
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        w, b = self.configuracion.nom_player(), dic_var["RIVAL"]
        if not is_white:
            w, b = b, w
        self.game.add_tag("White", w)
        self.game.add_tag("Black", b)

        self.with_takeback = True

        cmrival = self.configuracion.buscaRival("irina", None)
        self.xrival = self.procesador.creaGestorMotor(cmrival, None, 2)
        self.rival_name = dic_var["RIVAL"]
        self.xrival.set_option("Personality", self.rival_name)
        if not dic_var["FASTMOVES"]:
            self.xrival.set_option("Max Time", "5")
            self.xrival.set_option("Min Time", "1")
        self.xrival.name = _F(self.rival_name)

        self.lirm_engine = []
        self.next_test_resign = 0
        self.resign_limit = -99999  # never

        self.aperturaObl = self.aperturaStd = None

        self.human_is_playing = False
        self.state = ST_PLAYING
        self.siAnalizando = False

        self.aperturaStd = Apertura.AperturaPol(1)

        self.set_dispatcher(self.mueve_humano)
        self.main_window.set_notify(self.mueve_rival_base)


        self.pensando(True)

        self.main_window.ponActivarTutor(False)

        self.ayudas = 0
        self.ayudas_iniciales = 0

        self.xrival.is_white = self.is_engine_side_white

        self.siPrimeraJugadaHecha = False

        self.siTiempo = dic_var["SITIEMPO"]
        if self.siTiempo:
            self.maxSegundos = dic_var["MINUTOS"] * 60.0
            self.segundosJugada = dic_var["SEGUNDOS"]
            self.segExtra = dic_var.get("MINEXTRA", 0) * 60.0

            self.vtime = {WHITE: Util.Timer(self.maxSegundos), BLACK: Util.Timer(self.maxSegundos)}

        self.pensando(False)

        li = [TB_CANCEL, TB_RESIGN, TB_TAKEBACK, TB_REINIT, TB_ADJOURN, TB_PAUSE, TB_CONFIG, TB_UTILITIES]
        self.main_window.pon_toolbar(li)

        self.main_window.activaJuego(True, self.siTiempo)

        self.set_dispatcher(self.mueve_humano)
        self.setposition(self.game.last_position)
        self.mostrarIndicador(True)
        self.quitaAyudas(True, siQuitarAtras=False)
        self.ponPiezasAbajo(is_white)

        imagen = getattr(Iconos, "pm%s" % self.rival_name)

        self.main_window.base.lbRotulo1.ponImagen(imagen())
        self.main_window.base.lbRotulo1.show()

        self.ponCapInfoPorDefecto()

        self.pgnRefresh(True)

        if self.siTiempo:
            self.siPrimeraJugadaHecha = False
            tpBL = self.vtime[True].etiqueta()
            tpNG = self.vtime[False].etiqueta()
            player = self.configuracion.x_player
            bl, ng = player, self.rival_name
            if self.is_engine_side_white:
                bl, ng = ng, bl
            self.main_window.ponDatosReloj(bl, tpBL, ng, tpNG)
            self.refresh()

        self.dgt_setposition()
