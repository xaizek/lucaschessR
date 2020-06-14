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
    return PM(178182,179166)


def Gafas():
    return QtGui.QIcon(pmGafas())


def pmPuente():
    return PM(179166,179802)


def Puente():
    return QtGui.QIcon(pmPuente())


def pmWeb():
    return PM(179802,180984)


def Web():
    return QtGui.QIcon(pmWeb())


def pmMail():
    return PM(180984,181944)


def Mail():
    return QtGui.QIcon(pmMail())


def pmAyuda():
    return PM(181944,183125)


def Ayuda():
    return QtGui.QIcon(pmAyuda())


def pmFAQ():
    return PM(183125,184446)


def FAQ():
    return QtGui.QIcon(pmFAQ())


def pmActualiza():
    return PM(184446,185312)


def Actualiza():
    return QtGui.QIcon(pmActualiza())


def pmRefresh():
    return PM(185312,187704)


def Refresh():
    return QtGui.QIcon(pmRefresh())


def pmJuegaSolo():
    return PM(187704,189556)


def JuegaSolo():
    return QtGui.QIcon(pmJuegaSolo())


def pmPlayer():
    return PM(189556,190738)


def Player():
    return QtGui.QIcon(pmPlayer())


def pmJS_Rotacion():
    return PM(190738,192648)


def JS_Rotacion():
    return QtGui.QIcon(pmJS_Rotacion())


def pmElo():
    return PM(192648,194154)


def Elo():
    return QtGui.QIcon(pmElo())


def pmMate():
    return PM(194154,194715)


def Mate():
    return QtGui.QIcon(pmMate())


def pmEloTimed():
    return PM(194715,196199)


def EloTimed():
    return QtGui.QIcon(pmEloTimed())


def pmPGN():
    return PM(196199,198197)


def PGN():
    return QtGui.QIcon(pmPGN())


def pmPGN_Importar():
    return PM(198197,199787)


def PGN_Importar():
    return QtGui.QIcon(pmPGN_Importar())


def pmAyudaGR():
    return PM(199787,205665)


def AyudaGR():
    return QtGui.QIcon(pmAyudaGR())


def pmBotonAyuda():
    return PM(205665,208125)


def BotonAyuda():
    return QtGui.QIcon(pmBotonAyuda())


def pmColores():
    return PM(208125,209356)


def Colores():
    return QtGui.QIcon(pmColores())


def pmEditarColores():
    return PM(209356,211659)


def EditarColores():
    return QtGui.QIcon(pmEditarColores())


def pmGranMaestro():
    return PM(211659,212515)


def GranMaestro():
    return QtGui.QIcon(pmGranMaestro())


def pmFavoritos():
    return PM(212515,214281)


def Favoritos():
    return QtGui.QIcon(pmFavoritos())


def pmCarpeta():
    return PM(214281,214985)


def Carpeta():
    return QtGui.QIcon(pmCarpeta())


def pmDivision():
    return PM(214985,215650)


def Division():
    return QtGui.QIcon(pmDivision())


def pmDivisionF():
    return PM(215650,216764)


def DivisionF():
    return QtGui.QIcon(pmDivisionF())


def pmKibitzer():
    return PM(216764,217303)


def Kibitzer():
    return QtGui.QIcon(pmKibitzer())


def pmKibitzer_Pausa():
    return PM(217303,218167)


def Kibitzer_Pausa():
    return QtGui.QIcon(pmKibitzer_Pausa())


def pmKibitzer_Continuar():
    return PM(218167,218998)


def Kibitzer_Continuar():
    return QtGui.QIcon(pmKibitzer_Continuar())


def pmKibitzer_Terminar():
    return PM(218998,219922)


def Kibitzer_Terminar():
    return QtGui.QIcon(pmKibitzer_Terminar())


def pmDelete():
    return PM(218998,219922)


def Delete():
    return QtGui.QIcon(pmDelete())


def pmModificarP():
    return PM(219922,220988)


def ModificarP():
    return QtGui.QIcon(pmModificarP())


def pmGrupo_Si():
    return PM(220988,221450)


def Grupo_Si():
    return QtGui.QIcon(pmGrupo_Si())


def pmGrupo_No():
    return PM(221450,221773)


def Grupo_No():
    return QtGui.QIcon(pmGrupo_No())


def pmMotor_Si():
    return PM(221773,222235)


def Motor_Si():
    return QtGui.QIcon(pmMotor_Si())


def pmMotor_No():
    return PM(218998,219922)


def Motor_No():
    return QtGui.QIcon(pmMotor_No())


def pmMotor_Actual():
    return PM(222235,223252)


def Motor_Actual():
    return QtGui.QIcon(pmMotor_Actual())


def pmMotor():
    return PM(223252,223879)


def Motor():
    return QtGui.QIcon(pmMotor())


def pmMoverInicio():
    return PM(223879,224177)


def MoverInicio():
    return QtGui.QIcon(pmMoverInicio())


def pmMoverFinal():
    return PM(224177,224478)


def MoverFinal():
    return QtGui.QIcon(pmMoverFinal())


def pmMoverAdelante():
    return PM(224478,224833)


def MoverAdelante():
    return QtGui.QIcon(pmMoverAdelante())


def pmMoverAtras():
    return PM(224833,225198)


def MoverAtras():
    return QtGui.QIcon(pmMoverAtras())


