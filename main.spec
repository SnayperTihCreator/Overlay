# -*- mode: python ; coding: utf-8 -*-
import shutil
import sys
import os

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=["json", "psutil", "cProfile", "xml.etree.ElementTree", "requests"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='Overlay',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

#if not sys.argv[-1] == '--no-remove-build':  # Опционально: флаг для отмены удаления
#    shutil.rmtree('build', ignore_errors=True)

dist_path = os.path.join('dist', exe.name)  # Путь к собранному приложению
target_path = './'  # Куда переместить

if os.path.exists(dist_path):
    shutil.move(dist_path, target_path)
    shutil.rmtree('dist', ignore_errors=True)