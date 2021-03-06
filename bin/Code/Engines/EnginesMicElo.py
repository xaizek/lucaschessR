import Code
from Code import Util


def read_mic_engines():
    configuracion = Code.configuracion
    fichero = Code.path_resource("IntFiles", "mic_tourney.eval")

    with open(fichero) as f:
        li = []
        for linea in f:
            dic = eval(linea.strip())
            alias = dic["ALIAS"]
            nom_base_engine = dic["ENGINE"]
            id_info = dic["IDINFO"]
            elo = dic["ELO"]
            li_uci = [(d["name"], d["valor"]) for d in dic["LIUCI"]]

            engine = configuracion.dic_engines.get(nom_base_engine)
            if engine:
                eng = engine.clona()
                eng.name = alias
                eng.id_info = id_info
                eng.alias = alias
                eng.elo = elo
                eng.liUCI = li_uci
                if alias.isupper():
                    eng.name = Util.primera_mayuscula(alias)
                    eng.alias = eng.name
                    eng.book = Code.path_resource(
                        "Openings", "Players", "%s.bin" % alias.lower()
                    )
                else:
                    eng.book = None
                li.append(eng)
    return li


def only_gm_engines():
    li = [mtl for mtl in read_mic_engines() if mtl.book]
    li.sort(key=lambda uno: uno.name)
    return li


def all_engines():
    li = read_mic_engines()
    li.sort(key=lambda uno: uno.elo)
    return li