def pmMoverLibre():
    return PM(225198,225588)


def MoverLibre():
    return QtGui.QIcon(pmMoverLibre())


def pmMoverTiempo():
    return PM(225588,226167)


def MoverTiempo():
    return QtGui.QIcon(pmMoverTiempo())


def pmMoverMas():
    return PM(226167,227206)


def MoverMas():
    return QtGui.QIcon(pmMoverMas())


def pmMoverGrabar():
    return PM(227206,228062)


def MoverGrabar():
    return QtGui.QIcon(pmMoverGrabar())


def pmMoverGrabarTodos():
    return PM(228062,229106)


def MoverGrabarTodos():
    return QtGui.QIcon(pmMoverGrabarTodos())


def pmMoverJugar():
    return PM(218167,218998)


def MoverJugar():
    return QtGui.QIcon(pmMoverJugar())


def pmPelicula():
    return PM(229106,231240)


def Pelicula():
    return QtGui.QIcon(pmPelicula())


def pmPelicula_Pausa():
    return PM(231240,232999)


def Pelicula_Pausa():
    return QtGui.QIcon(pmPelicula_Pausa())


def pmPelicula_Seguir():
    return PM(232999,235088)


def Pelicula_Seguir():
    return QtGui.QIcon(pmPelicula_Seguir())


def pmPelicula_Rapido():
    return PM(235088,237147)


def Pelicula_Rapido():
    return QtGui.QIcon(pmPelicula_Rapido())


def pmPelicula_Lento():
    return PM(237147,239022)


def Pelicula_Lento():
    return QtGui.QIcon(pmPelicula_Lento())


def pmPelicula_Repetir():
    return PM(38040,40334)


def Pelicula_Repetir():
    return QtGui.QIcon(pmPelicula_Repetir())


def pmPelicula_PGN():
    return PM(239022,239930)


def Pelicula_PGN():
    return QtGui.QIcon(pmPelicula_PGN())


def pmMemoria():
    return PM(239930,241871)


def Memoria():
    return QtGui.QIcon(pmMemoria())


def pmEntrenar():
    return PM(241871,243410)


def Entrenar():
    return QtGui.QIcon(pmEntrenar())


def pmEnviar():
    return PM(241871,243410)


def Enviar():
    return QtGui.QIcon(pmEnviar())


def pmBoxRooms():
    return PM(243410,248213)


def BoxRooms():
    return QtGui.QIcon(pmBoxRooms())


def pmBoxRoom():
    return PM(248213,248675)


def BoxRoom():
    return QtGui.QIcon(pmBoxRoom())


def pmNewBoxRoom():
    return PM(248675,250183)


def NewBoxRoom():
    return QtGui.QIcon(pmNewBoxRoom())


def pmNuevoMas():
    return PM(248675,250183)


def NuevoMas():
    return QtGui.QIcon(pmNuevoMas())


def pmTemas():
    return PM(250183,252406)


def Temas():
    return QtGui.QIcon(pmTemas())


def pmTutorialesCrear():
    return PM(252406,258675)


def TutorialesCrear():
    return QtGui.QIcon(pmTutorialesCrear())


def pmMover():
    return PM(258675,259257)


def Mover():
    return QtGui.QIcon(pmMover())


def pmSeleccionar():
    return PM(259257,264961)


def Seleccionar():
    return QtGui.QIcon(pmSeleccionar())


def pmVista():
    return PM(264961,266885)


def Vista():
    return QtGui.QIcon(pmVista())


def pmInformacionPGNUno():
    return PM(266885,268263)


def InformacionPGNUno():
    return QtGui.QIcon(pmInformacionPGNUno())


def pmDailyTest():
    return PM(268263,270603)


def DailyTest():
    return QtGui.QIcon(pmDailyTest())


def pmJuegaPorMi():
    return PM(270603,272323)


def JuegaPorMi():
    return QtGui.QIcon(pmJuegaPorMi())


def pmArbol():
    return PM(272323,272957)


def Arbol():
    return QtGui.QIcon(pmArbol())


def pmGrabarFichero():
    return PM(68134,69597)


def GrabarFichero():
    return QtGui.QIcon(pmGrabarFichero())


def pmClipboard():
    return PM(272957,273735)


def Clipboard():
    return QtGui.QIcon(pmClipboard())


def pmFics():
    return PM(273735,274152)


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
    return PM(274152,277504)


def Flechas():
    return QtGui.QIcon(pmFlechas())


def pmMarcos():
    return PM(277504,278951)


def Marcos():
    return QtGui.QIcon(pmMarcos())


def pmSVGs():
    return PM(278951,282520)


def SVGs():
    return QtGui.QIcon(pmSVGs())


def pmAmarillo():
    return PM(282520,283772)


def Amarillo():
    return QtGui.QIcon(pmAmarillo())


def pmNaranja():
    return PM(283772,285004)


def Naranja():
    return QtGui.QIcon(pmNaranja())


def pmVerde():
    return PM(285004,286280)


def Verde():
    return QtGui.QIcon(pmVerde())


def pmAzul():
    return PM(286280,287368)


def Azul():
    return QtGui.QIcon(pmAzul())


def pmMagenta():
    return PM(287368,288656)


def Magenta():
    return QtGui.QIcon(pmMagenta())


def pmRojo():
    return PM(288656,289875)


