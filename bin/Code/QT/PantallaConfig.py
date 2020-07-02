from PySide2 import QtCore

from Code import DGT

from Code.QT import FormLayout
from Code.QT import Iconos
from Code import Util
from Code.Constantes import *


def opciones(parent, configuracion):
    form = FormLayout.FormLayout(parent, _("Configuration"), Iconos.Opciones(), anchoMinimo=640)

    # Datos generales ##############################################################################################
    form.separador()

    form.edit(_("Player's name"), configuracion.x_player)
    form.separador()
    form.combobox(_("Window style"), configuracion.estilos(), configuracion.x_style)
    form.separador()

    liTraducciones = configuracion.list_translations()
    trActual = configuracion.translator()
    li = []
    for k, trad, porc, author in liTraducciones:
        rotulo = "%s" % trad
        if int(porc) < 90:
            rotulo += " (%s%%)" % porc
        li.append((rotulo, k))
    form.combobox(_("Language"), li, trActual)
    form.separador()

    li = [
        (_("Play against an engine"), MENU_PLAY_ANY_ENGINE),
        (_("Opponents for young players"), MENU_PLAY_YOUNG_PLAYERS),
        (_("Both"), MENU_PLAY_BOTH),
    ]
    form.combobox(_("Menu Play"), li, configuracion.x_menu_play)
    form.separador()

    form.checkbox(_("Check for updates at startup"), configuracion.x_check_for_update)

    form.add_tab(_("General"))

    # Sonidos ########################################################################################################
    form.separador()
    form.checkbox(_("Beep after opponent's move"), configuracion.x_sound_beep)
    form.separador()
    form.apart(_("Sound on in"))
    form.checkbox(_("Results"), configuracion.x_sound_results)
    form.checkbox(_("Rival moves"), configuracion.x_sound_move)
    form.separador()
    form.checkbox(_("Activate sounds with our moves") + ":", configuracion.x_sound_our)

    form.add_tab(_("Sounds"))

    # Tutor ##########################################################################################################
    form.separador()
    form.combobox(_("Engine"), configuracion.listaCambioTutor(), configuracion.tutor.clave)
    form.float(_("Duration of tutor analysis (secs)"), float(configuracion.x_tutor_mstime / 1000.0))
    form.spinbox(_("Depth"), 0, 40, 100, configuracion.x_tutor_depth)

    form.spinbox(_("Number of moves evaluated by engine(MultiPV)"), 0, 512, 100, configuracion.x_tutor_multipv)
    form.separador()
    form.checkbox(_("Tutor enabled"), configuracion.x_default_tutor_active)

    liPosTutor = [
        (_("Horizontal"), POS_TUTOR_HORIZONTAL),
        (_("Horizontal") + " 2+1", POS_TUTOR_HORIZONTAL_2_1),
        (_("Horizontal") + " 1+2", POS_TUTOR_HORIZONTAL_1_2),
        (_("Vertical"), POS_TUTOR_VERTICAL),
    ]
    form.combobox(_("Tutor boards position"), liPosTutor, configuracion.x_tutor_view)
    form.separador()
    form.separador()
    form.apart(_("Sensitivity"))
    form.spinbox(_("Minimum difference in centipawns"), 0, 1000, 70, configuracion.x_tutor_difpoints)
    form.spinbox(_("Minimum difference in %"), 0, 1000, 70, configuracion.x_tutor_difporc)

    form.add_tab(_("Tutor"))

    # Engines #####################################################################################################
    form.separador()
    form.checkbox(_("Work in the background, when possible"), not configuracion.x_engine_notbackground)
    form.separador()
    form.checkbox("%s -> %s:" % (_("Save engines log"), "UserData/EngineLogs"), configuracion.x_log_engines)
    form.separador()
    form.folder(_("Gaviota Tablebases"), configuracion.x_carpeta_gaviota, configuracion.carpeta_gaviota_defecto())
    form.separador()

    form.add_tab(_("Engines"))

    # Boards #########################################################################################################
    form.separador()
    form.checkbox(_("Visual effects"), configuracion.x_show_effects)

    drap = {1: 100, 2: 150, 3: 200, 4: 250, 5: 300, 6: 350, 7: 400, 8: 450, 9: 500}
    drapV = {}
    for x in drap:
        drapV[drap[x]] = x
    form.dial(
        "%s (%s=1)" % (_("Speed"), _("Default")),
        1,
        len(drap),
        drapV.get(configuracion.x_pieces_speed, 100),
        siporc=False,
    )
    form.separador()

    liMouseSH = [
        (_("Type fixed: you must always indicate origin and destination"), False),
        (_("Type predictive: program tries to guess your intention"), True),
    ]
    form.combobox(_("Mouse shortcuts"), liMouseSH, configuracion.x_mouse_shortcuts)
    form.checkbox(_("Show candidates"), configuracion.x_show_candidates)
    form.checkbox(_("Always promote to queen\nALT key allows to change"), configuracion.x_autopromotion_q)
    form.checkbox(_("Show cursor when engine is thinking"), configuracion.x_cursor_thinking)
    form.separador()
    form.checkbox(_("Enable captured material window by default"), configuracion.x_captures_activate)
    # liMat = [
    #     (_("Difference material"), "D"),
    #     (_("Captured material at beginning"), "C"),
    #     (_("Material advantage"), "M"),
    # ]
    # form.combobox(_("Show material"), liMat, configuracion.x_capture_option)
    form.separador()
    form.checkbox(_("Enable information panel by default"), configuracion.x_info_activate)
    form.separador()
    liDB = [(_("None"), ""), (_("DGT"), "DGT"), (_("Novag") + " - %s" % _("developed by Graham O'Neill"), "NOVAG")]
    form.combobox(_("Digital board"), liDB, configuracion.x_digital_board)
    form.separador()
    form.checkbox(_("Show configuracion icon"), configuracion.x_opacity_tool_board > 6)
    liPos = [(_("Bottom"), "B"), (_("Top"), "T")]
    form.combobox(_("Configuration icon position"), liPos, configuracion.x_position_tool_board)
    form.separador()
    form.checkbox(_("Show icon when position has graphic information"), configuracion.x_director_icon)
    form.separador()
    form.checkbox(_("Live graphics with the right mouse button"), configuracion.x_direct_graphics)

    form.add_tab(_("Boards"))

    # Aspect ########################################################################################################
    form.checkbox(_("By default"), False)
    form.separador()
    form.font(_("Font"), configuracion.x_font_family)

    form.apart(_("Menus"))
    form.spinbox(_("Font size"), 5, 64, 60, configuracion.x_menu_points)
    form.checkbox(_("Bold"), configuracion.x_menu_bold)

    form.separador()
    form.apart(_("Toolbars"))
    form.spinbox(_("Font size"), 5, 64, 60, configuracion.x_tb_fontpoints)
    form.checkbox(_("Bold"), configuracion.x_tb_bold)
    li = (
        (_("Only display the icon"), QtCore.Qt.ToolButtonIconOnly),
        (_("Only display the text"), QtCore.Qt.ToolButtonTextOnly),
        (_("The text appears beside the icon"), QtCore.Qt.ToolButtonTextBesideIcon),
        (_("The text appears under the icon"), QtCore.Qt.ToolButtonTextUnderIcon),
    )
    form.combobox(_("Icons"), li, configuracion.tipoIconos())

    form.separador()
    form.apart(_("PGN table"))
    form.spinbox(_("Width"), 283, 1000, 70, configuracion.x_pgn_width)
    form.spinbox(_("Height of each row"), 18, 99, 70, configuracion.x_pgn_rowheight)
    form.spinbox(_("Font size"), 10, 99, 70, configuracion.x_pgn_fontpoints)
    form.checkbox(_("PGN always in English"), configuracion.x_pgn_english)
    form.checkbox(_("PGN with figurines"), configuracion.x_pgn_withfigurines)
    form.separador()

    form.spinbox(_("Font size of information labels"), 8, 30, 70, configuracion.x_sizefont_infolabels)

    form.add_tab(_("Appearance"))

    # Perfomance ####################################################################################################
    perf = configuracion.perfomance

    def d(num):
        return " (%s %d)" % (_("default"), num)

    form.separador()
    form.apart(_("Bad moves: lost points to consider a move as bad"))
    form.spinbox(_("Bad move") + d(90), 20, 1000, 60, perf.bad_lostp)
    form.spinbox(_("Very bad move") + d(200), 50, 1000, 60, perf.very_bad_lostp)
    form.separador()
    form.spinbox(_("Degree of effect of bad moves on the game elo") + d(2), 0, 5, 40, perf.bad_factor)
    form.separador()
    form.apart(_("Good moves: minimum depth required by the engine to discover the move"))
    form.spinbox(_("Good move") + d(3), 2, 20, 40, perf.good_depth)
    form.spinbox(_("Very good move") + d(6), 3, 20, 40, perf.very_good_depth)

    form.add_tab(_("Performance"))

    # Salvado automatico #############################################################################################
    form.separador()
    form.file(_("Autosave to a PGN file"), "pgn", True, configuracion.x_salvar_pgn)
    form.checkbox(_("Won games"), configuracion.x_salvar_ganados)
    form.checkbox(_("Lost/Drawn games"), configuracion.x_salvar_perdidos)
    form.checkbox(_("Unfinished games"), configuracion.x_salvar_abandonados)
    form.separador()
    form.checkbox(_("Save as variation tutor's suggestion"), configuracion.x_save_tutor_variations)
    form.separador()
    form.file(_("Autosave to a CSV file moves played"), "csv", True, configuracion.x_salvar_csv)

    form.add_tab(_("Autosave"))

    # Modo no competitivo ############################################################################################
    form.separador()
    form.spinbox(_("Lucas-Elo"), 0, 3200, 70, configuracion.x_elo)
    form.separador()
    form.spinbox(_("Tourney-Elo"), 0, 3200, 70, configuracion.x_michelo)
    form.separador()
    form.spinbox(_("Fics-Elo"), 0, 3200, 70, configuracion.x_fics)
    form.separador()
    form.spinbox(_("Fide-Elo"), 0, 3200, 70, configuracion.x_fide)
    form.separador()
    form.spinbox(_("Lichess-Elo"), 0, 3200, 70, configuracion.x_lichess)

    form.add_tab(_("Change elos"))

    resultado = form.run()

    if resultado:
        accion, resp = resultado

        liGen, liSon, liTT, liEng, liB, liAsp, liPR, liSA, liNC = resp

        (
            configuracion.x_player,
            configuracion.x_style,
            translator,
            configuracion.x_menu_play,
            configuracion.x_check_for_update,
        ) = liGen

        configuracion.set_translator(translator)

        porDefecto = liAsp[0]
        if porDefecto:
            liAsp = "", 11, False, 11, False, QtCore.Qt.ToolButtonTextUnderIcon, 283, 22, 10, False, True, 10
        else:
            del liAsp[0]
        (
            configuracion.x_font_family,
            configuracion.x_menu_points,
            configuracion.x_menu_bold,
            configuracion.x_tb_fontpoints,
            configuracion.x_tb_bold,
            qt_iconstb,
            configuracion.x_pgn_width,
            configuracion.x_pgn_rowheight,
            configuracion.x_pgn_fontpoints,
            configuracion.x_pgn_english,
            configuracion.x_pgn_withfigurines,
            configuracion.x_sizefont_infolabels,
        ) = liAsp
        if configuracion.x_font_family == "System":
            configuracion.x_font_family = ""

        configuracion.set_tipoIconos(qt_iconstb)

        (
            configuracion.x_sound_beep,
            configuracion.x_sound_results,
            configuracion.x_sound_move,
            configuracion.x_sound_our,
        ) = liSon

        (
            configuracion.x_tutor_clave,
            tiempoTutor,
            configuracion.x_tutor_depth,
            configuracion.x_tutor_multipv,
            configuracion.x_default_tutor_active,
            configuracion.x_tutor_view,
            configuracion.x_tutor_difpoints,
            configuracion.x_tutor_difporc,
        ) = liTT
        configuracion.x_tutor_mstime = int(tiempoTutor * 1000)

        (
            configuracion.x_elo,
            configuracion.x_michelo,
            configuracion.x_fics,
            configuracion.x_fide,
            configuracion.x_lichess,
        ) = liNC

        (workinbackground, configuracion.x_log_engines, configuracion.x_carpeta_gaviota) = liEng
        configuracion.x_engine_notbackground = not workinbackground

        (
            configuracion.x_show_effects,
            rapidezMovPiezas,
            configuracion.x_mouse_shortcuts,
            configuracion.x_show_candidates,
            configuracion.x_autopromotion_q,
            configuracion.x_cursor_thinking,
            configuracion.x_captures_activate,
            # configuracion.x_capture_option,
            configuracion.x_info_activate,
            dboard,
            toolIcon,
            configuracion.x_position_tool_board,
            configuracion.x_director_icon,
            configuracion.x_direct_graphics,
        ) = liB
        configuracion.x_opacity_tool_board = 10 if toolIcon else 1
        configuracion.x_pieces_speed = drap[rapidezMovPiezas]
        if configuracion.x_digital_board != dboard:
            if dboard:
                DGT.ponON()
            configuracion.x_digital_board = dboard

        perf.bad_lostp, perf.very_bad_lostp, perf.bad_factor, perf.good_depth, perf.very_good_depth = liPR
        perf.very_bad_factor = perf.bad_factor * 4

        (
            configuracion.x_salvar_pgn,
            configuracion.x_salvar_ganados,
            configuracion.x_salvar_perdidos,
            configuracion.x_salvar_abandonados,
            configuracion.x_save_tutor_variations,
            configuracion.x_salvar_csv,
        ) = liSA
        configuracion.x_salvar_csv = Util.dirRelativo(configuracion.x_salvar_csv)

        return True
    else:
        return False


def opcionesPrimeraVez(parent, configuracion):
    form = FormLayout.FormLayout(parent, _("Player"), Iconos.Usuarios(), anchoMinimo=460)
    form.separador()
    form.edit(_("Player's name"), configuracion.x_player)
    result = form.run()
    if result:
        accion, resp = result
        player = resp[0].strip()
        if not player:
            player = _("Player")
        configuracion.x_player = player
        return True
    else:
        return False
