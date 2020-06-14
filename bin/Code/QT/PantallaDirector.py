import os

from PySide2 import QtWidgets, QtCore, QtGui

from Code import Util
from Code import TrListas
from Code import TabVisual
from Code.QT import Colocacion
from Code.QT import Columnas
from Code.QT import Controles
from Code.QT import Delegados
from Code.QT import FormLayout
from Code.QT import Grid
from Code.QT import Iconos
from Code.QT import PantallaTab
from Code.QT import PantallaTabVFlechas
from Code.QT import PantallaTabVMarcos
from Code.QT import PantallaTabVMarkers
from Code.QT import PantallaTabVSVGs
from Code.QT import QTUtil
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.QT import TabTipos


class WPanelDirector(QTVarios.WDialogo):
    def __init__(self, owner, tablero):
        self.owner = owner
        self.position = tablero.last_position
        self.tablero = tablero
        self.configuracion = tablero.configuracion
        self.fenm2 = self.position.fenm2()
        self.origin_new = None

        self.dbGestor = tablero.dbVisual
        self.leeRecursos()

        titulo = _("Director")
        icono = Iconos.Script()
        extparam = "tabvisualscript"
        QTVarios.WDialogo.__init__(self, tablero, titulo, icono, extparam)

        self.must_save = False
        self.ant_foto = None

        self.guion = TabVisual.Guion(tablero, self)

        # Guion
        li_acciones = [
            (_("Close"), Iconos.MainMenu(), self.terminar),
            (_("Cancel"), Iconos.Cancelar(), self.cancelar),
            (_("Save"), Iconos.Grabar(), self.grabar),
            (_("New"), Iconos.Nuevo(), self.gnuevo),
            (_("Insert"), Iconos.Insertar(), self.ginsertar),
            (_("Remove"), Iconos.Borrar(), self.gborrar),
            None,
            (_("Up"), Iconos.Arriba(), self.garriba),
            (_("Down"), Iconos.Abajo(), self.gabajo),
            None,
            (_("Mark"), Iconos.Marcar(), self.gmarcar),
            None,
            (_("File"), Iconos.Recuperar(), self.gfile),
            None,
        ]
        self.tb = Controles.TBrutina(self, li_acciones, siTexto=False, tamIcon=24)
        self.tb.setAccionVisible(self.grabar, False)

        o_columns = Columnas.ListaColumnas()
        o_columns.nueva("NUMERO", _("N."), 20, centered=True)
        o_columns.nueva("MARCADO", "", 20, centered=True, siChecked=True)
        o_columns.nueva("TIPO", _("Type"), 50, centered=True)
        o_columns.nueva("NOMBRE", _("Name"), 100, centered=True, edicion=Delegados.LineaTextoUTF8())
        o_columns.nueva("INFO", _("Information"), 100, centered=True)
        self.g_guion = Grid.Grid(self, o_columns, siCabeceraMovible=False, siEditable=True, siSeleccionMultiple=True)
        self.g_guion.fixMinWidth()

        self.register_grid(self.g_guion)

        self.chbSaveWhenFinished = Controles.CHB(
            self, _("Save when finished"), self.dbConfig.get("SAVEWHENFINISHED", False)
        )

        # Visuales
        self.selectBanda = PantallaTab.SelectBanda(self)

        lyG = Colocacion.V().control(self.g_guion).control(self.chbSaveWhenFinished)
        lySG = Colocacion.H().control(self.selectBanda).otro(lyG).relleno(1)
        layout = Colocacion.V().control(self.tb).otro(lySG).margen(3)

        self.setLayout(layout)

        self.restore_video()

        self.recuperar()
        self.ant_foto = self.foto()

        self.actualizaBandas()
        li = self.dbConfig["SELECTBANDA"]
        if li:
            self.selectBanda.recuperar(li)
        num_lb = self.dbConfig["SELECTBANDANUM"]
        if num_lb is not None:
            self.selectBanda.seleccionarNum(num_lb)

        self.ultDesde = "d4"
        self.ultHasta = "e5"

        self.g_guion.gotop()

    def addText(self):
        self.guion.cierraPizarra()
        tarea = TabVisual.GT_Texto(self.guion)
        fila = self.guion.nuevaTarea(tarea, -1)
        self.ponMarcado(fila, True)
        self.ponSiGrabar()
        self.guion.pizarra.show()
        self.guion.pizarra.mensaje.setFocus()

    def cambiadaPosicion(self):
        self.position = self.tablero.last_position
        self.fenm2 = self.position.fenm2()
        self.origin_new = None
        self.recuperar()

    def seleccionar(self, lb):
        if lb is None:
            self.owner.setChange(True)
            self.tablero.activaTodas()
        else:
            self.owner.setChange(False)
            self.tablero.disable_all()

    def funcion(self, number, siCtrl=False):
        if number == 9:
            if siCtrl:
                self.selectBanda.seleccionar(None)
            else:
                self.addText()
        elif number == 0 and siCtrl:  # Ctrl+F1
            self.borraUltimo()
        elif number == 1 and siCtrl:  # Ctrl+F2
            self.borraTodos()
        else:
            self.selectBanda.seleccionarNum(number)

    def grabar(self):
        li = self.guion.guarda()
        self.tablero.dbVisual_save(self.fenm2, li)

        self.must_save = False
        self.tb.setAccionVisible(self.grabar, False)
        self.tb.setAccionVisible(self.cancelar, False)
        self.tb.setAccionVisible(self.terminar, True)

    def ponSiGrabar(self):
        if not self.must_save:
            self.tb.setAccionVisible(self.grabar, True)
            self.tb.setAccionVisible(self.cancelar, True)
            self.tb.setAccionVisible(self.terminar, False)
            self.must_save = True

    def ponNoGrabar(self):
        self.tb.setAccionVisible(self.grabar, False)
        self.tb.setAccionVisible(self.cancelar, False)
        self.tb.setAccionVisible(self.terminar, True)
        self.must_save = False

    def recuperar(self):
        self.guion.recupera()
        self.ponNoGrabar()
        self.ant_foto = self.foto()
        self.refresh_guion()

    def tableroCambiadoTam(self):
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.show()
        QTUtil.refresh_gui()
        self.layout().setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)

    def grid_dato(self, grid, fila, oColumna):
        key = oColumna.clave
        if key == "NUMERO":
            return "%d" % (fila + 1,)
        if key == "MARCADO":
            return self.guion.marcado(fila)
        elif key == "TIPO":
            return self.guion.txt_tipo(fila)
        elif key == "NOMBRE":
            return self.guion.name(fila)
        elif key == "INFO":
            return self.guion.info(fila)

    def creaTareaBase(self, tp, xid, a1h8, fila):
        # if tp != TabVisual.TP_FLECHA: # Se indica al terminar en porque puede que no se grabe
        # self.ponSiGrabar()
        tpid = tp, xid
        if tp == "P":
            tarea = TabVisual.GT_PiezaMueve(self.guion)
            from_sq, to_sq = a1h8[:2], a1h8[2:]
            borra = self.tablero.dameNomPiezaEn(to_sq)
            tarea.desdeHastaBorra(from_sq, to_sq, borra)
            self.tablero.activaTodas()
        elif tp == "C":
            tarea = TabVisual.GT_PiezaCrea(self.guion)
            borra = self.tablero.dameNomPiezaEn(a1h8)
            tarea.from_sq(a1h8, borra)
            tarea.pieza(xid)
            self.tablero.activaTodas()
        elif tp == "B":
            tarea = TabVisual.GT_PiezaBorra(self.guion)
            tarea.from_sq(a1h8)
            tarea.pieza(xid)
        else:
            xid = str(xid)
            if tp == TabVisual.TP_FLECHA:
                dicFlecha = self.dbFlechas[xid]
                if dicFlecha is None:
                    return None, None
                regFlecha = TabTipos.Flecha()
                regFlecha.restore_dic(dicFlecha)
                regFlecha.tpid = tpid
                regFlecha.a1h8 = a1h8
                sc = self.tablero.creaFlecha(regFlecha)
                tarea = TabVisual.GT_Flecha(self.guion)
            elif tp == TabVisual.TP_MARCO:
                dicMarco = self.dbMarcos[xid]
                if dicMarco is None:
                    return None, None
                regMarco = TabTipos.Marco()
                regMarco.restore_dic(dicMarco)
                regMarco.tpid = tpid
                regMarco.a1h8 = a1h8
                sc = self.tablero.creaMarco(regMarco)
                tarea = TabVisual.GT_Marco(self.guion)
            elif tp == TabVisual.TP_SVG:
                dicSVG = self.dbSVGs[xid]
                if dicSVG is None:
                    return None, None
                regSVG = TabTipos.SVG()
                regSVG.restore_dic(dicSVG)
                regSVG.tpid = tpid
                regSVG.a1h8 = a1h8
                sc = self.tablero.creaSVG(regSVG, siEditando=True)
                tarea = TabVisual.GT_SVG(self.guion)
            elif tp == TabVisual.TP_MARKER:
                dicMarker = self.dbMarkers[xid]
                if dicMarker is None:
                    return None, None
                regMarker = TabTipos.Marker()
                regMarker.restore_dic(dicMarker)
                regMarker.tpid = tpid
                regMarker.a1h8 = a1h8
                sc = self.tablero.creaMarker(regMarker, siEditando=True)
                tarea = TabVisual.GT_Marker(self.guion)
            sc.ponRutinaPulsada(None, tarea.id())
            tarea.itemSC(sc)

        tarea.marcado(True)
        tarea.registro((tp, xid, a1h8))
        fila = self.guion.nuevaTarea(tarea, fila)

        return tarea, fila

    def creaTarea(self, tp, xid, a1h8, fila):

        tarea, fila = self.creaTareaBase(tp, xid, a1h8, fila)
        if tarea is None:
            return None, None
        tarea.registro((tp, xid, a1h8))

        self.g_guion.goto(fila, 0)

        self.ponMarcado(fila, True)

        return tarea, fila

    def editaNombre(self, name):
        liGen = [(None, None)]
        config = FormLayout.Editbox(_("Name"), ancho=160)
        liGen.append((config, name))
        ico = Iconos.Grabar()

        resultado = FormLayout.fedit(liGen, title=_("Name"), parent=self, icon=ico)
        if resultado:
            self.ponSiGrabar()
            accion, liResp = resultado
            name = liResp[0]
            return name
        return None

    def borrarPizarraActiva(self):
        for n in range(len(self.guion)):
            tarea = self.guion.tarea(n)
            if tarea.tp() == TabVisual.TP_TEXTO:
                if tarea.marcado():
                    self.borrar_lista([n])

    def gmarcar(self):
        if len(self.guion):
            menu = QTVarios.LCMenu(self)
            f = Controles.TipoLetra(puntos=8, peso=75)
            menu.ponFuente(f)
            menu.opcion(1, _("All"), Iconos.PuntoVerde())
            menu.opcion(2, _("None"), Iconos.PuntoNaranja())
            resp = menu.lanza()
            if resp:
                siTodos = resp == 1
                for n in range(len(self.guion)):
                    tarea = self.guion.tarea(n)
                    if tarea.tp() in (TabVisual.TP_TEXTO, TabVisual.TP_ACTION, TabVisual.TP_CONFIGURATION):
                        continue
                    siMarcado = tarea.marcado()
                    if siTodos:
                        if not siMarcado:
                            self.grid_setvalue(None, n, None, True)
                    else:
                        if siMarcado:
                            self.grid_setvalue(None, n, None, False)
                self.refresh_guion()

    def desdeHasta(self, titulo, from_sq, to_sq):
        liGen = [(None, None)]

        config = FormLayout.Casillabox(_("From square"))
        liGen.append((config, from_sq))

        config = FormLayout.Casillabox(_("To square"))
        liGen.append((config, to_sq))

        resultado = FormLayout.fedit(liGen, title=titulo, parent=self)
        if resultado:
            self.ponSiGrabar()
            resp = resultado[1]
            self.ultDesde = from_sq = resp[0]
            self.ultHasta = to_sq = resp[1]
            return from_sq, to_sq
        else:
            return None, None

    def datosSVG(self, tarea):
        col, fil, ancho, alto = tarea.get_datos()
        liGen = [(None, None)]

        def xconfig(label, value):
            config = FormLayout.Editbox(label, 80, tipo=float, decimales=3)
            liGen.append((config, value))

        xconfig(_("Column"), col)
        xconfig(_("Row"), fil)
        xconfig(_("Width"), ancho)
        xconfig(_("Height"), alto)

        resultado = FormLayout.fedit(liGen, title=tarea.txt_tipo(), parent=self)
        if resultado:
            col, fil, ancho, alto = resultado[1]
            tarea.set_datos(col, fil, ancho, alto)
            self.ponSiGrabar()
            return True
        else:
            return False

    def gfile(self):
        self.test_siGrabar()
        path = self.configuracion.ficheroFEN
        fich = QTUtil2.leeCreaFichero(self, path, "dbl")
        if fich:
            self.configuracion.ficheroFEN = Util.dirRelativo(fich)
            self.configuracion.graba()

            self.tablero.dbVisual_close()

            # self.tablero.borraMovibles()
            self.guion.cierraPizarra()
            self.recuperar()

    def gmas(self, siInsertar):
        ta = TabVisual.GT_Action(None)
        liActions = [(_F(txt), Iconos.PuntoRojo(), "GTA_%s" % action) for action, txt in ta.dicTxt.items()]

        # tc = TabVisual.GT_Configuration(None)
        # liConfigurations = [(txt, Iconos.PuntoVerde(), "GTC_%s" % configuracion) for configuracion, txt in tc.dicTxt.items()]

        liMore = [
            (_("Text"), Iconos.Texto(), TabVisual.TP_TEXTO),
            (_("Actions"), Iconos.Run(), liActions),
            # (_("Configuration"), Iconos.Configurar(), liConfigurations),
        ]
        resp = self.selectBanda.menuParaExterior(liMore)
        if resp:
            xid = resp
            fila = self.g_guion.recno() if siInsertar else -1
            if xid == TabVisual.TP_TEXTO:
                tarea = TabVisual.GT_Texto(self.guion)
                fila = self.guion.nuevaTarea(tarea, fila)
                self.ponMarcado(fila, True)
                self.ponSiGrabar()
            elif resp.startswith("GTA_"):
                self.creaAction(resp[4:], fila)
            # elif resp.startswith("GTC_"):
            #     key = resp[4:]
            #     txt = tc.dicTxt[key]
            #     if not self.creaConfiguration(txt, key, fila):
            #         return
            else:
                li = xid.split("_")
                tp = li[1]
                xid = int(li[2])
                from_sq, to_sq = self.desdeHasta(_("Director"), self.ultDesde, self.ultHasta)
                if from_sq:
                    self.creaTarea(tp, xid, from_sq + to_sq, fila)
            if siInsertar:
                self.g_guion.goto(fila, 0)
            else:
                self.g_guion.gobottom()

    def creaAction(self, action, fila):
        tarea = TabVisual.GT_Action(self.guion)
        tarea.action(action)
        fila = self.guion.nuevaTarea(tarea, fila)
        self.ponSiGrabar()
        self.refresh_guion()

    # def creaConfiguration(self, txt, configuracion, fila):
    #     liGen = [(None, None)]
    #     config = FormLayout.Editbox(_("Time in milliseconds"), 80, tipo=int)
    #     liGen.append((config, ""))
    #     ico = Iconos.Configurar()

    #     resultado = FormLayout.fedit(liGen, title=txt, parent=self, icon=ico)
    #     if resultado:
    #         accion, liResp = resultado
    #         value = liResp[0]
    #         tarea = TabVisual.GT_Configuration(self.guion)
    #         tarea.configuracion(configuracion)
    #         tarea.value(value)
    #         self.guion.nuevaTarea(tarea, fila)
    #         self.ponSiGrabar()
    #         self.refresh_guion()
    #         return True
    #     return False

    def gnuevo(self):
        self.gmas(False)

    def ginsertar(self):
        self.gmas(True)

    def borraUltimo(self):
        fila = len(self.guion) - 1
        if fila >= 0:
            lista = [fila]
            self.borrar_lista(lista)

    def borraTodos(self):
        num = len(self.guion)
        if num:
            self.borrar_lista(list(range(num)))

    def borrar_lista(self, lista=None):
        li = self.g_guion.recnosSeleccionados() if lista is None else lista
        if li:
            li.sort(reverse=True)
            for fila in li:
                self.ponMarcado(fila, False)
                sc = self.guion.itemTarea(fila)
                if sc:
                    self.tablero.borraMovible(sc)
                else:
                    tarea = self.guion.tarea(fila)
                    if tarea.tp() == TabVisual.TP_TEXTO:
                        self.guion.cierraPizarra()
                self.guion.borra(fila)
            if fila >= len(self.guion):
                fila = len(self.guion) - 1
            self.g_guion.goto(fila, 0)
            self.ponSiGrabar()
            self.refresh_guion()

    def gborrar(self):
        li = self.g_guion.recnosSeleccionados()
        if li:
            self.borrar_lista(li)

    def garriba(self):
        fila = self.g_guion.recno()
        if self.guion.arriba(fila):
            self.g_guion.goto(fila - 1, 0)
            self.refresh_guion()
            self.ponSiGrabar()

    def gabajo(self):
        fila = self.g_guion.recno()
        if self.guion.abajo(fila):
            self.g_guion.goto(fila + 1, 0)
            self.refresh_guion()
            self.ponSiGrabar()

    def grid_doble_click(self, grid, fila, col):
        key = col.clave
        if key == "INFO":
            tarea = self.guion.tarea(fila)
            sc = self.guion.itemTarea(fila)
            if sc:
                if tarea.tp() == TabVisual.TP_SVG:
                    if self.datosSVG(tarea):
                        self.tablero.refresh()

                else:
                    a1h8 = tarea.a1h8()
                    from_sq, to_sq = self.desdeHasta(tarea.txt_tipo() + " " + tarea.name(), a1h8[:2], a1h8[2:])
                    if from_sq:
                        sc = tarea.itemSC()
                        sc.ponA1H8(from_sq + to_sq)
                        self.tablero.refresh()

            mo = tarea.marcadoOwner()
            if mo:
                self.ponMarcadoOwner(fila, mo)
            self.refresh_guion()

    def keyPressEvent(self, event):
        self.owner.keyPressEvent(event)

    def foto(self):
        gn = self.guion.name
        gi = self.guion.info
        gt = self.guion.txt_tipo
        return [(gn(f), gi(f), gt(f)) for f in range(len(self.guion))]

    def refresh_guion(self):
        self.g_guion.refresh()
        if self.must_save:
            return
        nueva = self.foto()
        nv = len(nueva)
        if self.ant_foto is None or nv != len(self.ant_foto):
            self.ant_foto = nueva
            self.ponSiGrabar()
        else:
            for n in range(nv):
                if self.ant_foto[n] != nueva[n]:
                    self.ant_foto = nueva
                    self.ponSiGrabar()
                    break

    def grid_num_datos(self, grid):
        return len(self.guion) if self.guion else 0

    def clonaItemTarea(self, fila):
        tarea = self.guion.tarea(fila)
        bloqueDatos = tarea.bloqueDatos()
        tp = tarea.tp()
        if tp == TabVisual.TP_FLECHA:
            sc = self.tablero.creaFlecha(bloqueDatos)
        elif tp == TabVisual.TP_MARCO:
            sc = self.tablero.creaMarco(bloqueDatos)
        elif tp == TabVisual.TP_SVG:
            sc = self.tablero.creaSVG(bloqueDatos)
        elif tp == TabVisual.TP_MARKER:
            sc = self.tablero.creaMarker(bloqueDatos)
        else:
            return None
        return sc

    def ponMarcado(self, fila, siMarcado):
        self.guion.cambiaMarcaTarea(fila, siMarcado)
        itemSC = self.guion.itemTarea(fila)
        self.ponMarcadoItem(fila, self.tablero, itemSC, siMarcado)
        self.refresh_guion()

    def ponMarcadoItem(self, fila, tablero, itemSC, siMarcado):
        if itemSC:
            itemSC.setVisible(siMarcado)

        else:
            tarea = self.guion.tarea(fila)
            if isinstance(tarea, TabVisual.GT_PiezaMueve):
                from_sq, to_sq, borra = tarea.desdeHastaBorra()
                if siMarcado:
                    tablero.muevePieza(from_sq, to_sq)
                    tablero.ponFlechaSC(from_sq, to_sq)
                else:
                    tablero.muevePieza(to_sq, from_sq)
                    if borra:
                        tablero.creaPieza(borra, to_sq)
                    if tablero.flechaSC:
                        tablero.flechaSC.hide()
                tablero.activaTodas()

            elif isinstance(tarea, TabVisual.GT_PiezaCrea):
                from_sq, pz_borrada = tarea.from_sq()
                if siMarcado:
                    tablero.cambiaPieza(from_sq, tarea.pieza())
                else:
                    tablero.borraPieza(from_sq)
                    if pz_borrada:
                        tablero.creaPieza(pz_borrada, from_sq)
                tablero.activaTodas()

            elif isinstance(tarea, TabVisual.GT_PiezaBorra):
                if siMarcado:
                    tablero.borraPieza(tarea.from_sq())
                else:
                    tablero.cambiaPieza(tarea.from_sq(), tarea.pieza())
                tablero.activaTodas()

            elif isinstance(tarea, TabVisual.GT_Texto):
                self.guion.cierraPizarra()
                if siMarcado:
                    self.guion.writePizarra(tarea)
                for recno in range(len(self.guion)):
                    tarea = self.guion.tarea(recno)
                    if tarea.tp() == TabVisual.TP_TEXTO and fila != recno:
                        self.guion.cambiaMarcaTarea(recno, False)

            elif isinstance(tarea, TabVisual.GT_Action):
                if siMarcado:
                    tarea.run()
                    self.guion.cambiaMarcaTarea(fila, False)

    def grid_setvalue(self, grid, fila, oColumna, valor):
        key = oColumna.clave if oColumna else "MARCADO"
        if key == "MARCADO":
            self.ponMarcado(fila, valor > 0)
        elif key == "NOMBRE":
            tarea = self.guion.tarea(fila)
            tarea.name(valor.strip())
            self.ponSiGrabar()

    def editarBanda(self, cid):
        li = cid.split("_")
        tp = li[1]
        xid = li[2]
        ok = False
        if tp == TabVisual.TP_FLECHA:
            regFlecha = self.dbFlechas[xid]
            w = PantallaTabVFlechas.WTV_Flecha(self, regFlecha, True)
            if w.exec_():
                self.dbFlechas[xid] = w.regFlecha
                ok = True
        elif tp == TabVisual.TP_MARCO:
            regMarco = self.dbMarcos[xid]
            w = PantallaTabVMarcos.WTV_Marco(self, regMarco)
            if w.exec_():
                self.dbMarcos[xid] = w.regMarco
                ok = True
        elif tp == TabVisual.TP_SVG:
            regSVG = self.dbSVGs[xid]
            w = PantallaTabVSVGs.WTV_SVG(self, regSVG)
            if w.exec_():
                self.dbSVGs[xid] = w.regSVG
                ok = True
        elif tp == TabVisual.TP_MARKER:
            regMarker = self.dbMarkers[xid]
            w = PantallaTabVMarkers.WTV_Marker(self, regMarker)
            if w.exec_():
                self.dbMarkers[xid] = w.regMarker
                ok = True

        if ok:
            self.actualizaBandas()
            if len(self.guion):
                self.ponSiGrabar()

    def test_siGrabar(self):
        if self.must_save:
            if self.chbSaveWhenFinished.valor():
                self.grabar()
            self.must_save = False

    def closeEvent(self, event):
        self.test_siGrabar()
        self.cierraRecursos()

    def terminar(self):
        self.cierraRecursos()
        self.close()

    def cancelar(self):
        self.terminar()

    def portapapeles(self):
        self.tablero.salvaEnImagen()
        txt = _("Clipboard")
        QTUtil2.mensajeTemporal(self, _X(_("Saved to %1"), txt), 0.8)

    def grabarFichero(self):
        dirSalvados = self.configuracion.x_save_folder
        resp = QTUtil2.salvaFichero(self, _("File to save"), dirSalvados, _("File") + " PNG (*.png)", False)
        if resp:
            self.tablero.salvaEnImagen(resp, "png")
            txt = resp
            QTUtil2.mensajeTemporal(self, _X(_("Saved to %1"), txt), 0.8)
            direc = os.path.dirname(resp)
            if direc != dirSalvados:
                self.configuracion.x_save_folder = direc
                self.configuracion.graba()

    def flechas(self):
        w = PantallaTabVFlechas.WTV_Flechas(self, self.listaFlechas(), self.dbFlechas)
        w.exec_()
        self.actualizaBandas()
        QTUtil.refresh_gui()

    def listaFlechas(self):
        dic = self.dbFlechas.as_dictionary()
        li = []
        for k, dicFlecha in dic.items():
            flecha = TabTipos.Flecha()
            flecha.restore_dic(dicFlecha)
            flecha.id = int(k)
            li.append(flecha)

        li.sort(key=lambda x: x.ordenVista)
        return li

    def marcos(self):
        w = PantallaTabVMarcos.WTV_Marcos(self, self.listaMarcos(), self.dbMarcos)
        w.exec_()
        self.actualizaBandas()
        QTUtil.refresh_gui()

    def listaMarcos(self):
        dic = self.dbMarcos.as_dictionary()
        li = []
        for k, dicMarco in dic.items():
            marco = TabTipos.Marco()
            marco.restore_dic(dicMarco)
            marco.id = int(k)
            li.append(marco)
        li.sort(key=lambda x: x.ordenVista)
        return li

    def svgs(self):
        w = PantallaTabVSVGs.WTV_SVGs(self, self.listaSVGs(), self.dbSVGs)
        w.exec_()
        self.actualizaBandas()
        QTUtil.refresh_gui()

    def listaSVGs(self):
        dic = self.dbSVGs.as_dictionary()
        li = []
        for k, dicSVG in dic.items():
            svg = TabTipos.SVG()
            svg.restore_dic(dicSVG)
            svg.id = int(k)
            li.append(svg)
        li.sort(key=lambda x: x.ordenVista)
        return li

    def markers(self):
        w = PantallaTabVMarkers.WTV_Markers(self, self.listaMarkers(), self.dbMarkers)
        w.exec_()
        self.actualizaBandas()
        QTUtil.refresh_gui()

    def listaMarkers(self):
        dic = self.dbMarkers.as_dictionary()
        li = []
        for k, dic_marker in dic.items():
            marker = TabTipos.Marker()
            marker.restore_dic(dic_marker)
            marker.id = int(k)
            li.append(marker)
        li.sort(key=lambda x: x.ordenVista)
        return li

    def leeRecursos(self):
        self.dbConfig = self.dbGestor.dbConfig
        self.dbFlechas = self.dbGestor.dbFlechas
        self.dbMarcos = self.dbGestor.dbMarcos
        self.dbSVGs = self.dbGestor.dbSVGs
        self.dbMarkers = self.dbGestor.dbMarcos

    def cierraRecursos(self):
        if self.guion is not None:
            self.guion.cierraPizarra()
            self.dbConfig["SELECTBANDA"] = self.selectBanda.guardar()
            self.dbConfig["SELECTBANDANUM"] = self.selectBanda.numSeleccionada()
            self.dbConfig["SAVEWHENFINISHED"] = self.chbSaveWhenFinished.valor()
            self.dbGestor.close()

            self.save_video()
            self.guion.restoreTablero()
            self.guion = None

    def actualizaBandas(self):
        self.selectBanda.iniActualizacion()

        tipo = _("Arrows")
        for flecha in self.listaFlechas():
            pm = QtGui.QPixmap()
            pm.loadFromData(flecha.png, "PNG")
            xid = "_F_%d" % flecha.id
            name = flecha.name
            self.selectBanda.actualiza(xid, name, pm, tipo)

        tipo = _("Boxes")
        for marco in self.listaMarcos():
            pm = QtGui.QPixmap()
            pm.loadFromData(marco.png, "PNG")
            xid = "_M_%d" % marco.id
            name = marco.name
            self.selectBanda.actualiza(xid, name, pm, tipo)

        tipo = _("Images")
        for svg in self.listaSVGs():
            pm = QtGui.QPixmap()
            pm.loadFromData(svg.png, "PNG")
            xid = "_S_%d" % svg.id
            name = svg.name
            self.selectBanda.actualiza(xid, name, pm, tipo)

        tipo = _("Markers")
        for marker in self.listaMarkers():
            pm = QtGui.QPixmap()
            pm.loadFromData(marker.png, "PNG")
            xid = "_X_%d" % marker.id
            name = marker.name
            self.selectBanda.actualiza(xid, name, pm, tipo)

        self.selectBanda.finActualizacion()

        dicCampos = {
            TabVisual.TP_FLECHA: (
                "name",
                "altocabeza",
                "tipo",
                "destino",
                "color",
                "colorinterior",
                "colorinterior2",
                "opacidad",
                "redondeos",
                "forma",
                "ancho",
                "vuelo",
                "descuelgue",
            ),
            TabVisual.TP_MARCO: (
                "name",
                "color",
                "colorinterior",
                "colorinterior2",
                "grosor",
                "redEsquina",
                "tipo",
                "opacidad",
            ),
            TabVisual.TP_SVG: ("name", "opacidad"),
            TabVisual.TP_MARKER: ("name", "opacidad"),
        }
        dicDB = {
            TabVisual.TP_FLECHA: self.dbFlechas,
            TabVisual.TP_MARCO: self.dbMarcos,
            TabVisual.TP_SVG: self.dbSVGs,
            TabVisual.TP_MARKER: self.dbMarkers,
        }
        for k, sc in self.tablero.dicMovibles.items():
            bd = sc.bloqueDatos
            try:
                tp, xid = bd.tpid
                bdn = dicDB[tp][xid]
                for campo in dicCampos[tp]:
                    setattr(bd, campo, getattr(bdn, campo))
                sc.update()
            except:
                pass
        self.refresh_guion()

    def muevePieza(self, from_sq, to_sq):
        self.creaTarea("P", None, from_sq + to_sq, -1)
        self.tablero.muevePieza(from_sq, to_sq)

    def tableroPress(self, event, origin, siRight, siShift, siAlt, siCtrl):
        if origin:
            if not siRight:
                lb_sel = self.selectBanda.seleccionada
            else:
                if siCtrl:
                    if siAlt:
                        pos = 4
                    elif siShift:
                        pos = 5
                    else:
                        pos = 3
                else:
                    if siAlt:
                        pos = 1
                    elif siShift:
                        pos = 2
                    else:
                        pos = 0
                lb_sel = self.selectBanda.get_pos(pos)
            if lb_sel:
                nada, tp, nid = lb_sel.id.split("_")
                nid = int(nid)
                if tp == TabVisual.TP_FLECHA:
                    self.siGrabarInicio = self.must_save
                self.datos_new = self.creaTarea(tp, nid, origin + origin, -1)
                self.tp_new = tp
                if tp in (TabVisual.TP_FLECHA, TabVisual.TP_MARCO):
                    self.origin_new = origin
                    sc = self.datos_new[0].itemSC()
                    sc.mousePressExt(event)
                else:
                    self.origin_new = None

    def tableroMove(self, event):
        if self.origin_new:
            sc = self.datos_new[0].itemSC()
            sc.mouseMoveExt(event)

    def tableroRelease(self, a1, siRight, siShift, siAlt):
        if self.origin_new:
            tarea, fila = self.datos_new
            sc = tarea.itemSC()
            sc.mouseReleaseExt()
            self.g_guion.goto(fila, 0)
            if siRight:
                if a1 == self.origin_new:
                    if siShift:
                        pos = 8
                    elif siAlt:
                        pos = 7
                    else:
                        pos = 6
                    self.borrar_lista()
                    lb = self.selectBanda.get_pos(pos)
                    nada, tp, nid = lb.id.split("_")
                    nid = int(nid)
                    self.datos_new = self.creaTarea(tp, nid, a1 + a1, -1)
                    self.tp_new = tp
                li = self.guion.borraRepeticionUltima()
                if li:
                    self.borrar_lista(li)
                    self.origin_new = None
                    return

            else:
                if a1 is None or (a1 == self.origin_new and self.tp_new == TabVisual.TP_FLECHA):
                    self.borrar_lista()
                    if self.tp_new == TabVisual.TP_FLECHA:
                        if not self.siGrabarInicio:
                            self.ponNoGrabar()

                else:
                    self.ponSiGrabar()
                    self.refresh_guion()

            self.origin_new = None

    def tableroRemove(self, itemSC):
        tarea, n = self.guion.tareaItem(itemSC)
        if tarea:
            self.g_guion.goto(n, 0)
            self.borrar_lista()


