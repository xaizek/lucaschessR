import random
import time

import Code
from Code import Util
from Code import Position
from Code.QT import Iconos
from Code.QT import Controles
from Code.QT import QTUtil2
from Code.QT import QTVarios


class GestorChallenge101:
    def __init__(self, procesador):
        self.main_window = procesador.main_window
        self.tablero = self.main_window.tablero
        self.procesador = procesador
        self.configuracion = procesador.configuracion
        self.cod_variables = "challenge101"
        self.puntos_totales = 0
        self.puntos_ultimo = 0
        self.pendientes = 10
        self.st_randoms = set()
        self.st_lines = set()  # para no salvar mas de una vez una linea
        self.key = str(Util.today())
        random.seed()

        fmt = Code.path_resource("IntFiles", "tactic0.bm")

        with open(fmt) as f:
            self.li_lineas_posicion = [linea for linea in f if linea.strip()]

        self.siguiente_posicion()

    def siguiente_posicion(self):
        num_lineas_posicion = len(self.li_lineas_posicion)
        while True:
            random_pos = random.randint(0, num_lineas_posicion - 1)
            if not (random_pos in self.st_randoms):
                self.st_randoms.add(random_pos)
                break
        self.fen, self.result, self.pgn_result, self.pgn, self.difficult = (
            self.li_lineas_posicion[random_pos].strip().split("|")
        )
        self.difficult = int(self.difficult)

        self.cp = Position.Position()
        self.cp.read_fen(self.fen)

        self.is_white = " w " in self.fen
        self.tablero.bloqueaRotacion(False)
        self.tablero.set_dispatcher(self.mueve_humano)
        self.tablero.setposition(self.cp)
        self.tablero.ponerPiezasAbajo(self.is_white)
        self.tablero.activaColor(self.is_white)
        self.tablero.ponIndicador(self.is_white)

        self.intentos = 0
        self.max_intentos = (self.difficult + 1) // 2 + 4
        self.iniTime = time.time()

    def lee_results(self):
        dic = self.configuracion.leeVariables(self.cod_variables)
        results = dic.get("RESULTS", [])
        results.sort(key=lambda x: -x[1])
        return results

    def guarda_puntos(self):
        dic = self.configuracion.leeVariables(self.cod_variables)
        results = dic.get("RESULTS", [])
        if len(results) >= 10:
            ok = False
            for k, pts in results:
                if pts <= self.puntos_totales:
                    ok = True
                    break
        else:
            ok = True
        if ok:
            ok_find = False
            for n in range(len(results)):
                if results[n][0] == self.key:
                    ok_find = True
                    results[n] = (self.key, self.puntos_totales)
                    break
            if not ok_find:
                results.append((self.key, self.puntos_totales))
            results.sort(reverse=True, key=lambda x: "%4d%s" % (x[1], x[0]))
            if len(results) > 10:
                results = results[:10]
            dic["RESULTS"] = results
            self.configuracion.escVariables(self.cod_variables, dic)

    def menu(self):
        main_window = self.procesador.main_window
        main_window.cursorFueraTablero()
        menu = QTVarios.LCMenu(main_window)
        f = Controles.TipoLetra(name="Courier", puntos=12)
        fbold = Controles.TipoLetra(name="Courier", puntos=12, peso=700)
        fbolds = Controles.TipoLetra(name="Courier", puntos=12, peso=500, siSubrayado=True)
        menu.ponFuente(f)

        li_results = self.lee_results()
        icono = Iconos.PuntoAzul()

        menu.separador()
        titulo = ("** %s **" % _("Challenge 101")).center(30)
        if self.pendientes == 0:
            menu.opcion("close", titulo, Iconos.Terminar())
        else:
            menu.opcion("continuar", titulo, Iconos.Pelicula_Seguir())
        menu.separador()
        ok_en_lista = False
        for n, (fecha, pts) in enumerate(li_results, 1):
            if fecha == self.key:
                ok_en_lista = True
                ico = Iconos.PuntoEstrella()
                tipoLetra = fbolds
            else:
                ico = icono
                tipoLetra = None
            txt = str(fecha)[:16]
            menu.opcion(None, "%2d. %-20s %6d" % (n, txt, pts), ico, tipoLetra=tipoLetra)

        menu.separador()
        menu.opcion(None, "", Iconos.PuntoNegro())
        menu.separador()
        if self.puntos_ultimo:
            menu.opcion(None, ("+%d" % (self.puntos_ultimo)).center(30), Iconos.PuntoNegro(), tipoLetra=fbold)
        if self.pendientes == 0:
            if not ok_en_lista:
                menu.opcion(
                    None, ("%s: %d" % (_("Score"), self.puntos_totales)).center(30), Iconos.Gris(), tipoLetra=fbold
                )
            menu.separador()
            menu.opcion("close", _("GAME OVER").center(30), Iconos.Terminar())
        else:
            menu.opcion(
                None, ("%s: %d" % (_("Score"), self.puntos_totales)).center(30), Iconos.PuntoNegro(), tipoLetra=fbold
            )
            menu.separador()
            menu.opcion(
                None,
                ("%s: %d" % (_("Positions left"), self.pendientes)).center(30),
                Iconos.PuntoNegro(),
                tipoLetra=fbold,
            )
            menu.separador()
            menu.opcion(None, "", Iconos.PuntoNegro())
            menu.separador()
            menu.opcion("continuar", _("Continue"), Iconos.Pelicula_Seguir())
            menu.separador()
            menu.opcion("close", _("Close"), Iconos.MainMenu())

        resp = menu.lanza()

        return not (resp == "close" or self.pendientes == 0)

    def mueve_humano(self, from_sq, to_sq, promotion=None):
        self.savePosition()  # Solo cuando ha hecho un intento
        self.puntos_ultimo = 0
        if from_sq + to_sq == self.result:  # No hay coronaciones
            tm = time.time() - self.iniTime
            self.tablero.disable_all()
            self.cp.mover(from_sq, to_sq, promotion)
            self.tablero.setposition(self.cp)
            self.tablero.ponFlechaSC(from_sq, to_sq)

            puntos = int(1000 - (1000 / self.max_intentos) * self.intentos)
            puntos -= int(tm * 7)

            if puntos > 0:
                self.puntos_totales += puntos
                self.guarda_puntos()
                self.puntos_ultimo = puntos

            self.pendientes -= 1
            if self.menu():
                self.siguiente_posicion()
            return True
        else:
            self.intentos += 1
            if self.intentos < self.max_intentos:
                QTUtil2.mensajeTemporalSinImagen(
                    self.main_window, str(self.max_intentos - self.intentos), 0.5, puntos=24, background="#ffd985"
                )
            else:
                self.tablero.setposition(self.cp)
                self.tablero.ponFlechaSC(self.result[:2], self.result[2:])
                self.pendientes = 0
                self.menu()
                return True
        return False

    def savePosition(self):
        line = "%s|%s|%s|%s\n" % (self.fen, str(self.key)[:19], self.pgn_result, self.pgn)
        if not (line in self.st_lines):
            self.st_lines.add(line)
            fich = self.configuracion.ficheroPresentationPositions
            existe = Util.exist_file(fich)
            with open(fich, "at") as q:
                line = "%s|%s|%s|%s\n" % (self.fen, str(self.key)[:19], self.pgn_result, self.pgn)
                q.write(line)
            if not existe:
                self.procesador.entrenamientos.menu = None


