from Code import Apertura
from Code import Gestor
from Code import Move
from Code.QT import QTUtil2
from Code import Util
from Code.Engines import EngineResponse
from Code.Constantes import *


class GestorResistance(Gestor.Gestor):
    def inicio(self, resistance, numEngine, key):

        self.game_type = GT_RESISTANCE

        self.resistance = resistance
        self.numEngine = numEngine
        self.key = key
        is_white = "BLANCAS" in key
        self.segundos, self.puntos, self.maxerror = resistance.actual()
        self.movimientos = 0
        self.puntosRival = 0

        self.human_is_playing = False
        self.state = ST_PLAYING

        self.is_human_side_white = is_white
        self.is_engine_side_white = not is_white

        self.siBoxing = True

        self.rm_rival = None

        self.in_the_opening = False
        self.opening = Apertura.AperturaPol(5)  # lee las aperturas

        # debe hacerse antes que rival
        self.xarbitro = self.procesador.creaGestorMotor(self.configuracion.tutor, self.segundos * 1000, None)
        self.xarbitro.anulaMultiPV()

        engine = resistance.dameClaveEngine(numEngine)
        rival = self.configuracion.buscaRival(engine)
        self.xrival = self.procesador.creaGestorMotor(rival, self.segundos * 1000, None)

        self.main_window.pon_toolbar((TB_RESIGN, TB_REINIT, TB_CONFIG, TB_UTILITIES))
        self.main_window.activaJuego(True, False, siAyudas=False)
        self.set_dispatcher(self.mueve_humano)
        self.setposition(self.game.last_position)
        self.ponPiezasAbajo(is_white)
        self.quitaAyudas()
        self.ponActivarTutor(False)
        self.mostrarIndicador(True)
        self.ponRotuloObjetivo()
        self.ponRotuloActual()
        self.pgnRefresh(True)
        self.ponCapInfoPorDefecto()
        self.dgt_setposition()

        tp = self.resistance.tipo
        if tp:
            b = n = False
            if tp == "p2":
                if is_white:
                    b = True
                else:
                    n = True
            elif tp == "p1":
                if is_white:
                    n = True
                else:
                    b = True
            self.tablero.mostrarPiezas(b, n)

        self.siguiente_jugada()

    def ponRotuloObjetivo(self):
        rotulo = self.resistance.rotuloActual()
        rotulo += "<br><br><b>%s</b>: %s" % (_("Opponent"), self.xrival.name)
        rotulo += "<br><b>%s</b>: %s" % (_("Record"), self.resistance.dameEtiRecord(self.key, self.numEngine))

        self.ponRotulo1(rotulo)

    def ponRotuloActual(self):
        rotulo = "<b>%s</b>: %d" % (_("Moves"), self.movimientos)

        color = "black"
        if self.puntosRival != 0:
            color = "red" if self.puntosRival > 0 else "green"

        rotulo += '<br><b>%s</b>: <font color="%s"><b>%d</b></font>' % (_("Points"), color, -self.puntosRival)

        self.ponRotulo2(rotulo)

    def run_action(self, key):
        if key == TB_RESIGN:
            self.finJuego(False)

        elif key == TB_CLOSE:
            self.procesador.pararMotores()
            self.procesador.inicio()
            self.procesador.entrenamientos.resistance(self.resistance.tipo)

        elif key == TB_REINIT:
            self.reiniciar()

        elif key == TB_CONFIG:
            self.configurar(siSonidos=True, siCambioTutor=False, siBlinfold=False)

        elif key == TB_UTILITIES:
            self.utilidades(siArbol=self.state == ST_ENDGAME)

        elif key in self.procesador.li_opciones_inicio:
            self.procesador.run_action(key)

        else:
            Gestor.Gestor.rutinaAccionDef(self, key)

    def reiniciar(self):
        if len(self.game) and QTUtil2.pregunta(self.main_window, _("Restart the game?")):
            self.game.set_position()
            self.inicio(self.resistance, self.numEngine, self.key)

    def final_x(self):
        return self.finJuego(False)

    def siguiente_jugada(self):
        if self.state == ST_ENDGAME:
            return

        self.ponRotuloActual()

        self.state = ST_PLAYING

        self.human_is_playing = False
        self.put_view()
        is_white = self.game.last_position.is_white

        if self.game.is_finished():
            if self.game.is_mate():
                si_ganado = self.is_human_side_white != is_white
                if si_ganado:
                    self.movimientos += 2001
                self.finJuego(True)
                self.guardarGanados(si_ganado)
                return
            if self.game.is_draw():
                self.movimientos += 1001
                self.finJuego(True)
                self.guardarGanados(False)
                return

        siRival = is_white == self.is_engine_side_white
        self.ponIndicador(is_white)

        self.refresh()

        if siRival:
            self.pensando(True)
            self.disable_all()

            siPensar = True

            puntosRivalPrevio = self.puntosRival

            if self.in_the_opening:
                siBien, from_sq, to_sq, promotion = self.opening.run_engine(self.fenUltimo())
                if siBien:
                    self.rm_rival = EngineResponse.EngineResponse("Apertura", self.is_engine_side_white)
                    self.rm_rival.from_sq = from_sq
                    self.rm_rival.to_sq = to_sq
                    self.rm_rival.promotion = promotion
                    siPensar = False

            if siPensar:
                self.rm_rival = self.xrival.juegaSegundos(self.segundos)
                self.puntosRival = self.rm_rival.centipawns_abs()
                self.ponRotuloActual()
            self.pensando(False)

            if self.mueve_rival(self.rm_rival):
                lostmovepoints = self.puntosRival - puntosRivalPrevio
                if self.siBoxing and self.puntosRival > self.puntos:
                    if self.comprueba():
                        return
                if self.siBoxing and self.maxerror and lostmovepoints > self.maxerror:
                    if self.comprueba():
                        return

                self.siguiente_jugada()
        else:

            self.human_is_playing = True
            self.activaColor(is_white)

    def comprueba(self):
        self.disable_all()
        if self.xrival.confMotor.clave != self.xarbitro.confMotor.clave:
            if self.segundos > 10:
                sc = 10
            elif self.segundos < 3:
                sc = 3
            else:
                sc = self.segundos

            um = QTUtil2.mensEspera.inicio(self.main_window, _("Checking..."))

            rm = self.xarbitro.juegaSegundos(sc)
            um.final()
            previoRival = self.puntosRival
            self.puntosRival = -rm.centipawns_abs()
            self.ponRotuloActual()
            if self.maxerror:
                lostmovepoints = self.puntosRival - previoRival
                if lostmovepoints > self.maxerror:
                    self.movimientos -= 1
                    return self.finJuego(False)

        if self.puntosRival > self.puntos:
            self.movimientos -= 1
            return self.finJuego(False)

        return False

    def finJuego(self, siFinPartida):
        if self.siBoxing and self.movimientos:
            siRecord = self.resistance.put_result(self.numEngine, self.key, self.movimientos)
            if siRecord:
                txt = "<h2>%s<h2>" % (_("New record!"))
                txt += "<h3>%s<h3>" % (self.resistance.dameEtiRecord(self.key, self.numEngine))
                self.ponRotuloObjetivo()
            else:
                if siFinPartida:
                    txt = "<h2>%s<h2>" % (_("Game ended"))
                    txt += "<h3>%s<h3>" % (self.resistance.dameEti(Util.today(), self.movimientos))
                else:
                    txt = "<h3>%s</h3>" % (_X(_("You have lost %1 points."), str(-self.puntosRival)))

            if siFinPartida:
                self.mensajeEnPGN(txt)
            else:
                resp = QTUtil2.pregunta(
                    self.main_window,
                    txt + "<br>%s" % (_("Do you want to resign or continue playing?")),
                    label_yes=_("Resign"),
                    label_no=_("Continue"),
                )
                if not resp:
                    self.siBoxing = False
                    return False

        self.disable_all()
        self.state = ST_ENDGAME
        self.procesador.pararMotores()
        self.xarbitro.terminar()
        self.main_window.ajustaTam()
        self.main_window.resize(0, 0)
        if self.movimientos >= 1:
            li_options = [TB_CLOSE, TB_CONFIG, TB_UTILITIES]
            self.main_window.pon_toolbar(li_options)
        else:
            self.run_action(TB_CLOSE)

        return True

    def mueve_humano(self, from_sq, to_sq, promotion=None):
        move = self.checkmueve_humano(from_sq, to_sq, promotion)
        if not move:
            return False

        if self.in_the_opening:
            self.opening.check_human(self.fenUltimo(), from_sq, to_sq)

        self.move_the_pieces(move.liMovs)

        self.add_move(move, True)
        self.error = ""
        self.movimientos += 1
        self.siguiente_jugada()
        return True

    def add_move(self, move, siNuestra):
        self.game.add_move(move)

        self.ponFlechaSC(move.from_sq, move.to_sq)
        self.beepExtendido(siNuestra)

        self.pgnRefresh(self.game.last_position.is_white)
        self.refresh()

        self.dgt_setposition()

    def mueve_rival(self, respMotor):
        from_sq = respMotor.from_sq
        to_sq = respMotor.to_sq

        promotion = respMotor.promotion

        siBien, mens, move = Move.dameJugada(self.game, self.game.last_position, from_sq, to_sq, promotion)
        if siBien:
            self.error = ""
            self.add_move(move, False)
            self.move_the_pieces(move.liMovs, True)

            return True
        else:
            self.error = mens
            return False
