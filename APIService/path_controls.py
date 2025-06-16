import sys
from functools import cache
from pathlib import Path


@cache
def getAppPath():
    return (
        Path(sys.executable).parent
        if getattr(sys, "frozen", False)
        else Path(sys.argv[0]).parent
    )

__all__ = ["getAppPath"]