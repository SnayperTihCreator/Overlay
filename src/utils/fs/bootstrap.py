import os
import sys
import platform
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


class ToolsIniter:
    def __init__(self, name="tools"):
        self.tools_name = name
    
    def load(self):
        (getAppPath() / "plugins").mkdir(parents=True, exist_ok=True)
        (getAppPath() / self.tools_name / "common").mkdir(parents=True, exist_ok=True)
        (getAppPath() / self.tools_name / "windows").mkdir(parents=True, exist_ok=True)
        (getAppPath() / self.tools_name / "linux").mkdir(parents=True, exist_ok=True)
        sys.path.insert(0, str(getAppPath() / self.tools_name / "common"))
        match platform.system():
            case "Windows":
                sys.path.insert(0, str(getAppPath() / self.tools_name / "windows"))
            case "Linux":
                sys.path.insert(0, str(getAppPath() / self.tools_name / "linux"))
