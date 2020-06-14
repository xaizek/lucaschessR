import random
import time

import FasterCode

from Code import Util
from Code.Polyglots import Books
from Code import Position
from Code import Gestor
from Code import Move
from Code.Endings import LibChess
from Code import Game
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code import Routes
import Code
from Code.Constantes import *


class GR_Engine:
    def __init__(self, procesador, nlevel):
        self._label = "%s - %s %d" % (_("Engine"), _("Level"), nlevel)
        self.configuracion = procesador.configuracion
        self.level = nlevel
        if nlevel == 0:
            self.gestor = None
            self._nombre = self._label
        else:
            dEngines = self.elos()
            x = +1 if nlevel < 6 else -1
            while True:
                if len(dEngines[nlevel]) > 0:
                    nom_engine, depth, elo = random.choice(dEngines[nlevel])
                    break
                else:
                    nlevel += x
                    if nlevel > 6:
                        nlevel = 1
            rival = self.configuracion.buscaRival(nom_engine)
            self.gestor = procesador.creaGestorMotor(rival, None, depth)
            self._nombre = "%s %s %d" % (rival.name, _("Depth"), depth)
            self._label += "\n%s\n%s: %d" % (self._nombre, _("Estimated elo"), elo)

    def close(self):
        if self.gestor and self.gestor != self:
            self.gestor.terminar()
            self.gestor = None

    @property
    def label(self):
        return self._label

    @property
    def name(self):
        return self._nombre

    def play(self, fen):
        if self.gestor:
            mrm = self.gestor.analiza(fen)
            return mrm.rmBest().movimiento()
        else:
            return FasterCode.runFen(fen, 1, 0, 2)

    def elos(self):
        x = """stockfish 1284 1377 1377 1496
alaric 1154 1381 1813 2117
amyan 1096 1334 1502 1678
bikjump 1123 1218 1489 1572
cheng 1137 1360 1662 1714
chispa 1109 1180 1407 1711
clarabit 1119 1143 1172 1414
critter 1194 1614 1814 1897
discocheck 1138 1380 1608 1812
fruit 1373 1391 1869 1932
gaia 1096 1115 1350 1611
cyrano 1154 1391 1879 2123
garbochess 1146 1382 1655 1892
gaviota 1152 1396 1564 1879
greko 1158 1218 1390 1742
hamsters 1143 1382 1649 1899
komodo 1204 1406 1674 1891
lime 1143 1206 1493 1721
pawny 1096 1121 1333 1508
rhetoric 1131 1360 1604 1820
roce 1122 1150 1206 1497
rodent 1103 1140 1375 1712
umko 1120 1384 1816 1930
rybka 1881 2060 2141 2284
simplex 1118 1166 1411 1814
ufim 1189 1383 1928 2134
texel 1154 1387 1653 1874
toga 1236 1495 1928 2132"""
        d = {1: [], 2: [], 3: [], 4: [], 5: [], 6: []}

        def mas(engine, depth, celo):
            elo = int(celo)
            if elo < 1100:
                tp = 1
            elif elo < 1200:
                tp = 2
            elif elo < 1400:
                tp = 3
            elif elo < 1700:
                tp = 4
            elif elo < 2000:
                tp = 5
            elif elo < 2200:
                tp = 6
            else:
                return
            if engine in self.configuracion.dic_engines:
                d[tp].append((engine, depth, elo))

        for line in x.split("\n"):
            engine, d1, d2, d3, d4 = line.split(" ")
            mas(engine, 1, d1)
            mas(engine, 2, d2)
            mas(engine, 3, d3)
            mas(engine, 4, d4)
        return d