# def basico(procesador, hx, factor=1.0):
#     def m(cl, t=4.0):
#         n = len(cl) / 2
#         li = []
#         for x in range(n):
#             li.append(cl[x * 2] + cl[x * 2 + 1])
#         lista = []
#         for x in range(n - 1):
#             lista.append((li[x], li[x + 1]))
#         return procesador.cpu.muevePiezaLI(lista, t * factor, padre=hx)
#
#     li = [
#         "b6a6a8",
#         "b5a7c6b8",
#         "b3d5d8",
#         "c2c6e8",
#         "f2h2h8",
#         "g7h7h1e1",
#         "g6f4h3g1",
#         "g4h4h1",
#         "d2f3h4f5h6g8",
#         "e4a4a1",
#         "e2a6c8",
#         "g5c1",
#         "e7d7d1",
#         "b4f8",
#         "b2b7",
#         "e5f3d2b1",
#         "e6c4f1",
#         "f6f2",
#     ]
#
#     n = random.randint(0, 7)
#     primer = li[n]
#     del li[n]
#
#     hx = m(primer, 2.0 * factor)
#     for uno in li:
#         m(uno)
#     return procesador.cpu.setposition(procesador.posicionInicial)
#
#
# def partidaDia(procesador, hx):
#     dia = Util.today().day
#     lid = Util.ListSQL("../resources/IntFiles/31.pkl")
#     dic = lid[dia - 1]
#     lid.close()
#
#     liMovs = dic["XMOVS"].split("|")
#
#     cpu = procesador.cpu
#
#     padre = cpu.setposition(procesador.posicionInicial)
#     padre = cpu.duerme(0.6, padre=padre, siExclusiva=True)
#
#     for txt in liMovs:
#         li = txt.split(",")
#         tipo = li[0]
#
#         if tipo == "m":
#             from_sq, to_sq, segundos = li[1], li[2], float(li[3])
#             hx = cpu.muevePieza(from_sq, to_sq, segundos=segundos, padre=padre)
#
#         elif tipo == "b":
#             segundos, movim = float(li[1]), li[2]
#             n = cpu.duerme(segundos, padre=padre)
#             cpu.borraPieza(movim, padre=n)
#
#         elif tipo == "c":
#             m1, m2 = li[1], li[2]
#             cpu.cambiaPieza(m1, m2, padre=hx)
#
#         elif tipo == "d":
#             dato = float(li[1])
#             padre = cpu.duerme(dato, padre=hx, siExclusiva=True)
#
#         elif tipo == "t":
#             li = dic["TOOLTIP"].split(" ")
#             t = 0
#             texto = ""
#             for x in li:
#                 texto += x + " "
#                 t += len(x) + 1
#                 if t > 40:
#                     texto += "<br>"
#                     t = 0
#             texto += "<br>Source wikipedia: http://en.wikipedia.org/wiki/List_of_chess_games"
#             cpu.toolTip(texto, padre=hx)
#
#             # hx = cpu.duerme( 3.0, padre = hx )
