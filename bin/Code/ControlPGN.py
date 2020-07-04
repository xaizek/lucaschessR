import collections

import Code
from Code import Util
from Code.Constantes import *


class ControlPGN:
    def __init__(self, gestor):
        self.gestor = gestor
        self.siFigurines = Code.configuracion.x_pgn_withfigurines
        # self.game = self.gestor.game
        self.siMostrar = True

    def numDatos(self):
        if self.gestor.game:
            n = len(self.gestor.game)
            if self.gestor.game.if_starts_with_black:
                n += 1
            if n % 2 == 1:
                n += 1
            return n // 2
        else:
            return 0

    def soloJugada(self, fila, clave):
        lj = self.gestor.game.li_moves

        pos = fila * 2
        tam_lj = len(lj)

        if clave == "BLANCAS":
            if self.gestor.game.if_starts_with_black:
                pos -= 1
        else:
            if not self.gestor.game.if_starts_with_black:
                pos += 1

        if 0 <= pos <= (tam_lj - 1):
            return lj[pos]
        else:
            return None

    def dato(self, fila, clave):
        if clave == "NUMERO":
            return str(self.gestor.game.primeraJugada() + fila)

        move = self.soloJugada(fila, clave)
        if move:
            if self.siMostrar:
                return move.pgnFigurinesSP() if self.siFigurines else move.pgn_translated()
            else:
                return "-"
        else:
            return " "

    def conInformacion(self, fila, clave):
        if clave == "NUMERO":
            return None
        move = self.soloJugada(fila, clave)
        if move:
            if move.in_the_opening or move.li_nags or move.comment or (len(move.varitions) > 0):
                return move
        return None

    def analisis(self, fila, clave):
        if clave == "NUMERO":
            return None
        return self.soloJugada(fila, clave)
        # if move:
        # return move.analysis
        # else:
        # return None

    def liVariantesPV(self, move):
        li_resp = []
        if len(move.variations) > 0:
            for game in move.variations.list_games():
                if len(game):
                    move = game.move(0)
                    li_resp.append((move.from_sq, move.to_sq))

        return li_resp

    def mueve(self, fila, is_white):
        if_starts_with_black = self.gestor.game.if_starts_with_black

        if fila == 0 and is_white and if_starts_with_black:
            return

        lj = self.gestor.game.li_moves
        pos = fila * 2
        if not is_white:
            pos += 1
        if if_starts_with_black:
            pos -= 1

        tam_lj = len(lj)
        if tam_lj:

            siUltimo = (pos + 1) >= tam_lj
            if siUltimo:
                pos = tam_lj - 1

            move = self.gestor.game.move(pos)
            self.gestor.ponPosicion(move.position)

            lipvvar = []
            self.gestor.ponFlechaSC(move.from_sq, move.to_sq, lipvvar)

            if siUltimo:
                self.gestor.ponRevision(False)
                if self.gestor.human_is_playing and self.gestor.state == ST_PLAYING:
                    self.gestor.activaColor(self.gestor.is_human_side_white)
            else:
                self.gestor.ponRevision(self.gestor.state == ST_PLAYING)
                self.gestor.disable_all()
            self.gestor.refresh()

    def move(self, fila, clave):
        is_white = clave != "NEGRAS"

        pos = fila * 2
        if not is_white:
            pos += 1
        if self.gestor.game.if_starts_with_black:
            pos -= 1
        tam_lj = len(self.gestor.game)
        if tam_lj == 0:
            return None, None

        if pos >= len(self.gestor.game):
            pos = len(self.gestor.game) - 1

        return pos, self.gestor.game.move(pos)

    def actual(self):
        tipoJuego = self.gestor.game_type

        if tipoJuego == GT_AGAINST_GM:
            return self.actualGM()
        elif tipoJuego in (GT_AGAINST_PGN, GT_ALONE, GT_ROUTES, GT_TURN_ON_LIGHTS, GT_NOTE_DOWN):
            return self.gestor.actualPGN()

        if tipoJuego == GT_BOOK:
            rival = self.gestor.libro.name
        elif tipoJuego in (GT_FICS, GT_FIDE):
            rival = self.gestor.nombreObj
        elif self.gestor.xrival:  # foncap change
            rival = self.gestor.xrival.name  # foncap change
        else:  # foncap change
            rival = ""  # foncap change

        player = self.gestor.configuracion.nom_player()
        resultado = self.gestor.resultado
        is_human_side_white = self.gestor.is_human_side_white

        if resultado == RS_WIN_PLAYER:
            r = "1-0" if is_human_side_white else "0-1"
        elif resultado == RS_WIN_OPPONENT:
            r = "0-1" if is_human_side_white else "1-0"
        elif resultado == RS_DRAW:
            r = "1/2-1/2"
        else:
            r = "*"
        if is_human_side_white:
            blancas = player
            negras = rival
        else:
            blancas = rival
            negras = player
        hoy = Util.today()
        resp = '[Event "%s"]\n' % Code.lucas_chess
        # Site (lugar): el lugar donde el evento se llevo a cabo.
        # Esto debe ser en formato "Ciudad, Region PAIS", donde PAIS es el codigo del mismo
        # en tres letras de acuerdo al codigo del Comite Olimpico Internacional. Como ejemplo: "Mexico, D.F. MEX".
        resp += '[Date "%d.%02d.%02d"]\n' % (hoy.year, hoy.month, hoy.day)
        # Round (ronda): La ronda original de la game.
        resp += '[White "%s"]\n' % blancas
        resp += '[Black "%s"]\n' % negras
        resp += '[Result "%s"]\n' % r

        if self.gestor.fen:
            resp += '[FEN "%s"]\n' % self.gestor.fen

        xrival = getattr(self.gestor, "xrival", None)
        if xrival and not (tipoJuego in [GT_BOOK]):
            if xrival.motorProfundidad:
                resp += '[Depth "%d"]\n' % xrival.motorProfundidad

            if xrival.motorTiempoJugada:
                resp += '[TimeEngineMS "%d"]\n' % xrival.motorTiempoJugada

            if self.gestor.categoria:
                resp += '[Category "%s"]\n' % self.gestor.categoria.name()

        if not (tipoJuego in [GT_BOOK, GT_RESISTANCE]):
            if self.gestor.ayudasPGN:
                resp += '[Hints "%d"]\n' % self.gestor.ayudasPGN

        if tipoJuego in (GT_ELO, GT_MICELO):
            resp += '[WhiteElo "%d"]\n' % self.gestor.whiteElo
            resp += '[BlackElo "%d"]\n' % self.gestor.blackElo

        ap = self.gestor.game.opening
        if ap:
            resp += '[ECO "%s"]\n' % ap.eco
            resp += '[Opening "%s"]\n' % ap.trNombre

        dmore = getattr(self.gestor, "pgnLabelsAdded", None)
        if dmore:
            for k, v in dmore().items():
                resp += '[%s "%s"]\n' % (k, v)

        resp += "\n" + self.gestor.game.pgnBase()
        if not resp.endswith(r):
            resp += " %s" % r

        return resp

    def actualGM(self):
        gm = self.gestor.gm
        motorGM = self.gestor.motorGM

        partidaGM = motorGM.getLastGame()

        if partidaGM:
            event = partidaGM.event
            oponent = partidaGM.oponent
            fecha = partidaGM.date
            result = partidaGM.result
        else:
            event = "?"
            oponent = "?"
            fecha = "????.??.??"
            result = "*"

        if self.gestor.is_white:
            blancas = gm
            negras = oponent
        else:
            blancas = oponent
            negras = gm

        resp = '[Event "%s"]\n' % event
        resp += '[Date "%s"]\n' % fecha
        resp += '[White "%s"]\n' % blancas
        resp += '[Black "%s"]\n' % negras
        resp += '[Result "%s"]\n' % result.strip()

        ap = self.gestor.game.opening
        if ap:
            resp += '[ECO "%s"]\n' % ap.eco
            resp += '[Opening "%s"]\n' % ap.trNombre

        resp += "\n" + self.gestor.game.pgnBase() + " " + result.strip()

        return resp

    def dicCabeceraActual(self):
        resp = self.actual()
        dic = collections.OrderedDict()
        for linea in resp.split("\n"):
            linea = linea.strip()
            if linea.startswith("["):
                li = linea.split('"')
                if len(li) == 3:
                    clave = li[0][1:].strip()
                    valor = li[1]
                    dic[clave] = valor
            else:
                break
        return dic
