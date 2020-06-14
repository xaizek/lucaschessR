import sys
import signal

import os
import time
import subprocess
import threading
import psutil

import Code
from Code.Engines import Priorities
from Code.Constantes import prlk

DEBUG_ENGINE = False


def xpr(exe, line):
    if DEBUG_ENGINE:
        t = time.time()
        prlk("%0.04f %s" % (t - tdbg[0], line))
        tdbg[0] = t
    return True


def xprli(li):
    if DEBUG_ENGINE:
        t = time.time()
        dif = t - tdbg[0]
        for line in li:
            prlk("%0.04f %s" % (dif, line))
        tdbg[0] = t
    return True


if DEBUG_ENGINE:
    tdbg = [time.time()]
    xpr("", "DEBUG XMOTOR")


class EngineThread(object):
    def __init__(self, exe, priority, args):
        self.pid = None
        self.exe = os.path.abspath(exe)
        self.direxe = os.path.dirname(exe)
        self.priority = priority
        self.working = True
        self.liBuffer = []
        self.starting = True
        self.args = [os.path.basename(self.exe)]
        if args:
            self.args.extend(args)

        if Code.isLinux and Code.isWine and self.exe.lower().endswith(".exe"):
            self.args.insert(0, "/usr/bin/wine")

    def cerrar(self):
        self.working = False

    def put_line(self, line: str):
        if self.working:
            assert xpr(self.exe, "put>>> %s\n" % line)
            self.stdin_lock.acquire()
            line = line.encode("utf-8", errors="ignore")
            self.stdin.write(line + b"\n")
            self.stdin.flush()
            self.stdin_lock.release()

    def get_lines(self):
        self.stdout_lock.acquire()
        li = self.liBuffer
        self.liBuffer = []
        self.stdout_lock.release()
        return li

    def hay_datos(self):
        return len(self.liBuffer) > 0

    def reset(self):
        self.get_lines()

    def xstdout_thread(self, stdout, lock):
        try:
            while self.working:
                line = stdout.readline().decode("utf-8", errors="ignore")
                assert xpr(self.exe, line)
                if not line:
                    break
                lock.acquire()
                self.liBuffer.append(line)
                lock.release()
        except:
            pass
        finally:
            stdout.close()

    def start_engine(self):
        if Code.isWindows:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
        else:
            startupinfo = None
        curdir = os.path.abspath(os.curdir)  # problem with "." as curdir
        os.chdir(self.direxe)  # to fix problems with non ascii folders

        if Code.isLinux:
            argv0 = self.args[0]
            if not ("/" in argv0):
                self.args[0] = os.path.join(os.path.abspath(os.curdir), argv0)

        self.process = subprocess.Popen(
            self.args, stdout=subprocess.PIPE, stdin=subprocess.PIPE, startupinfo=startupinfo, shell=False
        )
        os.chdir(curdir)

        self.pid = self.process.pid
        if self.priority is not None:
            p = psutil.Process(self.pid)
            p.nice(Priorities.priorities.value(self.priority))

        self.stdin = self.process.stdin
        self.stdout = self.process.stdout

    def start(self):
        self.start_engine()

        self.stdout_lock = threading.Lock()
        stdout_thread = threading.Thread(target=self.xstdout_thread, args=(self.process.stdout, self.stdout_lock))
        stdout_thread.daemon = True
        stdout_thread.start()

        self.stdin_lock = threading.Lock()

        self.starting = False

    def close(self):
        self.working = False
        if self.pid:
            try:
                if self.process.poll() is None:
                    self.put_line("stop")
                    self.put_line("quit")
                    self.process.kill()
                    self.process.terminate()
            except:
                os.kill(self.pid, signal.SIGTERM)
                sys.stderr.write("INFO X CLOSE: except - the engine %s won't close properly.\n" % self.exe)

            self.pid = None


# class EngineDirect(EngineThread):
#     def cerrar(self):
#         self.close()
#
#     def put_line(self, line: str):
#         if self.working:
#             assert xpr(self.exe, "put>>> %s\n" % line)
#             line = line.encode("utf-8", errors="ignore")
#             self.stdin.write(line + b"\n")
#             self.stdin.flush()
#
#     def start(self):
#         self.start_engine()
#
#     def get_lines(self):
#         line = self.stdout.readline().decode("utf-8", errors="ignore")
#         return [line,]
#
#     def reset(self):
#         pass
#
#     def hay_datos(self):
#         return True
