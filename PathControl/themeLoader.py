from zipimport import zipimporter
from typing import Optional

from fs import open_fs
from attrs import define

from Service.metadata import metadata
from Service.versionControl import OverlayThemeMetadata

from .loader import Loader
from . import getAppPath


@define(repr=False)
class ThemeInfo:
    nameTheme: str
    metadataTheme: OverlayThemeMetadata
    
    def __repr__(self):
        return self.nameTheme
    
    @property
    def __docs_inter__(self):
        docsFirst = (self.metadataTheme.docs or "Has not docs").split("\n")[0]
        result = docsFirst
        result += f" [bright_cyan](V: {self.metadataTheme.version})[/bright_cyan]"
        return result
        
        


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
        for name in self.fs.listdir(""):
            try:
                yield ThemeInfo(name, metadata(f"theme::{name}"))
            except AttributeError:
                yield ThemeInfo(name, None)
