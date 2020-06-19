from PySide2 import QtGui

import Code

f = open(Code.path_resource("IntFiles", "Iconos.bin"), "rb")
binIconos = f.read()
f.close()


def icono(name):
    return eval("%s()"%name)


def pixmap(name):
    return eval("pm%s()"%name)


def PM(desde, hasta):
    pm = QtGui.QPixmap()
    pm.loadFromData(binIconos[desde:hasta])
    return pm

def pmLM():
    return PM(0,1248)


def LM():
    return QtGui.QIcon(pmLM())


def pmAplicacion64():
    return PM(1248,6430)


def Aplicacion64():
    return QtGui.QIcon(pmAplicacion64())


def pmDatos():
    return PM(6430,7617)


def Datos():
    return QtGui.QIcon(pmDatos())


def pmTutor():
    return PM(7617,9646)


def Tutor():
    return QtGui.QIcon(pmTutor())


def pmTablero():
    return PM(6430,7617)


def Tablero():
    return QtGui.QIcon(pmTablero())


def pmPartidaOriginal():
    return PM(9646,11623)


def PartidaOriginal():
    return QtGui.QIcon(pmPartidaOriginal())


def pmDGT():
    return PM(11623,12617)


def DGT():
    return QtGui.QIcon(pmDGT())


def pmFindAllMoves():
    return PM(12617,14213)


def FindAllMoves():
    return QtGui.QIcon(pmFindAllMoves())


def pmTamTablero():
    return PM(12617,14213)


def TamTablero():
    return QtGui.QIcon(pmTamTablero())


def pmMensEspera():
    return PM(14213,17961)


def MensEspera():
    return QtGui.QIcon(pmMensEspera())


def pmUtilidades():
    return PM(17961,24390)


def Utilidades():
    return QtGui.QIcon(pmUtilidades())


def pmTerminar():
    return PM(24390,26140)


def Terminar():
    return QtGui.QIcon(pmTerminar())


def pmNuevaPartida():
    return PM(26140,27888)


def NuevaPartida():
    return QtGui.QIcon(pmNuevaPartida())


def pmOpciones():
    return PM(27888,29616)


def Opciones():
    return QtGui.QIcon(pmOpciones())


def pmEntrenamiento():
    return PM(7617,9646)


def Entrenamiento():
    return QtGui.QIcon(pmEntrenamiento())


def pmAplazar():
    return PM(29616,32683)


def Aplazar():
    return QtGui.QIcon(pmAplazar())


def pmAplazamientos():
    return PM(32683,35999)


def Aplazamientos():
    return QtGui.QIcon(pmAplazamientos())


def pmCapturas():
    return PM(35999,38040)


def Capturas():
    return QtGui.QIcon(pmCapturas())


def pmReiniciar():
    return PM(38040,40334)


def Reiniciar():
    return QtGui.QIcon(pmReiniciar())


def pmMotores():
    return PM(40334,46233)


def Motores():
    return QtGui.QIcon(pmMotores())


def pmImportarGM():
    return PM(46233,48833)


def ImportarGM():
    return QtGui.QIcon(pmImportarGM())


def pmAbandonar():
    return PM(48833,52833)


def Abandonar():
    return QtGui.QIcon(pmAbandonar())


def pmEmpezar():
    return PM(52833,54869)


def Empezar():
    return QtGui.QIcon(pmEmpezar())


def pmOtros():
    return PM(54869,59339)


def Otros():
    return QtGui.QIcon(pmOtros())


def pmAnalizar():
    return PM(59339,60876)


def Analizar():
    return QtGui.QIcon(pmAnalizar())


def pmMainMenu():
    return PM(60876,65186)


def MainMenu():
    return QtGui.QIcon(pmMainMenu())


def pmFinPartida():
    return PM(65186,68134)


def FinPartida():
    return QtGui.QIcon(pmFinPartida())


def pmGrabar():
    return PM(68134,69597)


def Grabar():
    return QtGui.QIcon(pmGrabar())


def pmGrabarComo():
    return PM(69597,71649)


def GrabarComo():
    return QtGui.QIcon(pmGrabarComo())


def pmRecuperar():
    return PM(71649,74407)


def Recuperar():
    return QtGui.QIcon(pmRecuperar())


def pmInformacion():
    return PM(74407,76366)


def Informacion():
    return QtGui.QIcon(pmInformacion())


def pmNuevo():
    return PM(76366,77120)


def Nuevo():
    return QtGui.QIcon(pmNuevo())


def pmCopiar():
    return PM(77120,78301)


def Copiar():
    return QtGui.QIcon(pmCopiar())


def pmModificar():
    return PM(78301,82698)


def Modificar():
    return QtGui.QIcon(pmModificar())


def pmBorrar():
    return PM(82698,87689)


def Borrar():
    return QtGui.QIcon(pmBorrar())


def pmMarcar():
    return PM(87689,92618)


def Marcar():
    return QtGui.QIcon(pmMarcar())


def pmPegar():
    return PM(92618,94929)


def Pegar():
    return QtGui.QIcon(pmPegar())


def pmFichero():
    return PM(94929,99614)


def Fichero():
    return QtGui.QIcon(pmFichero())


def pmNuestroFichero():
    return PM(99614,102661)


def NuestroFichero():
    return QtGui.QIcon(pmNuestroFichero())


def pmFicheroRepite():
    return PM(102661,104157)


def FicheroRepite():
    return QtGui.QIcon(pmFicheroRepite())


def pmInformacionPGN():
    return PM(104157,105175)


def InformacionPGN():
    return QtGui.QIcon(pmInformacionPGN())


def pmVer():
    return PM(105175,106629)


def Ver():
    return QtGui.QIcon(pmVer())


def pmInicio():
    return PM(106629,108643)


def Inicio():
    return QtGui.QIcon(pmInicio())


def pmFinal():
    return PM(108643,110637)


def Final():
    return QtGui.QIcon(pmFinal())


def pmFiltrar():
    return PM(110637,117127)


def Filtrar():
    return QtGui.QIcon(pmFiltrar())


def pmArriba():
    return PM(117127,119280)


def Arriba():
    return QtGui.QIcon(pmArriba())


def pmAbajo():
    return PM(119280,121388)


def Abajo():
    return QtGui.QIcon(pmAbajo())


def pmEstadisticas():
    return PM(121388,123527)


def Estadisticas():
    return QtGui.QIcon(pmEstadisticas())


def pmCheck():
    return PM(123527,126751)


def Check():
    return QtGui.QIcon(pmCheck())


def pmTablas():
    return PM(126751,128374)


def Tablas():
    return QtGui.QIcon(pmTablas())


