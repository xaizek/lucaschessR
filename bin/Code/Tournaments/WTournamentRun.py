import time

from PySide2 import QtWidgets, QtCore

import Code
from Code import Util
from Code import Game
from Code import Move
from Code.Polyglots import Books
from Code import ControlPGN
from Code.Engines import EngineManager
from Code.SQL import UtilSQL
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Delegados
from Code.QT import Controles
from Code.QT import Tablero
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import QTUtil
from Code.QT import QTVarios
from Code.Tournaments import Tournament
from Code.Constantes import *


class TournamentRun:
    def __init__(self, file_tournament):
        self.file_tournament = file_tournament
        with self.tournament() as torneo:
            self.run_name = torneo.name()
            self.run_drawRange = torneo.drawRange()
            self.run_drawMinPly = torneo.drawMinPly()
            self.run_resign = torneo.resign()
            self.run_bookDepth = torneo.bookDepth()

    def name(self):
        return self.run_name

    def drawRange(self):
        return self.run_drawRange

    def drawMinPly(self):
        return self.run_drawMinPly

    def resign(self):
        return self.run_resign

    def bookDepth(self):
        return self.run_bookDepth

    def tournament(self):
        return Tournament.Tournament(self.file_tournament)

    def get_game_queued(self, file_work):
        with self.tournament() as torneo:
            self.run_name = torneo.name()
            self.run_drawRange = torneo.drawRange()
            self.run_drawMinPly = torneo.drawMinPly()
            self.run_resign = torneo.resign()
            self.run_bookDepth = torneo.bookDepth()
            return torneo.get_game_queued(file_work)

    def fenNorman(self):
        with self.tournament() as torneo:
            return torneo.fenNorman()

    def adjudicator_active(self):
        with self.tournament() as torneo:
            return torneo.adjudicator_active()

    def adjudicator(self):
        with self.tournament() as torneo:
            return torneo.adjudicator()

    def adjudicator_time(self):
        with self.tournament() as torneo:
            return torneo.adjudicator_time()

    def buscaHEngine(self, h):
        with self.tournament() as torneo:
            return torneo.buscaHEngine(h)

    def book(self):
        with self.tournament() as torneo:
            return torneo.book()

    def game_done(self, game):
        with self.tournament() as torneo:
            return torneo.game_done(game)

    def close(self):
        pass