def Rojo():
    return QtGui.QIcon(pmRojo())


def pmGris():
    return PM(289875,290833)


def Gris():
    return QtGui.QIcon(pmGris())


def pmAmarillo32():
    return PM(290833,292813)


def Amarillo32():
    return QtGui.QIcon(pmAmarillo32())


def pmNaranja32():
    return PM(292813,294937)


def Naranja32():
    return QtGui.QIcon(pmNaranja32())


def pmVerde32():
    return PM(294937,297058)


def Verde32():
    return QtGui.QIcon(pmVerde32())


def pmAzul32():
    return PM(297058,299437)


def Azul32():
    return QtGui.QIcon(pmAzul32())


def pmMagenta32():
    return PM(299437,301888)


def Magenta32():
    return QtGui.QIcon(pmMagenta32())


def pmRojo32():
    return PM(301888,303703)


def Rojo32():
    return QtGui.QIcon(pmRojo32())


def pmGris32():
    return PM(303703,305617)


def Gris32():
    return QtGui.QIcon(pmGris32())


def pmPuntoBlanco():
    return PM(305617,305966)


def PuntoBlanco():
    return QtGui.QIcon(pmPuntoBlanco())


def pmPuntoAmarillo():
    return PM(220988,221450)


def PuntoAmarillo():
    return QtGui.QIcon(pmPuntoAmarillo())


def pmPuntoNaranja():
    return PM(305966,306428)


def PuntoNaranja():
    return QtGui.QIcon(pmPuntoNaranja())


def pmPuntoVerde():
    return PM(221773,222235)


def PuntoVerde():
    return QtGui.QIcon(pmPuntoVerde())


def pmPuntoAzul():
    return PM(248213,248675)


def PuntoAzul():
    return QtGui.QIcon(pmPuntoAzul())


def pmPuntoMagenta():
    return PM(306428,306927)


def PuntoMagenta():
    return QtGui.QIcon(pmPuntoMagenta())


def pmPuntoRojo():
    return PM(306927,307426)


def PuntoRojo():
    return QtGui.QIcon(pmPuntoRojo())


def pmPuntoNegro():
    return PM(221450,221773)


def PuntoNegro():
    return QtGui.QIcon(pmPuntoNegro())


def pmPuntoEstrella():
    return PM(307426,307853)


def PuntoEstrella():
    return QtGui.QIcon(pmPuntoEstrella())


def pmComentario():
    return PM(307853,308490)


def Comentario():
    return QtGui.QIcon(pmComentario())


def pmComentarioMas():
    return PM(308490,309429)


def ComentarioMas():
    return QtGui.QIcon(pmComentarioMas())


def pmComentarioEditar():
    return PM(227206,228062)


def ComentarioEditar():
    return QtGui.QIcon(pmComentarioEditar())


def pmApertura():
    return PM(309429,310395)


def Apertura():
    return QtGui.QIcon(pmApertura())


def pmAperturaComentario():
    return PM(310395,311391)


def AperturaComentario():
    return QtGui.QIcon(pmAperturaComentario())


def pmMas():
    return PM(311391,311900)


def Mas():
    return QtGui.QIcon(pmMas())


def pmMasR():
    return PM(311900,312388)


def MasR():
    return QtGui.QIcon(pmMasR())


def pmMasDoc():
    return PM(312388,313189)


def MasDoc():
    return QtGui.QIcon(pmMasDoc())


def pmPotencia():
    return PM(184446,185312)


def Potencia():
    return QtGui.QIcon(pmPotencia())


def pmBMT():
    return PM(313189,314067)


def BMT():
    return QtGui.QIcon(pmBMT())


def pmOjo():
    return PM(314067,315189)


def Ojo():
    return QtGui.QIcon(pmOjo())


def pmOcultar():
    return PM(314067,315189)


def Ocultar():
    return QtGui.QIcon(pmOcultar())


def pmMostrar():
    return PM(315189,316245)


def Mostrar():
    return QtGui.QIcon(pmMostrar())


def pmBlog():
    return PM(316245,316767)


def Blog():
    return QtGui.QIcon(pmBlog())


def pmVariantes():
    return PM(316767,317674)


def Variantes():
    return QtGui.QIcon(pmVariantes())


def pmVariantesG():
    return PM(317674,320101)


def VariantesG():
    return QtGui.QIcon(pmVariantesG())


def pmCambiar():
    return PM(320101,321815)


def Cambiar():
    return QtGui.QIcon(pmCambiar())


def pmAnterior():
    return PM(321815,323869)


def Anterior():
    return QtGui.QIcon(pmAnterior())


def pmSiguiente():
    return PM(323869,325939)


def Siguiente():
    return QtGui.QIcon(pmSiguiente())


def pmSiguienteF():
    return PM(325939,328114)


def SiguienteF():
    return QtGui.QIcon(pmSiguienteF())


def pmAnteriorF():
    return PM(328114,330308)


def AnteriorF():
    return QtGui.QIcon(pmAnteriorF())


def pmX():
    return PM(330308,331590)


def X():
    return QtGui.QIcon(pmX())


def pmTools():
    return PM(331590,334191)


def Tools():
    return QtGui.QIcon(pmTools())


def pmTacticas():
    return PM(334191,336764)


def Tacticas():
    return QtGui.QIcon(pmTacticas())


