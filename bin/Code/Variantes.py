from Code import GestorVariantes


def editaVariante(procesador, game, titulo=None, siEngineActivo=False, siCompetitivo=False, is_white_bottom=None):
    wpantalla = procesador.main_window
    xtutor = procesador.XTutor()
    procesadorVariantes = procesador.clonVariantes(wpantalla, xtutor, siCompetitivo=siCompetitivo)

    gestorVariantes = GestorVariantes.GestorVariantes(procesadorVariantes)
    gestorVariantes.inicio(game, is_white_bottom, siEngineActivo, siCompetitivo)
    procesadorVariantes.gestor = gestorVariantes

    if titulo is None:
        titulo = game.pgnBaseRAW()

    procesadorVariantes.main_window.muestraVariantes(titulo)

    return gestorVariantes.valor()


def editaVarianteMoves(procesador, wpantalla, is_white_bottom, fen, lineaPGN, titulo=None):
    procesadorVariantes = procesador.clonVariantes(wpantalla)

    gestorVariantes = GestorVariantes.GestorVariantes(procesadorVariantes)
    gestorVariantes.inicio(fen, lineaPGN, False, is_white_bottom)
    procesadorVariantes.gestor = gestorVariantes

    if titulo is None:
        titulo = lineaPGN
    procesadorVariantes.main_window.muestraVariantes(titulo)

    return gestorVariantes.valor()  # pgn y a1h8, el a1h8 nos servira para editar las aperturas
