import FasterCode

from io import BytesIO

import collections
import copy
import os

from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt

from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import Piezas
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import TabElementos
from Code.QT import TabFlechas
from Code.QT import TabMarcos
from Code.QT import TabMarker
from Code.QT import TabSVG
from Code.QT import TabTipos
from Code.QT import Delegados
from Code import TabVisual
from Code import Util
import Code
from Code.Constantes import *
import Code.QT.PantallaColores as PantallaColores


class RegKB:
    def __init__(self, key, flags):
        self.key = key
        self.flags = flags


class Tablero(QtWidgets.QGraphicsView):
    def __init__(self, parent, config_board, siMenuVisual=True, siDirector=True):
        super(Tablero, self).__init__(None)

        self.setRenderHints(
            QtGui.QPainter.Antialiasing | QtGui.QPainter.TextAntialiasing | QtGui.QPainter.SmoothPixmapTransform
        )
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setDragMode(self.NoDrag)
        self.setInteractive(True)
        self.setTransformationAnchor(self.NoAnchor)
        self.escena = QtWidgets.QGraphicsScene(self)
        self.escena.setItemIndexMethod(self.escena.NoIndex)
        self.setScene(self.escena)
        self.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)

        self.main_window = parent
        self.configuracion = Code.configuracion

        self.siMenuVisual = siMenuVisual
        self.siDirector = siDirector and siMenuVisual
        self.siDirectorIcon = self.siDirector and self.configuracion.x_director_icon
        self.dirvisual = None
        self.guion = None
        self.lastFenM2 = ""
        self.dbVisual = TabVisual.DBGestorVisual(self.configuracion.ficheroRecursos, False)

        self.current_graphlive = None
        self.dic_graphlive = None

        self.rutinaDropsPGN = None

        self.config_board = config_board

        self.blindfold = None
        self.blindfoldModoPosicion = False

        self.siInicializado = False

        self.last_position = None

        self.siF11 = False

        self._dispatchSize = None  # configuracion en vivo, dirige a la rutina de la main_window afectada

        self.pendingRelease = None

        self.siPermitidoResizeExterno = True
        # TODO self.siPermitidoResizeExterno se ha cambiado a True, que efecto tendrá ?
        self.mensajero = None

        self.si_borraMovibles = True

        self.kb_buffer = []
        self.cad_buffer = ""

        self.hard_focus = True  # Controla que cada vez que se indique una posición active el foco al tablero

    def disable_hard_focus(self):
        self.hard_focus = False

    def init_kb_buffer(self, alsoCad=True):
        self.kb_buffer = []
        if alsoCad:
            self.cad_buffer = ""

    def exec_kb_buffer(self, key, flags):
        if key == Qt.Key_Escape:
            self.init_kb_buffer()
            return

        if key in (Qt.Key_Enter, Qt.Key_Return):
            if self.kb_buffer:
                last = self.kb_buffer[-1]
                key = last.key
                flags = last.flags | QtCore.Qt.AltModifier
            else:
                return

        if key in (Qt.Key_Backspace, Qt.Key_Delete):
            if hasattr(self.main_window, "gestor") and hasattr(self.main_window.gestor, "run_action"):
                self.main_window.gestor.run_action(TB_TAKEBACK)
                return

        siAlt = (flags & QtCore.Qt.AltModifier) > 0
        siCtrl = (flags & QtCore.Qt.ControlModifier) > 0

        okseguir = False

        if siAlt or siCtrl:

            # CTRL-C : copy fen al clipboard
            if siCtrl and key == Qt.Key_C:
                QTUtil.ponPortapapeles(self.last_position.fen())
                QTUtil2.message_bold(self, _("FEN is in clipboard"))

            # ALT-F -> Rota tablero
            if key == Qt.Key_F:
                self.intentaRotarTablero(None)

            # ALT-I Save image to clipboard (CTRL->no border)
            elif key == Qt.Key_I:
                self.salvaEnImagen(siCtrl=siCtrl, siAlt=siAlt)
                QTUtil2.message_bold(self, _("Board image is in clipboard"))

            # ALT-J Save image to file (CTRL->no border)
            elif key == Qt.Key_J:
                path = QTUtil2.salvaFichero(
                    self, _("File to save"), self.configuracion.x_save_folder, "%s PNG (*.png)" % _("File"), False
                )
                if path:
                    self.salvaEnImagen(path, "png", siCtrl=siCtrl, siAlt=siAlt)
                    self.configuracion.x_save_folder = os.path.dirname(path)
                    self.configuracion.graba()

            # ALT-K
            elif key == Qt.Key_K:
                self.showKeys()

            elif (
                hasattr(self.main_window, "gestor")
                and self.main_window.gestor
                and key in (Qt.Key_P, Qt.Key_N, Qt.Key_C)
            ):
                # P -> show information
                if key == Qt.Key_P and hasattr(self.main_window.gestor, "pgnInformacion"):
                    self.main_window.gestor.pgnInformacion()
                # ALT-N -> non distract mode
                elif key == Qt.Key_N and hasattr(self.main_window.gestor, "nonDistractMode"):
                    self.main_window.gestor.nonDistractMode()
                # ALT-C -> show captures
                elif key == Qt.Key_C and hasattr(self.main_window.gestor, "capturas"):
                    self.main_window.gestor.capturas()
                else:
                    okseguir = True
        else:
            okseguir = True

        if not okseguir:
            if self.kb_buffer:
                self.kb_buffer = self.kb_buffer[:-1]
                self.cad_buffer = ""
            return

        if self.mensajero and self.siActivasPiezas and not siAlt:

            # Entrada directa con el pgn
            if 128 > key > 32:
                self.cad_buffer += chr(key)
            if self.cad_buffer:
                FasterCode.set_fen(self.last_position.fen())
                li = FasterCode.get_exmoves()
                ok_ini = False
                busca = self.cad_buffer.lower()
                if busca.startswith("o-o") and not (busca[-1] in "o-"):
                    busca = "o-o"
                if busca == "o2":
                    busca = "o-o"
                    key = 33
                elif busca == "o3":
                    busca = "o-o-o"
                for m in li:
                    san = m._san.decode().lower().replace("+", "").replace("=", "")
                    if san == busca:
                        if busca == "o-o":
                            siExt = False
                            for mt in li:
                                if mt._san == "O-O-O":
                                    siExt = True
                                    break
                            if siExt and chr(key).lower() == "o":
                                ok_ini = True  # esperamos al siguiente caracter
                                break
                        self.cad_buffer = ""
                        self.mensajero(m._from, m._to, m._promotion)
                        return
                    elif san.startswith(busca):
                        ok_ini = True
                if not ok_ini:
                    self.cad_buffer = ""

            nk = len(self.kb_buffer)
            if nk == 4:
                k = chr(key).lower()
                if k in "qrbn":
                    from_sq = chr(self.kb_buffer[0].key).lower() + chr(self.kb_buffer[1].key)
                    to_sq = chr(self.kb_buffer[2].key).lower() + chr(self.kb_buffer[3].key)
                    self.mensajero(from_sq, to_sq, k)
            elif 48 < key < 57 or 64 < key < 73:  # coordenadas
                c = chr(key)
                if nk == 0:
                    if not c.isdigit():
                        self.kb_buffer.append(RegKB(key, flags))
                    return
                elif nk == 1:
                    if c.isdigit():
                        from_sq = chr(self.kb_buffer[0].key).lower() + c
                        pz = self.dameNomPiezaEn(from_sq)
                        if pz and (
                            (self.siActivasPiezasColor and pz.isupper())
                            or (not self.siActivasPiezasColor and pz.islower())
                        ):
                            self.kb_buffer.append(RegKB(key, flags))
                            self.markPosition(from_sq)
                        else:
                            self.markError(from_sq)
                            self.init_kb_buffer(False)
                    else:
                        self.kb_buffer[0] = RegKB(key, flags)
                    return
                elif nk == 2:
                    if c.isdigit():
                        self.kb_buffer[1] = RegKB(key, flags)
                    else:
                        self.kb_buffer.append(RegKB(key, flags))
                    return
                elif nk == 3:
                    if c.isdigit():
                        from_sq = chr(self.kb_buffer[0].key).lower() + chr(self.kb_buffer[1].key)
                        to_sq = chr(self.kb_buffer[2].key).lower() + c
                        # si es promocion esperamos una tecla mas
                        if (self.siActivasPiezasColor and from_sq[1] == "7" and to_sq[1] == "8") or (
                            not self.siActivasPiezasColor and from_sq[1] == "2" and to_sq[1] == "1"
                        ):
                            pz = self.dameNomPiezaEn(from_sq)
                            if pz and pz.lower() == "p":
                                self.markPosition(to_sq)
                                self.kb_buffer.append(RegKB(key, flags))
                                return  # esperamos promocion
                        if not self.mensajero(from_sq, to_sq, ""):
                            self.markError(from_sq)
                            self.init_kb_buffer()
                    else:
                        self.kb_buffer[2] = RegKB(key, flags)
                    return

    def sizeHint(self):
        return QtCore.QSize(self.ancho + 6, self.ancho + 6)

    def xremoveItem(self, item):
        scene = item.scene()
        if scene:
            scene.removeItem(item)

    def keyPressEvent(self, event):
        k = event.key()
        m = int(event.modifiers())

        if Qt.Key_F1 <= k <= Qt.Key_F10:
            if self.dirvisual and self.dirvisual.keyPressEvent(event):
                return
            if (m & QtCore.Qt.ControlModifier) > 0:
                if k == Qt.Key_F1:
                    self.borraUltimoMovible()
                elif k == Qt.Key_F2:
                    self.borraMovibles()
            elif self.lanzaDirector():
                self.dirvisual.keyPressEvent(event)
            return

        event.ignore()
        self.exec_kb_buffer(k, m)

    def activaMenuVisual(self, siActivar):
        self.siMenuVisual = siActivar

    def permitidoResizeExterno(self, sino=None):
        if sino is None:
            return self.siPermitidoResizeExterno
        else:
            self.siPermitidoResizeExterno = sino

    def maximizaTam(self, activadoF11):
        self.siF11 = activadoF11
        self.config_board.anchoPieza(1000)
        self.config_board.guardaEnDisco()
        self.cambiadoAncho()

    def normalTam(self, xanchoPieza):
        self.siF11 = False
        self.config_board.anchoPieza(xanchoPieza)
        self.config_board.guardaEnDisco()
        self.cambiadoAncho()

    def cambiadoAncho(self):
        is_white_bottom = self.is_white_bottom
        self.ponAncho()
        if not is_white_bottom:
            self.intentaRotarTablero(None)
        if self._dispatchSize:
            self._dispatchSize()

    def siMaximizado(self):
        return self.config_board.anchoPieza() == 1000

    def crea(self):
        nomPiezasOri = self.config_board.nomPiezas()
        if self.blindfold:
            self.piezas = Piezas.Blindfold(nomPiezasOri, self.blindfold)
        else:
            self.piezas = Code.todasPiezas.selecciona(nomPiezasOri)
        self.anchoPieza = self.config_board.anchoPieza()
        self.margenPieza = 2

        self.colorBlancas = self.config_board.colorBlancas()
        self.colorNegras = self.config_board.colorNegras()
        self.colorFondo = self.config_board.colorFondo()
        self.png64Blancas = self.config_board.png64Blancas()
        self.png64Negras = self.config_board.png64Negras()
        self.png64Fondo = self.config_board.png64Fondo()
        self.transBlancas = self.config_board.transBlancas()
        self.transNegras = self.config_board.transNegras()

        if self.config_board.extendedColor():
            self.colorExterior = self.colorFondo
            self.png64FondoExt = self.png64Fondo
        else:
            self.colorExterior = self.config_board.colorExterior()
            self.png64FondoExt = None

        self.colorTexto = self.config_board.colorTexto()

        self.colorFrontera = self.config_board.colorFrontera()

        self.exePulsadoNum = None
        self.exePulsadaLetra = None
        self.atajosRaton = None
        self.siActivasPiezas = False  # Control adicional, para responder a eventos del raton
        self.siActivasPiezasColor = None

        self.siPosibleRotarTablero = True

        self.is_white_bottom = True

        self.nCoordenadas = self.config_board.nCoordenadas()

        self.ponAncho()

    def calculaAnchoMXpieza(self):
        at = QTUtil.altoEscritorio() - 50 - 64
        if self.siF11:
            at += 50 + 64
        tr = 1.0 * self.config_board.tamRecuadro() / 100.0
        mp = self.margenPieza

        ap = int((1.0 * at - 16.0 * mp) / (8.0 + tr * 92.0 / 80))
        return ap

    def ponAncho(self):
        dTam = {16: (9, 23), 24: (10, 29), 32: (12, 33), 48: (14, 38), 64: (16, 42), 80: (18, 46)}

        ap = self.config_board.anchoPieza()
        if ap == 1000:
            ap = self.calculaAnchoMXpieza()
        if ap in dTam:
            self.puntos, self.margenCentro = dTam[ap]
        else:
            mx = 999999
            kt = 0
            for k in dTam:
                mt = abs(k - ap)
                if mt < mx:
                    mx = mt
                    kt = k
            pt, mc = dTam[kt]
            self.puntos = pt * ap / kt
            self.margenCentro = mc * ap / kt

        self.anchoPieza = ap

        self.anchoCasilla = ap + self.margenPieza * 2
        self.tamFrontera = self.margenCentro * 3.0 / 46.0

        self.margenCentro = self.margenCentro * self.config_board.tamRecuadro() / 100

        fx = self.config_board.tamFrontera()
        self.tamFrontera = int(self.tamFrontera * fx / 100)
        if fx > 0 and self.tamFrontera == 0:
            self.tamFrontera = 1

        self.puntos = self.puntos * self.config_board.tamLetra() * 12 / 1000

        # Guardamos las piezas
        if self.siInicializado:
            liPz = []
            for cpieza, piezaSC, is_active in self.liPiezas:
                if is_active:
                    position = piezaSC.bloquePieza
                    f = position.fila
                    c = position.columna
                    posA1H8 = chr(c + 96) + str(f)
                    liPz.append((cpieza, posA1H8))

            ap, apc = self.siActivasPiezas, self.siActivasPiezasColor
            siFlecha = self.flechaSC is not None

        self.rehaz()

        if self.siInicializado:
            if liPz:
                for cpieza, a1h8 in liPz:
                    self.creaPieza(cpieza, a1h8)
            if ap:
                self.activaColor(apc)
                self.ponIndicador(apc)

            if siFlecha:
                self.resetFlechaSC()

        self.siInicializado = True
        self.init_kb_buffer()

    def rehaz(self):
        self.escena.clear()
        self.liPiezas = []
        self.liFlechas = []
        self.flechaSC = None
        self.dicMovibles = collections.OrderedDict()  # Flechas, Marcos, SVG
        self.idUltimoMovibles = 0
        self.indicadorSC = None

        self.is_white_bottom = True

        # base
        if self.png64FondoExt:
            cajon = TabTipos.Imagen()
            cajon.pixmap = self.png64FondoExt
        else:
            cajon = TabTipos.Caja()
            cajon.colorRelleno = self.colorExterior
        self.ancho = ancho = cajon.position.alto = cajon.position.ancho = (
            self.anchoCasilla * 8 + self.margenCentro * 2 + 4
        )
        cajon.position.orden = 1
        cajon.colorRelleno = self.colorExterior
        cajon.tipo = QtCore.Qt.NoPen
        self.setFixedSize(ancho + 4, ancho + 4)
        if self.png64FondoExt:
            self.cajonSC = TabElementos.PixmapSC(self.escena, cajon)
        else:
            self.cajonSC = TabElementos.CajaSC(self.escena, cajon)

        # Frontera
        baseCasillasF = TabTipos.Caja()
        baseCasillasF.grosor = self.tamFrontera
        baseCasillasF.position.x = baseCasillasF.position.y = self.margenCentro - self.tamFrontera + 1
        baseCasillasF.position.alto = baseCasillasF.position.ancho = (
            self.anchoCasilla * 8 + 4 + (self.tamFrontera - 1) * 2
        )
        baseCasillasF.position.orden = 2
        baseCasillasF.colorRelleno = self.colorFrontera
        baseCasillasF.redEsquina = self.tamFrontera
        baseCasillasF.tipo = 0

        if baseCasillasF.grosor > 0:
            self.baseCasillasFSC = TabElementos.CajaSC(self.escena, baseCasillasF)

        # exterior squares
        if self.png64Fondo:
            baseCasillas = TabTipos.Imagen()
            baseCasillas.pixmap = self.png64Fondo
        else:
            baseCasillas = TabTipos.Caja()
            if not self.png64FondoExt:
                baseCasillas.colorRelleno = self.colorFondo
        baseCasillas.position.x = baseCasillas.position.y = self.margenCentro + 2
        baseCasillas.position.alto = baseCasillas.position.ancho = self.anchoCasilla * 8
        baseCasillas.position.orden = 2
        baseCasillas.tipo = 0
        if self.png64Fondo:
            self.baseCasillasSC = TabElementos.PixmapSC(self.escena, baseCasillas)
        else:
            self.baseCasillasSC = TabElementos.CajaSC(self.escena, baseCasillas)

        # squares
        def hazCasillas(tipo, png64, color, transparencia):
            siPixmap = len(png64) > 0
            if siPixmap:
                casilla = TabTipos.Imagen()
                casilla.pixmap = png64
                pixmap = None
            else:
                casilla = TabTipos.Caja()
                casilla.tipo = QtCore.Qt.NoPen
                casilla.colorRelleno = color
            casilla.position.orden = 4
            casilla.position.alto = casilla.position.ancho = self.anchoCasilla
            opacidad = 100.0 - transparencia * 1.0
            for x in range(4):
                for y in range(8):
                    una = casilla.copia()

                    k = self.margenCentro + 2
                    if y % 2 == tipo:
                        k += self.anchoCasilla
                    una.position.x = k + x * 2 * self.anchoCasilla
                    una.position.y = self.margenCentro + 2 + y * self.anchoCasilla
                    if siPixmap:
                        casillaSC = TabElementos.PixmapSC(self.escena, una, pixmap=pixmap)
                        pixmap = casillaSC.pixmap
                    else:
                        casillaSC = TabElementos.CajaSC(self.escena, una)
                    if opacidad != 100.0:
                        casillaSC.setOpacity(opacidad / 100.0)

        hazCasillas(1, self.png64Blancas, self.colorBlancas, self.transBlancas)
        hazCasillas(0, self.png64Negras, self.colorNegras, self.transNegras)

        # Coordenadas
        self.liCoordenadasVerticales = []
        self.liCoordenadasHorizontales = []

        anchoTexto = self.puntos + 4
        if self.margenCentro >= self.puntos or self.config_board.sepLetras() < 0:
            coord = TabTipos.Texto()
            tipoLetra = self.config_board.tipoLetra()
            peso = 75 if self.config_board.siBold() else 50
            coord.tipoLetra = TabTipos.TipoLetra(tipoLetra, self.puntos, peso=peso)
            coord.position.ancho = anchoTexto
            coord.position.alto = anchoTexto
            coord.position.orden = 7
            coord.colorTexto = self.colorTexto

            pCasillas = baseCasillas.position
            pFrontera = baseCasillasF.position
            gapCasilla = (self.anchoCasilla - anchoTexto) / 2
            sep = (
                self.margenCentro * self.config_board.sepLetras() * 38 / 50000
            )  # ancho = 38 -> sep = 5 -> sepLetras = 100

            def norm(x):
                if x < 0:
                    return 0
                if x > (ancho - anchoTexto):
                    return ancho - anchoTexto
                return x

            hx = norm(pCasillas.x + gapCasilla)
            hyS = norm(pFrontera.y + pFrontera.alto + sep)
            hyN = norm(pFrontera.y - anchoTexto - sep)

            vy = norm(pCasillas.y + gapCasilla)
            vxE = norm(pFrontera.x + pFrontera.ancho + sep)
            vxO = norm(pFrontera.x - anchoTexto - sep)

            for x in range(8):

                if self.nCoordenadas > 0:  # 2 o 3 o 4 o 5 o 6
                    d = {  # hS,     vO,     hN,     vE
                        2: (True, True, False, False),
                        3: (False, True, True, False),
                        4: (True, True, True, True),
                        5: (False, False, True, True),
                        6: (True, False, False, True),
                    }
                    liCo = d[self.nCoordenadas]
                    hor = coord.copia()
                    hor.valor = chr(97 + x)
                    hor.alineacion = "c"
                    hor.position.x = hx + x * self.anchoCasilla

                    if liCo[0]:
                        hor.position.y = hyS
                        horSC = TabElementos.TextoSC(self.escena, hor, self.pulsadaLetra)
                        self.liCoordenadasHorizontales.append(horSC)

                    if liCo[2]:
                        hor = hor.copia()
                        hor.position.y = hyN
                        horSC = TabElementos.TextoSC(self.escena, hor, self.pulsadaLetra)
                        self.liCoordenadasHorizontales.append(horSC)

                    ver = coord.copia()
                    ver.valor = chr(56 - x)
                    ver.alineacion = "c"
                    ver.position.y = vy + x * self.anchoCasilla

                    if liCo[1]:
                        ver.position.x = vxO
                        verSC = TabElementos.TextoSC(self.escena, ver, self.pulsadoNum)
                        self.liCoordenadasVerticales.append(verSC)

                    if liCo[3]:
                        ver = ver.copia()
                        ver.position.x = vxE
                        verSC = TabElementos.TextoSC(self.escena, ver, self.pulsadoNum)
                        self.liCoordenadasVerticales.append(verSC)

        # Indicador de color activo
        pFrontera = baseCasillasF.position
        pCajon = cajon.position
        ancho = pCajon.ancho - (pFrontera.x + pFrontera.ancho)
        gap = int(ancho / 8) * 2

        indicador = TabTipos.Circulo()
        indicador.position.x = (pFrontera.x + pFrontera.ancho) + gap / 2
        indicador.position.y = (pFrontera.y + pFrontera.alto) + gap / 2
        indicador.position.ancho = indicador.position.alto = ancho - gap
        indicador.position.orden = 2
        indicador.color = self.colorFrontera
        indicador.grosor = 1
        indicador.tipo = 1
        indicador.sur = indicador.position.y
        indicador.norte = gap / 2
        self.indicadorSC = TabElementos.CirculoSC(self.escena, indicador, rutina=self.intentaRotarTablero)

        # Lanzador de menu visual
        self.indicadorSC_menu = None
        self.scriptSC_menu = None
        if self.siMenuVisual:
            indicador_menu = TabTipos.Imagen()
            indicador_menu.position.x = pFrontera.x - ancho
            if self.configuracion.x_position_tool_board == "B":
                indicador_menu.position.y = pFrontera.y + pFrontera.alto + 2 * gap
            else:
                indicador_menu.position.y = 0

            indicador_menu.position.ancho = indicador_menu.position.alto = ancho - 2 * gap
            indicador_menu.position.orden = 2
            indicador_menu.color = self.colorFrontera
            indicador_menu.grosor = 1
            indicador_menu.tipo = 1
            indicador_menu.sur = indicador.position.y
            indicador_menu.norte = gap / 2
            self.indicadorSC_menu = TabElementos.PixmapSC(
                self.escena, indicador_menu, pixmap=Iconos.pmSettings(), rutina=self.lanzaMenuVisual
            )
            self.indicadorSC_menu.setOpacity(0.50 if self.configuracion.x_opacity_tool_board == 10 else 0.01)

            if self.siDirectorIcon:
                script = TabTipos.Imagen()
                script.position.x = pFrontera.x - ancho + ancho
                if self.configuracion.x_position_tool_board == "B":
                    script.position.y = pFrontera.y + pFrontera.alto + 2 * gap
                else:
                    script.position.y = 0

                script.position.ancho = script.position.alto = ancho - 2 * gap
                script.position.orden = 2
                script.color = self.colorFrontera
                script.grosor = 1
                script.tipo = 1
                script.sur = indicador.position.y
                script.norte = gap / 2
                self.scriptSC_menu = TabElementos.PixmapSC(
                    self.escena, script, pixmap=Iconos.pmLampara(), rutina=self.lanzaGuion
                )
                self.scriptSC_menu.hide()
                self.scriptSC_menu.setOpacity(0.70)

        self.init_kb_buffer()

    def setAcceptDropPGNs(self, rutinaDropsPGN):
        self.baseCasillasSC.setAcceptDrops(rutinaDropsPGN is not None)
        self.rutinaDropsPGN = rutinaDropsPGN

    def dropEvent(self, event):
        if self.rutinaDropsPGN is not None:
            mimeData = event.mimeData()
            if mimeData.hasUrls():
                li = mimeData.urls()
                if len(li) > 0:
                    self.rutinaDropsPGN(li[0].path().strip("/"))
        event.setDropAction(QtCore.Qt.IgnoreAction)
        event.ignore()
        # if mimeData.hasFormat('image/x-lc-dato'):
        #     dato = mimeData.data('image/x-lc-dato')
        #     p = event.pos()
        #     x = p.x()
        #     y = p.y()
        #     cx = self.punto2columna(x)
        #     cy = self.punto2fila(y)
        #     if cx in range(1, 9) and cy in range(1, 9):
        #         a1h8 = self.num2alg(cy, cx)
        #         self.dispatchDrop(a1h8, str(dato))
        #     event.setDropAction(QtCore.Qt.IgnoreAction)

    def showKeys(self):
        liKeys = [
            (_("ALT") + " F", _("Flip the board")),
            (_("CTRL") + " C", _("Copy FEN to clipboard")),
            (_("ALT") + " I", _("Copy board as image to clipboard")),
            (_("CTRL") + " I", _("Copy board as image to clipboard") + " (%s)" % _("without border")),
            (
                _("CTRL") + "+" + _("ALT") + " I",
                _("Copy board as image to clipboard") + " (%s)" % _("without coordinates"),
            ),
            (_("ALT") + " J", _("Copy board as image to a file")),
            (_("CTRL") + " J", _("Copy board as image to a file") + " (%s)" % _("without border")),
            (
                _("CTRL") + "+" + _("ALT") + " J",
                _("Copy board as image to a file") + " (%s)" % _("without coordinates"),
            ),
        ]
        if self.siActivasPiezas:
            liKeys.append((None, None))
            liKeys.append(("a1 ... h8", _("To indicate origin and destination of a move")))

        if hasattr(self.main_window, "gestor") and self.main_window.gestor:
            if hasattr(self.main_window.gestor, "rightMouse"):
                liKeys.append((None, None))
                liKeys.append(("P", _("Show/Hide PGN information")))
                liKeys.append((_("ALT") + "-C", _("Show/Hide captures")))
                liKeys.append((_("ALT") + "-N", _("Activate/Deactivate non distract mode")))

            if hasattr(self.main_window.gestor, "listHelpTeclado"):
                liKeys.append((None, None))
                liKeys.extend(self.main_window.gestor.listHelpTeclado())

        rondo = QTVarios.rondoPuntos()
        menu = QTVarios.LCMenu(self)
        menu.opcion(None, _("Active keys"), Iconos.Rename())
        menu.separador()
        for key, mess in liKeys:
            if key is None:
                menu.separador()
            else:
                menu.opcion(None, "%s [%s]" % (mess, key), rondo.otro())
        menu.lanza()

    def lanzaMenuVisual(self, siIzquierdo=False):
        if not self.siMenuVisual:
            return

        menu = QTVarios.LCMenu(self)

        menu.opcion("colors", _("Colors"), Iconos.Colores())
        menu.separador()
        menu.opcion("pieces", _("Pieces"), self.piezas.icono("K"))
        menu.separador()
        if not self.siMaximizado():
            menu.opcion("size", _("Change board size"), Iconos.TamTablero())
            menu.separador()

        menu.opcion("def_todo", _("Default"), Iconos.Defecto())

        menu.separador()
        if self.siDirector:
            menu.opcion("director", _("Director") + " [%s] " % _("F1-F10"), Iconos.Director())
            menu.separador()

        if self.siPosibleRotarTablero:
            menu.opcion("girar", _("Flip the board") + " [%s-F]" % _("ALT"), Iconos.JS_Rotacion())
            menu.separador()

        menu.opcion("keys", _("Active keys") + " [%s-K]" % _("ALT"), Iconos.Rename())
        menu.separador()

        resp = menu.lanza()
        if resp is None:
            return
        elif resp == "colors":
            menucol = QTVarios.LCMenu(self)
            menucol.opcion("editar", _("Edit"), Iconos.EditarColores())
            menucol.separador()
            liTemas = Util.restore_pickle(Code.configuracion.ficheroTemas)
            if liTemas:
                PantallaColores.ponMenuTemas(menucol, liTemas, "tt_")
                menucol.separador()
            for entry in Util.listdir(Code.path_resource("Themes")):
                fich = entry.name
                if fich.lower().endswith(".lktheme3"):
                    self.fich_ = fich[:-9]
                    name = self.fich_
                    menucol.opcion("ot_" + fich, name, Iconos.Division())
            resp = menucol.lanza()
            if resp:
                if resp == "editar":
                    w = PantallaColores.WColores(self)
                    w.exec_()
                else:
                    self.ponColores(liTemas, resp)

        elif resp == "pieces":
            menup = QTVarios.LCMenu(self)
            li = []
            for x in Util.listdir(Code.path_resource("Pieces")):
                try:
                    if x.is_dir():
                        ico = Code.todasPiezas.icono("K", x.name)
                        li.append((x.name, ico))
                except:
                    pass
            li.sort(key=lambda x: x[0])
            for x, ico in li:
                menup.opcion(x, x, ico)
            resp = menup.lanza()
            if resp:
                self.cambiaPiezas(resp)

        elif resp == "size":
            self.cambiaSize()

        elif resp == "girar":
            self.rotaTablero()

        elif resp == "director":
            self.lanzaDirector()

        elif resp == "keys":
            self.showKeys()

        elif resp.startswith("def_"):
            if resp.endswith("todo"):
                self.config_board = self.configuracion.resetConfTablero(
                    self.config_board.id(), self.config_board.anchoPieza()
                )
                self.reset(self.config_board)

    def lanzaDirector(self):
        if self.siDirector:
            if self.dirvisual:
                self.dirvisual.terminar()
                self.dirvisual = None
                return False
            else:
                from Code.QT import PantallaDirector

                self.dirvisual = PantallaDirector.Director(self)
            return True
        else:
            return False

    def cierraGuion(self):
        if self.guion is not None:
            self.guion.cierraPizarra()
            self.guion.cerrado = True
            self.guion = None

    def lanzaGuion(self):
        if self.guion is not None:
            self.cierraGuion()
        else:
            self.guion = TabVisual.Guion(self)
            self.guion.recupera()
            self.guion.play()

    def cambiaSize(self):
        imp = WTamTablero(self)
        imp.colocate()
        imp.exec_()

    def cambiaPiezas(self, cual):
        self.config_board.cambiaPiezas(cual)
        self.config_board.guardaEnDisco()
        ap, apc = self.siActivasPiezas, self.siActivasPiezasColor
        siFlecha = self.flechaSC is not None

        self.crea()
        if ap:
            self.activaColor(apc)
            self.ponIndicador(apc)

        if siFlecha:
            # self.ponFlechaSC( self.ultMovFlecha[0], self.ultMovFlecha[1])
            self.resetFlechaSC()

        self.init_kb_buffer()

        if self.config_board.is_base:
            nomPiezasOri = self.config_board.nomPiezas()
            Code.todasPiezas.saveAllPNG(nomPiezasOri, 20)  # reset IntFiles/Figs
            Delegados.generaPM(self.piezas)

    def ponColores(self, liTemas, resp):
        if resp.startswith("tt_"):
            tema = liTemas[int(resp[3:])]

        else:
            fich = Code.path_resource("Themes/%s" % resp[3:])
            tema = PantallaColores.eligeTema(self, fich)

        if tema:
            self.config_board.leeTema(tema["o_tema"])
            if "o_base" in tema:
                self.config_board.leeBase(tema["o_base"])

            self.config_board.guardaEnDisco()
            self.crea()

    def reset(self, config_board):
        self.config_board = config_board
        for item in self.escena.items():
            self.xremoveItem(item)
            del item
        self.crea()

    def key_current_graphlive(self, event):
        m = int(event.modifiers())
        key = ""
        if (m & QtCore.Qt.ControlModifier) > 0:
            key = "CTRL"
        if (m & QtCore.Qt.AltModifier) > 0:
            key += "ALT"
        if (m & QtCore.Qt.ShiftModifier) > 0:
            key += "SHIFT"
        return key

    def mousePressGraphLive(self, event, a1h8):
        if not self.configuracion.x_direct_graphics:
            return
        key = self.key_current_graphlive(event)
        key += "MR"
        if self.dic_graphlive is None:
            self.dic_graphlive = self.readGraphLive()
        elem = self.dic_graphlive[key] if key in self.dic_graphlive else None
        if elem:
            elem.a1h8 = a1h8 + a1h8
            if TabVisual.TP_FLECHA == elem.TP:
                self.current_graphlive = self.creaFlecha(elem)
                self.current_graphlive.mousePressExt(event)
            elif TabVisual.TP_MARCO == elem.TP:
                self.current_graphlive = self.creaMarco(elem)
                self.current_graphlive.mousePressExt(event)
            elif TabVisual.TP_MARKER == elem.TP:
                self.current_graphlive = self.creaMarker(elem)
                self.current_graphlive.mousePressExt(event)
            elif TabVisual.TP_SVG == elem.TP:
                self.current_graphlive = self.creaSVG(elem, False)
                self.current_graphlive.mousePressExt(event)

            self.current_graphlive.TP = elem.TP

    def mouseMoveGraphLive(self, event):
        if not self.configuracion.x_direct_graphics:
            return
        if self.current_graphlive.TP in (TabVisual.TP_FLECHA, TabVisual.TP_MARCO):
            self.current_graphlive.mouseMoveExt(event)
        self.current_graphlive.update()

    def readGraphLive(self):
        rel = {
            0: "MR",
            1: "ALTMR",
            2: "SHIFTMR",
            3: "CTRLMR",
            4: "CTRLALTMR",
            5: "CTRLSHIFTMR",
            6: "MR1",
            7: "ALTMR1",
            8: "SHIFTMR1",
        }
        dic = {}
        db = self.dbVisual
        li = self.dbVisual.dbConfig["SELECTBANDA"]
        if li:
            for xid, pos in li:
                if xid.startswith("_F"):
                    xdb = db.dbFlechas
                    tp = TabVisual.TP_FLECHA
                    obj = TabTipos.Flecha()
                elif xid.startswith("_M"):
                    xdb = db.dbMarcos
                    tp = TabVisual.TP_MARCO
                    obj = TabTipos.Marco()
                elif xid.startswith("_S"):
                    xdb = db.dbSVGs
                    tp = TabVisual.TP_SVG
                    obj = TabTipos.SVG()
                elif xid.startswith("_X"):
                    xdb = db.dbMarkers
                    tp = TabVisual.TP_MARKER
                    obj = TabTipos.Marker()
                else:
                    continue
                if pos in rel:
                    cnum_id = xid[3:]
                    dic_current = xdb[cnum_id]
                    obj.restore_dic(dic_current)
                    obj.TP = tp
                    obj.id = int(cnum_id)
                    obj.tpid = (tp, obj.id)
                    dic[rel[pos]] = obj
        return dic

    def remove_current_graphlive(self):
        if self.current_graphlive:
            self.current_graphlive.hide()
            del self.current_graphlive
            self.current_graphlive = None
            self.borraUltimoMovible()

    def mouseReleaseGraphLive(self, event):
        if not self.configuracion.x_direct_graphics:
            return
        h8 = self.event2a1h8(event)
        if h8 is not None:
            a1 = self.current_graphlive.bloqueDatos.a1h8[:2]
            key = self.key_current_graphlive(event)
            if a1 == h8 and not key.startswith("CTRL"):
                self.remove_current_graphlive()
                key += "MR1"
                elem = self.dic_graphlive[key]
                elem.a1h8 = a1 + a1
                tp = elem.TP
                if tp == TabVisual.TP_SVG:
                    self.current_graphlive = self.creaSVG(elem)
                    self.current_graphlive.TP = tp
                elif tp == TabVisual.TP_MARCO:
                    self.current_graphlive = self.creaMarco(elem)
                    self.current_graphlive.TP = tp
                elif tp == TabVisual.TP_MARKER:
                    self.current_graphlive = self.creaMarker(elem)
                    self.current_graphlive.TP = tp

            else:
                self.current_graphlive.ponA1H8(a1 + h8)
            keys = self.dicMovibles.keys()
            if len(keys) > 1:
                last = len(keys) - 1
                bd_last = self.current_graphlive.bloqueDatos
                st = set()
                for n, (pos, item) in enumerate(self.dicMovibles.items()):
                    if n != last:
                        bd = item.bloqueDatos
                        if hasattr(bd_last, "tpid") and bd_last.tpid == bd.tpid and bd_last.a1h8 in (bd.a1h8, bd.a1h8[2:] + bd.a1h8[:2]):
                            st.add(self.current_graphlive)
                            st.add(item)
                for item in st:
                    self.borraMovible(item)

            self.refresh()
        self.current_graphlive = None

    def mouseMoveEvent(self, event):
        if self.dirvisual and self.dirvisual.mouseMoveEvent(event):
            return
        pos = event.pos()
        x = pos.x()
        y = pos.y()
        minimo = self.margenCentro
        maximo = self.margenCentro + (self.anchoCasilla * 8)
        siDentro = (minimo < x < maximo) and (minimo < y < maximo)
        if siDentro and self.current_graphlive:
            return self.mouseMoveGraphLive(event)

        QtWidgets.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.dirvisual and self.dirvisual.mouseReleaseEvent(event):
            return
        if self.pendingRelease:
            for objeto in self.pendingRelease:
                objeto.hide()
                del objeto
            self.escena.update()
            self.update()
            self.pendingRelease = None
        QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
        if self.current_graphlive:
            self.mouseReleaseGraphLive(event)

    def event2a1h8(self, event):
        pos = event.pos()
        x = pos.x()
        y = pos.y()
        minimo = self.margenCentro
        maximo = self.margenCentro + (self.anchoCasilla * 8)
        if (minimo < x < maximo) and (minimo < y < maximo):
            xc = 1 + int(float(x - self.margenCentro) / self.anchoCasilla)
            yc = 1 + int(float(y - self.margenCentro) / self.anchoCasilla)

            if self.is_white_bottom:
                yc = 9 - yc
            else:
                xc = 9 - xc

            f = chr(48 + yc)
            c = chr(96 + xc)
            a1h8 = c + f
        else:
            a1h8 = None
        return a1h8

    def mousePressEvent(self, event):
        if self.dirvisual and self.dirvisual.mousePressEvent(event):
            return
        a1h8 = self.event2a1h8(event)

        siRight = event.button() == QtCore.Qt.RightButton
        if siRight and a1h8:
            return self.mousePressGraphLive(event, a1h8)

        QtWidgets.QGraphicsView.mousePressEvent(self, event)

        self.blindfoldPosicion(False, None, None)
        if a1h8 is None:
            if self.atajosRaton:
                self.atajosRaton(None)
            # QtWidgets.QGraphicsView.mousePressEvent(self,event)
            return

        if self.atajosRaton:
            self.atajosRaton(a1h8)
            # Atajos raton lanza show_candidates si hace falta

        elif hasattr(self.main_window, "gestor"):
            if hasattr(self.main_window.gestor, "colect_candidates"):
                liC = self.main_window.gestor.colect_candidates(a1h8)
                if liC:
                    self.show_candidates(liC)

    def checkLEDS(self):
        if not hasattr(self, "dicXML"):

            def lee(fich):
                f = open(Code.path_resource("IntFiles/Svg", "%s.svg" % fich))
                resp = f.read()
                f.close()
                return resp

            self.dicXML = {}
            self.dicXML["C"] = lee("candidate")
            self.dicXML["P+"] = lee("player_check")
            self.dicXML["Px"] = lee("player_capt")
            self.dicXML["P#"] = lee("player_mate")
            self.dicXML["R+"] = lee("rival_check")
            self.dicXML["Rx"] = lee("rival_capt")
            self.dicXML["R#"] = lee("rival_mate")
            self.dicXML["R"] = lee("rival")

    def markPositionExt(self, a1, h8, tipo):
        self.checkLEDS()
        lista = []
        for posCuadro in range(4):
            regSVG = TabTipos.SVG()
            regSVG.a1h8 = a1 + h8
            regSVG.xml = self.dicXML[tipo]
            regSVG.siMovible = False
            regSVG.posCuadro = posCuadro
            regSVG.anchoCasilla = self.anchoCasilla
            if a1 != h8:
                regSVG.anchoCasilla *= 7.64
            svg = TabSVG.SVGCandidate(self.escena, regSVG, False)
            lista.append(svg)
        self.escena.update()

        def quita():
            for objeto in lista:
                objeto.hide()
                del objeto
            self.update()

        QtCore.QTimer.singleShot(1600 if tipo == "C" else 500, quita)

    def markPosition(self, a1):
        self.markPositionExt(a1, a1, "C")

    def markError(self, a1):
        if a1:
            self.markPositionExt(a1, a1, "R")

    def show_candidates(self, liC):
        if not liC or not self.configuracion.x_show_candidates:
            return
        self.checkLEDS()

        dicPosCuadro = {"C": 0, "P+": 1, "Px": 1, "P#": 1, "R+": 2, "R#": 2, "Rx": 3}
        self.pendingRelease = []
        for a1, tp in liC:
            regSVG = TabTipos.SVG()
            regSVG.a1h8 = a1 + a1
            regSVG.xml = self.dicXML[tp]
            regSVG.siMovible = False
            regSVG.posCuadro = dicPosCuadro[tp]
            regSVG.anchoCasilla = self.anchoCasilla
            svg = TabSVG.SVGCandidate(self.escena, regSVG, False)
            self.pendingRelease.append(svg)
        self.escena.update()

    def mouseDoubleClickEvent(self, event):
        item = self.itemAt(event.pos())
        if item:
            if item == self.flechaSC:
                self.flechaSC.hide()

    def wheelEvent(self, event):
        if QtWidgets.QApplication.keyboardModifiers() == QtCore.Qt.ControlModifier:
            if self.permitidoResizeExterno():
                salto = event.delta() < 0
                ap = self.config_board.anchoPieza()
                if ap > 500:
                    ap = 64
                ap += 4 * (+1 if salto else -1)
                if ap >= 10:
                    self.config_board.anchoPieza(ap)
                    self.config_board.guardaEnDisco()
                    self.cambiadoAncho()
                    return

        elif hasattr(self.main_window, "tableroWheelEvent"):
            self.main_window.tableroWheelEvent(self, event.delta() < 0)

    def set_dispatcher(self, mensajero, atajosRaton=None):
        if self.dirvisual:
            self.dirvisual.cambiadoMensajero()
        self.mensajero = mensajero
        if atajosRaton:
            self.atajosRaton = atajosRaton
        self.init_kb_buffer()

    def dbVisual_setFichero(self, fichero):
        self.dbVisual.setFichero(fichero)

    def dbVisual_setShowAllways(self, ok):
        self.dbVisual.showAllways(ok)

    def dbVisual_setSaveAllways(self, ok):
        self.dbVisual.saveAllways(ok)

    def dbVisual_close(self):
        self.dbVisual.close()

    def dbVisual_contiene(self, fenm2):
        return fenm2 in self.dbVisual.dbFEN and len(self.dbVisual.dbFEN[fenm2]) > 0

    def dbVisual_lista(self, fenm2):
        return self.dbVisual.dbFEN[fenm2]

    def dbVisual_save(self, fenm2, lista):
        self.dbVisual.dbFEN[fenm2] = lista

    def saveVisual(self):
        alm = self.almSaveVisual = Util.Record()
        alm.siMenuVisual = self.siMenuVisual
        alm.siDirector = self.siDirector
        alm.siDirectorIcon = self.siDirectorIcon
        alm.dirvisual = self.dirvisual
        alm.guion = self.guion
        alm.lastFenM2 = self.lastFenM2
        alm.nomdbVisual = self.dbVisual.fichero
        alm.dbVisual_showAllways = self.dbVisual.showAllways()

    def restoreVisual(self):
        alm = self.almSaveVisual
        self.siMenuVisual = alm.siMenuVisual
        self.siDirector = alm.siDirector
        self.siDirectorIcon = alm.siDirectorIcon
        self.dirvisual = alm.dirvisual
        self.guion = alm.guion
        self.lastFenM2 = alm.lastFenM2
        self.dbVisual.setFichero(alm.nomdbVisual)
        self.dbVisual.showAllways(alm.dbVisual_showAllways)

    def setUltPosicion(self, position):
        self.cierraGuion()
        self.last_position = position
        if self.siDirectorIcon or self.dbVisual.showAllways():
            fenm2 = position.fenm2()
            if self.lastFenM2 != fenm2:
                self.lastFenM2 = fenm2
                if self.dbVisual_contiene(fenm2):
                    if self.siDirectorIcon:
                        self.scriptSC_menu.show()
                    if self.dbVisual.showAllways():
                        self.lanzaGuion()
                elif self.siDirectorIcon:
                    self.scriptSC_menu.hide()

    def setposition(self, position, siBorraMoviblesAhora=True):
        if self.dirvisual:
            self.dirvisual.cambiadaPosicionAntes()
        elif self.dbVisual.saveAllways():
            self.dbVisual.saveMoviblesTablero(self)

        if self.si_borraMovibles and siBorraMoviblesAhora:
            self.borraMovibles()
        self.ponPosicionBase(position)

        if self.dirvisual:
            self.dirvisual.cambiadaPosicionDespues()

    def removePieces(self):
        for x in self.liPiezas:
            if x[2]:
                self.xremoveItem(x[1])
        self.liPiezas = []

    def ponPosicionBase(self, position):
        self.blindfoldPosicion(True, position, self.last_position)

        self.siActivasPiezas = False
        self.removePieces()

        squares = position.squares
        for k in squares.keys():
            if squares[k]:
                self.ponPieza(squares[k], k)

        self.escena.update()
        if self.hard_focus:
            self.setFocus()
        self.ponIndicador(position.is_white)
        if self.flechaSC:
            self.xremoveItem(self.flechaSC)
            del self.flechaSC
            self.flechaSC = None
            self.quitaFlechas()
        self.init_kb_buffer()
        self.setUltPosicion(position)
        QtCore.QCoreApplication.processEvents(QtCore.QEventLoop.ExcludeUserInputEvents)

    def fila2punto(self, fila):
        factor = (8 - fila) if self.is_white_bottom else (fila - 1)
        return factor * (self.anchoPieza + self.margenPieza * 2) + self.margenCentro + self.margenPieza + 2

    def columna2punto(self, columna):
        factor = (columna - 1) if self.is_white_bottom else (8 - columna)
        return factor * (self.anchoPieza + self.margenPieza * 2) + self.margenCentro + self.margenPieza + 2

    def punto2fila(self, pos):
        pos -= self.margenCentro + self.margenPieza + 2
        pos //= self.anchoPieza + self.margenPieza * 2
        if self.is_white_bottom:
            return int(8 - pos)
        else:
            return int(pos + 1)

    def punto2columna(self, pos):
        pos -= self.margenCentro + self.margenPieza + 2
        pos //= self.anchoPieza + self.margenPieza * 2
        if self.is_white_bottom:
            return int(pos + 1)
        else:
            return int(8 - pos)

    def colocaPieza(self, bloquePieza, posA1H8):
        bloquePieza.fila = int(posA1H8[1])
        bloquePieza.columna = ord(posA1H8[0]) - 96
        self.recolocaPieza(bloquePieza)

    def recolocaPieza(self, bloquePieza):
        position = bloquePieza.position
        position.x = self.columna2punto(bloquePieza.columna)
        position.y = self.fila2punto(bloquePieza.fila)

    def creaPieza(self, cpieza, posA1H8):
        bloque_pieza = TabTipos.Pieza()
        p = bloque_pieza.position
        p.ancho = self.anchoPieza
        p.alto = self.anchoPieza
        p.orden = ZVALUE_PIECE
        bloque_pieza.pieza = cpieza
        self.colocaPieza(bloque_pieza, posA1H8)
        piezaSC = TabElementos.PiezaSC(self.escena, bloque_pieza, self)

        # piezaSC.setOpacity(self.opacidad[0 if cpieza.isupper() else 1])

        self.liPiezas.append([cpieza, piezaSC, True])
        return piezaSC

    def ponPieza(self, pieza, posA1H8):
        for x in self.liPiezas:
            if not x[2] and x[0] == pieza:
                piezaSC = x[1]
                self.colocaPieza(piezaSC.bloquePieza, posA1H8)
                self.escena.addItem(piezaSC)
                piezaSC.update()
                x[2] = True
                return piezaSC

        return self.creaPieza(pieza, posA1H8)

    def mostrarPiezas(self, siW, siB):
        if siW and siB:
            self.blindfold = None
        elif siW and not siB:
            self.blindfold = BLINDFOLD_BLACK
        elif siB and not siW:
            self.blindfold = BLINDFOLD_WHITE
        else:
            self.blindfold = BLINDFOLD_ALL
        self.blindfoldReset()

    def blindfoldChange(self, modoPosicion):
        self.blindfold = None if self.blindfold else BLINDFOLD_CONFIG
        self.blindfoldReset()
        self.blindfoldModoPosicion = modoPosicion if self.blindfold else False

    def blindfoldReset(self):
        ap, apc = self.siActivasPiezas, self.siActivasPiezasColor
        siFlecha = self.flechaSC is not None

        is_white_bottom = self.is_white_bottom

        atajosRaton = self.atajosRaton

        self.crea()
        if not is_white_bottom:
            self.intentaRotarTablero(None)

        if ap:
            self.activaColor(apc)
            self.ponIndicador(apc)

        if siFlecha:
            self.resetFlechaSC()

        self.atajosRaton = atajosRaton
        self.init_kb_buffer()

    def blindfoldQuitar(self):
        if self.blindfold:
            self.blindfold = None
            self.blindfoldReset()

    def blindfoldPosicion(self, inicio, nueposicion, ultposicion):
        if self.blindfoldModoPosicion:
            if inicio:
                if ultposicion and nueposicion.fen() != ultposicion.fen():
                    b = self.blindfold
                    self.blindfold = None
                    self.blindfoldReset()
                    self.blindfold = b
            else:
                self.blindfoldReset()

    def blindfoldConfig(self):
        nomPiezasOri = self.config_board.nomPiezas()
        w = Piezas.WBlindfold(self, nomPiezasOri)
        if w.exec_():
            self.blindfold = BLINDFOLD_CONFIG
            self.blindfoldReset()

    def buscaPieza(self, posA1H8):
        if posA1H8 is None:
            return -1
        fila = int(posA1H8[1])
        columna = ord(posA1H8[0]) - 96
        for num, x in enumerate(self.liPiezas):
            if x[2]:
                pieza = x[1].bloquePieza
                if pieza.fila == fila and pieza.columna == columna:
                    return num
        return -1

    def damePiezaEn(self, posA1H8):
        npieza = self.buscaPieza(posA1H8)
        if npieza >= 0:
            return self.liPiezas[npieza][1]
        return None

    def dameNomPiezaEn(self, posA1H8):
        npieza = self.buscaPieza(posA1H8)
        if npieza >= 0:
            return self.liPiezas[npieza][0]
        return None

    def muevePiezaTemporal(self, desdeA1H8, hastaA1H8):
        npieza = self.buscaPieza(desdeA1H8)
        if npieza >= 0:
            piezaSC = self.liPiezas[npieza][1]
            fila = int(hastaA1H8[1])
            columna = ord(hastaA1H8[0]) - 96
            x = self.columna2punto(columna)
            y = self.fila2punto(fila)
            piezaSC.setPos(x, y)

    def muevePieza(self, desdeA1H8, hastaA1H8):
        npieza = self.buscaPieza(desdeA1H8)
        if npieza >= 0:
            self.borraPieza(hastaA1H8)
            piezaSC = self.liPiezas[npieza][1]
            self.colocaPieza(piezaSC.bloquePieza, hastaA1H8)
            piezaSC.rehazPosicion()
            piezaSC.update()
            self.escena.update()

    def reponPieza(self, posA1H8):
        npieza = self.buscaPieza(posA1H8)
        if npieza >= 0:
            piezaSC = self.liPiezas[npieza][1]
            piezaSC.rehazPosicion()
            piezaSC.update()
            self.escena.update()

    def borraPieza(self, posA1H8):
        npieza = self.buscaPieza(posA1H8)
        if npieza >= 0:
            piezaSC = self.liPiezas[npieza][1]
            self.xremoveItem(piezaSC)
            self.liPiezas[npieza][2] = False
            self.escena.update()

    def borraPiezaTipo(self, posA1H8, tipo):
        fila = int(posA1H8[1])
        columna = ord(posA1H8[0]) - 96
        for num, x in enumerate(self.liPiezas):
            if x[2]:
                pieza = x[1].bloquePieza
                if pieza.fila == fila and pieza.columna == columna and pieza.pieza == tipo:
                    piezaSC = self.liPiezas[num][1]
                    self.xremoveItem(piezaSC)
                    self.liPiezas[num][2] = False
                    self.escena.update()
                    return

    def cambiaPieza(self, posA1H8, nueva):
        self.borraPieza(posA1H8)
        return self.creaPieza(nueva, posA1H8)

    def activaColor(self, is_white):
        self.siActivasPiezas = True
        self.siActivasPiezasColor = is_white
        for pieza, piezaSC, is_active in self.liPiezas:
            if is_active:
                if is_white is None:
                    resp = True
                else:
                    if pieza.isupper():
                        resp = is_white
                    else:
                        resp = not is_white
                piezaSC.activa(resp)
        self.init_kb_buffer()

    def setDispatchMove(self, rutina):
        for pieza, piezaSC, is_active in self.liPiezas:
            if is_active:
                piezaSC.setDispatchMove(rutina)

    def activaTodas(self):
        self.siActivasPiezas = True
        for num, una in enumerate(self.liPiezas):
            pieza, piezaSC, is_active = una
            if is_active:
                piezaSC.activa(True)
        self.init_kb_buffer()

    def disable_all(self):
        self.siActivasPiezas = False
        self.siActivasPiezasColor = None
        for num, una in enumerate(self.liPiezas):
            pieza, piezaSC, is_active = una
            if is_active:
                piezaSC.activa(False)
        self.init_kb_buffer()

    def num2alg(self, fila, columna):
        return chr(96 + columna) + str(fila)

    def alg2num(self, a1):
        x = self.columna2punto(ord(a1[0]) - 96)
        y = self.fila2punto(ord(a1[1]) - 48)
        return x, y

    def intentaMover(self, piezaSC, posCursor, eventButton):
        pieza = piezaSC.bloquePieza
        from_sq = self.num2alg(pieza.fila, pieza.columna)

        x = int(posCursor.x())
        y = int(posCursor.y())
        cx = self.punto2columna(x)
        cy = self.punto2fila(y)

        if cx in range(1, 9) and cy in range(1, 9):
            to_sq = self.num2alg(cy, cx)

            x = self.columna2punto(cx)
            y = self.fila2punto(cy)
            piezaSC.setPos(x, y)
            if to_sq == from_sq:
                return

            if not self.mensajero(from_sq, to_sq):
                x, y = self.alg2num(from_sq)
                piezaSC.setPos(x, y)

            # -CONTROL-
            self.init_kb_buffer()

        piezaSC.rehazPosicion()
        piezaSC.update()
        self.escena.update()
        QTUtil.refresh_gui()

    def ponIndicador(self, is_white):
        bd = self.indicadorSC.bloqueDatos
        if is_white:
            bd.colorRelleno = self.colorBlancas
            siAbajo = self.is_white_bottom
        else:
            bd.colorRelleno = self.colorNegras
            siAbajo = not self.is_white_bottom
        bd.position.y = bd.sur if siAbajo else bd.norte
        self.indicadorSC.mostrar()

    def resetFlechaSC(self):
        if self.flechaSC:
            a1h8 = self.flechaSC.bloqueDatos.a1h8
            self.ponFlechaSC(a1h8[:2], a1h8[2:])

    def ponFlechaSC(self, desdeA1h8, hastaA1h8):
        a1h8 = desdeA1h8 + hastaA1h8
        if self.flechaSC is None:
            self.flechaSC = self.creaFlechaSC(a1h8)
        self.flechaSC.show()
        self.flechaSC.ponA1H8(a1h8)
        self.flechaSC.update()

    def ponFlechaSCvar(self, liArrows, destino=None, opacidad=None):
        if destino is None:
            destino = "m"
        if opacidad is None:
            opacidad = 0.4
        for from_sq, to_sq in liArrows:
            if from_sq and to_sq:
                self.creaFlechaMulti(from_sq + to_sq, False, destino=destino, opacidad=opacidad)

    def pulsadaFlechaSC(self):
        self.flechaSC.hide()

    def creaFlechaMulti(self, a1h8, siMain, destino="c", opacidad=0.9):
        bf = copy.deepcopy(self.config_board.fTransicion() if siMain else self.config_board.fAlternativa())
        bf.a1h8 = a1h8
        bf.destino = destino
        bf.opacidad = opacidad

        flecha = self.creaFlecha(bf)
        self.liFlechas.append(flecha)
        flecha.show()

    def creaFlechaSC(self, a1h8):
        bf = copy.deepcopy(self.config_board.fTransicion())
        bf.a1h8 = a1h8
        bf.anchoCasilla = self.anchoCasilla
        bf.siMovible = False

        return self.creaFlecha(bf, self.pulsadaFlechaSC)

    def creaFlechaTmp(self, desdeA1h8, hastaA1h8, siMain):
        bf = copy.deepcopy(self.config_board.fTransicion() if siMain else self.config_board.fAlternativa())
        bf.a1h8 = desdeA1h8 + hastaA1h8
        flecha = self.creaFlecha(bf)
        self.liFlechas.append(flecha)
        flecha.show()

    def creaFlechaPremove(self, desde, hasta):
        bf = copy.deepcopy(self.config_board.fActivo())
        bf.a1h8 = desde + hasta
        flecha = self.creaFlecha(bf)
        self.liFlechas.append(flecha)
        flecha.show()
        self.update()

    def creaFlechaTutor(self, desdeA1h8, hastaA1h8, factor):
        bf = copy.deepcopy(self.config_board.fTransicion())
        bf.a1h8 = desdeA1h8 + hastaA1h8
        bf.opacidad = max(factor, 0.20)
        bf.ancho = max(bf.ancho * 2 * (factor ** 2.2), bf.ancho / 3)
        bf.altocabeza = max(bf.altocabeza * (factor ** 2.2), bf.altocabeza / 3)
        bf.vuelo = bf.altocabeza / 3
        bf.grosor = 1
        bf.redondeos = True
        bf.forma = "1"
        bf.position.orden = ZVALUE_PIECE + 1

        flecha = self.creaFlecha(bf)
        self.liFlechas.append(flecha)
        flecha.show()

    def ponFlechasTmp(self, lista, ms=None):
        if self.flechaSC:
            self.flechaSC.hide()
        for from_sq, to_sq, siMain in lista:
            self.creaFlechaTmp(from_sq, to_sq, siMain)
        QTUtil.refresh_gui()

        def quitaFlechasTmp():
            self.quitaFlechas()
            if self.flechaSC:
                self.flechaSC.show()

        if ms is None:
            ms = 2000 if len(lista) > 1 else 1400
        QtCore.QTimer.singleShot(2000 if len(lista) > 1 else 1400, quitaFlechasTmp)

    def creaFlechaMov(self, desdeA1h8, hastaA1h8, modo):
        bf = TabTipos.Flecha()
        bf.trasparencia = 0.9
        bf.position.orden = ZVALUE_PIECE + 1
        bf.anchoCasilla = self.anchoCasilla
        bf.color = self.config_board.fTransicion().color
        bf.redondeos = False
        bf.forma = "a"

        siPieza = self.buscaPieza(hastaA1h8) > -1
        if modo == "m":  # movimientos
            bf.tipo = 2
            bf.grosor = 2
            bf.altocabeza = 6
            bf.destino = "m" if siPieza else "c"

        elif modo == "c":  # captura
            bf.tipo = 1
            bf.grosor = 2
            bf.altocabeza = 8
            bf.destino = "m" if siPieza else "c"

        elif modo == "b":  # base para doble movimiento
            bf.tipo = 1
            bf.grosor = 2
            bf.altocabeza = 0
            bf.destino = "c"

        elif modo == "bm":  # base para doble movimiento
            bf.tipo = 2
            bf.grosor = 2
            bf.altocabeza = 0
            bf.destino = "c"

        elif modo == "2":  # m2
            bf = copy.deepcopy(self.config_board.fTransicion())
            bf.trasparencia = 1.0
            bf.destino = "c"

        elif modo == "3":  # m2+
            bf.tipo = 2
            bf.grosor = 3
            bf.altocabeza = 0
            bf.destino = "m"
            bf.position.orden = ZVALUE_PIECE - 1

        elif modo == "4":  # m2+
            bf.tipo = 1
            bf.grosor = 2
            bf.altocabeza = 0
            bf.destino = "m"
            bf.position.orden = ZVALUE_PIECE - 1

        elif modo == "e1":  # ent_pos1
            bf.tipo = 1
            bf.grosor = 2
            bf.altocabeza = 6
            bf.destino = "m"

        elif modo == "e2":  # ent_pos1
            bf.tipo = 2
            bf.grosor = 2
            bf.altocabeza = 6
            bf.destino = "m"

        elif modo.startswith("ms"):
            resto = modo[2:]
            bf = copy.deepcopy(self.config_board.fActivo())
            bf.opacidad = float(resto) / 100.0
            bf.anchoCasilla = self.anchoCasilla

        elif modo.startswith("mt"):
            resto = modo[2:]
            bf = self.config_board.fRival().copia()
            bf.opacidad = float(resto) / 100.0
            bf.anchoCasilla = self.anchoCasilla

        elif modo.startswith("m1"):
            resto = modo[2:]
            bf = self.config_board.fTransicion().copia()
            bf.opacidad = float(resto) / 100.0
            bf.anchoCasilla = self.anchoCasilla

        if self.anchoPieza > 24:
            bf.grosor = bf.grosor * 15 / 10
            bf.altocabeza = bf.altocabeza * 15 / 10

        bf.a1h8 = desdeA1h8 + hastaA1h8

        flecha = self.creaFlecha(bf)
        self.liFlechas.append(flecha)
        flecha.show()

    def quitaFlechas(self):
        for flecha in self.liFlechas:
            self.xremoveItem(flecha)
            flecha.hide()
            del flecha
        self.liFlechas = []
        self.update()

    def ponerPiezasAbajo(self, is_white_bottom):
        if self.is_white_bottom == is_white_bottom:
            return
        self.is_white_bottom = is_white_bottom
        for ver in self.liCoordenadasVerticales:
            ver.bloqueDatos.valor = str(9 - int(ver.bloqueDatos.valor))
            ver.update()

        for hor in self.liCoordenadasHorizontales:
            hor.bloqueDatos.valor = chr(97 + 104 - ord(hor.bloqueDatos.valor))
            hor.update()

        for pieza, piezaSC, siVisible in self.liPiezas:
            if siVisible:
                self.recolocaPieza(piezaSC.bloquePieza)
                piezaSC.rehazPosicion()
                piezaSC.update()

        self.escena.update()

    def showCoordenadas(self, ok):
        for coord in self.liCoordenadasHorizontales:
            coord.setVisible(ok)
        for coord in self.liCoordenadasVerticales:
            coord.setVisible(ok)

    def peonCoronando(self, is_white):
        if self.configuracion.x_autopromotion_q:
            modifiers = QtWidgets.QApplication.keyboardModifiers()
            if modifiers != QtCore.Qt.AltModifier:
                return "Q" if is_white else "q"
        menu = QTVarios.LCMenu(self)
        for txt, pieza in ((_("Queen"), "Q"), (_("Rook"), "R"), (_("Bishop"), "B"), (_("Knight"), "N")):
            if not is_white:
                pieza = pieza.lower()
            menu.opcion(pieza, txt, self.piezas.icono(pieza))

        resp = menu.lanza()
        if resp:
            return resp
        else:
            return "q"

    def refresh(self):
        self.escena.update()
        QTUtil.refresh_gui()

    def pulsadoNum(self, siIzq, siActivar, number):
        if (
            not siIzq
        ):  # si es derecho lo dejamos para el menu visual, y el izquierdo solo muestra capturas, si se quieren ver movimientos, que active show candidates
            return
        if self.exePulsadoNum:
            self.exePulsadoNum(siActivar, int(number))

    def pulsadaLetra(self, siIzq, siActivar, letra):
        if (
            not siIzq
        ):  # si es derecho lo dejamos para el menu visual, y el izquierdo solo muestra capturas, si se quieren ver movimientos, que active show candidates
            return
        if self.exePulsadaLetra:
            self.exePulsadaLetra(siActivar, letra)

    def salvaEnImagen(self, fichero=None, tipo=None, siCtrl=False, siAlt=False):
        actInd = actScr = False
        if self.indicadorSC_menu:
            if self.indicadorSC_menu.isVisible():
                actInd = True
                self.indicadorSC_menu.hide()
        if self.siDirectorIcon and self.scriptSC_menu:
            if self.scriptSC_menu.isVisible():
                actScr = True
                self.scriptSC_menu.hide()

        if siAlt and not siCtrl:
            pm = QtGui.QPixmap.grabWidget(self)
        else:
            x = 0
            y = 0
            w = self.width()
            h = self.height()
            if siCtrl and not siAlt:
                x = self.tamFrontera
                y = self.tamFrontera
                w -= self.tamFrontera * 2 + 2
                h -= self.tamFrontera * 2 + 2
            elif siAlt and siCtrl:
                x += self.margenCentro
                y += self.margenCentro
                w -= self.margenCentro * 2
                h -= self.margenCentro * 2
            pm = QtGui.QPixmap.grabWidget(self, x, y, w, h)
        if fichero is None:
            QTUtil.ponPortapapeles(pm, tipo="p")
        else:
            pm.save(fichero, tipo)

        if actInd:
            self.indicadorSC_menu.show()
        if actScr:
            self.scriptSC_menu.show()

    def thumbnail(self, ancho):
        # escondemos piezas+flechas
        for pieza, piezaSC, siVisible in self.liPiezas:
            if siVisible:
                piezaSC.hide()
        for flecha in self.liFlechas:
            flecha.hide()
        if self.flechaSC:
            self.flechaSC.hide()

        pm = QtGui.QPixmap.grabWidget(self)
        thumb = pm.scaled(ancho, ancho, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)

        # mostramos piezas+flechas
        for pieza, piezaSC, siVisible in self.liPiezas:
            if siVisible:
                piezaSC.show()
        for flecha in self.liFlechas:
            flecha.show()
        if self.flechaSC:
            self.flechaSC.show()

        byte_array = QtCore.QByteArray()
        xbuffer = QtCore.QBuffer(byte_array)
        xbuffer.open(QtCore.QIODevice.WriteOnly)
        thumb.save(xbuffer, "PNG")

        bytes_io = BytesIO(byte_array)
        contents = bytes_io.getvalue()
        bytes_io.close()

        return contents

    def a1h8_fc(self, a1h8):
        df = int(a1h8[1])
        dc = ord(a1h8[0]) - 96
        hf = int(a1h8[3])
        hc = ord(a1h8[2]) - 96
        if self.is_white_bottom:
            df = 9 - df
            hf = 9 - hf
        else:
            dc = 9 - dc
            hc = 9 - hc

        return df, dc, hf, hc

    def fc_a1h8(self, df, dc, hf, hc):
        if self.is_white_bottom:
            df = 9 - df
            hf = 9 - hf
        else:
            dc = 9 - dc
            hc = 9 - hc

        a1h8 = chr(dc + 96) + str(df) + chr(hc + 96) + str(hf)

        return a1h8

    def creaMarco(self, bloqueMarco):
        bloqueMarcoN = copy.deepcopy(bloqueMarco)
        bloqueMarcoN.anchoCasilla = self.anchoCasilla

        return TabMarcos.MarcoSC(self.escena, bloqueMarcoN)

    def creaSVG(self, bloqueSVG, siEditando=False):
        bloqueSVGN = copy.deepcopy(bloqueSVG)
        bloqueSVGN.anchoCasilla = self.anchoCasilla

        return TabSVG.SVGSC(self.escena, bloqueSVGN, siEditando=siEditando)

    def creaMarker(self, bloqueMarker, siEditando=False):
        bloqueMarkerN = copy.deepcopy(bloqueMarker)
        bloqueMarkerN.anchoCasilla = self.anchoCasilla

        return TabMarker.MarkerSC(self.escena, bloqueMarkerN, siEditando=siEditando)

    def creaFlecha(self, bloqueFlecha, rutina=None):
        bloqueFlechaN = copy.deepcopy(bloqueFlecha)
        bloqueFlechaN.anchoCasilla = self.anchoCasilla

        return TabFlechas.FlechaSC(self.escena, bloqueFlechaN, rutina)

    def intentaRotarTablero(self, siIzquierdo):
        if self.siPosibleRotarTablero:
            self.rotaTablero()

    def rotaTablero(self):
        self.ponerPiezasAbajo(not self.is_white_bottom)
        if self.flechaSC:
            # self.ponFlechaSC( self.ultMovFlecha[0], self.ultMovFlecha[1])
            self.resetFlechaSC()
        bd = self.indicadorSC.bloqueDatos
        self.ponIndicador(bd.colorRelleno == self.colorBlancas)
        for k, uno in self.dicMovibles.items():
            uno.posicion2xy()
        for flecha in self.liFlechas:
            flecha.posicion2xy()
        self.escena.update()

        if hasattr(self.main_window, "capturas"):
            self.main_window.capturas.ponLayout(self.is_white_bottom)

    def registraMovible(self, bloqueSC):
        self.idUltimoMovibles += 1
        bloqueSC.idMovible = self.idUltimoMovibles
        self.dicMovibles[self.idUltimoMovibles] = bloqueSC

    def exportaMovibles(self):
        if self.dicMovibles:
            li = []
            for k, v in self.dicMovibles.items():
                xobj = str(v)
                if "Marco" in xobj:
                    tp = "M"
                elif "Flecha" in xobj:
                    tp = "F"
                elif "SVG" in xobj:
                    tp = "S"
                else:
                    continue
                li.append((tp, v.bloqueDatos))

            return Util.var2txt(li)
        else:
            return ""

    def importaMovibles(self, xData):
        self.borraMovibles()
        if xData:
            liDatos = Util.txt2var(str(xData))
            for tp, bloqueDatos in liDatos:
                if tp == "M":
                    self.creaMarco(bloqueDatos)
                elif tp == "F":
                    self.creaFlecha(bloqueDatos)
                elif tp == "S":
                    self.creaSVG(bloqueDatos)
                elif tp == "X":
                    self.creaMarker(bloqueDatos)

    def borraMovible(self, itemSC):
        for k, uno in self.dicMovibles.items():
            if uno == itemSC:
                del self.dicMovibles[k]
                self.xremoveItem(uno)
                return

    def borraUltimoMovibleA1(self, a1):
        for k, uno in reversed(self.dicMovibles.items()):
            a1h8 = uno.bloqueDatos.a1h8
            if a1h8.startswith(a1) or a1h8.endswith(a1):
                self.borraMovible(uno)
                break

    def borraUltimoMovible(self):
        keys = list(self.dicMovibles.keys())
        if keys:
            self.xremoveItem(self.dicMovibles[keys[-1]])
            del self.dicMovibles[keys[-1]]

    def borraMovibles(self):
        for k, uno in self.dicMovibles.items():
            self.xremoveItem(uno)
        self.dicMovibles = collections.OrderedDict()
        self.lastFenM2 = None

    def bloqueaRotacion(self, siBloquea):  # se usa en la presentacion para que no rote
        self.siPosibleRotarTablero = not siBloquea

    def dispatchSize(self, rutinaControl):
        self._dispatchSize = rutinaControl

    def fen_active(self):
        li = []
        for x in range(8):
            li.append(["", "", "", "", "", "", "", ""])

        for x in self.liPiezas:
            if x[2]:
                piezaSC = x[1]
                bp = piezaSC.bloquePieza
                li[8 - bp.fila][bp.columna - 1] = x[0]

        lineas = []
        for x in range(8):
            uno = ""
            num = 0
            for y in range(8):
                if li[x][y]:
                    if num:
                        uno += str(num)
                        num = 0
                    uno += li[x][y]
                else:
                    num += 1
            if num:
                uno += str(num)
            lineas.append(uno)

        bd = self.indicadorSC.bloqueDatos
        is_white = bd.colorRelleno == self.colorBlancas

        resto = "w" if is_white else "b"
        resto += " KQkq - 0 1"

        return "/".join(lineas) + " " + resto

    def copiaPosicionDe(self, otroTablero):
        for x in self.liPiezas:
            if x[2]:
                self.xremoveItem(x[1])
        self.liPiezas = []
        for cpieza, piezaSC, is_active in otroTablero.liPiezas:
            if is_active:
                position = piezaSC.bloquePieza
                f = position.fila
                c = position.columna
                posA1H8 = chr(c + 96) + str(f)
                self.creaPieza(cpieza, posA1H8)

        if not otroTablero.is_white_bottom:
            self.rotaTablero()

        if otroTablero.indicadorSC.isVisible():
            bdOT = otroTablero.indicadorSC.bloqueDatos
            is_white = bdOT.colorRelleno == otroTablero.colorBlancas
            siIndicadorAbajo = bdOT.position.y == bdOT.sur

            bd = self.indicadorSC.bloqueDatos
            bd.position.y = bd.sur if siIndicadorAbajo else bd.norte
            bd.colorRelleno = self.colorBlancas if is_white else self.colorNegras
            self.indicadorSC.mostrar()

        if otroTablero.flechaSC and otroTablero.flechaSC.isVisible():
            a1h8 = otroTablero.flechaSC.bloqueDatos.a1h8
            desdeA1h8, hastaA1h8 = a1h8[:2], a1h8[2:]
            self.ponFlechaSC(desdeA1h8, hastaA1h8)

        self.escena.update()
        self.setFocus()

    def terminar(self):
        if self.dirvisual:
            self.dirvisual.terminar()


