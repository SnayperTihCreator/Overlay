import zipimport
from zipimport import zipimporter
from typing import Iterator

from fs import open_fs
from attrs import define
from PySide6.QtCore import qWarning

from core.metadata import metadata, MetaData
from utils.fs import getAppPath

from .base import Loader


@define(repr=False)
class ThemeInfo:
    nameTheme: str
    metadataTheme: MetaData
    
    def __repr__(self):
        return self.nameTheme
    
    @property
    def __docs_inter__(self):
        docsFirst = (self.metadataTheme.description or "Has not docs").split("\n")[0]
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
        try:
            themePath = self.folder / f"{name}.overtheme"
            importer = zipimporter(str(themePath))
            moduleTheme = importer.load_module("theme")
            return getattr(moduleTheme, name)
        except zipimport.ZipImportError:
            qWarning(f"Не удалось загрузить тему: {name}")
            raise
    
    def list(self) -> Iterator[ThemeInfo]:
        for name in self.fs.listdir(""):
            try:
                yield ThemeInfo(name, metadata(f"theme::{name}"))
            except AttributeError:
                yield ThemeInfo(name, None)
