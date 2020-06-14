import operator
import os

from FasterCode import xpv_pv, pv_xpv

from Code import Move
from Code import Util
import Code


class GMpartida:
    def __init__(self, linea):
        self.xpv, self.event, self.oponent, self.date, self.opening, self.result, self.color = linea.split("|")
        self.liPV = xpv_pv(self.xpv).split(" ")
        self.lenPV = len(self.liPV)

    def toline(self):
        return "%s|%s|%s|%s|%s|%s|%s" % (
            self.xpv,
            self.event,
            self.oponent,
            self.date,
            self.opening,
            self.result,
            self.color,
        )

    def isWhite(self, siWhite):
        if siWhite:
            return "W" in self.color
        else:
            return "B" in self.color

    def isValidMove(self, ply, move):
        if ply < self.lenPV:
            return self.liPV[ply] == move
        else:
            return False

    def isFinished(self, ply):
        return ply >= self.lenPV

    def move(self, ply):
        return None if self.isFinished(ply) else self.liPV[ply]

    def rotulo(self, siGM=True):
        if siGM:
            return _("Opponent") + ": <b>%s (%s)</b>" % (self.oponent, self.date)
        else:
            return "%s (%s)" % (self.oponent, self.date)

    def rotuloBasico(self, siGM=True):
        if siGM:
            return _("Opponent") + ": %s (%s)" % (self.oponent, self.date)
        else:
            return "%s (%s)" % (self.oponent, self.date)


class GM:
    def __init__(self, carpeta, gm):
        self.gm = gm
        self.carpeta = carpeta

        self.dicAciertos = {}

        self.liGMPartidas = self.read()

        self.ply = 0
        self.lastGame = None

    def __len__(self):
        return len(self.liGMPartidas)

    def getLastGame(self):
        return self.lastGame

    def read(self):
        # (kupad fix) linux is case sensitive and can't find the xgm file because ficheroGM is all lower-case, but all
        # the xgm files have the first letter capitalized (including ones recently downloaded)
        ficheroGM = "%s%s.xgm" % (self.gm[0].upper(), self.gm[1:])
        f = open(os.path.join(self.carpeta, ficheroGM), "r")
        li = []
        for linea in f:
            linea = linea.strip()
            if linea:
                li.append(GMpartida(linea))
        f.close()
        return li

    def colorFilter(self, isWhite):
        self.liGMPartidas = [gmp for gmp in self.liGMPartidas if gmp.isWhite(isWhite)]

    def play(self, move):
        move = move.lower()

        liP = []
        ok = False
        nextPly = self.ply + 1
        for gmPartida in self.liGMPartidas:
            if gmPartida.isValidMove(self.ply, move):
                self.lastGame = gmPartida  # - Siempre hay una ultima
                ok = True
                if not gmPartida.isFinished(nextPly):
                    liP.append(gmPartida)

        self.liGMPartidas = liP
        self.ply += 1
        return ok

    def isValidMove(self, move):
        move = move.lower()

        for gmPartida in self.liGMPartidas:
            if gmPartida.isValidMove(self.ply, move):
                return True
        return False

    def isFinished(self):
        for gmp in self.liGMPartidas:
            if not gmp.isFinished(self.ply):
                return False
        return True

    def alternativas(self):
        li = []
        for gmPartida in self.liGMPartidas:
            move = gmPartida.move(self.ply)
            if move and not (move in li):
                li.append(move)
        return li

    def dameJugadasTXT(self, position_before, siGM):
        li = []
        dRepeticiones = {}
        for gmPartida in self.liGMPartidas:
            move = gmPartida.move(self.ply)
            if move:
                if not (move in dRepeticiones):
                    dRepeticiones[move] = [len(li), 1]
                    from_sq, to_sq, promotion = move[:2], move[2:4], move[4:]
                    siBien, mens, move = Move.dameJugada(gmPartida, position_before, from_sq, to_sq, promotion)
                    li.append([from_sq, to_sq, promotion, gmPartida.rotuloBasico(siGM), move.pgn_translated()])
                else:
                    dRepeticiones[move][1] += 1
                    pos = dRepeticiones[move][0]
                    li[pos][3] = _("%d games") % dRepeticiones[move][1]
        return li

    def rotuloPartidaSiUnica(self, siGM=True):
        if len(self.liGMPartidas) == 1:
            return self.liGMPartidas[0].rotulo(siGM)
        else:
            return ""

    def resultado(self, game):
        gPartida = self.lastGame
        opening = game.opening.trNombre if game.opening else gPartida.opening

        txt = _("Opponent") + " : <b>" + gPartida.oponent + "</b><br>"
        event = gPartida.event
        if event:
            txt += _("Event") + " : <b>" + event + "</b><br>"
        txt += _("Date") + " : <b>" + gPartida.date + "</b><br>"
        txt += _("Opening") + " : <b>" + opening + "</b><br>"
        txt += _("Result") + " : <b>" + gPartida.result + "</b><br>"
        txt += "<br>" * 2
        aciertos = 0
        for v in self.dicAciertos.values():
            if v:
                aciertos += 1
        total = len(self.dicAciertos)
        if total:
            porc = int(aciertos * 100.0 / total)
            txt += _("Hints") + " : <b>%d%%</b>" % porc
        else:
            porc = 0

        event = " - %s" % event if event else ""
        txtResumen = "%s%s - %s - %s" % (gPartida.oponent, event, gPartida.date, gPartida.result)

        return txt, porc, txtResumen

    def ponPartidaElegida(self, numPartida):
        self.liGMPartidas = [self.liGMPartidas[numPartida]]

    def genToSelect(self):
        liRegs = []
        for num, part in enumerate(self.liGMPartidas):
            dic = dict(
                NOMBRE=part.oponent, FECHA=part.date, ECO=part.opening, RESULT=part.result, NUMERO=num, EVENT=part.event
            )
            liRegs.append(dic)
        return liRegs

    def write(self):
        fichero_gm = self.gm + ".xgm"
        with open(os.path.join(self.carpeta, fichero_gm), "wb") as q:
            for part in self.liGMPartidas:
                q.write(part.toline() + "\n")

    def remove(self, num):
        del self.liGMPartidas[num]
        self.write()