def pmAtras():
    return PM(128374,129893)


def Atras():
    return QtGui.QIcon(pmAtras())


def pmBuscar():
    return PM(129893,131878)


def Buscar():
    return QtGui.QIcon(pmBuscar())


def pmLibros():
    return PM(131878,134006)


def Libros():
    return QtGui.QIcon(pmLibros())


def pmAceptar():
    return PM(134006,137353)


def Aceptar():
    return QtGui.QIcon(pmAceptar())


def pmCancelar():
    return PM(137353,139336)


def Cancelar():
    return QtGui.QIcon(pmCancelar())


def pmDefecto():
    return PM(139336,142655)


def Defecto():
    return QtGui.QIcon(pmDefecto())


def pmInsertar():
    return PM(142655,145051)


def Insertar():
    return QtGui.QIcon(pmInsertar())


def pmJugar():
    return PM(145051,147260)


def Jugar():
    return QtGui.QIcon(pmJugar())


def pmConfigurar():
    return PM(147260,150344)


def Configurar():
    return QtGui.QIcon(pmConfigurar())


def pmS_Aceptar():
    return PM(134006,137353)


def S_Aceptar():
    return QtGui.QIcon(pmS_Aceptar())


def pmS_Cancelar():
    return PM(137353,139336)


def S_Cancelar():
    return QtGui.QIcon(pmS_Cancelar())


def pmS_Microfono():
    return PM(150344,155785)


def S_Microfono():
    return QtGui.QIcon(pmS_Microfono())


def pmS_LeerWav():
    return PM(46233,48833)


def S_LeerWav():
    return QtGui.QIcon(pmS_LeerWav())


def pmS_Play():
    return PM(155785,161123)


def S_Play():
    return QtGui.QIcon(pmS_Play())


def pmS_StopPlay():
    return PM(161123,161733)


def S_StopPlay():
    return QtGui.QIcon(pmS_StopPlay())


def pmS_StopMicrofono():
    return PM(161123,161733)


def S_StopMicrofono():
    return QtGui.QIcon(pmS_StopMicrofono())


def pmS_Record():
    return PM(161733,164966)


def S_Record():
    return QtGui.QIcon(pmS_Record())


def pmS_Limpiar():
    return PM(82698,87689)


def S_Limpiar():
    return QtGui.QIcon(pmS_Limpiar())


def pmHistorial():
    return PM(164966,166229)


def Historial():
    return QtGui.QIcon(pmHistorial())


def pmPegar16():
    return PM(166229,167223)


def Pegar16():
    return QtGui.QIcon(pmPegar16())


def pmRivalesMP():
    return PM(167223,169905)


def RivalesMP():
    return QtGui.QIcon(pmRivalesMP())


def pmCamara():
    return PM(169905,171427)


def Camara():
    return QtGui.QIcon(pmCamara())


def pmUsuarios():
    return PM(171427,172667)


def Usuarios():
    return QtGui.QIcon(pmUsuarios())


def pmResistencia():
    return PM(172667,175729)


def Resistencia():
    return QtGui.QIcon(pmResistencia())


def pmCebra():
    return PM(175729,178182)


def Cebra():
    return QtGui.QIcon(pmCebra())


def pmGafas():
    return PM(178182,179340)


def Gafas():
    return QtGui.QIcon(pmGafas())


def pmPuente():
    return PM(179340,179976)


def Puente():
    return QtGui.QIcon(pmPuente())


def pmWeb():
    return PM(179976,181158)


def Web():
    return QtGui.QIcon(pmWeb())


def pmMail():
    return PM(181158,182118)


def Mail():
    return QtGui.QIcon(pmMail())


def pmAyuda():
    return PM(182118,183299)


def Ayuda():
    return QtGui.QIcon(pmAyuda())


def pmFAQ():
    return PM(183299,184620)


def FAQ():
    return QtGui.QIcon(pmFAQ())


def pmActualiza():
    return PM(184620,185486)


def Actualiza():
    return QtGui.QIcon(pmActualiza())


def pmRefresh():
    return PM(185486,187878)


def Refresh():
    return QtGui.QIcon(pmRefresh())


def pmJuegaSolo():
    return PM(187878,189730)


def JuegaSolo():
    return QtGui.QIcon(pmJuegaSolo())


def pmPlayer():
    return PM(189730,190912)


def Player():
    return QtGui.QIcon(pmPlayer())


def pmJS_Rotacion():
    return PM(190912,192822)


def JS_Rotacion():
    return QtGui.QIcon(pmJS_Rotacion())


def pmElo():
    return PM(192822,194328)


def Elo():
    return QtGui.QIcon(pmElo())


def pmMate():
    return PM(194328,194889)


def Mate():
    return QtGui.QIcon(pmMate())


def pmEloTimed():
    return PM(194889,196373)


def EloTimed():
    return QtGui.QIcon(pmEloTimed())


def pmPGN():
    return PM(196373,198371)


def PGN():
    return QtGui.QIcon(pmPGN())


def pmPGN_Importar():
    return PM(198371,199961)


def PGN_Importar():
    return QtGui.QIcon(pmPGN_Importar())


def pmAyudaGR():
    return PM(199961,205839)


def AyudaGR():
    return QtGui.QIcon(pmAyudaGR())


def pmBotonAyuda():
    return PM(205839,208299)


def BotonAyuda():
    return QtGui.QIcon(pmBotonAyuda())


def pmColores():
    return PM(208299,209530)


def Colores():
    return QtGui.QIcon(pmColores())


def pmEditarColores():
    return PM(209530,211833)


def EditarColores():
    return QtGui.QIcon(pmEditarColores())


def pmGranMaestro():
    return PM(211833,212689)


def GranMaestro():
    return QtGui.QIcon(pmGranMaestro())


def pmFavoritos():
    return PM(212689,214455)


def Favoritos():
    return QtGui.QIcon(pmFavoritos())


def pmCarpeta():
    return PM(214455,215159)


def Carpeta():
    return QtGui.QIcon(pmCarpeta())


def pmDivision():
    return PM(215159,215824)


def Division():
    return QtGui.QIcon(pmDivision())


def pmDivisionF():
    return PM(215824,216938)


def DivisionF():
    return QtGui.QIcon(pmDivisionF())


def pmKibitzer():
    return PM(216938,217477)


def Kibitzer():
    return QtGui.QIcon(pmKibitzer())


def pmKibitzer_Pausa():
    return PM(217477,218341)


def Kibitzer_Pausa():
    return QtGui.QIcon(pmKibitzer_Pausa())


def pmKibitzer_Continuar():
    return PM(218341,219172)


