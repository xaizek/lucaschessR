import os

from PySide2 import QtCore, QtWidgets

import Code
from Code.Constantes import FEN_INITIAL
from Code.QT import Colocacion
from Code.QT import Controles
from Code.QT import FormLayout
from Code.QT import Iconos
from Code.QT import QTUtil2
from Code.QT import QTVarios
from Code.SQL import UtilSQL
from Code import Util


class WFiltrar(QtWidgets.QDialog):
    def __init__(self, wParent, o_columns, liFiltro, dbSaveNom=None):
        super(WFiltrar, self).__init__()

        if dbSaveNom is None:
            dbSaveNom = Code.configuracion.ficheroFiltrosPGN

        self.setWindowTitle(_("Filter"))
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog | QtCore.Qt.WindowTitleHint)
        self.setWindowIcon(Iconos.Filtrar())

        self.liFiltro = liFiltro
        nFiltro = len(liFiltro)
        self.dbSaveNom = dbSaveNom

        li_fields = [(x.cabecera, '"%s"' % x.clave) for x in o_columns.liColumnas if x.clave != "number" and x.clave != "opening"]
        li_fields.insert(0, ("", None))
        liCondicion = [
            ("", None),
            (_("Equal"), "="),
            (_("Not equal"), "<>"),
            (_("Greater than"), ">"),
            (_("Less than"), "<"),
            (_("Greater than or equal"), ">="),
            (_("Less than or equal"), "<="),
            (_("Like (wildcard = *)"), "LIKE"),
            (_("Not like (wildcard = *)"), "NOT LIKE"),
        ]

        liUnion = [("", None), (_("AND"), "AND"), (_("OR"), "OR")]

        f = Controles.TipoLetra(puntos=12)  # 0, peso=75 )

        lbCol = Controles.LB(self, _("Column")).ponFuente(f)
        lbPar0 = Controles.LB(self, "(").ponFuente(f)
        lbPar1 = Controles.LB(self, ")").ponFuente(f)
        lbCon = Controles.LB(self, _("Condition")).ponFuente(f)
        lbVal = Controles.LB(self, _("Value")).ponFuente(f)
        lbUni = Controles.LB(self, "+").ponFuente(f)

        ly = Colocacion.G()
        ly.controlc(lbUni, 0, 0).controlc(lbPar0, 0, 1).controlc(lbCol, 0, 2)
        ly.controlc(lbCon, 0, 3).controlc(lbVal, 0, 4).controlc(lbPar1, 0, 5)

        self.numC = 8
        liC = []

        union, par0, campo, condicion, valor, par1 = None, False, None, None, "", False
        for i in range(self.numC):
            if i > 0:
                c_union = Controles.CB(self, liUnion, union)
                ly.controlc(c_union, i + 1, 0)
            else:
                c_union = None

            c_par0 = Controles.CHB(self, "", par0).anchoFijo(20)
            ly.controlc(c_par0, i + 1, 1)
            c_campo = Controles.CB(self, li_fields, campo)
            ly.controlc(c_campo, i + 1, 2)
            c_condicion = Controles.CB(self, liCondicion, condicion)
            ly.controlc(c_condicion, i + 1, 3)
            c_valor = Controles.ED(self, valor)
            ly.controlc(c_valor, i + 1, 4)
            c_par1 = Controles.CHB(self, "", par1).anchoFijo(20)
            ly.controlc(c_par1, i + 1, 5)

            liC.append((c_union, c_par0, c_campo, c_condicion, c_valor, c_par1))

        self.liC = liC

        # Toolbar
        li_acciones = [
            (_("Accept"), Iconos.Aceptar(), self.aceptar),
            None,
            (_("Cancel"), Iconos.Cancelar(), self.reject),
            None,
            (_("Reinit"), Iconos.Reiniciar(), self.reiniciar),
            None,
            (_("Save/Restore"), Iconos.Grabar(), self.grabar),
            None,
        ]

        tb = QTVarios.LCTB(self, li_acciones)

        # Layout
        layout = Colocacion.V().control(tb).otro(ly).margen(3)
        self.setLayout(layout)

        liC[0][2].setFocus()

        if nFiltro > 0:
            self.lee_filtro(self.liFiltro)

    def grabar(self):
        if not self.lee_filtro_actual():
            return
        with UtilSQL.DictSQL(self.dbSaveNom, tabla="Filters") as dbc:
            liConf = dbc.keys(si_ordenados=True)
            if len(liConf) == 0 and len(self.liFiltro) == 0:
                return
            menu = Controles.Menu(self)
            SELECCIONA, BORRA, GRABA = range(3)
            for x in liConf:
                menu.opcion((SELECCIONA, x), x, Iconos.PuntoAzul())
            menu.separador()

            if len(self.liFiltro) > 0:
                submenu = menu.submenu(_("Save current"), Iconos.Mas())
                if liConf:
                    for x in liConf:
                        submenu.opcion((GRABA, x), x, Iconos.PuntoAmarillo())
                submenu.separador()
                submenu.opcion((GRABA, None), _("New"), Iconos.NuevoMas())

            if liConf:
                menu.separador()
                submenu = menu.submenu(_("Remove"), Iconos.Delete())
                for x in liConf:
                    submenu.opcion((BORRA, x), x, Iconos.PuntoRojo())
            resp = menu.lanza()

            if resp:
                op, name = resp

                if op == SELECCIONA:
                    liFiltro = dbc[name]
                    self.lee_filtro(liFiltro)
                elif op == BORRA:
                    if QTUtil2.pregunta(self, _X(_("Delete %1 ?"), name)):
                        del dbc[name]
                elif op == GRABA:
                    if self.lee_filtro_actual():
                        if name is None:
                            liGen = [FormLayout.separador]
                            liGen.append((_("Name") + ":", ""))

                            resultado = FormLayout.fedit(liGen, title=_("Filter"), parent=self, icon=Iconos.Libre())
                            if resultado:
                                accion, liGen = resultado

                                name = liGen[0].strip()
                                if name:
                                    dbc[name] = self.liFiltro
                        else:
                            dbc[name] = self.liFiltro

    def lee_filtro(self, liFiltro):
        self.liFiltro = liFiltro
        nFiltro = len(liFiltro)

        for i in range(self.numC):
            if nFiltro > i:
                union, par0, campo, condicion, valor, par1 = liFiltro[i]
            else:
                union, par0, campo, condicion, valor, par1 = None, False, None, None, "", False
            c_union, c_par0, c_campo, c_condicion, c_valor, c_par1 = self.liC[i]
            if c_union:
                c_union.ponValor(union)
            c_par0.ponValor(par0)
            c_campo.ponValor(campo)
            c_condicion.ponValor(condicion)
            c_valor.ponTexto(valor)
            c_par1.ponValor(par1)

    def reiniciar(self):
        for i in range(self.numC):
            self.liC[i][1].ponValor(False)
            self.liC[i][2].setCurrentIndex(0)
            self.liC[i][3].setCurrentIndex(0)
            self.liC[i][4].ponTexto("")
            self.liC[i][5].ponValor(False)
            if i > 0:
                self.liC[i][0].setCurrentIndex(0)
        self.aceptar()

    def lee_filtro_actual(self):
        self.liFiltro = []

        npar = 0

        for i in range(self.numC):
            par0 = self.liC[i][1].valor()
            campo = self.liC[i][2].valor()
            condicion = self.liC[i][3].valor()
            valor = self.liC[i][4].texto().rstrip()
            par1 = self.liC[i][5].valor()

            if campo and condicion:
                if campo == "PLIES":
                    valor = valor.strip()
                    if valor.isdigit():
                        valor = "%d" % int(valor)  # fonkap patch %3d -> %d
                if par0:
                    npar += 1
                if par1:
                    npar -= 1
                if npar < 0:
                    break
                if i > 0:
                    union = self.liC[i][0].valor()
                    if union:
                        self.liFiltro.append([union, par0, campo, condicion, valor, par1])
                else:
                    self.liFiltro.append([None, par0, campo, condicion, valor, par1])
            else:
                break
        if npar:
            QTUtil2.message_error(self, _("The parentheses are unbalanced."))
            return False
        return True

    def aceptar(self):
        if self.lee_filtro_actual():
            self.accept()

    def where(self):
        where = ""
        for union, par0, campo, condicion, valor, par1 in self.liFiltro:
            valor = valor.upper()
            if condicion in ("LIKE", "NOT LIKE"):
                valor = valor.replace("*", "%")
                if not ("%" in valor):
                    valor = "%" + valor + "%"

            if union:
                where += " %s " % union
            if par0:
                where += "("
            if condicion in ("=", "<>") and not valor:
                where += "(( %s %s ) OR (%s %s ''))" % (campo, "IS NULL" if condicion == "=" else "IS NOT NULL", campo, condicion)
            else:
                valor = valor.upper()
                if valor.isupper():
                    where += "UPPER(%s) %s '%s'" % (campo, condicion, valor)  # fonkap patch
                elif valor.isdigit():  # fonkap patch
                    where += "CAST(%s as decimal) %s %s" % (campo, condicion, valor)  # fonkap patch
                else:
                    where += "%s %s '%s'" % (campo, condicion, valor)  # fonkap patch
            if par1:
                where += ")"
        return where


