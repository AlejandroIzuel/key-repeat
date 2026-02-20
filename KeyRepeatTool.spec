# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file — for local builds:
#   pip install pyinstaller
#   pyinstaller KeyRepeatTool.spec

a = Analysis(
    ["key_repeat.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=["keyboard"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="KeyRepeatTool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,        # no console window, just the GUI
    icon=None,            # add an .ico path here if you want a custom icon
)
