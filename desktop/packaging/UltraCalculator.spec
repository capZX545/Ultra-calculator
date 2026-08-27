# -*- mode: python ; coding: utf-8 -*-
"""Frozen desktop build. Run from the repo root:

    pyinstaller desktop/packaging/UltraCalculator.spec --noconfirm --clean
"""

from __future__ import annotations

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

packaging = Path(SPECPATH).resolve()
desktop = packaging.parent
repo = desktop.parent
calc = desktop / "calc"
icon_ico = packaging / "icon.ico"

datas = [
    (str(calc / "formulas.json"), "calc"),
    (str(calc / "elements.json"), "calc"),
    (str(calc / "sources.json"), "calc"),
]
binaries = []
hiddenimports = [
    "tkinter",
    "tkinter.ttk",
    "tkinter.font",
    "tkinter.filedialog",
    "tkinter.messagebox",
    "numpy",
    "scipy",
    "scipy.optimize",
    "scipy.integrate",
    "scipy.stats",
    "scipy.special",
    "sympy",
    "sympy.parsing.sympy_parser",
    "mpmath",
    "calc",
    "calc.app",
    "calc.engine",
    "calc.algorithms",
    "calc.chemtools",
    "calc.circuits",
    "calc.circguide",
    "calc.seqfind",
    "calc.problems",
    "calc.wordprob",
    "calc.graphs",
    "calc.matrixlab",
    "calc.statsdata",
    "calc.triangle",
    "calc.searchall",
    "calc.sessionstore",
    "calc.latexout",
    "calc.lookup",
    "calc.sanitize",
    "calc.teach",
    "calc.i18n",
    "calc.units",
]
for pkg in ("numpy", "scipy", "sympy", "mpmath"):
    try:
        d, b, h = collect_all(pkg)
        datas += d
        binaries += b
        hiddenimports += h
    except Exception:
        pass

a = Analysis(
    [str(desktop / "run.py")],
    pathex=[str(desktop)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["pytest", "matplotlib", "notebook", "IPython", "pandas", "tkinter.test"],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="UltraCalculator",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=True,
    icon=str(icon_ico) if icon_ico.is_file() else None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="UltraCalculator",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Ultra Calculator.app",
        icon=str(icon_ico) if icon_ico.is_file() else None,
        bundle_identifier="org.capzx545.ultracalculator",
    )
