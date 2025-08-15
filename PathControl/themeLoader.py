from zipimport import zipimporter

from fs import open_fs

from .loader import Loader
from . import getAppPath


class ThemeLoader(Loader):
    def __init__(self):
        super().__init__()
        self.folder = getAppPath() / "resource"
        self.fs = open_fs("resource://theme")
    
    def load(self):
        pass
    
    def loadTheme(self, name):
        themePath = self.folder / f"{name}.overtheme"
        importer = zipimporter(str(themePath))
        moduleTheme = importer.load_module("theme")
        return getattr(moduleTheme, name)
    
    def list(self):
        return self.fs.listdir("")
