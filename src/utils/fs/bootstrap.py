import os
import site
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
    
    def _register_path(self, path: Path):
        """Создает папку и интегрирует её в Python как site-пакет."""
        path.mkdir(parents=True, exist_ok=True)
        path_str = str(path)
        site.addsitedir(path_str)
        if path_str in sys.path:
            sys.path.remove(path_str)
        sys.path.insert(0, path_str)
    
    def load(self):
        self._register_path(getAppPath() / self.tools_name / "common")
        
        match platform.system():
            case "Windows":
                os_folder = "windows"
                self._register_path(getAppPath() / self.tools_name / os_folder)
                os.add_dll_directory((getAppPath() / self.tools_name / os_folder).as_posix())
            
            case "Linux":
                os_folder = "linux"
                os_path = getAppPath() / self.tools_name / os_folder
                self._register_path(os_path)
                os.environ["LD_LIBRARY_PATH"] = f"{os_path}:{os.environ.get('LD_LIBRARY_PATH', '')}"
            case _:
                print(f"Warning: OS {platform.system()} is not explicitly supported.")
        
        plugins_path = getAppPath() / "plugins"
        plugins_path.mkdir(parents=True, exist_ok=True)
        sys.path.insert(0, str(plugins_path))