class WTamTablero(QtWidgets.QDialog):
    def __init__(self, tablero):

        QtWidgets.QDialog.__init__(self, tablero.parent())

        self.setWindowTitle(_("Change board size"))
        self.setWindowIcon(Iconos.TamTablero())
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)

        self._dispatchSize = tablero._dispatchSize
        self.tablero = tablero
        self.config_board = tablero.config_board

        ap = self.config_board.anchoPieza()

        self.antes = ap

        liTams = [
            (_("Very large"), 80),
            (_("Large"), 64),
            (_("Medium"), 48),
            (_("Medium-small"), 32),
            (_("Small"), 24),
            (_("Very small"), 16),
            (_("Custom size"), 0),
            (_("Initial size"), -1),
            (_("Default"), -2),
        ]

        self.cb = Controles.CB(self, liTams, self.anchoParaCB(ap)).capturaCambiado(self.cambiadoTamCB)

        minimo = 10
        maximo = tablero.calculaAnchoMXpieza() + 30

        self.sb = Controles.SB(self, ap, minimo, maximo).capturaCambiado(self.cambiadoTamSB)

        self.sl = Controles.SL(self, minimo, maximo, ap, self.cambiadoTamSL, tick=0).ponAncho(180)

        btAceptar = Controles.PB(self, "", rutina=self.aceptar, plano=False).ponIcono(Iconos.Aceptar())

        layout = Colocacion.G()
        layout.control(btAceptar, 0, 0).control(self.cb, 0, 1).control(self.sb, 0, 2)
        layout.controlc(self.sl, 1, 0, 1, 3).margen(5)
        self.setLayout(layout)

        self.siOcupado = False
        self.siCambio = False
        self.tablero.permitidoResizeExterno(False)

    def anchoParaCB(self, ap):
        return ap if ap in (80, 64, 48, 32, 24, 16) else 0

    def colocate(self):
        self.show()  # Necesario para que calcule bien el tama_o antes de colocar
        pos = self.tablero.parent().mapToGlobal(self.tablero.pos())

        y = pos.y() - self.frameGeometry().height()
        if y < 0:
            y = 0
        pos.setY(y)
        self.move(pos)

    def aceptar(self):
        self.close()

    def cambiaAncho(self):
        is_white_bottom = self.tablero.is_white_bottom
        self.tablero.cambiadoAncho()
        if not is_white_bottom:
            self.tablero.intentaRotarTablero(None)

    def dispatch(self):
        t = self.tablero
        if t._dispatchSize:
            t._dispatchSize()
        self.siCambio = True

    def cambiadoTamCB(self):
        if self.siOcupado:
            return
        self.siOcupado = True
        ct = self.config_board
        tam = self.cb.valor()

        if tam == 0:
            ct.anchoPieza(self.tablero.anchoPieza)
        elif tam == -1:
            tpz = self.antes
            ct.anchoPieza(tpz)
            self.cb.ponValor(self.anchoParaCB(tpz))
            self.cambiaAncho()
        elif tam == -2:
            self.cb.ponValor(self.anchoParaCB(ct.ponDefAnchoPieza()))
            self.cambiaAncho()
        else:
            ct.anchoPieza(tam)
            self.cambiaAncho()

        self.sb.ponValor(self.tablero.anchoPieza)
        self.sl.ponValor(self.tablero.anchoPieza)
        self.siOcupado = False
        self.dispatch()

    def cambiadoTamSB(self):
        if self.siOcupado:
            return
        self.siOcupado = True
        tam = self.sb.valor()
        self.config_board.anchoPieza(tam)
        self.cb.ponValor(self.anchoParaCB(tam))
        self.cambiaAncho()
        self.sl.ponValor(tam)
        self.siOcupado = False
        self.dispatch()

    def cambiadoTamSL(self):
        if self.siOcupado:
            return
        self.siOcupado = True
        tam = self.sl.valor()
        self.config_board.anchoPieza(tam)
        self.cb.ponValor(self.anchoParaCB(tam))
        self.sb.ponValor(tam)
        self.cambiaAncho()
        self.siOcupado = False
        self.dispatch()

    def closeEvent(self, event):
        self.config_board.guardaEnDisco()
        self.close()
        if self.siCambio:
            self.dispatch()
        if self.config_board.is_base:
            self.tablero.permitidoResizeExterno(self.config_board.is_base)


