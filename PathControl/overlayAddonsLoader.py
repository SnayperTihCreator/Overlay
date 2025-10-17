import zipimport
from fnmatch import fnmatch

from fs import open_fs

from . import getAppPath
from .loader import Loader


class OverlayAddonsLoader(Loader):
    def __init__(self):
        super().__init__()
        self.folder = getAppPath() / "resource"
        self.fs = open_fs("resource://overlay_addons")
    
    def load(self):
        pass
    
    def find_prefix(self, prefix):
        for file in self.list():
            if fnmatch(file, f"{prefix}.oaddons"):
                return file
        raise ValueError(f"Not found to {prefix}")
    
    def import_module(self, name):
        path = self.folder / f"{name}.oaddons"
        importer = zipimport.zipimporter(str(path))
        module = importer.load_module(name)
        return module
    
    def list(self) -> list[str]:
        return self.fs.listdir("")