def pmCancelarPeque():
    return PM(336764,337326)


def CancelarPeque():
    return QtGui.QIcon(pmCancelarPeque())


def pmAceptarPeque():
    return PM(222235,223252)


def AceptarPeque():
    return QtGui.QIcon(pmAceptarPeque())


def pmP_16c():
    return PM(337326,337850)


def P_16c():
    return QtGui.QIcon(pmP_16c())


def pmLibre():
    return PM(337850,340242)


def Libre():
    return QtGui.QIcon(pmLibre())


def pmEnBlanco():
    return PM(340242,340968)


def EnBlanco():
    return QtGui.QIcon(pmEnBlanco())


def pmDirector():
    return PM(340968,343942)


def Director():
    return QtGui.QIcon(pmDirector())


def pmTorneos():
    return PM(343942,345680)


def Torneos():
    return QtGui.QIcon(pmTorneos())


def pmAperturas():
    return PM(345680,346605)


def Aperturas():
    return QtGui.QIcon(pmAperturas())


def pmV_Blancas():
    return PM(346605,346885)


def V_Blancas():
    return QtGui.QIcon(pmV_Blancas())


def pmV_Blancas_Mas():
    return PM(346885,347165)


def V_Blancas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas())


def pmV_Blancas_Mas_Mas():
    return PM(347165,347437)


def V_Blancas_Mas_Mas():
    return QtGui.QIcon(pmV_Blancas_Mas_Mas())


def pmV_Negras():
    return PM(347437,347712)


def V_Negras():
    return QtGui.QIcon(pmV_Negras())


def pmV_Negras_Mas():
    return PM(347712,347987)


def V_Negras_Mas():
    return QtGui.QIcon(pmV_Negras_Mas())


def pmV_Negras_Mas_Mas():
    return PM(347987,348256)


def V_Negras_Mas_Mas():
    return QtGui.QIcon(pmV_Negras_Mas_Mas())


def pmV_Blancas_Igual_Negras():
    return PM(348256,348558)


def V_Blancas_Igual_Negras():
    return QtGui.QIcon(pmV_Blancas_Igual_Negras())


def pmMezclar():
    return PM(142655,145051)


def Mezclar():
    return QtGui.QIcon(pmMezclar())


def pmVoyager():
    return PM(348558,350520)


def Voyager():
    return QtGui.QIcon(pmVoyager())


def pmReindexar():
    return PM(350520,352337)


def Reindexar():
    return QtGui.QIcon(pmReindexar())


def pmRename():
    return PM(352337,353321)


def Rename():
    return QtGui.QIcon(pmRename())


def pmAdd():
    return PM(353321,354274)


def Add():
    return QtGui.QIcon(pmAdd())


def pmMas22():
    return PM(354274,354938)


def Mas22():
    return QtGui.QIcon(pmMas22())


def pmMenos22():
    return PM(354938,355382)


def Menos22():
    return QtGui.QIcon(pmMenos22())


def pmTransposition():
    return PM(355382,355901)


def Transposition():
    return QtGui.QIcon(pmTransposition())


def pmRat():
    return PM(355901,361605)


def Rat():
    return QtGui.QIcon(pmRat())


def pmAlligator():
    return PM(361605,366597)


def Alligator():
    return QtGui.QIcon(pmAlligator())


def pmAnt():
    return PM(366597,373295)


def Ant():
    return QtGui.QIcon(pmAnt())


def pmBat():
    return PM(373295,376249)


def Bat():
    return QtGui.QIcon(pmBat())


def pmBear():
    return PM(376249,383528)


def Bear():
    return QtGui.QIcon(pmBear())


def pmBee():
    return PM(383528,388530)


def Bee():
    return QtGui.QIcon(pmBee())


def pmBird():
    return PM(388530,394589)


def Bird():
    return QtGui.QIcon(pmBird())


def pmBull():
    return PM(394589,401558)


def Bull():
    return QtGui.QIcon(pmBull())


def pmBulldog():
    return PM(401558,408449)


def Bulldog():
    return QtGui.QIcon(pmBulldog())


def pmButterfly():
    return PM(408449,415823)


def Butterfly():
    return QtGui.QIcon(pmButterfly())


def pmCat():
    return PM(415823,422095)


def Cat():
    return QtGui.QIcon(pmCat())


def pmChicken():
    return PM(422095,427906)


def Chicken():
    return QtGui.QIcon(pmChicken())


def pmCow():
    return PM(427906,434649)


def Cow():
    return QtGui.QIcon(pmCow())


def pmCrab():
    return PM(434649,440238)


def Crab():
    return QtGui.QIcon(pmCrab())


def pmCrocodile():
    return PM(440238,446379)


def Crocodile():
    return QtGui.QIcon(pmCrocodile())


def pmDeer():
    return PM(446379,452686)


def Deer():
    return QtGui.QIcon(pmDeer())


def pmDog():
    return PM(452686,459289)


def Dog():
    return QtGui.QIcon(pmDog())


def pmDonkey():
    return PM(459289,464936)


def Donkey():
    return QtGui.QIcon(pmDonkey())


def pmDuck():
    return PM(464936,471479)


def Duck():
    return QtGui.QIcon(pmDuck())


def pmEagle():
    return PM(471479,476297)


def Eagle():
    return QtGui.QIcon(pmEagle())