def dic_gm():
    dic = {}
    nomfich = "GM/_listaGM.txt"
    nomfich = Code.path_resource(nomfich)
    with open(nomfich, "rt") as f:
        for linea in f:
            if linea:
                li = linea.split("|")
                gm = li[0].lower()
                name = li[1]
                dic[gm] = name
        return dic


def lista_gm():
    dic = dic_gm()
    li = []

    for entry in Util.listdir(Code.path_resource("GM")):
        fich = entry.name.lower()
        if fich.endswith(".xgm"):
            gm = fich[:-4].lower()
            try:
                li.append((dic[gm], gm, True, True))
            except:
                pass
    li = sorted(li, key=operator.itemgetter(0))
    return li


def lista_gm_personal(carpeta):
    li = []
    for entry in Util.listdir(carpeta):
        fich = entry.name.lower()
        if fich.endswith(".xgm"):
            gm = fich[:-4]

            siW = siB = False
            with open(os.path.join(carpeta, fich)) as f:
                for linea in f:
                    try:
                        gmp = GMpartida(linea.strip())
                    except:
                        continue
                    if not siW:
                        siW = gmp.isWhite(True)
                    if not siB:
                        siB = gmp.isWhite(False)
                    if siW and siB:
                        break
            if siW or siB:
                li.append((gm, gm, siW, siB))
    li = sorted(li)
    return li


def hayGMpersonal(carpeta):
    return len(lista_gm_personal(carpeta)) > 0


class FabGM:
    def __init__(self, configuracion, nomEntrenamiento, liJugadores):
        self.configuracion = configuracion
        self.nomEntrenamiento = nomEntrenamiento
        self.li_players = liJugadores

        self.f = None

        self.added = 0

    def write(self, txt):
        if self.f is None:
            fichero = os.path.join(self.configuracion.dirPersonalTraining, self.nomEntrenamiento) + ".xgm"
            self.f = open(fichero, "wb")
        self.f.write(txt)
        self.added += 1

    def close(self):
        if self.f:
            self.f.close()
            self.f = None

    def masMadera(self, game, result):
        dic = game.dicTags()
        if not ("White" in dic) or not ("Black" in dic) or (result and not ("Result" in dic)):
            return

        if self.li_players:
            is_white = False
            is_black = False

            for x in ["Black", "White"]:
                if x in dic:
                    player = dic[x].upper()
                    si = False
                    for uno in self.li_players:
                        siContrario = uno.startswith("^")
                        if siContrario:
                            uno = uno[1:]

                        siZ = uno.endswith("*")
                        siA = uno.startswith("*")
                        uno = uno.replace("*", "").strip().upper()
                        if siA:
                            if player.endswith(uno):
                                si = True
                            if siZ:  # form apara poner siA y siZ
                                si = uno in player
                        elif siZ:
                            if player.startswith(uno):
                                si = True
                        elif uno == player:
                            si = True
                        if si:
                            break
                    if si:
                        if x == "Black":
                            if siContrario:
                                is_white = True
                            else:
                                is_black = True
                        else:
                            if siContrario:
                                is_black = True
                            else:
                                is_white = True

            if not (is_white or is_black):
                return

            self.masMaderaUno(dic, game, is_white, is_black, result)
        else:
            self.masMaderaUno(dic, game, True, False, result)
            self.masMaderaUno(dic, game, False, True, result)

    def masMaderaUno(self, dic, game, is_white, is_black, tpResult):
        pk = ""
        for move in game.li_moves:
            pk += move.movimiento() + " "

        event = dic.get("Event", "-")
        oponente = dic["White"] + "-" + dic["Black"]
        date = dic.get("Date", "-").replace("?", "").strip(".")
        eco = dic.get("Eco", "-")
        result = dic.get("Result", "-")
        color = "W" if is_white else "B"
        if tpResult:
            siEmpate = "2" in result
            siGanaBlancas = not siEmpate and result.startswith("1")
            siGanaNegras = not siEmpate and result.startswith("0")
            if tpResult == 1:
                if not ((is_white and siGanaBlancas) or (is_black and siGanaNegras)):
                    return
            else:
                if not (siEmpate or (is_white and siGanaBlancas) or (is_black and siGanaNegras)):
                    return

        def nopipe(txt):
            return txt.replace("|", " ").strip() if "|" in txt else txt

        self.write(
            "%s|%s|%s|%s|%s|%s|%s\n"
            % (pv_xpv(pk.strip()), nopipe(event), nopipe(oponente), nopipe(date), eco, result, color)
        )

    def xprocesa(self):
        self.close()
        return self.added
