import collections

from PySide2 import QtWidgets, QtCore, QtGui

from Code import Move
from Code import Game
from Code import TrListas
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTVarios
from Code.QT import Tablero
from Code.QT import PantallaColores

from Code.Constantes import *

V_SIN, V_IGUAL, V_BLANCAS, V_NEGRAS, V_BLANCAS_MAS, V_NEGRAS_MAS, V_BLANCAS_MAS_MAS, V_NEGRAS_MAS_MAS = (
    0,
    11,
    14,
    15,
    16,
    17,
    18,
    19,
)


class BoardLines(QtWidgets.QWidget):
    def __init__(self, panelOpening, configuracion):
        QtWidgets.QWidget.__init__(self)

        self.panelOpening = panelOpening
        self.dbop = panelOpening.dbop

        self.configuracion = configuracion

        self.partidabase = panelOpening.partidabase
        self.num_jg_inicial = len(self.partidabase)
        self.pos_move = self.num_jg_inicial

        config_board = configuracion.config_board("POSLINES", 32)
        self.tablero = Tablero.Tablero(self, config_board)
        self.tablero.crea()
        self.tablero.ponerPiezasAbajo(True)
        self.tablero.set_dispatcher(self.mueve_humano)
        self.tablero.dispatchSize(self.ajustaAncho)
        self.tablero.dbVisual_setFichero(self.dbop.nom_fichero)
        self.tablero.dbVisual_setShowAllways(True)
        self.tablero.dbVisual_setSaveAllways(True)

        self.tablero.ponerPiezasAbajo(self.dbop.getconfig("WHITEBOTTOM", True))

        self.dbop.setdbVisual_Tablero(self.tablero)  # To close

        self.intervalo = configuracion.x_interval_replay

        tipoLetra = Controles.TipoLetra(puntos=configuracion.x_pgn_fontpoints)

        lybt, bt = QTVarios.lyBotonesMovimiento(self, "", siTiempo=True, siLibre=False, tamIcon=24)

        self.lbPGN = Controles.LB(self).ponWrap()
        self.lbPGN.colocate = self.colocatePartida
        self.lbPGN.setStyleSheet(
            "QLabel{ border-style: groove; border-width: 2px; border-color: LightSlateGray; padding: 8px;}"
        )
        self.lbPGN.ponFuente(tipoLetra)
        self.lbPGN.setOpenExternalLinks(False)

        def muestraPos(txt):
            self.colocatePartida(int(txt))

        self.lbPGN.linkActivated.connect(muestraPos)

        self.siFigurines = configuracion.x_pgn_withfigurines

        dicNAGs = TrListas.dicNAGs()
        self.dicValoracion = collections.OrderedDict()
        self.dicValoracion[GOOD_MOVE] = (dicNAGs[1], PantallaColores.nag2ico(1, 16))
        self.dicValoracion[BAD_MOVE] = (dicNAGs[2], PantallaColores.nag2ico(2, 16))
        self.dicValoracion[VERY_GOOD_MOVE] = (dicNAGs[3], PantallaColores.nag2ico(3, 16))
        self.dicValoracion[VERY_POOR_MOVE] = (dicNAGs[4], PantallaColores.nag2ico(4, 16))
        self.dicValoracion[SPECULATIVE_MOVE] = (dicNAGs[5], PantallaColores.nag2ico(5, 16))
        self.dicValoracion[QUESTIONABLE_MOVE] = (dicNAGs[6], PantallaColores.nag2ico(6, 16))
        self.dicValoracion[NO_RATING] = (_("No rating"), QtGui.QIcon())

        self.dicVentaja = collections.OrderedDict()
        self.dicVentaja[V_SIN] = (_("Undefined"), QtGui.QIcon())
        self.dicVentaja[V_IGUAL] = (dicNAGs[11], Iconos.V_Blancas_Igual_Negras())
        self.dicVentaja[V_BLANCAS] = (dicNAGs[14], Iconos.V_Blancas())
        self.dicVentaja[V_BLANCAS_MAS] = (dicNAGs[16], Iconos.V_Blancas_Mas())
        self.dicVentaja[V_BLANCAS_MAS_MAS] = (dicNAGs[18], Iconos.V_Blancas_Mas_Mas())
        self.dicVentaja[V_NEGRAS] = (dicNAGs[15], Iconos.V_Negras())
        self.dicVentaja[V_NEGRAS_MAS] = (dicNAGs[17], Iconos.V_Negras_Mas())
        self.dicVentaja[V_NEGRAS_MAS_MAS] = (dicNAGs[19], Iconos.V_Negras_Mas_Mas())

        # Valoracion
        li_options = [(tit[0], k, tit[1]) for k, tit in self.dicValoracion.items()]
        self.cbValoracion = Controles.CB(self, li_options, 0).capturaCambiado(self.cambiadoValoracion)
        self.cbValoracion.ponFuente(tipoLetra)

        # Ventaja
        li_options = [(tit, k, icon) for k, (tit, icon) in self.dicVentaja.items()]
        self.cbVentaja = Controles.CB(self, li_options, 0).capturaCambiado(self.cambiadoVentaja)
        self.cbVentaja.ponFuente(tipoLetra)

        # Comentario
        self.emComentario = Controles.EM(self, siHTML=False).capturaCambios(self.cambiadoComentario)
        self.emComentario.ponFuente(tipoLetra)
        self.emComentario.altoFijo(5 * configuracion.x_pgn_rowheight)
        lyVal = Colocacion.H().control(self.cbValoracion).control(self.cbVentaja)
        lyEd = Colocacion.V().otro(lyVal).control(self.emComentario)

        # Apertura
        self.lbApertura = Controles.LB(self).alinCentrado().ponFuente(tipoLetra).ponWrap()

        lyt = Colocacion.H().relleno().control(self.tablero).relleno()

        lya = Colocacion.H().relleno().control(self.lbPGN).relleno()

        layout = Colocacion.V()
        layout.otro(lyt)
        layout.otro(lybt)
        layout.otro(lya)
        layout.otro(lyEd)
        layout.control(self.lbApertura)
        layout.relleno().margen(0)
        self.setLayout(layout)

        self.ajustaAncho()

        self.siReloj = False

        self.ponPartida(self.partidabase)

    def ponPartida(self, game):
        game.test_apertura()
        self.game = game
        rotulo = game.rotuloApertura()
        if rotulo is not None:
            trans = game.rotuloTransposition()
            if trans is not None:
                rotulo += "\n%s: %s" % (_("Transposition"), trans)
        else:
            rotulo = ""
        self.lbApertura.ponTexto(rotulo)

    def process_toolbar(self):
        getattr(self, self.sender().clave)()

    def setvalue(self, key, valor):
        if self.fenm2:
            dic = self.dbop.getfenvalue(self.fenm2)
            dic[key] = valor
            self.dbop.setfenvalue(self.fenm2, dic)

    def cambiadoValoracion(self):
        self.setvalue("VALORACION", self.cbValoracion.valor())

    def cambiadoVentaja(self):
        self.setvalue("VENTAJA", self.cbVentaja.valor())

    def cambiadoComentario(self):
        self.setvalue("COMENTARIO", self.emComentario.texto().strip())

    def ajustaAncho(self):
        self.setFixedWidth(self.tablero.ancho + 20)
        self.lbPGN.anchoFijo(self.tablero.ancho)

    def camposEdicion(self, siVisible):
        if self.siMoves:
            self.lbValoracion.setVisible(siVisible)
            self.cbValoracion.setVisible(siVisible)
            self.lbVentaja.setVisible(siVisible)
            self.cbVentaja.setVisible(siVisible)
            self.emComentario.setVisible(siVisible)

    def mueve_humano(self, from_sq, to_sq, promotion=""):
        cpActual = self.game.move(self.pos_move).position if self.pos_move >= 0 else self.game.first_position
        if cpActual.siPeonCoronando(from_sq, to_sq):
            promotion = self.tablero.peonCoronando(cpActual.is_white)
            if promotion is None:
                return

        siBien, mens, move = Move.dameJugada(self.game, cpActual, from_sq, to_sq, promotion)

        if siBien:
            game = Game.Game()
            game.leeOtra(self.game)

            if self.pos_move < len(self.game) - 1:
                game.li_moves = game.li_moves[: self.pos_move + 1]
            game.add_move(move)
            self.panelOpening.mueve_humano(game)

    def resetValues(self):
        self.cbValoracion.ponValor(NO_RATING)
        self.cbVentaja.ponValor(V_SIN)
        self.emComentario.ponTexto("")

    def colocatePartida(self, pos):
        self.fenm2 = None
        num_jugadas = len(self.game)
        if num_jugadas == 0:
            self.pos_move = -1
            self.lbPGN.ponTexto("")
            self.tablero.setposition(self.game.first_position)
            self.resetValues()
            self.activaPiezas()
            return

        if pos >= num_jugadas:
            self.siReloj = False
            pos = num_jugadas - 1
        elif pos < self.num_jg_inicial - 1:
            pos = self.num_jg_inicial - 1

        p = self.game

        numJugada = 1
        pgn = ""
        style_number = "color:teal; font-weight: bold;"
        style_moves = "color:black;"
        style_select = "color:navy;font-weight: bold;"
        salta = 0
        for n, move in enumerate(p.li_moves):
            if n % 2 == salta:
                pgn += '<span style="%s">%d.</span>' % (style_number, numJugada)
                numJugada += 1

            xp = move.pgn_html(self.siFigurines)
            if n == pos:
                xp = '<span style="%s">%s</span>' % (style_select, xp)
            else:
                xp = '<span style="%s">%s</span>' % (style_moves, xp)

            pgn += '<a href="%d" style="text-decoration:none;">%s</a> ' % (n, xp)

        self.lbPGN.ponTexto(pgn)

        self.pos_move = pos

        if pos < 0:
            self.tablero.setposition(self.game.first_position)
            self.resetValues()
            self.activaPiezas()
            return

        move = self.game.move(self.pos_move)
        position = move.position if move else self.game.first_position
        self.fenm2 = position.fenm2()
        dic = self.dbop.getfenvalue(self.fenm2)
        valoracion = dic.get("VALORACION", NO_RATING)
        ventaja = dic.get("VENTAJA", V_SIN)
        comment = dic.get("COMENTARIO", "")
        self.cbValoracion.ponValor(valoracion)
        self.cbVentaja.ponValor(ventaja)
        self.emComentario.ponTexto(comment)

        self.tablero.setposition(position)
        if move:
            self.tablero.ponFlechaSC(move.from_sq, move.to_sq)
            position_before = move.position_before
            fenM2_base = position_before.fenm2()
            # dicP = self.dbop.getfenvalue(fenM2_base)
            # if "ANALISIS" in dicP:
            #     mrm = dicP["ANALISIS"]
            #     rm = mrm.mejorMov()
            #     self.tablero.creaFlechaMulti(rm.movimiento(), False)

        if self.siReloj:
            self.tablero.disable_all()
        else:
            self.activaPiezas()

        self.panelOpening.setJugada(self.pos_move)

    def activaPiezas(self):
        self.tablero.disable_all()
        if not self.siReloj and self.pos_move >= self.num_jg_inicial - 1:
            if self.pos_move >= 0:
                move = self.game.move(self.pos_move)
                color = not move.is_white()
            else:
                color = True
            self.tablero.activaColor(color)

    def MoverInicio(self):
        self.colocatePartida(0)

    def MoverAtras(self):
        self.colocatePartida(self.pos_move - 1)

    def MoverAdelante(self):
        self.colocatePartida(self.pos_move + 1)

    def MoverFinal(self):
        self.colocatePartida(99999)

    def MoverTiempo(self):
        if self.siReloj:
            self.siReloj = False
        else:
            self.siReloj = True
            if self.pos_move == len(self.game) - 1:
                self.MoverInicio()
            self.lanzaReloj()
        self.activaPiezas()

    def toolbar_rightmouse(self):
        QTVarios.change_interval(self, self.configuracion)
        self.intervalo = self.configuracion.x_interval_replay

    def lanzaReloj(self):
        if self.siReloj:
            self.MoverAdelante()
            QtCore.QTimer.singleShot(self.intervalo, self.lanzaReloj)
