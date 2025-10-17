import zipimport
from fnmatch import fnmatch
from typing import Optional

from fs import open_fs

from . import getAppPath
from .loader import Loader
from .platformCurrent import getSystem


class OverlayAddonsLoader(Loader):
    def __init__(self):
        super().__init__()
        self.folder = getAppPath() / "resource"
        self.fs = open_fs("resource://overlay_addons")
        self.available_platforms = [
            "win32",
            "linux"
        ]
    
    def load(self):
        pass
    
    def find_prefix(self, prefix):
        for file in self.list():
            if fnmatch(file, f"{prefix}.oaddons"):
                return file
        raise ValueError(f"Not found to {prefix}")
    
    def find_platform_prefix(self, prefix) -> Optional[str]:
        platform, window = getSystem()
        
        # Сначала ищем наиболее специфичный вариант
        specific_key = f"{prefix}_{platform}_{window}"
        if specific_key in self.list():
            return specific_key
        
        # Затем ищем вариант для текущей платформы с любым оконным менеджером
        platform_any_key = f"{prefix}_{platform}_any"
        if platform_any_key in self.list():
            return platform_any_key
        
        # Наконец, ищем наиболее общий вариант
        any_any_key = f"{prefix}_any_any"
        if any_any_key in self.list():
            return any_any_key
        
        # Если ничего не найдено
        return
    
    def import_module(self, name):
        path = self.folder / f"{name}.oaddons"
        importer = zipimport.zipimporter(str(path))
        module = importer.load_module(name)
        return module
    
    def list(self) -> list[str]:
        return self.fs.listdir("")
