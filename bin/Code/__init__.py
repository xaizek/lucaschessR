import sys
import os

lucas_chess = None  # asignado en Translate

folder_OS = os.path.realpath(os.path.join("OS", sys.platform))

folder_engines = os.path.join(folder_OS, "Engines")
sys.path.insert(0, folder_OS)
sys.path.insert(0, os.path.realpath(os.curdir))

folder_resources = os.path.realpath("../Resources")
folder_root = os.path.realpath("..")


def path_resource(*lista):
    p = folder_resources
    for x in lista:
        p = os.path.join(p, x)
    return os.path.realpath(p)


current_dir = os.path.realpath(os.path.dirname(sys.argv[0]))
if current_dir:
    os.chdir(current_dir)

sys.path.append(os.path.join(current_dir, "Code"))

isLinux = sys.platform == "linux2"
isWindows = not isLinux
if isLinux:
    startfile = os.system
else:
    startfile = os.startfile

dgt = None
dgtDispatch = None

configuracion = None  # Actualizado en configuracion tras lee()
procesador = None

todasPiezas = None

tbook = path_resource("Openings", "GMopenings.bin")
tbookPTZ = path_resource("Openings", "fics15.bin")
tbookI = path_resource("Openings", "irina.bin")
xtutor = None

list_engine_managers = None

mate_en_dos = 154996

runSound = None

VERSION = "R0.21"
DEBUG = False
DEBUG_ENGINE = False