def pmElephant():
    return PM(476297,482778)


def Elephant():
    return QtGui.QIcon(pmElephant())


def pmFish():
    return PM(482778,489619)


def Fish():
    return QtGui.QIcon(pmFish())


def pmFox():
    return PM(489619,496402)


def Fox():
    return QtGui.QIcon(pmFox())


def pmFrog():
    return PM(496402,502818)


def Frog():
    return QtGui.QIcon(pmFrog())


def pmGiraffe():
    return PM(502818,509996)


def Giraffe():
    return QtGui.QIcon(pmGiraffe())


def pmGorilla():
    return PM(509996,516535)


def Gorilla():
    return QtGui.QIcon(pmGorilla())


def pmHippo():
    return PM(516535,523656)


def Hippo():
    return QtGui.QIcon(pmHippo())


def pmHorse():
    return PM(523656,530203)


def Horse():
    return QtGui.QIcon(pmHorse())


def pmInsect():
    return PM(530203,536138)


def Insect():
    return QtGui.QIcon(pmInsect())


def pmLion():
    return PM(536138,545048)


def Lion():
    return QtGui.QIcon(pmLion())


def pmMonkey():
    return PM(545048,552727)


def Monkey():
    return QtGui.QIcon(pmMonkey())


def pmMoose():
    return PM(552727,559351)


def Moose():
    return QtGui.QIcon(pmMoose())


def pmMouse():
    return PM(355901,361605)


def Mouse():
    return QtGui.QIcon(pmMouse())


def pmOwl():
    return PM(559351,566057)


def Owl():
    return QtGui.QIcon(pmOwl())


def pmPanda():
    return PM(566057,570091)


def Panda():
    return QtGui.QIcon(pmPanda())


def pmPenguin():
    return PM(570091,575640)


def Penguin():
    return QtGui.QIcon(pmPenguin())


def pmPig():
    return PM(575640,583680)


def Pig():
    return QtGui.QIcon(pmPig())


def pmRabbit():
    return PM(583680,590981)


def Rabbit():
    return QtGui.QIcon(pmRabbit())


def pmRhino():
    return PM(590981,597368)


def Rhino():
    return QtGui.QIcon(pmRhino())


def pmRooster():
    return PM(597368,602631)


def Rooster():
    return QtGui.QIcon(pmRooster())


def pmShark():
    return PM(602631,608401)


def Shark():
    return QtGui.QIcon(pmShark())


def pmSheep():
    return PM(608401,612232)


def Sheep():
    return QtGui.QIcon(pmSheep())


def pmSnake():
    return PM(612232,618257)


def Snake():
    return QtGui.QIcon(pmSnake())


def pmTiger():
    return PM(618257,626294)


def Tiger():
    return QtGui.QIcon(pmTiger())


def pmTurkey():
    return PM(626294,633708)


def Turkey():
    return QtGui.QIcon(pmTurkey())


def pmTurtle():
    return PM(633708,640429)


def Turtle():
    return QtGui.QIcon(pmTurtle())


def pmWolf():
    return PM(640429,643524)


def Wolf():
    return QtGui.QIcon(pmWolf())


def pmSteven():
    return PM(643524,650676)


def Steven():
    return QtGui.QIcon(pmSteven())


def pmWheel():
    return PM(650676,658741)


def Wheel():
    return QtGui.QIcon(pmWheel())


def pmWheelchair():
    return PM(658741,667545)


def Wheelchair():
    return QtGui.QIcon(pmWheelchair())


def pmTouringMotorcycle():
    return PM(667545,673857)


def TouringMotorcycle():
    return QtGui.QIcon(pmTouringMotorcycle())


def pmContainer():
    return PM(673857,679192)


def Container():
    return QtGui.QIcon(pmContainer())


def pmBoatEquipment():
    return PM(679192,684715)


def BoatEquipment():
    return QtGui.QIcon(pmBoatEquipment())


def pmCar():
    return PM(684715,689361)


def Car():
    return QtGui.QIcon(pmCar())


def pmLorry():
    return PM(689361,695397)


def Lorry():
    return QtGui.QIcon(pmLorry())


def pmCarTrailer():
    return PM(695397,699494)


def CarTrailer():
    return QtGui.QIcon(pmCarTrailer())


def pmTowTruck():
    return PM(699494,704252)


def TowTruck():
    return QtGui.QIcon(pmTowTruck())


def pmQuadBike():
    return PM(704252,710221)


def QuadBike():
    return QtGui.QIcon(pmQuadBike())


def pmRecoveryTruck():
    return PM(710221,715218)


def RecoveryTruck():
    return QtGui.QIcon(pmRecoveryTruck())


def pmContainerLoader():
    return PM(715218,720360)


def ContainerLoader():
    return QtGui.QIcon(pmContainerLoader())


def pmPoliceCar():
    return PM(720360,725192)


def PoliceCar():
    return QtGui.QIcon(pmPoliceCar())


def pmExecutiveCar():
    return PM(725192,729870)


def ExecutiveCar():
    return QtGui.QIcon(pmExecutiveCar())


def pmTruck():
    return PM(729870,735333)


def Truck():
    return QtGui.QIcon(pmTruck())


def pmExcavator():
    return PM(735333,740224)


def Excavator():
    return QtGui.QIcon(pmExcavator())


def pmCabriolet():
    return PM(740224,745062)