def Kibitzer_Continuar():
    return QtGui.QIcon(pmKibitzer_Continuar())


def pmKibitzer_Terminar():
    return PM(219172,220096)


def Kibitzer_Terminar():
    return QtGui.QIcon(pmKibitzer_Terminar())


def pmDelete():
    return PM(219172,220096)


def Delete():
    return QtGui.QIcon(pmDelete())


def pmModificarP():
    return PM(220096,221162)


def ModificarP():
    return QtGui.QIcon(pmModificarP())


def pmGrupo_Si():
    return PM(221162,221624)


def Grupo_Si():
    return QtGui.QIcon(pmGrupo_Si())


def pmGrupo_No():
    return PM(221624,221947)


def Grupo_No():
    return QtGui.QIcon(pmGrupo_No())


def pmMotor_Si():
    return PM(221947,222409)


def Motor_Si():
    return QtGui.QIcon(pmMotor_Si())


def pmMotor_No():
    return PM(219172,220096)


def Motor_No():
    return QtGui.QIcon(pmMotor_No())


def pmMotor_Actual():
    return PM(222409,223426)


def Motor_Actual():
    return QtGui.QIcon(pmMotor_Actual())


def pmMotor():
    return PM(223426,224053)


def Motor():
    return QtGui.QIcon(pmMotor())


def pmMoverInicio():
    return PM(224053,224351)


def MoverInicio():
    return QtGui.QIcon(pmMoverInicio())


def pmMoverFinal():
    return PM(224351,224652)


def MoverFinal():
    return QtGui.QIcon(pmMoverFinal())


def pmMoverAdelante():
    return PM(224652,225007)


def MoverAdelante():
    return QtGui.QIcon(pmMoverAdelante())


def pmMoverAtras():
    return PM(225007,225372)


def MoverAtras():
    return QtGui.QIcon(pmMoverAtras())


def pmMoverLibre():
    return PM(225372,225762)


def MoverLibre():
    return QtGui.QIcon(pmMoverLibre())


def pmMoverTiempo():
    return PM(225762,226341)


def MoverTiempo():
    return QtGui.QIcon(pmMoverTiempo())


def pmMoverMas():
    return PM(226341,227380)


def MoverMas():
    return QtGui.QIcon(pmMoverMas())


def pmMoverGrabar():
    return PM(227380,228236)


def MoverGrabar():
    return QtGui.QIcon(pmMoverGrabar())


def pmMoverGrabarTodos():
    return PM(228236,229280)


def MoverGrabarTodos():
    return QtGui.QIcon(pmMoverGrabarTodos())


def pmMoverJugar():
    return PM(218341,219172)


def MoverJugar():
    return QtGui.QIcon(pmMoverJugar())


def pmPelicula():
    return PM(229280,231414)


def Pelicula():
    return QtGui.QIcon(pmPelicula())


def pmPelicula_Pausa():
    return PM(231414,233173)


def Pelicula_Pausa():
    return QtGui.QIcon(pmPelicula_Pausa())


def pmPelicula_Seguir():
    return PM(233173,235262)


def Pelicula_Seguir():
    return QtGui.QIcon(pmPelicula_Seguir())


def pmPelicula_Rapido():
    return PM(235262,237321)


def Pelicula_Rapido():
    return QtGui.QIcon(pmPelicula_Rapido())


def pmPelicula_Lento():
    return PM(237321,239196)


def Pelicula_Lento():
    return QtGui.QIcon(pmPelicula_Lento())


def pmPelicula_Repetir():
    return PM(38040,40334)


def Pelicula_Repetir():
    return QtGui.QIcon(pmPelicula_Repetir())


def pmPelicula_PGN():
    return PM(239196,240104)


def Pelicula_PGN():
    return QtGui.QIcon(pmPelicula_PGN())


def pmMemoria():
    return PM(240104,242045)


def Memoria():
    return QtGui.QIcon(pmMemoria())


def pmEntrenar():
    return PM(242045,243584)


def Entrenar():
    return QtGui.QIcon(pmEntrenar())


def pmEnviar():
    return PM(242045,243584)


def Enviar():
    return QtGui.QIcon(pmEnviar())


def pmBoxRooms():
    return PM(243584,248387)


def BoxRooms():
    return QtGui.QIcon(pmBoxRooms())


def pmBoxRoom():
    return PM(248387,248849)


def BoxRoom():
    return QtGui.QIcon(pmBoxRoom())


def pmNewBoxRoom():
    return PM(248849,250357)


def NewBoxRoom():
    return QtGui.QIcon(pmNewBoxRoom())


def pmNuevoMas():
    return PM(248849,250357)


def NuevoMas():
    return QtGui.QIcon(pmNuevoMas())


def pmTemas():
    return PM(250357,252580)


def Temas():
    return QtGui.QIcon(pmTemas())


def pmTutorialesCrear():
    return PM(252580,258849)


def TutorialesCrear():
    return QtGui.QIcon(pmTutorialesCrear())


def pmMover():
    return PM(258849,259431)


def Mover():
    return QtGui.QIcon(pmMover())


def pmSeleccionar():
    return PM(259431,265135)


def Seleccionar():
    return QtGui.QIcon(pmSeleccionar())


def pmVista():
    return PM(265135,267059)


def Vista():
    return QtGui.QIcon(pmVista())


def pmInformacionPGNUno():
    return PM(267059,268437)


def InformacionPGNUno():
    return QtGui.QIcon(pmInformacionPGNUno())


def pmDailyTest():
    return PM(268437,270777)


def DailyTest():
    return QtGui.QIcon(pmDailyTest())


def pmJuegaPorMi():
    return PM(270777,272497)


def JuegaPorMi():
    return QtGui.QIcon(pmJuegaPorMi())


def pmArbol():
    return PM(272497,273131)


def Arbol():
    return QtGui.QIcon(pmArbol())


def pmGrabarFichero():
    return PM(68134,69597)


def GrabarFichero():
    return QtGui.QIcon(pmGrabarFichero())


def pmClipboard():
    return PM(273131,273909)


def Clipboard():
    return QtGui.QIcon(pmClipboard())


def pmFics():
    return PM(273909,274326)


def Fics():
    return QtGui.QIcon(pmFics())


def pmFide():
    return PM(9646,11623)


def Fide():
    return QtGui.QIcon(pmFide())


def pmFichPGN():
    return PM(26140,27888)


def FichPGN():
    return QtGui.QIcon(pmFichPGN())


def pmFlechas():
    return PM(274326,277678)


def Flechas():
    return QtGui.QIcon(pmFlechas())


def pmMarcos():
    return PM(277678,279125)