class GestorRoutes(Gestor.Gestor):
    def inicio(self, route):
        self.route = route
        if not hasattr(self, "time_start"):
            self.time_start = time.time()
        self.state = route.state

        self.game_type = GT_ROUTES

    def finPartida(self):
        self.procesador.inicio()
        self.route.add_time(time.time() - self.time_start, self.state)

    def final_x(self):
        self.finPartida()
        return False

    def add_move(self, move, siNuestra):
        self.game.add_move(move)

        self.ponFlechaSC(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

        self.dgt_setposition()


class GestorRoutesPlay(GestorRoutes):
    def inicio(self, route):
        GestorRoutes.inicio(self, route)

        line = route.get_line()

        opening = line.opening
        is_white = opening.is_white if opening.is_white is not None else random.choice([True, False])
        self.liPVopening = opening.pv.split(" ")
        self.posOpening = 0
        self.is_opening = len(opening.pv) > 0
        self.book = Books.Libro("P", Code.tbookI, Code.tbookI, True)
        self.book.polyglot()

        self.engine = GR_Engine(self.procesador, line.engine)
        self.must_win = route.must_win()
        self.is_rival_thinking = False

        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.main_window.ponActivarTutor(False)

        self.ayudas_iniciales = 0

        li_options = [TB_CLOSE, TB_CONFIG, TB_REINIT]
        self.main_window.pon_toolbar(li_options)

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.main_window.quitaAyudas(True)

        self.ponRotulo1(self.engine.label)
        if self.must_win:
            self.ponRotulo2(_("You must win to pass this game"))

        self.set_dispatcher(self.mueve_humano)
        self.ponPosicion(self.game.last_position)
        self.mostrarIndicador(True)
        self.ponPiezasAbajo(is_white)

        self.pgnRefresh(True)
        QTUtil.refresh_gui()

        self.dgt_setposition()

        self.siguiente_jugada()

    def finPartida(self):
        self.engine.close()
        GestorRoutes.finPartida(self)

    def run_action(self, key):
        if key == TB_CLOSE:
            self.finPartida()
            self.procesador.showRoute()

        elif key == TB_REINIT:
            self.game.set_position()
            self.inicio(self.route)

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True)

        elif key == TB_UTILITIES:
            self.utilidades()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return

        if self.game.is_finished():
            self.lineaTerminada()
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.ponIndicador(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white
        if siRival:
            self.juegaRival()
        else:
            self.human_is_playing = True
            self.activaColor(is_white)

    def juegaRival(self):
        if self.is_opening:
            pv = self.liPVopening[self.posOpening]
            self.posOpening += 1
            if self.posOpening == len(self.liPVopening):
                self.is_opening = False
        else:
            fen = self.game.last_position.fen()
            pv = None
            if self.book:
                pv = self.book.eligeJugadaTipo(fen, "au")
                if not pv:
                    self.book = None
            if not pv:
                if len(self.game.last_position) <= 4:
                    t4 = LibChess.T4(self.configuracion)
                    pv = t4.best_move(fen)
                    t4.close()
                if not pv:
                    pv = self.engine.play(fen)

        siBien, mens, move = Move.dameJugada(self.game, self.game.last_position, pv[:2], pv[2:4], pv[4:])
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        self.siguiente_jugada()

    def mueve_humano(self, from_sq, to_sq, promotion=None):
        jgSel = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not jgSel:
            return False

        fen = self.game.last_position.fen()
        pv = jgSel.movimiento().lower()
        if self.is_opening:
            op_pv = self.liPVopening[self.posOpening]
            if pv != op_pv:
                if self.must_win:
                    QTUtil2.mensajeTemporal(self.main_window, _("Wrong move"), 2)
                    self.run_action(TB_REINIT)
                else:
                    QTUtil2.message_error(
                        self.main_window, "%s\n%s" % (_("Wrong move"), _("Right move: %s") % Game.pv_san(fen, op_pv))
                    )
                    self.sigueHumano()
                return False
            self.posOpening += 1
            if self.posOpening == len(self.liPVopening):
                self.is_opening = False

        self.move_the_pieces(jgSel.liMovs)

        self.add_move(jgSel, True)
        self.error = ""

        self.siguiente_jugada()
        return True

    def lineaTerminada(self):
        self.disable_all()
        self.human_is_playing = False
        self.state = ST_ENDGAME
        self.refresh()
        li_options = [TB_CLOSE, TB_UTILITIES]
        self.main_window.pon_toolbar(li_options)
        jgUlt = self.game.last_jg()

        siwin = (jgUlt.is_white() == self.is_human_side_white) and not jgUlt.is_draw

        self.guardarGanados(siwin)

        if siwin:
            if self.route.end_playing():
                mensaje = _("Congratulations, you have completed the game.")
            else:
                mensaje = _("Well done")
            self.mensajeEnPGN(mensaje)
        else:
            if self.must_win:
                QTUtil2.message_error(self.main_window, _("You must win to pass this step."))
                li_options = [TB_CLOSE, TB_CONFIG, TB_UTILITIES, TB_REINIT]
                self.main_window.pon_toolbar(li_options)
            else:
                self.route.end_playing()

    def actualPGN(self):
        resp = '[Event "%s"]\n' % _("Transsiberian Railway")
        hoy = Util.today()
        resp += '[Date "%d-%d-%d"]\n' % (hoy.year, hoy.month, hoy.day)

        lbe = self.engine.name

        white, black = self.configuracion.x_player, lbe
        if not self.is_human_side_white:
            white, black = black, white

        resp += '[White "%s"]\n' % white
        resp += '[Black "%s"]\n' % black

        last_jg = self.game.last_jg()
        result = last_jg.resultado()
        if last_jg.is_draw:
            result = "1/2-1/2"
        else:
            result = "1-0" if last_jg.is_white() else "0-1"

        resp += '[Result "%s"]\n' % result

        ap = self.game.opening
        resp += '[ECO "%s"]\n' % ap.eco
        resp += '[Opening "%s"]\n' % ap.trNombre

        resp += "\n" + self.game.pgnBase() + " " + result

        return resp


class GestorRoutesEndings(GestorRoutes):
    def inicio(self, route):
        GestorRoutes.inicio(self, route)

        ending = self.route.get_ending()
        if "|" in ending:
            self.is_guided = True
            self.t4 = None
            self.fen, label, pv = ending.split("|")
            self.liPV = pv.split(" ")
            self.posPV = 0
        else:
            self.is_guided = False
            self.t4 = LibChess.T4(self.configuracion)
            self.fen = ending + " - - 0 1"

        self.is_rival_thinking = False

        cp = Position.Position()
        cp.read_fen(self.fen)

        is_white = cp.is_white

        self.game.set_position(cp)
        self.game.pending_opening = False

        self.warnings = 0
        self.max_warnings = 5

        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.main_window.ponActivarTutor(False)
        self.quitaAyudas(True)

        self.ayudas_iniciales = 0

        li_options = [TB_CLOSE, TB_HELP]
        self.main_window.pon_toolbar(li_options)

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.main_window.quitaAyudas(True)
        self.set_dispatcher(self.mueve_humano)
        self.ponPosicion(self.game.last_position)
        self.mostrarIndicador(True)
        self.ponPiezasAbajo(is_white)

        self.ponWarnings()

        self.pgnRefresh(True)
        QTUtil.refresh_gui()

        self.dgt_setposition()

        if self.is_guided:
            self.ponRotulo1("<b>%s</b>" % label)

        self.siguiente_jugada()

    def ponWarnings(self):
        if self.warnings <= self.max_warnings:
            self.ponRotulo2(_("Warnings: %d/%d" % (self.warnings, self.max_warnings)))
        else:
            self.ponRotulo2(_("You must repeat the puzzle."))

    def run_action(self, key):
        if key == TB_CLOSE:
            self.finPartida()
            self.procesador.showRoute()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True, siCambioTutor=True)

        elif key == TB_HELP:
            self.ayuda()

        elif key == TB_NEXT:
            if self.route.km_pending():
                self.inicio(self.route)
            else:
                self.finPartida()
                self.procesador.showRoute()

        elif key == TB_UTILITIES:
            self.utilidades()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def finPartida(self):
        if self.t4:
            self.t4.close()
        GestorRoutes.finPartida(self)

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return

        if self.game.is_finished():
            self.lineaTerminada()
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.ponIndicador(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white
        if siRival:
            if self.is_guided:
                pv = self.liPV[self.posPV].split("-")[0]
                self.posPV += 1
            else:
                fen = self.game.last_position.fen()
                pv = self.t4.best_move(fen)
            self.mueve_rival(pv[:2], pv[2:4], pv[4:])
            self.siguiente_jugada()
        else:
            self.human_is_playing = True
            self.activaColor(is_white)

    def show_error(self, mens):
        QTUtil2.mensajeTemporal(self.main_window, "   %s    " % mens, 1, background="#FF9B00", position="ad")

    def show_mens(self, mens):
        QTUtil2.mensajeTemporal(self.main_window, mens, 4, position="tb", background="#C3D6E8")

    def mueve_humano(self, from_sq, to_sq, promotion=None):
        jgSel = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not jgSel:
            return False

        if self.is_guided:
            pvSel = jgSel.movimiento().lower()
            pvObj = self.liPV[self.posPV]
            li = pvObj.split("-")
            if li[0] != pvSel:
                if pvSel in li:
                    pgn = Game.pv_pgn(jgSel.position_before.fen(), pvObj)
                    self.show_mens(_("You have selected one correct move, but the line use %s") % pgn)
                    self.ponFlechaSC(pvObj[:2], pvObj[2:4])
                    self.ayuda(False)
                else:
                    self.show_error(_("Wrong move"))
                    self.warnings += 1
                    self.ponWarnings()
                self.sigueHumano()
                return False
            self.posPV += 1
        else:
            fen = self.game.last_position.fen()
            pv = jgSel.movimiento().lower()
            b_wdl = self.t4.wdl(fen)
            m_wdl = self.t4.wdl_move(fen, pv)

            if b_wdl != m_wdl:
                self.show_error(_("Wrong move"))
                self.warnings += 1
                self.ponWarnings()
                self.ponPosicion(self.game.last_position)
                self.sigueHumano()
                return False

        self.move_the_pieces(jgSel.liMovs)

        self.add_move(jgSel, True)
        self.error = ""

        self.siguiente_jugada()
        return True

    def mueve_rival(self, from_sq, to_sq, promotion):
        siBien, mens, move = Move.dameJugada(self.game, self.game.last_position, from_sq, to_sq, promotion)
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        return True

    def ayuda(self, siWarning=True):
        if self.is_guided:
            pvObj = self.liPV[self.posPV]
            li = pvObj.split("-")
        else:
            li = self.t4.better_moves(self.game.last_position.fen(), None)
        liMovs = [(pv[:2], pv[2:4], n == 0) for n, pv in enumerate(li)]
        self.tablero.ponFlechasTmp(liMovs)
        if siWarning:
            self.warnings += self.max_warnings
            self.ponWarnings()

    def lineaTerminada(self):
        self.disable_all()
        self.human_is_playing = False
        self.state = ST_ENDGAME
        self.refresh()

        jgUlt = self.game.last_jg()
        if jgUlt.is_draw:
            mensaje = "%s<br>%s" % (_("Draw"), _("You must repeat the puzzle."))
            self.mensajeEnPGN(mensaje)
            self.inicio(self.route)
        elif self.warnings <= self.max_warnings:
            self.main_window.pon_toolbar([TB_CLOSE, TB_UTILITIES])
            self.mensajeEnPGN(_("Done"))
            self.route.end_ending()
        else:
            QTUtil2.message_bold(self.main_window)
            mensaje = "%s<br>%s" % (_("Done with errors."), _("You must repeat the puzzle."))
            self.mensajeEnPGN(mensaje)
            self.inicio(self.route)

    def actualPGN(self):
        resp = '[Event "%s"]\n' % _("Transsiberian Railway")
        resp += '[FEN "%s"\n' % self.game.first_position.fen()

        resp += "\n" + self.game.pgnBase()

        return resp


class GestorRoutesTactics(GestorRoutes):
    def inicio(self, route):
        GestorRoutes.inicio(self, route)

        tactica = self.route.get_tactic()

        self.partida_objetivo = Game.fen_partida(tactica.fen, tactica.pgn)

        self.is_rival_thinking = False

        cp = Position.Position()
        cp.read_fen(tactica.fen)

        self.fen = tactica.fen

        is_white = cp.is_white

        self.game.set_position(cp)
        self.game.pending_opening = False

        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.main_window.ponActivarTutor(False)

        self.ayudas_iniciales = 0

        li_options = [TB_CLOSE, TB_HELP]
        self.main_window.pon_toolbar(li_options)

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.main_window.quitaAyudas(True)
        self.set_dispatcher(self.mueve_humano)
        self.ponPosicion(self.game.last_position)
        self.mostrarIndicador(True)
        self.ponPiezasAbajo(is_white)
        # self.ponRotulo1("<b>%s</b>" % tactica.label)
        self.ponRotulo2(route.mens_tactic(False))
        self.pgnRefresh(True)
        QTUtil.refresh_gui()

        self.dgt_setposition()

        self.siguiente_jugada()

    def run_action(self, key):
        if key == TB_CLOSE:
            self.finPartida()
            self.procesador.showRoute()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True, siCambioTutor=True)

        elif key == TB_HELP:
            self.ayuda()

        elif key == TB_NEXT:
            if self.route.km_pending():
                self.inicio(self.route)
            else:
                self.finPartida()
                self.procesador.showRoute()

        elif key == TB_UTILITIES:
            self.utilidades()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def jugadaObjetivo(self):
        return self.partida_objetivo.move(self.game.num_moves())

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return

        if len(self.game) == self.partida_objetivo.num_moves():
            self.lineaTerminada()
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()

        is_white = self.game.last_position.is_white

        self.ponIndicador(is_white)
        self.refresh()

        siRival = is_white == self.is_engine_side_white
        if siRival:
            move = self.jugadaObjetivo()
            self.mueve_rival(move.from_sq, move.to_sq, move.promotion)
            self.siguiente_jugada()
        else:
            self.human_is_playing = True
            self.activaColor(is_white)

    def mueve_humano(self, from_sq, to_sq, promotion=None):
        jgSel = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not jgSel:
            return False

        jgObj = self.jugadaObjetivo()
        if jgObj.movimiento() != jgSel.movimiento():
            for pvar in jgObj.pvariantes:
                jgObjV = pvar.move(0)
                if jgObjV.movimiento() == jgSel.movimiento():

                    QTUtil2.mensajeTemporal(
                        self.main_window,
                        _("You have selected one correct move, but the line use %s") % jgObj.pgn_translated(),
                        3,
                        position="ad",
                    )
                    self.ayuda(False)
                    self.sigueHumano()
                    return False
            QTUtil2.mensajeTemporal(self.main_window, _("Wrong move"), 0.8, position="ad")
            self.route.error_tactic(self.partida_objetivo.num_moves())
            self.ponRotulo2(self.route.mens_tactic(False))
            self.sigueHumano()
            return False

        self.move_the_pieces(jgSel.liMovs)

        self.add_move(jgSel, True)
        self.error = ""

        self.siguiente_jugada()
        return True

    def mueve_rival(self, from_sq, to_sq, promotion):
        siBien, mens, move = Move.dameJugada(self.game, self.game.last_position, from_sq, to_sq, promotion)
        self.add_move(move, False)
        self.move_the_pieces(move.liMovs, True)
        return True

    def ayuda(self, siQuitarPuntos=True):
        jgObj = self.jugadaObjetivo()
        liMovs = [(jgObj.from_sq, jgObj.to_sq, True)]
        for pvar in jgObj.pvariantes:
            jg0 = pvar.move(0)
            liMovs.append((jg0.from_sq, jg0.to_sq, False))
        self.tablero.ponFlechasTmp(liMovs)
        if siQuitarPuntos:
            self.route.error_tactic(self.partida_objetivo.num_moves())
            self.ponRotulo2(self.route.mens_tactic(False))

    def lineaTerminada(self):
        self.disable_all()
        self.refresh()
        km = self.route.end_tactic()
        if not self.route.go_fast:
            mensaje = "%s<br>%s" % (_("Done"), _("You have traveled %s") % Routes.km_mi(km, self.route.is_miles))
            self.mensajeEnPGN(mensaje)
        self.human_is_playing = False
        self.state = ST_ENDGAME
        if self.route.go_fast:
            self.run_action(TB_NEXT)
        else:
            li_options = [TB_CLOSE, TB_UTILITIES, TB_NEXT]
            self.main_window.pon_toolbar(li_options)
            self.ponRotulo2(self.route.mens_tactic(True))

    def actualPGN(self):
        resp = '[Event "%s"]\n' % _("Transsiberian Railway")
        resp += '[FEN "%s"\n' % self.game.first_position.fen()

        resp += "\n" + self.game.pgnBase()

        return resp