def Cabriolet():
    return QtGui.QIcon(pmCabriolet())


def pmMixerTruck():
    return PM(745062,751372)


def MixerTruck():
    return QtGui.QIcon(pmMixerTruck())


def pmForkliftTruckLoaded():
    return PM(751372,757520)


def ForkliftTruckLoaded():
    return QtGui.QIcon(pmForkliftTruckLoaded())


def pmAmbulance():
    return PM(757520,763570)


def Ambulance():
    return QtGui.QIcon(pmAmbulance())


def pmDieselLocomotiveBoxcar():
    return PM(763570,767576)


def DieselLocomotiveBoxcar():
    return QtGui.QIcon(pmDieselLocomotiveBoxcar())


def pmTractorUnit():
    return PM(767576,773043)


def TractorUnit():
    return QtGui.QIcon(pmTractorUnit())


def pmFireTruck():
    return PM(773043,779382)


def FireTruck():
    return QtGui.QIcon(pmFireTruck())


def pmCargoShip():
    return PM(779382,783723)


def CargoShip():
    return QtGui.QIcon(pmCargoShip())


def pmSubwayTrain():
    return PM(783723,788613)


def SubwayTrain():
    return QtGui.QIcon(pmSubwayTrain())


def pmTruckMountedCrane():
    return PM(788613,794354)


def TruckMountedCrane():
    return QtGui.QIcon(pmTruckMountedCrane())


def pmAirAmbulance():
    return PM(794354,799467)


def AirAmbulance():
    return QtGui.QIcon(pmAirAmbulance())


def pmAirplane():
    return PM(799467,804355)


def Airplane():
    return QtGui.QIcon(pmAirplane())


def pmCaracol():
    return PM(804355,806171)


def Caracol():
    return QtGui.QIcon(pmCaracol())


def pmUno():
    return PM(806171,808633)


def Uno():
    return QtGui.QIcon(pmUno())


def pmMotoresExternos():
    return PM(808633,810535)


def MotoresExternos():
    return QtGui.QIcon(pmMotoresExternos())


def pmDatabase():
    return PM(810535,811851)


def Database():
    return QtGui.QIcon(pmDatabase())


def pmDatabaseMas():
    return PM(811851,813310)


def DatabaseMas():
    return QtGui.QIcon(pmDatabaseMas())


def pmDatabaseImport():
    return PM(813310,813946)


def DatabaseImport():
    return QtGui.QIcon(pmDatabaseImport())


def pmDatabaseExport():
    return PM(813946,814591)


def DatabaseExport():
    return QtGui.QIcon(pmDatabaseExport())


def pmDatabaseDelete():
    return PM(814591,815714)


def DatabaseDelete():
    return QtGui.QIcon(pmDatabaseDelete())


def pmDatabaseMaintenance():
    return PM(815714,817210)


def DatabaseMaintenance():
    return QtGui.QIcon(pmDatabaseMaintenance())


def pmAtacante():
    return PM(817210,817815)


def Atacante():
    return QtGui.QIcon(pmAtacante())


def pmAtacada():
    return PM(817815,818381)


def Atacada():
    return QtGui.QIcon(pmAtacada())


def pmGoToNext():
    return PM(818381,818793)


def GoToNext():
    return QtGui.QIcon(pmGoToNext())


def pmBlancas():
    return PM(818793,819144)


def Blancas():
    return QtGui.QIcon(pmBlancas())


def pmNegras():
    return PM(819144,819390)


def Negras():
    return QtGui.QIcon(pmNegras())


def pmFolderChange():
    return PM(71649,74407)


def FolderChange():
    return QtGui.QIcon(pmFolderChange())


def pmMarkers():
    return PM(819390,821085)


def Markers():
    return QtGui.QIcon(pmMarkers())


def pmTop():
    return PM(821085,821669)


def Top():
    return QtGui.QIcon(pmTop())


def pmBottom():
    return PM(821669,822258)


def Bottom():
    return QtGui.QIcon(pmBottom())


def pmSTS():
    return PM(822258,824449)


def STS():
    return QtGui.QIcon(pmSTS())


def pmRun():
    return PM(824449,826173)


def Run():
    return QtGui.QIcon(pmRun())


def pmRun2():
    return PM(826173,827693)


def Run2():
    return QtGui.QIcon(pmRun2())


def pmWorldMap():
    return PM(827693,830434)


def WorldMap():
    return QtGui.QIcon(pmWorldMap())


def pmAfrica():
    return PM(830434,832920)


def Africa():
    return QtGui.QIcon(pmAfrica())


def pmMaps():
    return PM(832920,833864)


def Maps():
    return QtGui.QIcon(pmMaps())


def pmSol():
    return PM(833864,834790)


def Sol():
    return QtGui.QIcon(pmSol())


def pmSolNubes():
    return PM(834790,835653)


def SolNubes():
    return QtGui.QIcon(pmSolNubes())


def pmSolNubesLluvia():
    return PM(835653,836613)


def SolNubesLluvia():
    return QtGui.QIcon(pmSolNubesLluvia())


def pmLluvia():
    return PM(836613,837452)


def Lluvia():
    return QtGui.QIcon(pmLluvia())


def pmInvierno():
    return PM(837452,839028)


def Invierno():
    return QtGui.QIcon(pmInvierno())


def pmFixedElo():
    return PM(164966,166229)


