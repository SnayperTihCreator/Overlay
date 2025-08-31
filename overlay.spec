# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import toml

sys.path.append(os.getcwd())
from PathControl.storageControls import OpenManager

import PathControl.qtStorageControls
import assets_rc

with OpenManager():
    data_file = open("qt://app/metadata.toml", encoding="utf-8").read()
    data = toml.loads(data_file)

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
        a.binaries,
        a.datas,
        [],
        name=f'Overlay({data["version"]})',
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
        icon=['assets/icons/icon.png'],
    )