def Marcos():
    return QtGui.QIcon(pmMarcos())


def pmSVGs():
    return PM(279125,282694)


def SVGs():
    return QtGui.QIcon(pmSVGs())


def pmAmarillo():
    return PM(282694,283946)


def Amarillo():
    return QtGui.QIcon(pmAmarillo())


def pmNaranja():
    return PM(283946,285178)


def Naranja():
    return QtGui.QIcon(pmNaranja())


def pmVerde():
    return PM(285178,286454)


def Verde():
    return QtGui.QIcon(pmVerde())


def pmAzul():
    return PM(286454,287542)


def Azul():
    return QtGui.QIcon(pmAzul())


def pmMagenta():
    return PM(287542,288830)


def Magenta():
    return QtGui.QIcon(pmMagenta())


def pmRojo():
    return PM(288830,290049)


def Rojo():
    return QtGui.QIcon(pmRojo())


def pmGris():
    return PM(290049,291007)


def Gris():
    return QtGui.QIcon(pmGris())


def pmAmarillo32():
    return PM(291007,292987)


def Amarillo32():
    return QtGui.QIcon(pmAmarillo32())


def pmNaranja32():
    return PM(292987,295111)


def Naranja32():
    return QtGui.QIcon(pmNaranja32())


def pmVerde32():
    return PM(295111,297232)


def Verde32():
    return QtGui.QIcon(pmVerde32())


def pmAzul32():
    return PM(297232,299611)


def Azul32():
    return QtGui.QIcon(pmAzul32())


def pmMagenta32():
    return PM(299611,302062)


def Magenta32():
    return QtGui.QIcon(pmMagenta32())


def pmRojo32():
    return PM(302062,303877)


def Rojo32():
    return QtGui.QIcon(pmRojo32())


def pmGris32():
    return PM(303877,305791)


def Gris32():
    return QtGui.QIcon(pmGris32())


def pmPuntoBlanco():
    return PM(305791,306140)


def PuntoBlanco():
    return QtGui.QIcon(pmPuntoBlanco())


def pmPuntoAmarillo():
    return PM(221162,221624)


def PuntoAmarillo():
    return QtGui.QIcon(pmPuntoAmarillo())


def pmPuntoNaranja():
    return PM(306140,306602)


def PuntoNaranja():
    return QtGui.QIcon(pmPuntoNaranja())


def pmPuntoVerde():
    return PM(221947,222409)


def PuntoVerde():
    return QtGui.QIcon(pmPuntoVerde())


def pmPuntoAzul():
    return PM(248387,248849)


def PuntoAzul():
    return QtGui.QIcon(pmPuntoAzul())


def pmPuntoMagenta():
    return PM(306602,307101)


def PuntoMagenta():
    return QtGui.QIcon(pmPuntoMagenta())


def pmPuntoRojo():
    return PM(307101,307600)


def PuntoRojo():
    return QtGui.QIcon(pmPuntoRojo())


def pmPuntoNegro():
    return PM(221624,221947)


def PuntoNegro():
    return QtGui.QIcon(pmPuntoNegro())


def pmPuntoEstrella():
    return PM(307600,308027)


def PuntoEstrella():
    return QtGui.QIcon(pmPuntoEstrella())


def pmComentario():
    return PM(308027,308664)


def Comentario():
    return QtGui.QIcon(pmComentario())


def pmComentarioMas():
    return PM(308664,309603)


def ComentarioMas():
    return QtGui.QIcon(pmComentarioMas())


def pmComentarioEditar():
    return PM(227380,228236)


def ComentarioEditar():
    return QtGui.QIcon(pmComentarioEditar())


def pmApertura():
    return PM(309603,310569)


def Apertura():
    return QtGui.QIcon(pmApertura())


def pmAperturaComentario():
    return PM(310569,311565)


def AperturaComentario():
    return QtGui.QIcon(pmAperturaComentario())


def pmMas():
    return PM(311565,312074)


def Mas():
    return QtGui.QIcon(pmMas())


def pmMasR():
    return PM(312074,312562)


def MasR():
    return QtGui.QIcon(pmMasR())


def pmMasDoc():
    return PM(312562,313363)


def MasDoc():
    return QtGui.QIcon(pmMasDoc())


def pmPotencia():
    return PM(184620,185486)


def Potencia():
    return QtGui.QIcon(pmPotencia())


def pmBMT():
    return PM(313363,314241)


def BMT():
    return QtGui.QIcon(pmBMT())


def pmOjo():
    return PM(314241,315363)


def Ojo():
    return QtGui.QIcon(pmOjo())


def pmOcultar():
    return PM(314241,315363)


def Ocultar():
    return QtGui.QIcon(pmOcultar())


def pmMostrar():
    return PM(315363,316419)


def Mostrar():
    return QtGui.QIcon(pmMostrar())


def pmBlog():
    return PM(316419,316941)


def Blog():
    return QtGui.QIcon(pmBlog())


def pmVariantes():
    return PM(316941,317848)


def Variantes():
    return QtGui.QIcon(pmVariantes())


def pmVariantesG():
    return PM(317848,320275)


def VariantesG():
    return QtGui.QIcon(pmVariantesG())


def pmCambiar():
    return PM(320275,321989)


def Cambiar():
    return QtGui.QIcon(pmCambiar())


def pmAnterior():
    return PM(321989,324043)


def Anterior():
    return QtGui.QIcon(pmAnterior())


def pmSiguiente():
    return PM(324043,326113)


def Siguiente():
    return QtGui.QIcon(pmSiguiente())


def pmSiguienteF():
    return PM(326113,328288)


def SiguienteF():
    return QtGui.QIcon(pmSiguienteF())


def pmAnteriorF():
    return PM(328288,330482)


def AnteriorF():
    return QtGui.QIcon(pmAnteriorF())


def pmX():
    return PM(330482,331764)


def X():
    return QtGui.QIcon(pmX())


def pmTools():
    return PM(331764,334365)


def Tools():
    return QtGui.QIcon(pmTools())


def pmTacticas():
    return PM(334365,336938)


def Tacticas():
    return QtGui.QIcon(pmTacticas())


def pmCancelarPeque():
    return PM(336938,337500)


def CancelarPeque():
    return QtGui.QIcon(pmCancelarPeque())


def pmAceptarPeque():
    return PM(222409,223426)


def AceptarPeque():
    return QtGui.QIcon(pmAceptarPeque())


def pmP_16c():
    return PM(337500,338024)


def P_16c():
    return QtGui.QIcon(pmP_16c())


def pmLibre():
    return PM(338024,340416)


def Libre():
    return QtGui.QIcon(pmLibre())