def FixedElo():
    return QtGui.QIcon(pmFixedElo())


def pmSoundTool():
    return PM(839028,841487)


def SoundTool():
    return QtGui.QIcon(pmSoundTool())


def pmVoyager1():
    return PM(841487,843937)


def Voyager1():
    return QtGui.QIcon(pmVoyager1())


def pmTrain():
    return PM(843937,845307)


def Train():
    return QtGui.QIcon(pmTrain())


def pmPlay():
    return PM(232999,235088)


def Play():
    return QtGui.QIcon(pmPlay())


def pmMeasure():
    return PM(126751,128374)


def Measure():
    return QtGui.QIcon(pmMeasure())


def pmPlayGame():
    return PM(845307,849665)


def PlayGame():
    return QtGui.QIcon(pmPlayGame())


def pmScanner():
    return PM(849665,850006)


def Scanner():
    return QtGui.QIcon(pmScanner())


def pmMenos():
    return PM(850006,850531)


def Menos():
    return QtGui.QIcon(pmMenos())


def pmSchool():
    return PM(850531,851072)


def School():
    return QtGui.QIcon(pmSchool())


def pmLaw():
    return PM(851072,851688)


def Law():
    return QtGui.QIcon(pmLaw())


def pmLearnGame():
    return PM(851688,852121)


def LearnGame():
    return QtGui.QIcon(pmLearnGame())


def pmLonghaul():
    return PM(852121,853047)


def Longhaul():
    return QtGui.QIcon(pmLonghaul())


def pmTrekking():
    return PM(853047,853741)


def Trekking():
    return QtGui.QIcon(pmTrekking())


def pmPassword():
    return PM(853741,854194)


def Password():
    return QtGui.QIcon(pmPassword())


def pmSQL_RAW():
    return PM(845307,849665)


def SQL_RAW():
    return QtGui.QIcon(pmSQL_RAW())


def pmSun():
    return PM(313189,314067)


def Sun():
    return QtGui.QIcon(pmSun())


def pmLight32():
    return PM(854194,855894)


def Light32():
    return QtGui.QIcon(pmLight32())


def pmTOL():
    return PM(855894,856603)


def TOL():
    return QtGui.QIcon(pmTOL())


def pmUned():
    return PM(856603,857023)


def Uned():
    return QtGui.QIcon(pmUned())


def pmUwe():
    return PM(857023,857992)


def Uwe():
    return QtGui.QIcon(pmUwe())


def pmThinking():
    return PM(857992,858781)


def Thinking():
    return QtGui.QIcon(pmThinking())


def pmWashingMachine():
    return PM(858781,859444)


def WashingMachine():
    return QtGui.QIcon(pmWashingMachine())


def pmTerminal():
    return PM(859444,862988)


def Terminal():
    return QtGui.QIcon(pmTerminal())


def pmManualSave():
    return PM(862988,863571)


def ManualSave():
    return QtGui.QIcon(pmManualSave())


def pmSettings():
    return PM(863571,864009)


def Settings():
    return QtGui.QIcon(pmSettings())


def pmStrength():
    return PM(864009,864680)


def Strength():
    return QtGui.QIcon(pmStrength())


def pmSingular():
    return PM(864680,865535)


def Singular():
    return QtGui.QIcon(pmSingular())


def pmScript():
    return PM(865535,866104)


def Script():
    return QtGui.QIcon(pmScript())


def pmTexto():
    return PM(866104,868949)


def Texto():
    return QtGui.QIcon(pmTexto())


def pmLampara():
    return PM(868949,869658)


def Lampara():
    return QtGui.QIcon(pmLampara())


def pmFile():
    return PM(869658,871958)


def File():
    return QtGui.QIcon(pmFile())


def pmCalculo():
    return PM(871958,872884)


def Calculo():
    return QtGui.QIcon(pmCalculo())


def pmOpeningLines():
    return PM(872884,873562)


def OpeningLines():
    return QtGui.QIcon(pmOpeningLines())


def pmStudy():
    return PM(873562,874475)


def Study():
    return QtGui.QIcon(pmStudy())


def pmLichess():
    return PM(874475,875365)


def Lichess():
    return QtGui.QIcon(pmLichess())


def pmMiniatura():
    return PM(875365,876292)


def Miniatura():
    return QtGui.QIcon(pmMiniatura())


def pmLocomotora():
    return PM(876292,877073)


def Locomotora():
    return QtGui.QIcon(pmLocomotora())


def pmTrainSequential():
    return PM(877073,878214)


def TrainSequential():
    return QtGui.QIcon(pmTrainSequential())


def pmTrainStatic():
    return PM(878214,879174)


def TrainStatic():
    return QtGui.QIcon(pmTrainStatic())


def pmTrainPositions():
    return PM(879174,880155)


def TrainPositions():
    return QtGui.QIcon(pmTrainPositions())


def pmTrainEngines():
    return PM(880155,881589)


def TrainEngines():
    return QtGui.QIcon(pmTrainEngines())


def pmError():
    return PM(48833,52833)


def Error():
    return QtGui.QIcon(pmError())


def pmAtajos():
    return PM(881589,882768)


def Atajos():
    return QtGui.QIcon(pmAtajos())


def pmTOLline():
    return PM(882768,883872)


def TOLline():
    return QtGui.QIcon(pmTOLline())


