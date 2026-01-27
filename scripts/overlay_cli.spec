# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

from PyInstaller.building.utils import logger

SPECPATH: str
BASE_DIR = os.path.dirname(SPECPATH)
sys.path.append(os.path.join(BASE_DIR, 'src'))

a = Analysis(
    [os.path.join(BASE_DIR, 'src', 'overlay_cli.py')],
    pathex=[os.path.join(BASE_DIR, 'src')],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["PySide6", "shiboken6"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='OverlayCLI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