class PosTablero(Tablero):
    def activaTodas(self):
        for pieza, piezaSC, is_active in self.liPiezas:
            piezaSC.activa(True)

    def keyPressEvent(self, event):
        k = event.key()
        if (96 > k > 64) and chr(k) in "PQKRNB":
            self.parent().cambiaPiezaSegun(chr(k))
        else:
            Tablero.keyPressEvent(self, event)
        event.ignore()

    def mousePressEvent(self, event):
        x = event.x()
        y = event.y()
        cx = self.punto2columna(x)
        cy = self.punto2fila(y)
        siEvent = True
        if cx in range(1, 9) and cy in range(1, 9):
            a1h8 = self.num2alg(cy, cx)
            siIzq = event.button() == QtCore.Qt.LeftButton
            siDer = event.button() == QtCore.Qt.RightButton
            if self.squares.get(a1h8):
                self.parent().ultimaPieza = self.squares.get(a1h8)
                if hasattr(self.parent(), "ponCursor"):
                    self.parent().ponCursor()
                    # ~ if siIzq:
                    # ~ QtWidgets.QGraphicsView.mousePressEvent(self,event)
                if siDer:
                    if hasattr(self, "mensBorrar"):
                        self.mensBorrar(a1h8)
                    siEvent = False
            else:
                if siDer:
                    if hasattr(self, "mensCrear"):
                        self.mensCrear(a1h8)
                    siEvent = False
                if siIzq:
                    if hasattr(self, "mensRepetir"):
                        self.mensRepetir(a1h8)
                    siEvent = False
        else:
            Tablero.mousePressEvent(self, event)
            return
        if siEvent:
            QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def ponDispatchDrop(self, dispatch):
        self.dispatchDrop = dispatch

    def dropEvent(self, event):
        mimeData = event.mimeData()
        if mimeData.hasFormat("image/x-lc-dato"):
            dato = mimeData.data("image/x-lc-dato").data().decode()
            p = event.pos()
            x = p.x()
            y = p.y()
            cx = self.punto2columna(x)
            cy = self.punto2fila(y)
            if cx in range(1, 9) and cy in range(1, 9):
                a1h8 = self.num2alg(cy, cx)
                self.dispatchDrop(a1h8, dato)
            event.setDropAction(QtCore.Qt.IgnoreAction)
        event.ignore()