def pmEnBlanco():
    return PM(340416,341142)


def EnBlanco():
    return QtGui.QIcon(pmEnBlanco())


def pmDirector():
    return PM(341142,344116)


def Director():
    return QtGui.QIcon(pmDirector())


def pmTorneos():
    return PM(344116,345854)


def Torneos():
    return QtGui.QIcon(pmTorneos())


def pmAperturas():
    return PM(345854,346779)


def Aperturas():
    return QtGui.QIcon(pmAperturas())


def pmV_Blancas():
    return PM(346779,347059)


def V_Blancas():
    return QtGui.QIcon(pmV_Blancas())


def pmV_Blancas_Mas():
    return PM(347059,347339)


def V_Blancas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas())


def pmV_Blancas_Mas_Mas():
    return PM(347339,347611)


def V_Blancas_Mas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas_Mas())


def pmV_Negras():
    return PM(347611,347886)


def V_Negras():
    return QtGui.QIcon(pmV_Negras())


def pmV_Negras_Mas():
    return PM(347886,348161)


def V_Negras_Mas():
    return QtGui.QIcon(pmV_Negras_Mas())


def pmV_Negras_Mas_Mas():
    return PM(348161,348430)


def V_Negras_Mas_Mas():
    return QtGui.QIcon(pmV_Negras_Mas_Mas())


def pmV_Blancas_Igual_Negras():
    return PM(348430,348732)


def V_Blancas_Igual_Negras():
    return QtGui.QIcon(pmV_Blancas_Igual_Negras())


def pmMezclar():
    return PM(142655,145051)


def Mezclar():
    return QtGui.QIcon(pmMezclar())


def pmVoyager():
    return PM(348732,350694)


def Voyager():
    return QtGui.QIcon(pmVoyager())


def pmReindexar():
    return PM(350694,352511)


def Reindexar():
    return QtGui.QIcon(pmReindexar())


def pmRename():
    return PM(352511,353495)


def Rename():
    return QtGui.QIcon(pmRename())


def pmAdd():
    return PM(353495,354448)


def Add():
    return QtGui.QIcon(pmAdd())


def pmMas22():
    return PM(354448,355112)


def Mas22():
    return QtGui.QIcon(pmMas22())


def pmMenos22():
    return PM(355112,355556)


def Menos22():
    return QtGui.QIcon(pmMenos22())


def pmTransposition():
    return PM(355556,356075)


def Transposition():
    return QtGui.QIcon(pmTransposition())


def pmRat():
    return PM(356075,361779)


def Rat():
    return QtGui.QIcon(pmRat())


def pmAlligator():
    return PM(361779,366771)


def Alligator():
    return QtGui.QIcon(pmAlligator())


def pmAnt():
    return PM(366771,373469)


def Ant():
    return QtGui.QIcon(pmAnt())


def pmBat():
    return PM(373469,376423)


def Bat():
    return QtGui.QIcon(pmBat())


def pmBear():
    return PM(376423,383702)


def Bear():
    return QtGui.QIcon(pmBear())


def pmBee():
    return PM(383702,388704)


def Bee():
    return QtGui.QIcon(pmBee())


def pmBird():
    return PM(388704,394763)


def Bird():
    return QtGui.QIcon(pmBird())


def pmBull():
    return PM(394763,401732)


def Bull():
    return QtGui.QIcon(pmBull())


def pmBulldog():
    return PM(401732,408623)


def Bulldog():
    return QtGui.QIcon(pmBulldog())


def pmButterfly():
    return PM(408623,415997)


def Butterfly():
    return QtGui.QIcon(pmButterfly())


def pmCat():
    return PM(415997,422269)


def Cat():
    return QtGui.QIcon(pmCat())


def pmChicken():
    return PM(422269,428080)


def Chicken():
    return QtGui.QIcon(pmChicken())


def pmCow():
    return PM(428080,434823)


def Cow():
    return QtGui.QIcon(pmCow())


def pmCrab():
    return PM(434823,440412)


def Crab():
    return QtGui.QIcon(pmCrab())


def pmCrocodile():
    return PM(440412,446553)


def Crocodile():
    return QtGui.QIcon(pmCrocodile())


def pmDeer():
    return PM(446553,452860)


def Deer():
    return QtGui.QIcon(pmDeer())


def pmDog():
    return PM(452860,459463)


def Dog():
    return QtGui.QIcon(pmDog())


def pmDonkey():
    return PM(459463,465110)


def Donkey():
    return QtGui.QIcon(pmDonkey())


def pmDuck():
    return PM(465110,471653)


def Duck():
    return QtGui.QIcon(pmDuck())


def pmEagle():
    return PM(471653,476471)


def Eagle():
    return QtGui.QIcon(pmEagle())


def pmElephant():
    return PM(476471,482952)


def Elephant():
    return QtGui.QIcon(pmElephant())


def pmFish():
    return PM(482952,489793)


def Fish():
    return QtGui.QIcon(pmFish())


def pmFox():
    return PM(489793,496576)


def Fox():
    return QtGui.QIcon(pmFox())


def pmFrog():
    return PM(496576,502992)


def Frog():
    return QtGui.QIcon(pmFrog())


def pmGiraffe():
    return PM(502992,510170)


def Giraffe():
    return QtGui.QIcon(pmGiraffe())


def pmGorilla():
    return PM(510170,516709)


def Gorilla():
    return QtGui.QIcon(pmGorilla())


def pmHippo():
    return PM(516709,523830)


def Hippo():
    return QtGui.QIcon(pmHippo())


def pmHorse():
    return PM(523830,530377)


def Horse():
    return QtGui.QIcon(pmHorse())


def pmInsect():
    return PM(530377,536312)


def Insect():
    return QtGui.QIcon(pmInsect())


def pmLion():
    return PM(536312,545222)


def Lion():
    return QtGui.QIcon(pmLion())


def pmMonkey():
    return PM(545222,552901)


def Monkey():
    return QtGui.QIcon(pmMonkey())


def pmMoose():
    return PM(552901,559525)


def Moose():
    return QtGui.QIcon(pmMoose())


def pmMouse():
    return PM(356075,361779)


def Mouse():
    return QtGui.QIcon(pmMouse())


def pmOwl():
    return PM(559525,566231)


def Owl():
    return QtGui.QIcon(pmOwl())


def pmPanda():
    return PM(566231,570265)


def Panda():
    return QtGui.QIcon(pmPanda())


def pmPenguin():
    return PM(570265,575814)


def Penguin():
    return QtGui.QIcon(pmPenguin())


def pmPig():
    return PM(575814,583854)


def Pig():
    return QtGui.QIcon(pmPig())


