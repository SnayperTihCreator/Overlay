# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import pathlib
import zipfile

sys.path.append(os.getcwd())

from PyInstaller.building.build_main import Analysis
# noinspection PyUnresolvedReferences
from PyInstaller.building.api import EXE, COLLECT, PYZ, logger

from MinTools import OpenManager
from Service.metadata import version
# noinspection PyUnresolvedReferences
import assets_rc

DISTPATH: str


def buildZipFile(dist: pathlib.Path, dir_name: str):
    folderApp = dist / dir_name
    zipFile = dist / f"{dir_name}.zip"
    if folderApp.exists():
        logger.info("📁 Сборка архива")
        with zipfile.ZipFile(zipFile, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for file_path in folderApp.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(folderApp)
                    zipf.write(file_path, arcname)
        logger.info("📁 Архив собран")


with OpenManager():
    a = Analysis(
        ['main.py'],
        pathex=[],
        binaries=[],
        datas=[],
        hiddenimports=["json", "psutil", "cProfile", "xml.etree.ElementTree", "requests", "numpy"],
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
        [],
        exclude_binaries=True,
        name=f'Overlay',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        disable_windowed_traceback=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
        icon=['assets/icons/icon.png'],
    )
    
    coll = COLLECT(
        exe,
        a.binaries,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name=f'Overlay({version("App")})',
    )
    
    buildZipFile(pathlib.Path(DISTPATH), coll.name)