class TableroEstatico(Tablero):
    def mousePressEvent(self, event):
        pos = event.pos()
        x = pos.x()
        y = pos.y()
        minimo = self.margenCentro
        maximo = self.margenCentro + (self.anchoCasilla * 8)
        if not ((minimo < x < maximo) and (minimo < y < maximo)):
            if self.atajosRaton:
                self.atajosRaton(None)
            Tablero.mousePressEvent(self, event)
            return
        xc = 1 + int(float(x - self.margenCentro) / self.anchoCasilla)
        yc = 1 + int(float(y - self.margenCentro) / self.anchoCasilla)

        if self.is_white_bottom:
            yc = 9 - yc
        else:
            xc = 9 - xc

        f = chr(48 + yc)
        c = chr(96 + xc)

        self.main_window.pulsada_celda(c + f)

        Tablero.mousePressEvent(self, event)


class TableroEstaticoMensaje(TableroEstatico):
    def __init__(self, parent, config_board, color_mens, size_factor=None):
        self.color_mens = "#574b3c" if color_mens is None else color_mens
        self.size_factor = 1.0 if size_factor is None else size_factor
        TableroEstatico.__init__(self, parent, config_board)

    def rehaz(self):
        Tablero.rehaz(self)
        self.mens = TabTipos.Texto()
        self.mens.tipoLetra = TabTipos.TipoLetra(puntos=self.anchoCasilla * 2 * self.size_factor, peso=750)
        self.mens.position.ancho = self.anchoCasilla * 6
        self.mens.position.alto = self.anchoCasilla * 6
        self.mens.position.orden = 99
        self.mens.colorTexto = self.color_mens
        self.mens.valor = ""
        self.mens.alineacion = "c"
        self.mens.position.x = (self.ancho - self.mens.position.ancho) / 2
        self.mens.position.y = (self.ancho - self.mens.position.ancho) / 2
        self.mensSC = TabElementos.TextoSC(self.escena, self.mens)

        self.mens2 = TabTipos.Texto()
        self.mens2.tipoLetra = TabTipos.TipoLetra(puntos=self.anchoCasilla * self.size_factor, peso=750)
        self.mens2.position.ancho = self.anchoCasilla * 6
        self.mens2.position.alto = self.anchoCasilla * 6
        self.mens2.position.orden = 99
        self.mens2.colorTexto = self.color_mens
        self.mens2.valor = ""
        self.mens2.alineacion = "c"
        self.mens2.position.x = self.mens.position.x + self.anchoCasilla*2
        self.mens2.position.y = self.mens.position.y
        self.mensSC2 = TabElementos.TextoSC(self.escena, self.mens2)

    def pon_texto(self, texto, opacity):
        self.mens.valor = texto
        self.mensSC.setOpacity(opacity)
        self.mensSC.show()
        self.escena.update()

    def pon_textos(self, texto1, texto2, opacity):
        self.mens.valor = texto1
        self.mensSC.setOpacity(opacity)
        self.mensSC.show()
        self.mens2.valor = texto2
        self.mensSC2.setOpacity(opacity)
        self.mensSC2.show()
        self.escena.update()

    def remove_pieces(self, st):
        for a1h8 in st:
            self.borraPieza(a1h8)

