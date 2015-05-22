#!/usr/bin/python
# -*- coding: utf-8 -*-

# source d'inspiration: http://wiki.wxpython.org/cx_freeze

import sys, os, subprocess, multiprocessing
from cx_Freeze import setup, Executable
from PyQt5 import QtCore

#############################################################################
# preparation des options
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'lib')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'res', 'certs')))

print(sys.path)
includes = ["sip", "re", "json", "logging",
            "hashlib", "os", "urllib",
            "ucoinpy", "pylibscrypt", "requests"]
excludes = []
packages = ["libnacl", "encodings"]

includefiles = []
if sys.platform == "win32":
    app = QtCore.QCoreApplication(sys.argv)
    pyqt_path = QtCore.QCoreApplication.libraryPaths()[0]
    print(pyqt_path)
    libEGL_path = os.path.join(os.path.dirname(pyqt_path), "libEGL.dll")
    includefiles.append(libEGL_path)
    includefiles.append("platforms/win32/libsodium.dll")

elif sys.platform == "darwin":
    pass
else:
    pass

options = {"path": sys.path,
           "includes": includes,
           "include_files": includefiles,
           "excludes": excludes,
           "packages": packages,
           }

#############################################################################
# preparation des cibles
base = None
file_type=""
icon="cutecoin.png"
if sys.platform == "win32":
    base = "Win32GUI"
    file_type=".exe"
    icon="cutecoin.ico"

target = Executable(
    script = "src/cutecoin/main.py",
    targetName="cutecoin"+file_type,
    base = base,
    compress = False,
    icon = icon,
    )

#############################################################################
# creation du setup
setup(
    name = "cutecoin",
    version = "0.10",
    description = "UCoin client",
    author = "Inso",
    options = {"build_exe": options},
    executables = [target]
    )