def pmRabbit():
    return PM(583854,591155)


def Rabbit():
    return QtGui.QIcon(pmRabbit())


def pmRhino():
    return PM(591155,597542)


def Rhino():
    return QtGui.QIcon(pmRhino())


def pmRooster():
    return PM(597542,602805)


def Rooster():
    return QtGui.QIcon(pmRooster())


def pmShark():
    return PM(602805,608575)


def Shark():
    return QtGui.QIcon(pmShark())


def pmSheep():
    return PM(608575,612406)


def Sheep():
    return QtGui.QIcon(pmSheep())


def pmSnake():
    return PM(612406,618431)


def Snake():
    return QtGui.QIcon(pmSnake())


def pmTiger():
    return PM(618431,626468)


def Tiger():
    return QtGui.QIcon(pmTiger())


def pmTurkey():
    return PM(626468,633882)


def Turkey():
    return QtGui.QIcon(pmTurkey())


def pmTurtle():
    return PM(633882,640603)


def Turtle():
    return QtGui.QIcon(pmTurtle())


def pmWolf():
    return PM(640603,643698)


def Wolf():
    return QtGui.QIcon(pmWolf())


def pmSteven():
    return PM(643698,650850)


def Steven():
    return QtGui.QIcon(pmSteven())


def pmWheel():
    return PM(650850,658915)


def Wheel():
    return QtGui.QIcon(pmWheel())


def pmWheelchair():
    return PM(658915,667719)


def Wheelchair():
    return QtGui.QIcon(pmWheelchair())


def pmTouringMotorcycle():
    return PM(667719,674031)


def TouringMotorcycle():
    return QtGui.QIcon(pmTouringMotorcycle())


def pmContainer():
    return PM(674031,679366)


def Container():
    return QtGui.QIcon(pmContainer())


def pmBoatEquipment():
    return PM(679366,684889)


def BoatEquipment():
    return QtGui.QIcon(pmBoatEquipment())


def pmCar():
    return PM(684889,689535)


def Car():
    return QtGui.QIcon(pmCar())


def pmLorry():
    return PM(689535,695571)


def Lorry():
    return QtGui.QIcon(pmLorry())


def pmCarTrailer():
    return PM(695571,699668)


def CarTrailer():
    return QtGui.QIcon(pmCarTrailer())


def pmTowTruck():
    return PM(699668,704426)


def TowTruck():
    return QtGui.QIcon(pmTowTruck())


def pmQuadBike():
    return PM(704426,710395)


def QuadBike():
    return QtGui.QIcon(pmQuadBike())


def pmRecoveryTruck():
    return PM(710395,715392)


def RecoveryTruck():
    return QtGui.QIcon(pmRecoveryTruck())


def pmContainerLoader():
    return PM(715392,720534)


def ContainerLoader():
    return QtGui.QIcon(pmContainerLoader())


def pmPoliceCar():
    return PM(720534,725366)


def PoliceCar():
    return QtGui.QIcon(pmPoliceCar())


def pmExecutiveCar():
    return PM(725366,730044)


def ExecutiveCar():
    return QtGui.QIcon(pmExecutiveCar())


def pmTruck():
    return PM(730044,735507)


def Truck():
    return QtGui.QIcon(pmTruck())


def pmExcavator():
    return PM(735507,740398)


def Excavator():
    return QtGui.QIcon(pmExcavator())


def pmCabriolet():
    return PM(740398,745236)


def Cabriolet():
    return QtGui.QIcon(pmCabriolet())


def pmMixerTruck():
    return PM(745236,751546)


def MixerTruck():
    return QtGui.QIcon(pmMixerTruck())


def pmForkliftTruckLoaded():
    return PM(751546,757694)


def ForkliftTruckLoaded():
    return QtGui.QIcon(pmForkliftTruckLoaded())


def pmAmbulance():
    return PM(757694,763744)


def Ambulance():
    return QtGui.QIcon(pmAmbulance())


def pmDieselLocomotiveBoxcar():
    return PM(763744,767750)


def DieselLocomotiveBoxcar():
    return QtGui.QIcon(pmDieselLocomotiveBoxcar())


def pmTractorUnit():
    return PM(767750,773217)


def TractorUnit():
    return QtGui.QIcon(pmTractorUnit())


def pmFireTruck():
    return PM(773217,779556)


def FireTruck():
    return QtGui.QIcon(pmFireTruck())


def pmCargoShip():
    return PM(779556,783897)


def CargoShip():
    return QtGui.QIcon(pmCargoShip())


def pmSubwayTrain():
    return PM(783897,788787)


def SubwayTrain():
    return QtGui.QIcon(pmSubwayTrain())


def pmTruckMountedCrane():
    return PM(788787,794528)


def TruckMountedCrane():
    return QtGui.QIcon(pmTruckMountedCrane())


def pmAirAmbulance():
    return PM(794528,799641)


def AirAmbulance():
    return QtGui.QIcon(pmAirAmbulance())


def pmAirplane():
    return PM(799641,804529)


def Airplane():
    return QtGui.QIcon(pmAirplane())


def pmCaracol():
    return PM(804529,806345)


def Caracol():
    return QtGui.QIcon(pmCaracol())


def pmUno():
    return PM(806345,808807)


def Uno():
    return QtGui.QIcon(pmUno())


def pmMotoresExternos():
    return PM(808807,810709)


def MotoresExternos():
    return QtGui.QIcon(pmMotoresExternos())


def pmDatabase():
    return PM(810709,812025)


def Database():
    return QtGui.QIcon(pmDatabase())


def pmDatabaseMas():
    return PM(812025,813484)


def DatabaseMas():
    return QtGui.QIcon(pmDatabaseMas())


def pmDatabaseImport():
    return PM(813484,814120)


def DatabaseImport():
    return QtGui.QIcon(pmDatabaseImport())


def pmDatabaseExport():
    return PM(814120,814765)


def DatabaseExport():
    return QtGui.QIcon(pmDatabaseExport())


def pmDatabaseDelete():
    return PM(814765,815888)


def DatabaseDelete():
    return QtGui.QIcon(pmDatabaseDelete())


def pmDatabaseMaintenance():
    return PM(815888,817384)


def DatabaseMaintenance():
    return QtGui.QIcon(pmDatabaseMaintenance())


def pmAtacante():
    return PM(817384,817989)


def Atacante():
    return QtGui.QIcon(pmAtacante())


def pmAtacada():
    return PM(817989,818555)


def Atacada():
    return QtGui.QIcon(pmAtacada())


def pmGoToNext():
    return PM(818555,818967)


def GoToNext():
    return QtGui.QIcon(pmGoToNext())


