from PySide2 import QtWidgets

from Code.QT import Colocacion, Controles, Iconos


class EDCelda(Controles.ED):
    def focusOutEvent(self, event):
        self.parent.focusOut(self)
        Controles.ED.focusOutEvent(self, event)


class WEdMove(QtWidgets.QWidget):
    def __init__(self, owner):
        QtWidgets.QWidget.__init__(self)

        self.PM_EMPTY, self.PM_OK, self.PM_WRONG, self.PM_REPEATED, self.PM_MOVE = (
            Iconos.pmPuntoBlanco(),
            Iconos.pmAceptarPeque(),
            Iconos.pmDelete(),
            Iconos.pmRepeat(),
            Iconos.pmMover(),
        )

        self.owner = owner

        self.origen = EDCelda(self, "").caracteres(2).controlrx("(|[a-h][1-8])").anchoFijo(32).alinCentrado()

        self.flecha = flecha = Controles.LB(self).ponImagen(self.PM_MOVE)
        flecha.mousePressEvent = self.pulsa_flecha

        self.destino = EDCelda(self, "").caracteres(2).controlrx("(|[a-h][1-8])").anchoFijo(32).alinCentrado()

        self.result = Controles.LB(self).ponWrap().ponImagen(self.PM_EMPTY)

        ly = (
            Colocacion.H()
            .relleno()
            .control(self.origen)
            .espacio(2)
            .control(flecha)
            .espacio(2)
            .control(self.destino)
            .espacio(2)
            .control(self.result)
            .margen(0)
            .relleno()
        )
        self.setLayout(ly)

    def focusOut(self, quien):
        self.owner.ponUltimaCelda(quien)

    def activa(self):
        self.setFocus()
        self.origen.setFocus()

    def activaDestino(self):
        self.setFocus()
        self.destino.setFocus()

    def movimiento(self):
        from_sq = self.origen.texto()
        if len(from_sq) != 2:
            from_sq = ""

        to_sq = self.destino.texto()
        if len(to_sq) != 2:
            from_sq = ""

        return from_sq + to_sq

    def deshabilita(self):
        self.origen.deshabilitado(True)
        self.destino.deshabilitado(True)

    def habilita(self):
        self.origen.deshabilitado(False)
        self.destino.deshabilitado(False)
        self.result.ponImagen(self.PM_EMPTY)

    def limpia(self):
        self.origen.ponTexto("")
        self.destino.ponTexto("")
        self.result.ponImagen(self.PM_EMPTY)
        self.habilita()
        self.origen.setFocus()

    def correcta(self):
        self.result.ponImagen(self.PM_OK)

    def error(self):
        self.result.ponImagen(self.PM_WRONG)

    def repetida(self):
        self.result.ponImagen(self.PM_REPEATED)

    def pulsa_flecha(self, event):
        self.limpia()
