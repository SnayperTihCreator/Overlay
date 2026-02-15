from zipimport import zipimporter
from typing import Iterator
import logging

from fs import open_fs
from attrs import define

from core.metadata import metadata, MetaData
from utils.fs import getAppPath

from .base import Loader

logger = logging.getLogger(__name__)


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
        logger.info("ThemeLoader initialized.")
    
    def load(self):
        pass
    
    def loadTheme(self, name):
        logger.info(f"Loading theme archive: {name}")
        try:
            themePath = self.folder / f"{name}.overtheme"
            importer = zipimporter(str(themePath))
            moduleTheme = importer.load_module("theme")
            logger.info(f"Theme loaded successfully: {name}")
            return getattr(moduleTheme, name)
        except Exception as e:
            logger.warning(f"Failed to load theme '{name}': {e}")
            logger.error(f"Critical error loading theme '{name}'", exc_info=True)
            raise
    
    def list(self) -> Iterator[ThemeInfo]:
        for name in self.fs.listdir(""):
            try:
                yield ThemeInfo(name, metadata(f"theme::{name}"))
            except AttributeError:
                logger.warning(f"Metadata missing/corrupt for theme '{name}': {e}")
                yield ThemeInfo(name, None)
