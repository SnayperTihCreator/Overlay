import os
import sys
from functools import cache
from pathlib import Path


@cache
def getAppPath():
    return (
        Path(sys.executable).parent
        if getattr(sys, "frozen", False)
        else Path(os.getcwd())
    )


@cache
def getAssetsPath():
    path = getattr(sys, "_MEIPASS", os.getcwd())
    return Path(path) / "assets"