class EM_SQL(Controles.EM):
    def __init__(self, owner, where, li_fields):
        self.li_fields = li_fields
        Controles.EM.__init__(self, owner, where, siHTML=False)

    def mousePressEvent(self, event):
        Controles.EM.mousePressEvent(self, event)
        if event.button() == QtCore.Qt.RightButton:
            menu = QTVarios.LCMenu(self)
            rondo = QTVarios.rondoPuntos()
            for txt, key in self.li_fields:
                menu.opcion(key, txt, rondo.otro())
            resp = menu.lanza()
            if resp:
                self.insertarTexto(resp)


class WFiltrarRaw(QTVarios.WDialogo):
    def __init__(self, wParent, o_columns, where):
        QtWidgets.QDialog.__init__(self, wParent)

        QTVarios.WDialogo.__init__(self, wParent, _("Filter"), Iconos.Filtrar(), "rawfilter")

        self.where = ""
        li_fields = [(x.cabecera, x.key) for x in o_columns.liColumnas if x.key != "number"]

        f = Controles.TipoLetra(puntos=12)  # 0, peso=75 )

        lbRaw = Controles.LB(self, "%s:" % _("Raw SQL")).ponFuente(f)
        self.edRaw = EM_SQL(self, where, li_fields).altoFijo(72).anchoMinimo(512).ponFuente(f)

        lbHelp = Controles.LB(self, _("Right button to select a column of database")).ponFuente(f)
        lyHelp = Colocacion.H().relleno().control(lbHelp).relleno()

        ly = Colocacion.H().control(lbRaw).control(self.edRaw)

        # Toolbar
        li_acciones = [(_("Accept"), Iconos.Aceptar(), self.aceptar), None, (_("Cancel"), Iconos.Cancelar(), self.reject), None]
        tb = QTVarios.LCTB(self, li_acciones)

        # Layout
        layout = Colocacion.V().control(tb).otro(ly).otro(lyHelp).margen(3)
        self.setLayout(layout)

        self.edRaw.setFocus()

        self.restore_video(siTam=False)

    def aceptar(self):
        self.where = self.edRaw.texto()
        self.save_video()
        self.accept()


