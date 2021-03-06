import copy
import datetime
import random

import FasterCode

import Code
from Code import Apertura
from Code import Gestor
from Code import Game
from Code import Adjourns
from Code.QT import PantallaJuicio
from Code.QT import QTUtil2
from Code.SQL import Base
from Code import Util
from Code.SQL import UtilSQL
from Code.Constantes import *


class GestorFideFics(Gestor.Gestor):
    def selecciona(self, tipoJuego):
        self.game_type = tipoJuego
        if tipoJuego == GT_FICS:
            self._db = Code.path_resource("IntFiles", "FicsElo.db")
            self._activo = self.configuracion.ficsActivo
            self._ponActivo = self.configuracion.ponFicsActivo
            self.nombreObj = _("Fics-player")  # self.cabs[ "White" if self.is_human_side_white else "Black" ]
            self._fichEstad = self.configuracion.fichEstadFicsElo
            self._titulo = _("Fics-Elo")
            self._newTitulo = _("New Fics-Elo")
            self._TIPO = "FICS"

        elif tipoJuego == GT_FIDE:
            self._db = Code.path_resource("IntFiles", "FideElo.db")
            self._activo = self.configuracion.fideActivo
            self._ponActivo = self.configuracion.ponFideActivo
            self.nombreObj = _("Fide-player")  # self.cabs[ "White" if self.is_human_side_white else "Black" ]
            self._fichEstad = self.configuracion.fichEstadFideElo
            self._titulo = _("Fide-Elo")
            self._newTitulo = _("New Fide-Elo")
            self._TIPO = "FIDE"

        elif tipoJuego == GT_LICHESS:
            self._db = Code.path_resource("IntFiles", "LichessElo.db")
            self._activo = self.configuracion.lichessActivo
            self._ponActivo = self.configuracion.ponLichessActivo
            self.nombreObj = _("Lichess-player")
            self._fichEstad = self.configuracion.fichEstadLichessElo
            self._titulo = _("Lichess-Elo")
            self._newTitulo = _("New Lichess-Elo")
            self._TIPO = "LICHESS"

    def elige_juego(self, nivel):
        color = self.determinaColor(nivel)
        db = Base.DBBase(self._db)
        dbf = db.dbfT("data", "ROWID", condicion="LEVEL=%d AND WHITE=%d" % (nivel, 1 if color else 0))
        dbf.leer()
        reccount = dbf.reccount()
        recno = random.randint(1, reccount)
        dbf.goto(recno)
        xid = dbf.ROWID
        dbf.cerrar()
        db.cerrar()

        return xid

    def read_id(self, xid):
        db = Base.DBBase(self._db)
        dbf = db.dbfT("data", "LEVEL,WHITE,CABS,MOVS", condicion="ROWID=%d" % xid)
        dbf.leer()
        dbf.gotop()

        self.nivel = dbf.LEVEL

        is_white = dbf.WHITE
        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        pv = FasterCode.xpv_pv(dbf.MOVS)
        self.partidaObj = Game.Game()
        self.partidaObj.read_pv(pv)
        self.posJugadaObj = 0
        self.numJugadasObj = self.partidaObj.num_moves()

        li = dbf.CABS.split("\n")
        for x in li:
            if x:
                key, valor = x.split("=")
                self.game.add_tag(key, valor)

        dbf.cerrar()
        db.cerrar()

    def inicio(self, id_game):
        self.base_inicio(id_game)
        self.siguiente_jugada()

    def base_inicio(self, id_game):
        self.resultado = None
        self.human_is_playing = False
        self.state = ST_PLAYING
        self.analysis = None
        self.comment = None
        self.siAnalizando = False

        self.siCompetitivo = True

        self.read_id(id_game)
        self.id_game = id_game

        self.eloObj = int(self.game.get_tag("WhiteElo" if self.is_human_side_white else "BlackElo"))
        self.eloUsu = self._activo()

        self.pwin = Util.fideELO(self.eloUsu, self.eloObj, +1)
        self.pdraw = Util.fideELO(self.eloUsu, self.eloObj, 0)
        self.plost = Util.fideELO(self.eloUsu, self.eloObj, -1)

        self.puntos = 0

        self.is_tutor_enabled = False
        self.main_window.ponActivarTutor(self.is_tutor_enabled)

        self.ayudas = 0
        self.ayudas_iniciales = 0

        self.xtutor.maximizaMultiPV()

        self.book = Apertura.AperturaPol(999)

        self.pon_toolbar()

        self.main_window.activaJuego(True, False, siAyudas=False)
        self.set_dispatcher(self.mueve_humano)
        self.setposition(self.game.last_position)
        self.ponPiezasAbajo(self.is_human_side_white)
        self.quitaAyudas(True, siQuitarAtras=True)
        self.mostrarIndicador(True)
        rotulo = "%s: <b>%d</b> | %s: <b>%d</b>" % (self._titulo, self.eloUsu, _("Elo rival"), self.eloObj)
        rotulo += " | %+d %+d %+d" % (self.pwin, self.pdraw, self.plost)
        self.ponRotulo1(rotulo)

        self.ponRotulo2("")
        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()

        self.dgt_setposition()

    def ponPuntos(self):
        self.ponRotulo2("%s : <b>%d</b>" % (_("Points"), self.puntos))

    def pon_toolbar(self):
        liTool = (TB_RESIGN, TB_ADJOURN, TB_CONFIG, TB_UTILITIES)
        self.main_window.pon_toolbar(liTool)

    def run_action(self, key):
        if key in (TB_RESIGN, TB_CANCEL):
            self.rendirse()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True)

        elif key == TB_TAKEBACK:
            self.atras()

        elif key == TB_UTILITIES:
            self.utilidadesElo()

        elif key == TB_ADJOURN:
            self.adjourn()

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def adjourn(self):
        if len(self.game) > 0 and QTUtil2.pregunta(self.main_window, _("Do you want to adjourn the game?")):
            dic = {
                "IDGAME": self.id_game,
                "POSJUGADAOBJ": self.posJugadaObj,
                "GAME_SAVE": self.game.save(),
                "PUNTOS": self.puntos,
            }

            with Adjourns.Adjourns() as adj:
                adj.add(self.game_type, dic, self._titulo)
                self.analizaTerminar()
                adj.si_seguimos(self)

    def run_adjourn(self, dic):
        id_game = dic["IDGAME"]
        self.base_inicio(id_game)
        self.posJugadaObj = dic["POSJUGADAOBJ"]
        self.game.restore(dic["GAME_SAVE"])
        self.puntos = dic["PUNTOS"]
        self.mueveJugada(GO_END)
        self.ponPuntos()

        self.siguiente_jugada()

    def final_x(self):
        return self.rendirse()

    def rendirse(self):
        if self.state == ST_ENDGAME:
            self.analizaTerminar()
            return True
        if len(self.game) > 0:
            if not QTUtil2.pregunta(self.main_window, _("Do you want to resign?") + " (%d)" % self.plost):
                return False  # no abandona
            self.puntos = -999
            self.analizaTerminar()
            self.muestra_resultado()
        else:
            self.analizaTerminar()
            self.procesador.inicio()

        return False

    def analizaInicio(self):
        if not self.is_finished():
            self.xtutor.ac_inicio(self.game)
            self.siAnalizando = True

    def analizaEstado(self):
        self.xtutor.engine.ac_lee()
        self.mrm = copy.deepcopy(self.xtutor.ac_estado())
        return self.mrm

    def analizaMinimo(self, minTime):
        self.mrm = copy.deepcopy(self.xtutor.ac_minimo(minTime, False))
        return self.mrm

    def analizaFinal(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xtutor.ac_final(-1)

    def analizaTerminar(self):
        if self.siAnalizando:
            self.siAnalizando = False
            self.xtutor.terminar()

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()
        is_white = self.game.last_position.is_white

        num_moves = len(self.game)
        if num_moves >= self.numJugadasObj:
            self.muestra_resultado()
            return

        siRival = is_white == self.is_engine_side_white
        self.ponIndicador(is_white)

        self.refresh()

        if siRival:
            self.add_move(False)
            self.siguiente_jugada()
        else:

            self.human_is_playing = True
            self.pensando(True)
            if self.continueTt:
                self.analizaInicio()
            self.activaColor(is_white)
            self.pensando(False)

    def mueve_humano(self, from_sq, to_sq, promotion=""):
        jgUsu = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not jgUsu:
            return False

        jgObj = self.partidaObj.move(self.posJugadaObj)

        analisis = None
        comment = None

        comentarioUsu = ""
        comentarioObj = ""

        siAnalizaJuez = jgUsu.movimiento() != jgObj.movimiento()
        if self.book:
            fen = self.fenUltimo()
            siBookUsu = self.book.check_human(fen, from_sq, to_sq)
            siBookObj = self.book.check_human(fen, jgObj.from_sq, jgObj.to_sq)
            if siBookUsu:
                comentarioUsu = _("book move")
            if siBookObj:
                comentarioObj = _("book move")
            if siBookUsu and siBookObj:
                if jgObj.movimiento() != jgUsu.movimiento():
                    # comment = "%s: %s" % (_("Same book move"), jgObj.pgn_translated())
                    # else:
                    bmove = _("book move")
                    comment = "%s: %s %s\n%s: %s %s" % (
                        self.nombreObj,
                        jgObj.pgn_translated(),
                        bmove,
                        self.configuracion.x_player,
                        jgUsu.pgn_translated(),
                        bmove,
                    )
                    w = PantallaJuicio.MensajeF(self.main_window, comment)
                    w.mostrar()
                siAnalizaJuez = False
            else:
                if not siBookObj:
                    self.book = None

        if siAnalizaJuez:
            um = QTUtil2.analizando(self.main_window)
            if not self.continueTt:
                self.analizaInicio()
            mrm = self.analizaMinimo(5000)
            position = self.game.last_position

            rmUsu, nada = mrm.buscaRM(jgUsu.movimiento())
            if rmUsu is None:
                self.analizaFinal()
                rmUsu = self.xtutor.valora(position, jgUsu.from_sq, jgUsu.to_sq, jgUsu.promotion)
                mrm.agregaRM(rmUsu)
                self.analizaInicio()

            rmObj, posObj = mrm.buscaRM(jgObj.movimiento())
            if rmObj is None:
                self.analizaFinal()
                rmObj = self.xtutor.valora(position, jgObj.from_sq, jgObj.to_sq, jgObj.promotion)
                posObj = mrm.agregaRM(rmObj)
                self.analizaInicio()

            analisis = mrm, posObj
            um.final()

            w = PantallaJuicio.WJuicio(self, self.xtutor, self.nombreObj, position, mrm, rmObj, rmUsu, analisis)
            w.exec_()

            analisis = w.analysis
            dpts = w.difPuntos()

            self.puntos += dpts
            self.ponPuntos()

            comentarioUsu += " %s" % (rmUsu.abrTexto())
            comentarioObj += " %s" % (rmObj.abrTexto())

            comentarioPuntos = "%s = %d %+d %+d = %d" % (
                _("Points"),
                self.puntos - dpts,
                rmUsu.centipawns_abs(),
                -rmObj.centipawns_abs(),
                self.puntos,
            )

            comment = "%s: %s %s\n%s: %s %s\n%s" % (
                self.nombreObj,
                jgObj.pgn_translated(),
                comentarioObj,
                self.configuracion.x_player,
                jgUsu.pgn_translated(),
                comentarioUsu,
                comentarioPuntos,
            )

        self.analizaFinal()

        self.add_move(True, comment, analisis)
        self.siguiente_jugada()
        return True

    def add_move(self, siNuestra, comment=None, analisis=None):

        move = self.partidaObj.move(self.posJugadaObj)
        self.posJugadaObj += 1
        if analisis:
            move.analysis = analisis
        if comment:
            move.comment = comment

        if comment:
            self.comment = comment.replace("\n", "<br><br>") + "<br>"

        if not siNuestra:
            if self.posJugadaObj:
                self.comment = None

        self.game.add_move(move)
        self.move_the_pieces(move.liMovs, True)
        self.tablero.setposition(move.position)
        self.ponFlechaSC(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

        self.dgt_setposition()

    def muestra_resultado(self):
        self.analizaTerminar()
        self.disable_all()
        self.human_is_playing = False

        self.state = ST_ENDGAME

        if self.puntos < -50:
            mensaje = _X(_("Unfortunately you have lost against %1."), self.nombreObj)
            quien = RS_WIN_OPPONENT
            difelo = self.plost
        elif self.puntos > 50:
            mensaje = _X(_("Congratulations you have won against %1."), self.nombreObj)
            quien = RS_WIN_PLAYER
            difelo = self.pwin
        else:
            mensaje = _X(_("Draw against %1."), self.nombreObj)
            quien = RS_DRAW
            difelo = self.pdraw

        self.beepResultadoCAMBIAR(quien)

        nelo = self.eloUsu + difelo
        if nelo < 0:
            nelo = 0
        self._ponActivo(nelo)

        self.historial(self.eloUsu, nelo)
        self.configuracion.graba()

        mensaje += "<br><br>%s : %d<br>" % (self._newTitulo, self._activo())

        self.mensajeEnPGN(mensaje)
        self.ponFinJuego()

    def historial(self, elo, nelo):
        dic = {}
        dic["FECHA"] = datetime.datetime.now()
        dic["NIVEL"] = self.nivel
        dic["RESULTADO"] = self.resultado
        dic["AELO"] = elo
        dic["NELO"] = nelo

        lik = UtilSQL.ListSQL(self._fichEstad)
        lik.append(dic)
        lik.close()

        dd = UtilSQL.DictSQL(self._fichEstad, tabla="color")
        key = "%s-%d" % (self._TIPO, self.nivel)
        dd[key] = self.is_human_side_white
        dd.close()

    def determinaColor(self, nivel):
        key = "%s-%d" % (self._TIPO, nivel)

        dd = UtilSQL.DictSQL(self._fichEstad, tabla="color")
        previo = dd.get(key, random.randint(0, 1) == 0)
        dd.close()
        return not previo

    def atras(self):
        if len(self.game) > 2:
            self.analizaFinal()
            ndel = self.game.anulaUltimoMovimiento(self.is_human_side_white)
            self.game.assign_opening()
            self.posJugadaObj -= ndel
            self.analysis = None
            self.goto_end()
            self.refresh()
            self.siguiente_jugada()
