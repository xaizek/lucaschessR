import os

from PySide2 import QtWidgets, QtCore

from Code import Game
from Code import Variantes
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import Iconos
from Code.QT import QTVarios
from Code import TrListas
import Code


class WVariantes(QtWidgets.QWidget):
    def __init__(self, owner):
        self.owner = owner
        configuracion = Code.configuracion
        self.siFigurines = configuracion.x_pgn_withfigurines
        puntos = configuracion.x_pgn_fontpoints

        QtWidgets.QWidget.__init__(self, self.owner)

        li_acciones = (
            (_("Append"), Iconos.Mas(), self.tbMasVariante),
            None,
            ("%s+%s" % (_("Append"), _("Engine")), Iconos.MasR(), self.tbMasVarianteR),
            None,
            (_("Edit"), Iconos.ComentarioEditar(), self.tbEditarVariante),
            None,
            (_("Remove"), Iconos.Borrar(), self.tbBorrarVariante),
            None,
        )
        tbVariantes = Controles.TBrutina(self, li_acciones, siTexto=False, tamIcon=16)

        self.em = Controles.EM(self)  # .capturaCambios(self.variantesCambiado)
        self.em.setReadOnly(True)
        self.em.capturaDobleClick(self.dobleClick)

        ly = Colocacion.V().control(tbVariantes).control(self.em).margen(3)

        f = Controles.TipoLetra(puntos=puntos)

        gbVariantes = Controles.GB(self.owner, _("Variations"), ly).ponFuente(f)

        layout = Colocacion.H().control(gbVariantes).margen(0)
        self.setLayout(layout)

        self.li_variations = []

        self.move = None

    def ponJugada(self, move):
        self.move = move

        self.li_variations = move.variations.list_games()
        self.mostrar()

    def mostrar(self):
        if self.li_variations:
            html = '<table cellpadding="2" cellspacing="0" border="1" style="border-color: lightgray" width="100%">'
            for n, game in enumerate(self.li_variations):
                bgcolor = "#F5F5F5" if n % 2 else "white"
                pgn = game.pgn_html(siFigurines=self.siFigurines)
                html += '<tr bgcolor="%s"><td>%s</td></tr>' % (bgcolor, pgn)
            html += "</table>"
        else:
            html = ""
        self.em.ponHtml(html)

    def select(self):
        if len(self.li_variations) == 0:
            return None
        menu = QTVarios.LCMenu(self)
        rondo = QTVarios.rondoPuntos()
        for num, variante in enumerate(self.li_variations):
            move = variante.move(0)
            menu.opcion(num, "%d. %s" % (num + 1, move.pgnBaseSP()), rondo.otro())
        return menu.lanza()

    def editar(self, number, siEngineActivo=False):
        if number == -1:
            game = Game.Game(ini_posicion=self.move.position_before)
        else:
            game = self.li_variations[number]

        game = Variantes.editaVariante(
            Code.procesador,
            game,
            siEngineActivo=siEngineActivo,
            is_white_bottom=self.owner.wParent.gestor.tablero.is_white_bottom,
        )
        # game = Code.procesador.gestorPartida(self, game, False, self.owner.wParent.gestor.tablero)
        if game:
            # if number == -1:
            #     self.li_variations.append(game)
            # else:
            #     self.li_variations[number] = game
            self.move.variations.change(number, game)
            self.mostrar()

    def dobleClick(self, event):
        txt = self.em.texto()
        pos = self.em.position()
        # Hay que ver cuantos \n hay antes de esa position
        fila = txt[:pos].count("\n") - 1
        if fila == -1:
            self.tbMasVariante()
        else:
            self.editar(fila)

    def tbMasVariante(self, siEngineActivo=False):
        self.editar(-1, False)

    def tbMasVarianteR(self):
        self.editar(-1, True)

    def tbEditarVariante(self):
        num = self.select()
        if num is None:
            self.editar(-1)
        else:
            self.editar(num)

    def tbBorrarVariante(self):
        num = self.select()
        if num is not None:
            del self.li_variations[num]
            self.move.variations.remove(num)
            self.mostrar()