class Director:
    def __init__(self, tablero):
        self.tablero = tablero
        self.ultTareaSelect = None
        self.director = False
        self.directorItemSC = None
        self.w = WPanelDirector(self, tablero)
        self.w.show()
        self.guion = self.w.guion

    def show(self):
        self.w.show()

    def cambiadaPosicionAntes(self):
        self.w.test_siGrabar()

    def cambiadaPosicionDespues(self):
        self.w.cambiadaPosicion()
        self.guion.saveTablero()

    def cambiadoMensajero(self):
        self.w.test_siGrabar()
        self.w.terminar()

    def muevePieza(self, from_sq, to_sq, promotion=None):
        self.w.creaTarea("P", None, from_sq + to_sq, -1)
        self.tablero.muevePieza(from_sq, to_sq)
        return True

    def setChange(self, ok):
        self.director = ok
        self.ultTareaSelect = None
        self.directorItemSC = None
        # if ok:
        #     self.tablero.activaTodas()
        # else:
        #     self.tablero.disable_all()

    def keyPressEvent(self, event):
        k = event.key()
        if QtCore.Qt.Key_F1 <= k <= QtCore.Qt.Key_F10:
            f = k - QtCore.Qt.Key_F1
            m = int(event.modifiers())
            siCtrl = (m & QtCore.Qt.ControlModifier) > 0
            self.w.funcion(f, siCtrl)
            return True
        else:
            return False

    def mousePressEvent(self, event):
        siRight = event.button() == QtCore.Qt.RightButton
        p = event.pos()
        a1h8 = self.punto2a1h8(p)
        m = int(event.modifiers())
        siCtrl = (m & QtCore.Qt.ControlModifier) > 0
        siShift = (m & QtCore.Qt.ShiftModifier) > 0
        siAlt = (m & QtCore.Qt.AltModifier) > 0

        li_tareas = self.guion.tareasPosicion(p)

        if siRight and siShift and siAlt:
            pz_borrar = self.tablero.dameNomPiezaEn(a1h8)
            menu = Controles.Menu(self.tablero)
            dicPieces = TrListas.dicNomPiezas()
            icoPiece = self.tablero.piezas.icono

            if pz_borrar or len(li_tareas):
                mrem = menu.submenu(_("Remove"), Iconos.Delete())
                if pz_borrar:
                    rotulo = dicPieces[pz_borrar.upper()]
                    mrem.opcion(("rem_pz", None), rotulo, icoPiece(pz_borrar))
                    mrem.separador()
                for pos_guion, tarea in li_tareas:
                    rotulo = "%s - %s - %s" % (tarea.txt_tipo(), tarea.name(), tarea.info())
                    mrem.opcion(("rem_gr", pos_guion), rotulo, Iconos.Delete())
                    mrem.separador()
                menu.separador()

            for pz in "KQRBNPkqrbnp":
                if pz != pz_borrar:
                    if pz == "k":
                        menu.separador()
                    menu.opcion(("create", pz), dicPieces[pz.upper()], icoPiece(pz))
            resp = menu.lanza()
            if resp is not None:
                orden, arg = resp
                if orden == "rem_gr":
                    self.w.g_guion.goto(arg, 0)
                    self.w.borrar_lista()
                elif orden == "rem_pz":
                    self.w.creaTarea("B", pz_borrar, a1h8, -1)

                elif orden == "create":
                    self.w.creaTarea("C", arg, a1h8, -1)
            return True

        if self.director:
            return self.mousePressEvent_Drop(event)

        self.w.tableroPress(event, a1h8, siRight, siShift, siAlt, siCtrl)

        return True

    def mousePressEvent_Drop(self, event):
        p = event.pos()
        li_tareas = self.guion.tareasPosicion(p)  # (pos_guion, tarea)...
        nli_tareas = len(li_tareas)
        if nli_tareas > 0:
            if nli_tareas > 1:  # Guerra
                posic = None
                for x in range(nli_tareas):
                    if self.ultTareaSelect == li_tareas[x][1]:
                        posic = x
                        break
                if posic is None:
                    posic = 0
                else:
                    posic += 1
                    if posic >= nli_tareas:
                        posic = 0
            else:
                posic = 0

            tarea_elegida = li_tareas[posic][1]

            if self.ultTareaSelect:
                self.ultTareaSelect.itemSC().activa(False)
            self.ultTareaSelect = tarea_elegida
            itemSC = self.ultTareaSelect.itemSC()
            itemSC.activa(True)
            itemSC.mousePressExt(event)
            self.directorItemSC = itemSC

            return True
        else:
            self.ultTareaSelect = None
            return False

    def punto2a1h8(self, punto):
        xc = 1 + int(float(punto.x() - self.tablero.margenCentro) / self.tablero.anchoCasilla)
        yc = 1 + int(float(punto.y() - self.tablero.margenCentro) / self.tablero.anchoCasilla)

        if self.tablero.is_white_bottom:
            yc = 9 - yc
        else:
            xc = 9 - xc

        if not ((1 <= xc <= 8) and (1 <= yc <= 8)):
            return None

        f = chr(48 + yc)
        c = chr(96 + xc)
        a1h8 = c + f
        return a1h8

    def mouseMoveEvent(self, event):
        if self.director:
            if self.directorItemSC:
                self.directorItemSC.mouseMoveEvent(event)
            return False
        self.w.tableroMove(event)
        return True

    def mouseReleaseEvent(self, event):
        if self.director:
            if self.directorItemSC:
                self.directorItemSC.mouseReleaseExt()
                self.directorItemSC.activa(False)
                self.directorItemSC = None
                self.w.refresh_guion()
                return True
            else:
                return False

        a1h8 = self.punto2a1h8(event.pos())
        if a1h8:
            siRight = event.button() == QtCore.Qt.RightButton
            m = int(event.modifiers())
            siShift = (m & QtCore.Qt.ShiftModifier) > 0
            siAlt = (m & QtCore.Qt.AltModifier) > 0
            self.w.tableroRelease(a1h8, siRight, siShift, siAlt)
        return True

    def terminar(self):
        if self.w:
            self.w.terminar()
            self.w = None