class WTournamentRun(QtWidgets.QWidget):
    def __init__(self, file_tournament, file_work):
        QtWidgets.QWidget.__init__(self)

        Code.list_engine_managers = EngineManager.ListEngineManagers()
        self.torneo = TournamentRun(file_tournament)  # Tournament.Tournament(file_tournament)
        self.file_work = file_work
        self.db_work = UtilSQL.ListSQL(file_work)

        self.setWindowTitle("%s - %s %d" % (self.torneo.name(), _("Worker"), int(file_work[-5:])))
        self.setWindowIcon(Iconos.Torneos())

        # Toolbar
        self.tb = Controles.TBrutina(self, tamIcon=24)

        # Tablero
        conf_tablero = Code.configuracion.config_board("TOURNEYPLAY", 36)
        self.tablero = Tablero.Tablero(self, conf_tablero)
        self.tablero.crea()
        Delegados.generaPM(self.tablero.piezas)

        # PGN
        self.configuracion = Code.configuracion
        self.game = Game.Game()
        self.pgn = ControlPGN.ControlPGN(self)
        ly_pgn = self.crea_bloque_informacion()

        self.is_closed = False
        self.state = None
        self.current_side = WHITE

        ly_tt = Colocacion.V().control(self.tb).control(self.tablero)

        layout = Colocacion.H().otro(ly_tt).otro(ly_pgn).relleno().margen(3)
        self.setLayout(layout)

        self.pon_estado(ST_WAITING)

    def pon_estado(self, state):
        self.state = state
        self.pon_toolbar(state)

    def pon_toolbar(self, state):
        li_acciones = [(_("Close"), Iconos.Close(), self.close), None]
        if state == ST_PLAYING:
            li_acciones.extend(
                [
                    (_("Pause"), Iconos.Pause(), self.pausa),
                    None,
                    (_("Adjudication"), Iconos.EndGame(), self.adjudication),
                    None,
                ]
            )
        elif state == ST_PAUSE:
            li_acciones.extend(
                [
                    (_("Continue"), Iconos.Continue(), self.seguir),
                    None,
                    (_("Adjudication"), Iconos.EndGame(), self.adjudication),
                    None,
                ]
            )
        self.tb.reset(li_acciones)

    def crea_bloque_informacion(self):
        configuracion = Code.configuracion
        n_ancho_pgn = configuracion.x_pgn_width
        n_ancho_color = (n_ancho_pgn - 52 - 24) // 2
        n_ancho_labels = max(int((n_ancho_pgn - 3) // 2), 140)
        # # Pgn
        o_columnas = Columnas.ListaColumnas()
        o_columnas.nueva("NUMERO", _("N."), 52, centered=True)
        si_figurines_pgn = configuracion.x_pgn_withfigurines
        o_columnas.nueva(
            "BLANCAS", _("White"), n_ancho_color, edicion=Delegados.EtiquetaPGN(True if si_figurines_pgn else None)
        )
        o_columnas.nueva(
            "NEGRAS", _("Black"), n_ancho_color, edicion=Delegados.EtiquetaPGN(False if si_figurines_pgn else None)
        )
        self.grid_pgn = Grid.Grid(self, o_columnas, siCabeceraMovible=False)
        self.grid_pgn.setMinimumWidth(n_ancho_pgn)
        self.grid_pgn.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.grid_pgn.tipoLetra(puntos=configuracion.x_pgn_fontpoints)
        self.grid_pgn.ponAltoFila(configuracion.x_pgn_rowheight)

        # # Blancas y negras
        f = Controles.TipoLetra(puntos=configuracion.x_sizefont_infolabels + 2, peso=75)
        bl, ng = "", ""
        alto_lb = 48
        self.lb_player = {}
        for side in (WHITE, BLACK):
            self.lb_player[side] = Controles.LB(self, bl).anchoFijo(n_ancho_labels).altoFijo(alto_lb)
            self.lb_player[side].alinCentrado().ponFuente(f).ponWrap()
            self.lb_player[side].setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)
        self.lb_player[WHITE].ponColorFondoN("black", "white")
        self.lb_player[BLACK].ponColorFondoN("white", "black")

        # Relojes
        f = Controles.TipoLetra("Arial Black", puntos=26, peso=75)

        self.lb_reloj = {}
        for side in (WHITE, BLACK):
            self.lb_reloj[side] = (
                Controles.LB(self, "00:00")
                .ponFuente(f)
                .alinCentrado()
                .ponColorFondoN("#076C9F", "#EFEFEF")
                .anchoMinimo(n_ancho_labels)
            )
            self.lb_reloj[side].setFrameStyle(QtWidgets.QFrame.Box | QtWidgets.QFrame.Raised)

        # Rotulos de informacion
        f = Controles.TipoLetra(puntos=configuracion.x_sizefont_infolabels)
        self.lbRotulo3 = Controles.LB(self).ponWrap().ponFuente(f)

        # Layout
        lyColor = Colocacion.G()
        lyColor.controlc(self.lb_player[WHITE], 0, 0).controlc(self.lb_player[BLACK], 0, 1)
        lyColor.controlc(self.lb_reloj[WHITE], 1, 0).controlc(self.lb_reloj[BLACK], 1, 1)

        # Abajo
        lyAbajo = Colocacion.V()
        lyAbajo.setSizeConstraint(lyAbajo.SetFixedSize)
        lyAbajo.control(self.lbRotulo3)

        lyV = Colocacion.V().otro(lyColor).control(self.grid_pgn)
        lyV.otro(lyAbajo).margen(7)

        return lyV

    def grid_num_datos(self, grid):
        return self.pgn.numDatos()

    def busca_trabajo(self):
        if self.torneo:
            self.tournament_game = self.torneo.get_game_queued(self.file_work)
            if self.tournament_game is None:
                return
            self.procesa_game()
            if not self.is_closed:
                self.busca_trabajo()

    def procesa_game(self):
        self.pon_estado(ST_PLAYING)

        # Configuración
        self.fen_inicial = self.torneo.fenNorman()

        # Cerramos los motores anteriores si los hay
        Code.list_engine_managers.close_all()

        if self.torneo.adjudicator_active():
            conf_engine = Code.configuracion.buscaRival(self.torneo.adjudicator())
            self.xadjudicator = EngineManager.EngineManager(self, conf_engine)
            self.xadjudicator.opciones(self.torneo.adjudicator_time() * 1000, 0, False)
            self.xadjudicator.anulaMultiPV()
        else:
            self.xadjudicator = None
        self.next_control = 0

        self.max_segundos = self.tournament_game.minutos * 60.0
        self.segundos_jugada = self.tournament_game.segundos_jugada

        # abrimos motores
        rival = {
            WHITE: self.torneo.buscaHEngine(self.tournament_game.hwhite),
            BLACK: self.torneo.buscaHEngine(self.tournament_game.hblack),
        }
        for side in (WHITE, BLACK):
            self.lb_player[side].ponTexto(rival[side].name)

        self.vtime = {}

        self.book = {}
        self.bookRR = {}

        self.xengine = {}

        for side in (WHITE, BLACK):
            rv = rival[side]
            self.xengine[side] = EngineManager.EngineManager(self, rv)
            self.xengine[side].opciones(rv.time * 1000, rv.depth, False)
            self.xengine[side].ponGuiDispatch(self.gui_dispatch)

            self.vtime[side] = Util.Timer(self.max_segundos)

            bk = rv.book
            if bk == "*":
                bk = self.torneo.book()
            if bk == "-":  # Puede que el torneo tenga "-"
                bk = None
            if bk:
                self.book[side] = Books.Libro("P", bk, bk, True)
                self.book[side].polyglot()
            else:
                self.book[side] = None
            self.bookRR[side] = rv.bookRR

        self.game = Game.Game(fen=self.fen_inicial)
        self.pgn.game = self.game

        self.lbRotulo3.altoFijo(32)

        self.tablero.disable_all()
        self.tablero.ponPosicion(self.game.last_position)
        self.grid_pgn.refresh()

        for side in (WHITE, BLACK):
            ot = self.vtime[side]
            eti, eti2 = ot.etiquetaDif2()
            self.pon_reloj_side(side, eti, eti2)

        while self.state == ST_PAUSE or self.siguiente_jugada():
            if self.state == ST_PAUSE:
                QTUtil.refresh_gui()
                time.sleep(0.1)
            if self.is_closed:
                break
        for side in (WHITE, BLACK):
            self.xengine[side].terminar()

        if not self.is_closed:
            if self.game_finished():
                self.save_game_done()

    def save_game_done(self):
        self.game.add_tag("Site", Code.lucas_chess)
        self.game.add_tag("Event", self.torneo.name())

        hoy = Util.today()
        self.game.add_tag("Date", "%d-%02d-%02d" % (hoy.year, hoy.month, hoy.day))

        motor_white = self.xengine[WHITE].confMotor
        motor_black = self.xengine[BLACK].confMotor
        self.game.add_tag("White", motor_white.name)
        self.game.add_tag("Black", motor_black.name)
        if motor_white.elo:
            self.game.add_tag("WhiteElo", motor_white.elo)
        if motor_black.elo:
            self.game.add_tag("BlackElo", motor_black.elo)

        self.game.set_extend_tags()
        self.game.sort_tags()

        self.tournament_game.result = self.game.result
        self.tournament_game.game_save = self.game.save(True)
        self.torneo.game_done(self.tournament_game)

    def terminar(self):
        self.is_closed = True
        if self.torneo:
            Code.list_engine_managers.close_all()
            self.torneo.close()
            self.db_work.close()
            self.torneo = None
            self.db_work = None
            Util.remove_file(self.file_work)

    def closeEvent(self, event):
        self.terminar()

    def pausa(self):
        self.pon_estado(ST_PAUSE)

    def seguir(self):
        self.pon_estado(ST_PLAYING)

    def adjudication(self):
        self.pon_estado(ST_PAUSE)
        QTUtil.refresh_gui()
        menu = QTVarios.LCMenu(self)
        menu.opcion(RESULT_DRAW, RESULT_DRAW, Iconos.Tablas())
        menu.separador()
        menu.opcion(RESULT_WIN_WHITE, RESULT_WIN_WHITE, Iconos.Blancas())
        menu.separador()
        menu.opcion(RESULT_WIN_BLACK, RESULT_WIN_BLACK, Iconos.Negras())
        resp = menu.lanza()
        if resp is not None:
            self.game.set_termination(TERMINATION_ADJUDICATION, resp)
            self.save_game_done()

    def pon_reloj(self):
        if self.is_closed or self.game_finished():
            return False

        ot = self.vtime[self.current_side]

        eti, eti2 = ot.etiquetaDif2()
        if eti:
            self.pon_reloj_side(self.current_side, eti, eti2)

        if ot.siAgotado():
            self.game.set_termination_time()
            return False

        QTUtil.refresh_gui()
        return True

    def pon_reloj_side(self, side, tm, tm2):
        if tm2 is not None:
            tm += '<br><FONT SIZE="-4">' + tm2
        self.lb_reloj[side].ponTexto(tm)

    def reloj_start(self, is_white):
        self.vtime[is_white].iniciaMarcador()

    def reloj_stop(self, is_white):
        self.vtime[is_white].paraMarcador(self.segundos_jugada)
        self.pon_reloj()

    def reloj_pause(self, is_white):
        self.vtime[is_white].anulaMarcador()
        self.pon_reloj()

    def eligeJugadaBook(self, book, tipo):
        bdepth = self.torneo.bookDepth()
        if bdepth == 0 or len(self.game) < bdepth:
            fen = self.fenUltimo()
            pv = book.eligeJugadaTipo(fen, tipo)
            if pv:
                return True, pv[:2], pv[2:4], pv[4:]
        return False, None, None, None

    def add_move(self, move):
        self.game.add_move(move)

        self.tablero.borraMovibles()
        self.tablero.ponFlechaSC(move.from_sq, move.to_sq)
        self.grid_pgn.refresh()
        self.grid_pgn.gobottom(2 if self.game.last_position.is_white else 1)

        self.refresh()

    def refresh(self):
        self.tablero.escena.update()
        self.update()
        QTUtil.refresh_gui()

    def game_finished(self):
        return self.game.termination != TERMINATION_UNKNOWN

    def showPV(self, pv, nArrows):
        if not pv:
            return True
        self.tablero.quitaFlechas()
        tipo = "mt"
        opacidad = 100
        pv = pv.strip()
        while "  " in pv:
            pv = pv.replace("  ", " ")
        lipv = pv.split(" ")
        npv = len(lipv)
        nbloques = min(npv, nArrows)
        salto = (80 - 15) * 2 / (nbloques - 1) if nbloques > 1 else 0
        cambio = max(30, salto)

        for n in range(nbloques):
            pv = lipv[n]
            self.tablero.creaFlechaMov(pv[:2], pv[2:4], tipo + str(opacidad))
            if n % 2 == 1:
                opacidad -= cambio
                cambio = salto
            tipo = "ms" if tipo == "mt" else "mt"
        return True

    def siguiente_jugada(self):
        if self.test_is_finished():
            return False

        self.current_side = is_white = self.game.is_white()

        self.tablero.ponIndicador(is_white)

        move_found = False
        analisis = None
        bk = self.book[is_white]
        if bk:
            move_found, from_sq, to_sq, promotion = self.eligeJugadaBook(bk, self.bookRR[is_white])
            if not move_found:
                self.book[is_white] = None

        if not move_found:
            xrival = self.xengine[is_white]
            tiempoBlancas = self.vtime[True].tiempoPendiente
            tiempoNegras = self.vtime[False].tiempoPendiente
            segundosJugada = xrival.motorTiempoJugada
            self.reloj_start(is_white)
            mrm = xrival.juegaTiempoTorneo(self.game, tiempoBlancas, tiempoNegras, segundosJugada)
            if self.state == ST_PAUSE:
                self.reloj_pause(is_white)
                self.tablero.borraMovibles()
                return True
            self.reloj_stop(is_white)
            if mrm is None:
                return False
            rm = mrm.mejorMov()
            from_sq = rm.from_sq
            to_sq = rm.to_sq
            promotion = rm.promotion
            analisis = mrm, 0

        siBien, mens, move = Move.dameJugada(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if not move:
            return False
        if analisis:
            move.analysis = analisis
            move.del_nags()
        self.add_move(move)
        self.move_the_pieces(move.liMovs)

        return True

    def grid_dato(self, grid, fila, oColumna):
        controlPGN = self.pgn

        col = oColumna.clave
        if col == "NUMERO":
            return controlPGN.dato(fila, col)

        move = controlPGN.soloJugada(fila, col)
        if move is None:
            return ""

        color = None
        info = ""
        indicador_inicial = None

        stNAGS = set()

        if move.analysis:
            mrm, pos = move.analysis
            rm = mrm.li_rm[pos]
            mate = rm.mate
            si_w = move.position_before.is_white
            if mate:
                if mate == 1:
                    info = ""
                else:
                    if not si_w:
                        mate = -mate
                    info = "(M%+d)" % mate
            else:
                pts = rm.puntos
                if not si_w:
                    pts = -pts
                info = "(%+0.2f)" % float(pts / 100.0)

            nag, color_nag = mrm.set_nag_color(self.configuracion, rm)
            stNAGS.add(nag)

        if move.in_the_opening:
            indicador_inicial = "R"

        pgn = move.pgnFigurinesSP() if self.configuracion.x_pgn_withfigurines else move.pgn_translated()

        return pgn, color, info, indicador_inicial, stNAGS

    def gui_dispatch(self, rm):
        if self.is_closed or self.state != ST_PLAYING:
            return False
        if not rm.sinInicializar:
            p = Game.Game(self.game.last_position)
            p.read_pv(rm.pv)
            rm.is_white = self.game.last_position.is_white
            txt = "<b>[%s]</b> (%s) %s" % (rm.name, rm.abrTexto(), p.pgn_translated())
            self.lbRotulo3.ponTexto(txt)
            self.showPV(rm.pv, 1)
        return self.pon_reloj()

    def clocks_finished(self):
        if self.vtime[WHITE].siAgotado():
            self.game.set_termination(TERMINATION_WIN_ON_TIME, RESULT_WIN_BLACK)
            return True
        if self.vtime[BLACK].siAgotado():
            self.game.set_termination(TERMINATION_WIN_ON_TIME, RESULT_WIN_WHITE)
            return True
        return False

    def test_is_finished(self):
        if self.clocks_finished():
            return True

        num_moves = len(self.game)
        if num_moves == 0:
            return False

        if self.state != ST_PLAYING or self.is_closed or self.game_finished() or self.game.is_finished():
            return True

        if num_moves < 2:
            return False

        self.next_control -= 1
        if self.next_control > 0 and self.xadjudicator:
            return False
        self.next_control = 20

        last_jg = self.game.last_jg()
        mrm, pos = last_jg.analysis
        rmUlt = mrm.li_rm[pos]
        jgAnt = self.game.move(-2)
        mrm, pos = jgAnt.analysis
        rmAnt = mrm.li_rm[pos]

        # Draw
        pUlt = rmUlt.centipawns_abs()
        pAnt = rmAnt.centipawns_abs()
        dr = self.torneo.drawRange()
        if dr > 0 and num_moves >= self.torneo.drawMinPly():
            if abs(pUlt) <= dr and abs(pAnt) <= dr:
                if self.xadjudicator:
                    mrmTut = self.xadjudicator.analiza(self.game.last_position.fen())
                    rmTut = mrmTut.mejorMov()
                    pTut = rmTut.centipawns_abs()
                    if abs(pTut) <= dr:
                        self.game.set_termination(TERMINATION_ADJUDICATION, RESULT_DRAW)
                        return True
                    return False
                else:
                    self.game.set_termination(TERMINATION_ADJUDICATION, RESULT_DRAW)
                    return True

        # Resign
        rs = self.torneo.resign()
        if 0 < rs <= abs(pUlt):
            if self.xadjudicator:
                rmTut = self.xadjudicator.juegaPartida(self.game)
                pTut = rmTut.centipawns_abs()
                if abs(pTut) >= rs:
                    is_white = self.game.last_position.is_white
                    if pTut > 0:
                        result = RESULT_WIN_WHITE if is_white else RESULT_WIN_BLACK
                    else:
                        result = RESULT_WIN_BLACK if is_white else RESULT_WIN_WHITE
                    self.game.set_termination(TERMINATION_ADJUDICATION, result)
                    return True
            else:
                if rs <= abs(pAnt):
                    if (pAnt > 0 and pUlt > 0) or (pAnt < 0 and pUlt < 0):
                        result = RESULT_WIN_WHITE if pUlt > 0 else RESULT_WIN_BLACK
                        self.game.set_termination(TERMINATION_ADJUDICATION, result)
                        return True

        return False

    def move_the_pieces(self, liMovs):
        for movim in liMovs:
            if movim[0] == "b":
                self.tablero.borraPieza(movim[1])
            elif movim[0] == "m":
                self.tablero.muevePieza(movim[1], movim[2])
            elif movim[0] == "c":
                self.tablero.cambiaPieza(movim[1], movim[2])