def pmTOLchange():
    return PM(883872,886094)


def TOLchange():
    return QtGui.QIcon(pmTOLchange())


def pmPack():
    return PM(886094,887267)


def Pack():
    return QtGui.QIcon(pmPack())


def pmHome():
    return PM(179802,180984)


def Home():
    return QtGui.QIcon(pmHome())


def pmImport8():
    return PM(887267,888025)


def Import8():
    return QtGui.QIcon(pmImport8())


def pmExport8():
    return PM(888025,888650)


def Export8():
    return QtGui.QIcon(pmExport8())


def pmTablas8():
    return PM(888650,889442)


def Tablas8():
    return QtGui.QIcon(pmTablas8())


def pmBlancas8():
    return PM(889442,890472)


def Blancas8():
    return QtGui.QIcon(pmBlancas8())


def pmNegras8():
    return PM(890472,891311)


def Negras8():
    return QtGui.QIcon(pmNegras8())


def pmBook():
    return PM(891311,891885)


def Book():
    return QtGui.QIcon(pmBook())


def pmWrite():
    return PM(891885,892791)


def Write():
    return QtGui.QIcon(pmWrite())


def pmAlt():
    return PM(892791,893233)


def Alt():
    return QtGui.QIcon(pmAlt())


def pmShift():
    return PM(893233,893573)


def Shift():
    return QtGui.QIcon(pmShift())


def pmRightMouse():
    return PM(893573,894373)


def RightMouse():
    return QtGui.QIcon(pmRightMouse())


def pmControl():
    return PM(894373,894898)


def Control():
    return QtGui.QIcon(pmControl())


def pmFinales():
    return PM(894898,895985)


def Finales():
    return QtGui.QIcon(pmFinales())


def pmEditColumns():
    return PM(895985,896717)


def EditColumns():
    return QtGui.QIcon(pmEditColumns())


def pmResizeAll():
    return PM(896717,897227)


def ResizeAll():
    return QtGui.QIcon(pmResizeAll())


def pmChecked():
    return PM(897227,897733)


def Checked():
    return QtGui.QIcon(pmChecked())


def pmUnchecked():
    return PM(897733,897981)


def Unchecked():
    return QtGui.QIcon(pmUnchecked())


def pmBuscarC():
    return PM(897981,898425)


def BuscarC():
    return QtGui.QIcon(pmBuscarC())


def pmPeonBlanco():
    return PM(898425,900606)


def PeonBlanco():
    return QtGui.QIcon(pmPeonBlanco())


def pmPeonNegro():
    return PM(900606,902130)


def PeonNegro():
    return QtGui.QIcon(pmPeonNegro())


def pmReciclar():
    return PM(902130,902854)


def Reciclar():
    return QtGui.QIcon(pmReciclar())


def pmLanzamiento():
    return PM(902854,903567)


def Lanzamiento():
    return QtGui.QIcon(pmLanzamiento())


def pmEndGame():
    return PM(903567,903981)


def EndGame():
    return QtGui.QIcon(pmEndGame())


def pmPause():
    return PM(903981,904850)


def Pause():
    return QtGui.QIcon(pmPause())


def pmContinue():
    return PM(904850,906054)


def Continue():
    return QtGui.QIcon(pmContinue())


def pmClose():
    return PM(906054,906753)


def Close():
    return QtGui.QIcon(pmClose())


def pmStop():
    return PM(906753,907786)


def Stop():
    return QtGui.QIcon(pmStop())


def pmFactoryPolyglot():
    return PM(907786,908606)


def FactoryPolyglot():
    return QtGui.QIcon(pmFactoryPolyglot())


def pmTags():
    return PM(908606,909429)


def Tags():
    return QtGui.QIcon(pmTags())


def pmAppearance():
    return PM(909429,910156)


def Appearance():
    return QtGui.QIcon(pmAppearance())


def pmFill():
    return PM(910156,911194)


def Fill():
    return QtGui.QIcon(pmFill())


def pmSupport():
    return PM(911194,911926)


def Support():
    return QtGui.QIcon(pmSupport())


def pmOrder():
    return PM(911926,912724)


def Order():
    return QtGui.QIcon(pmOrder())


def pmPlay1():
    return PM(912724,914019)


def Play1():
    return QtGui.QIcon(pmPlay1())


def pmRemove1():
    return PM(914019,915146)


def Remove1():
    return QtGui.QIcon(pmRemove1())


def pmNew1():
    return PM(915146,915468)


def New1():
    return QtGui.QIcon(pmNew1())


def pmMensError():
    return PM(915468,917532)


def MensError():
    return QtGui.QIcon(pmMensError())


def pmMensInfo():
    return PM(917532,920087)


def MensInfo():
    return QtGui.QIcon(pmMensInfo())


def pmJump():
    return PM(920087,920762)


def Jump():
    return QtGui.QIcon(pmJump())


def pmCaptures():
    return PM(920762,921889)


def Captures():
    return QtGui.QIcon(pmCaptures())


def pmRepeat():
    return PM(921889,922548)


def Repeat():
    return QtGui.QIcon(pmRepeat())


def pmCount():
    return PM(922548,923078)


def Count():
    return QtGui.QIcon(pmCount())


def pmMate15():
    return PM(923078,924164)


def Mate15():
    return QtGui.QIcon(pmMate15())