def pmBlancas():
    return PM(818967,819318)


def Blancas():
    return QtGui.QIcon(pmBlancas())


def pmNegras():
    return PM(819318,819564)


def Negras():
    return QtGui.QIcon(pmNegras())


def pmFolderChange():
    return PM(71649,74407)


def FolderChange():
    return QtGui.QIcon(pmFolderChange())


def pmMarkers():
    return PM(819564,821259)


def Markers():
    return QtGui.QIcon(pmMarkers())


def pmTop():
    return PM(821259,821843)


def Top():
    return QtGui.QIcon(pmTop())


def pmBottom():
    return PM(821843,822432)


def Bottom():
    return QtGui.QIcon(pmBottom())


def pmSTS():
    return PM(822432,824623)


def STS():
    return QtGui.QIcon(pmSTS())


def pmRun():
    return PM(824623,826347)


def Run():
    return QtGui.QIcon(pmRun())


def pmRun2():
    return PM(826347,827867)


def Run2():
    return QtGui.QIcon(pmRun2())


def pmWorldMap():
    return PM(827867,830608)


def WorldMap():
    return QtGui.QIcon(pmWorldMap())


def pmAfrica():
    return PM(830608,833094)


def Africa():
    return QtGui.QIcon(pmAfrica())


def pmMaps():
    return PM(833094,834038)


def Maps():
    return QtGui.QIcon(pmMaps())


def pmSol():
    return PM(834038,834964)


def Sol():
    return QtGui.QIcon(pmSol())


def pmSolNubes():
    return PM(834964,835827)


def SolNubes():
    return QtGui.QIcon(pmSolNubes())


def pmSolNubesLluvia():
    return PM(835827,836787)


def SolNubesLluvia():
    return QtGui.QIcon(pmSolNubesLluvia())


def pmLluvia():
    return PM(836787,837626)


def Lluvia():
    return QtGui.QIcon(pmLluvia())


def pmInvierno():
    return PM(837626,839202)


def Invierno():
    return QtGui.QIcon(pmInvierno())


def pmFixedElo():
    return PM(164966,166229)


def FixedElo():
    return QtGui.QIcon(pmFixedElo())


def pmSoundTool():
    return PM(839202,841661)


def SoundTool():
    return QtGui.QIcon(pmSoundTool())


def pmVoyager1():
    return PM(841661,844111)


def Voyager1():
    return QtGui.QIcon(pmVoyager1())


def pmTrain():
    return PM(844111,845481)


def Train():
    return QtGui.QIcon(pmTrain())


def pmPlay():
    return PM(233173,235262)


def Play():
    return QtGui.QIcon(pmPlay())


def pmMeasure():
    return PM(126751,128374)


def Measure():
    return QtGui.QIcon(pmMeasure())


def pmPlayGame():
    return PM(845481,849839)


def PlayGame():
    return QtGui.QIcon(pmPlayGame())


def pmScanner():
    return PM(849839,850180)


def Scanner():
    return QtGui.QIcon(pmScanner())


def pmMenos():
    return PM(850180,850705)


def Menos():
    return QtGui.QIcon(pmMenos())


def pmSchool():
    return PM(850705,852067)


def School():
    return QtGui.QIcon(pmSchool())


def pmLaw():
    return PM(852067,852683)


def Law():
    return QtGui.QIcon(pmLaw())


def pmLearnGame():
    return PM(852683,853116)


def LearnGame():
    return QtGui.QIcon(pmLearnGame())


def pmLonghaul():
    return PM(853116,854042)


def Longhaul():
    return QtGui.QIcon(pmLonghaul())


def pmTrekking():
    return PM(854042,854736)


def Trekking():
    return QtGui.QIcon(pmTrekking())


def pmPassword():
    return PM(854736,855189)


def Password():
    return QtGui.QIcon(pmPassword())


def pmSQL_RAW():
    return PM(845481,849839)


def SQL_RAW():
    return QtGui.QIcon(pmSQL_RAW())


def pmSun():
    return PM(313363,314241)


def Sun():
    return QtGui.QIcon(pmSun())


def pmLight32():
    return PM(855189,856889)


def Light32():
    return QtGui.QIcon(pmLight32())


def pmTOL():
    return PM(856889,857598)


def TOL():
    return QtGui.QIcon(pmTOL())


def pmUned():
    return PM(857598,858018)


def Uned():
    return QtGui.QIcon(pmUned())


def pmUwe():
    return PM(858018,858987)


def Uwe():
    return QtGui.QIcon(pmUwe())


def pmThinking():
    return PM(858987,859776)


def Thinking():
    return QtGui.QIcon(pmThinking())


def pmWashingMachine():
    return PM(859776,860439)


def WashingMachine():
    return QtGui.QIcon(pmWashingMachine())


def pmTerminal():
    return PM(860439,863983)


def Terminal():
    return QtGui.QIcon(pmTerminal())


def pmManualSave():
    return PM(863983,864566)


def ManualSave():
    return QtGui.QIcon(pmManualSave())


def pmSettings():
    return PM(864566,865004)


def Settings():
    return QtGui.QIcon(pmSettings())


def pmStrength():
    return PM(865004,865675)


def Strength():
    return QtGui.QIcon(pmStrength())


def pmSingular():
    return PM(865675,866530)


def Singular():
    return QtGui.QIcon(pmSingular())


def pmScript():
    return PM(866530,867099)


def Script():
    return QtGui.QIcon(pmScript())


def pmTexto():
    return PM(867099,869944)


def Texto():
    return QtGui.QIcon(pmTexto())


def pmLampara():
    return PM(869944,870653)


def Lampara():
    return QtGui.QIcon(pmLampara())


def pmFile():
    return PM(870653,872953)


def File():
    return QtGui.QIcon(pmFile())


def pmCalculo():
    return PM(872953,873879)


def Calculo():
    return QtGui.QIcon(pmCalculo())


def pmOpeningLines():
    return PM(873879,874557)


def OpeningLines():
    return QtGui.QIcon(pmOpeningLines())


def pmStudy():
    return PM(874557,875470)


def Study():
    return QtGui.QIcon(pmStudy())


def pmLichess():
    return PM(875470,876360)


def Lichess():
    return QtGui.QIcon(pmLichess())


def pmMiniatura():
    return PM(876360,877287)


def Miniatura():
    return QtGui.QIcon(pmMiniatura())


def pmLocomotora():
    return PM(877287,878068)


def Locomotora():
    return QtGui.QIcon(pmLocomotora())


def pmTrainSequential():
    return PM(878068,879209)


def TrainSequential():
    return QtGui.QIcon(pmTrainSequential())


