from pathlib import Path
from zipimport import zipimporter
import logging

from fs import open_fs

from utils.fs import getAppPath

from .base import Loader

logger = logging.getLogger(__name__)


class PluginLoader(Loader):
    def __init__(self):
        super().__init__()
        self.folder: Path = (getAppPath() / "plugins")
        self.fs = open_fs("plugin://")
        
        self.plugins = {}
        self.types_plugins = {}
        self.errors = {}
        logger.info(f"PluginLoader initialized. Folder: {self.folder}")
    
    def load(self):
        for plugin in self.folder.glob("*.plugin"):
            plugin_name = plugin.stem
            importer = zipimporter(str(plugin))
            try:
                module = importer.load_module(plugin_name)
                types = self.searchType(module)
                self.plugins[plugin_name] = module
                self.types_plugins[plugin_name] = types
                self.errors[plugin_name] = None
                logger.info(f"Plugin '{plugin_name}' loaded. Types: {types}")
            except Exception as e:
                self.plugins[plugin_name] = None
                self.types_plugins[plugin_name] = []
                self.errors[plugin_name] = e
                logger.warning(f"Failed to load plugin '{plugin_name}': {e}")
                logger.error(f"Critical error loading plugin '{plugin_name}'", exc_info=True)
        logger.info(f"Plugin loading finished. Total loaded: {len(self.plugins)}")
    
    def getTypes(self, plugin_name):
        return self.types_plugins[plugin_name]
    
    def getError(self, plugin_name):
        return self.errors[plugin_name]
    
    @staticmethod
    def searchType(module):
        types = []
        if hasattr(module, "createWindow"):
            types.append("Window")
        if hasattr(module, "createWidget"):
            types.append("Widget")
        return types
    
    def list(self) -> list[str]:
        return self.fs.listdir("")