class InformacionPGN(QtWidgets.QWidget):
    def __init__(self, wParent):
        QtWidgets.QWidget.__init__(self, wParent)

        self.wParent = wParent

        self.move = None
        self.game = None

        configuracion = Code.configuracion

        puntos = configuracion.x_pgn_fontpoints

        f = Controles.TipoLetra(puntos=puntos, peso=75)
        f9 = Controles.TipoLetra(puntos=puntos)
        ftxt = f9

        # Apertura
        self.lbApertura = (
            Controles.LB(self, "").ponFuente(f).alinCentrado().ponColorFondoN("#eeeeee", "#474d59").ponWrap()
        )
        self.lbApertura.hide()

        # Valoracion
        li_options = [("-", None)]
        dicNAGs = TrListas.dicNAGs()

        carpNAGs = Code.path_resource("IntFiles", "NAGs")

        ico_vacio = QTVarios.fsvg2ico("%s/$0.svg" % (carpNAGs,), 16)

        for x in dicNAGs:
            if x:
                fsvg = "%s/$%d.svg" % (carpNAGs, x)
                if os.path.isfile(fsvg):
                    li_options.append(("$%d : %s" % (x, dicNAGs[x]), x, QTVarios.fsvg2ico(fsvg, 16)))
                else:
                    li_options.append(("$%d : %s" % (x, dicNAGs[x]), x, ico_vacio))
        self.maxNAGs = 10
        self.liNAGs = []
        for x in range(self.maxNAGs):
            cb = (
                Controles.CB(self, li_options, "")
                .ponAnchoMinimo()
                .capturaCambiado(self.valoracionCambiada)
                .ponFuente(f9)
            )
            if x:
                cb.hide()
            self.liNAGs.append(cb)

        btNAGS = Controles.PB(self, "", self.masNAGs).ponIcono(Iconos.Mas()).anchoFijo(22)

        lyH = Colocacion.H().control(self.liNAGs[0]).control(btNAGS)
        ly = Colocacion.V().otro(lyH)
        for x in range(1, self.maxNAGs):
            ly.control(self.liNAGs[x])

        self.gbValoracion = Controles.GB(self, _("Rating"), ly).ponFuente(f)

        # Comentarios
        self.comment = (
            Controles.EM(self, siHTML=False).capturaCambios(self.comentarioCambiado).ponFuente(ftxt).anchoMinimo(200)
        )
        ly = Colocacion.H().control(self.comment).margen(3)
        self.gbComentario = Controles.GB(self, _("Comments"), ly).ponFuente(f)

        # Variantes
        self.variantes = WVariantes(self)

        self.splitter = splitter = QtWidgets.QSplitter(self)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        splitter.addWidget(self.gbComentario)
        splitter.addWidget(self.variantes)

        layout = Colocacion.V()
        layout.control(self.lbApertura)
        layout.control(self.gbValoracion)
        layout.control(self.splitter)
        layout.margen(1)

        self.setLayout(layout)

    def masNAGs(self):
        for cb in self.liNAGs:
            if not cb.isVisible():
                cb.ponValor("-")
                cb.show()
                return

    def ponJG(self, game, move, opening):
        self.game = game
        self.move = move

        if not opening:
            self.lbApertura.hide()

        siJG = self.move is not None
        self.gbValoracion.setVisible(siJG)
        self.variantes.setVisible(siJG)

        if siJG:
            self.gbComentario.ponTexto(_("Comments"))
            if opening:
                self.lbApertura.ponTexto(opening)
                if move.in_the_opening:
                    self.lbApertura.ponColorFondoN("#eeeeee", "#474d59")
                else:
                    self.lbApertura.ponColorFondoN("#ffffff", "#aaaaaa")
                self.lbApertura.show()

            self.comment.ponTexto(move.comment)
            self.variantes.ponJugada(move)

            self.ponNAGs(move.li_nags)

        else:
            self.gbComentario.ponTexto("%s - %s" % (_("Game"), _("Comments")))
            if game:
                self.comment.ponTexto(game.firstComment)
                if opening:
                    self.lbApertura.ponTexto(opening)
                    self.lbApertura.ponColorFondoN("#eeeeee", "#474d59")
                    self.lbApertura.show()

    def ponNAGs(self, li):
        n = 0
        for nag in li:
            cb = self.liNAGs[n]
            cb.ponValor(nag)
            cb.show()
            n += 1
        if n == 0:
            cb = self.liNAGs[0]
            cb.ponValor("-")
            cb.show()
        else:
            for x in range(n, self.maxNAGs):
                cb = self.liNAGs[x]
                cb.ponValor("-")
                cb.hide()

    def keyPressEvent(self, event):
        pass  # Para que ESC no cierre el programa

    def comentarioCambiado(self):
        if self.move:
            self.move.comment = self.comment.texto()
        else:
            self.game.firstComment = self.comment.texto()

    def valoracionCambiada(self, npos):
        if self.move:
            li = []
            for x in range(self.maxNAGs):
                v = self.liNAGs[x].valor()
                if v:
                    li.append(v)
            self.move.li_nags = li
            self.ponNAGs(li)