def pmTrainStatic():
    return PM(879209,880169)


def TrainStatic():
    return QtGui.QIcon(pmTrainStatic())


def pmTrainPositions():
    return PM(880169,881150)


def TrainPositions():
    return QtGui.QIcon(pmTrainPositions())


def pmTrainEngines():
    return PM(881150,882584)


def TrainEngines():
    return QtGui.QIcon(pmTrainEngines())


def pmError():
    return PM(48833,52833)


def Error():
    return QtGui.QIcon(pmError())


def pmAtajos():
    return PM(882584,883763)


def Atajos():
    return QtGui.QIcon(pmAtajos())


def pmTOLline():
    return PM(883763,884867)


def TOLline():
    return QtGui.QIcon(pmTOLline())


def pmTOLchange():
    return PM(884867,887089)


def TOLchange():
    return QtGui.QIcon(pmTOLchange())


def pmPack():
    return PM(887089,888262)


def Pack():
    return QtGui.QIcon(pmPack())


def pmHome():
    return PM(179976,181158)


def Home():
    return QtGui.QIcon(pmHome())


def pmImport8():
    return PM(888262,889020)


def Import8():
    return QtGui.QIcon(pmImport8())


def pmExport8():
    return PM(889020,889645)


def Export8():
    return QtGui.QIcon(pmExport8())


def pmTablas8():
    return PM(889645,890437)


def Tablas8():
    return QtGui.QIcon(pmTablas8())


def pmBlancas8():
    return PM(890437,891467)


def Blancas8():
    return QtGui.QIcon(pmBlancas8())


def pmNegras8():
    return PM(891467,892306)


def Negras8():
    return QtGui.QIcon(pmNegras8())


def pmBook():
    return PM(892306,892880)


def Book():
    return QtGui.QIcon(pmBook())


def pmWrite():
    return PM(892880,894085)


def Write():
    return QtGui.QIcon(pmWrite())


def pmAlt():
    return PM(894085,894527)


def Alt():
    return QtGui.QIcon(pmAlt())


def pmShift():
    return PM(894527,894867)


def Shift():
    return QtGui.QIcon(pmShift())


def pmRightMouse():
    return PM(894867,895667)


def RightMouse():
    return QtGui.QIcon(pmRightMouse())


def pmControl():
    return PM(895667,896192)


def Control():
    return QtGui.QIcon(pmControl())


def pmFinales():
    return PM(896192,897279)


def Finales():
    return QtGui.QIcon(pmFinales())


def pmEditColumns():
    return PM(897279,898011)


def EditColumns():
    return QtGui.QIcon(pmEditColumns())


def pmResizeAll():
    return PM(898011,898521)


def ResizeAll():
    return QtGui.QIcon(pmResizeAll())


def pmChecked():
    return PM(898521,899027)


def Checked():
    return QtGui.QIcon(pmChecked())


def pmUnchecked():
    return PM(899027,899275)


def Unchecked():
    return QtGui.QIcon(pmUnchecked())


def pmBuscarC():
    return PM(899275,899719)


def BuscarC():
    return QtGui.QIcon(pmBuscarC())


def pmPeonBlanco():
    return PM(899719,901900)


def PeonBlanco():
    return QtGui.QIcon(pmPeonBlanco())


def pmPeonNegro():
    return PM(901900,903424)


def PeonNegro():
    return QtGui.QIcon(pmPeonNegro())


def pmReciclar():
    return PM(903424,904148)


def Reciclar():
    return QtGui.QIcon(pmReciclar())


def pmLanzamiento():
    return PM(904148,904861)


def Lanzamiento():
    return QtGui.QIcon(pmLanzamiento())


def pmEndGame():
    return PM(904861,905275)


def EndGame():
    return QtGui.QIcon(pmEndGame())


def pmPause():
    return PM(905275,906144)


def Pause():
    return QtGui.QIcon(pmPause())


def pmContinue():
    return PM(906144,907348)


def Continue():
    return QtGui.QIcon(pmContinue())


def pmClose():
    return PM(907348,908047)


def Close():
    return QtGui.QIcon(pmClose())


def pmStop():
    return PM(908047,909080)


def Stop():
    return QtGui.QIcon(pmStop())


def pmFactoryPolyglot():
    return PM(909080,909900)


def FactoryPolyglot():
    return QtGui.QIcon(pmFactoryPolyglot())


def pmTags():
    return PM(909900,910723)


def Tags():
    return QtGui.QIcon(pmTags())


def pmAppearance():
    return PM(910723,911450)


def Appearance():
    return QtGui.QIcon(pmAppearance())


def pmFill():
    return PM(911450,912488)


def Fill():
    return QtGui.QIcon(pmFill())


def pmSupport():
    return PM(912488,913220)


def Support():
    return QtGui.QIcon(pmSupport())


def pmOrder():
    return PM(913220,914018)


def Order():
    return QtGui.QIcon(pmOrder())


def pmPlay1():
    return PM(914018,915313)


def Play1():
    return QtGui.QIcon(pmPlay1())


def pmRemove1():
    return PM(915313,916440)


def Remove1():
    return QtGui.QIcon(pmRemove1())


def pmNew1():
    return PM(916440,916762)


def New1():
    return QtGui.QIcon(pmNew1())


def pmMensError():
    return PM(916762,918826)


def MensError():
    return QtGui.QIcon(pmMensError())


def pmMensInfo():
    return PM(918826,921381)


def MensInfo():
    return QtGui.QIcon(pmMensInfo())


def pmJump():
    return PM(921381,922056)


def Jump():
    return QtGui.QIcon(pmJump())


def pmCaptures():
    return PM(922056,923237)


def Captures():
    return QtGui.QIcon(pmCaptures())


def pmRepeat():
    return PM(923237,923896)


def Repeat():
    return QtGui.QIcon(pmRepeat())


def pmCount():
    return PM(923896,924572)


def Count():
    return QtGui.QIcon(pmCount())


def pmMate15():
    return PM(924572,925643)


def Mate15():
    return QtGui.QIcon(pmMate15())


def pmCoordinates():
    return PM(925643,926796)


def Coordinates():
    return QtGui.QIcon(pmCoordinates())


def pmKnight():
    return PM(926796,928039)


def Knight():
    return QtGui.QIcon(pmKnight())


def pmCorrecto():
    return PM(928039,929065)


def Correcto():
    return QtGui.QIcon(pmCorrecto())


def pmBlocks():
    return PM(929065,929402)


def Blocks():
    return QtGui.QIcon(pmBlocks())


def pmWest():
    return PM(929402,930508)


def West():
    return QtGui.QIcon(pmWest())


