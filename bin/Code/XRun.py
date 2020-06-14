import subprocess
import sys

import Code


def run_lucas(*args):
    li = []
    iswindows = Code.isWindows
    if sys.argv[0].endswith(".py"):
        li.append("python")
        li.append("./LucasR.py")
    else:
        li.append("LucasR.exe" if iswindows else "./LucasR")
    li.extend(args)
    return subprocess.Popen(li)