def mensajeEntrenamientos(owner, liCreados, liNoCreados):
    txt = ""
    if liCreados:
        txt += _("Created the following trainings") + ":"
        txt += "<ul>"
        for x in liCreados:
            txt += "<li>%s</li>" % os.path.basename(x)
        txt += "</ul>"
    if liNoCreados:
        txt += _("No trainings created due to lack of data") + ":"
        txt += "<ul>"
        for x in liNoCreados:
            txt += "<li>%s</li>" % os.path.basename(x)
        txt += "</ul>"
    QTUtil2.message_bold(owner, txt)


def crearTactic(procesador, wowner, liRegistros, rutinaDatos):
    # Se pide el name de la carpeta
    liGen = [(None, None)]

    liGen.append((_("Name") + ":", ""))

    liGen.append((None, None))

    liJ = [(_("Default"), 0), (_("White"), 1), (_("Black"), 2)]
    config = FormLayout.Combobox(_("Point of view"), liJ)
    liGen.append((config, 0))

    eti = _("Create tactics training")
    resultado = FormLayout.fedit(liGen, title=eti, parent=wowner, anchoMinimo=460, icon=Iconos.Tacticas())

    if not resultado:
        return
    accion, liGen = resultado
    menuname = liGen[0].strip()
    if not menuname:
        return
    pointview = str(liGen[1])

    restDir = Util.valid_filename(menuname)
    nomDir = os.path.join(Code.configuracion.dirPersonalTraining, "Tactics", restDir)
    nomIni = os.path.join(nomDir, "Config.ini")
    if os.path.isfile(nomIni):
        dicIni = Util.ini2dic(nomIni)
        n = 1
        while True:
            if "TACTIC%d" % n in dicIni:
                if "MENU" in dicIni["TACTIC%d" % n]:
                    if dicIni["TACTIC%d" % n]["MENU"].upper() == menuname.upper():
                        break
                else:
                    break
                n += 1
            else:
                break
        nomTactic = "TACTIC%d" % n
    else:
        nomDirTac = os.path.join(Code.configuracion.dirPersonalTraining, "Tactics")
        Util.create_folder(nomDirTac)
        Util.create_folder(nomDir)
        nomTactic = "TACTIC1"
        dicIni = {}
    nomFNS = os.path.join(nomDir, "Puzzles.fns")
    if os.path.isfile(nomFNS):
        n = 1
        nomFNS = os.path.join(nomDir, "Puzzles-%d.fns")
        while os.path.isfile(nomFNS % n):
            n += 1
        nomFNS = nomFNS % n

    # Se crea el fichero con los puzzles
    f = open(nomFNS, "wt", encoding="utf-8", errors="ignore")

    nregs = len(liRegistros)
    tmpBP = QTUtil2.BarraProgreso(wowner, menuname, _("Game"), nregs)
    tmpBP.mostrar()

    fen0 = FEN_INITIAL

    for n in range(nregs):

        if tmpBP.is_canceled():
            break

        tmpBP.pon(n + 1)

        recno = liRegistros[n]

        dicValores = rutinaDatos(recno)
        plies = dicValores["PLIES"]
        if plies == 0:
            continue

        pgn = dicValores["PGN"]
        li = pgn.split("\n")
        if len(li) == 1:
            li = pgn.split("\r")
        li = [linea for linea in li if not linea.strip().startswith("[")]
        num_moves = " ".join(li).replace("\r", "").replace("\n", "")
        if not num_moves.strip("*"):
            continue

        def xdic(k):
            x = dicValores.get(k, "")
            if x is None:
                x = ""
            elif "?" in x:
                x = x.replace(".?", "").replace("?", "")
            return x.strip()

        fen = dicValores.get("FEN")
        if not fen:
            fen = fen0

        event = xdic("EVENT")
        site = xdic("SITE")
        date = xdic("DATE")
        if site == event:
            es = event
        else:
            es = event + " " + site
        es = es.strip()
        if date:
            if es:
                es += " (%s)" % date
            else:
                es = date
        white = xdic("WHITE")
        black = xdic("BLACK")
        wb = ("%s-%s" % (white, black)).strip("-")
        titulo = ""
        if es:
            titulo += "<br>%s" % es
        if wb:
            titulo += "<br>%s" % wb

        for other in ("TASK", "SOURCE"):
            v = xdic(other)
            if v:
                titulo += "<br>%s" % v

        txt = fen + "|%s|%s\n" % (titulo, num_moves)

        f.write(txt)

    f.close()
    tmpBP.cerrar()

    # Se crea el fichero de control
    dicIni[nomTactic] = d = {}
    d["MENU"] = menuname
    d["FILESW"] = "%s:100" % os.path.basename(nomFNS)
    d["POINTVIEW"] = pointview

    Util.dic2ini(nomIni, dicIni)

    QTUtil2.message_bold(
        wowner, (_("Tactic training %s created.") % menuname + "\n" + _("You can access this training from<br>menu Trainings<br>➔Learn tactics by repetition<br>➔%s") % restDir)
    )

    procesador.entrenamientos.rehaz()
