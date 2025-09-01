from pathlib import Path
from zipimport import zipimporter

from fs import open_fs

from .loader import Loader
from PathControl import getAppPath


class PluginLoader(Loader):
    def __init__(self):
        super().__init__()
        self.folder: Path = (getAppPath() / "plugins")
        self.fs = open_fs("plugin://")
        
        self.plugins = {}
        self.types_plugins = {}
        self.errors = {}
    
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
            except Exception as e:
                self.plugins[plugin_name] = None
                self.types_plugins[plugin_name] = []
                self.errors[plugin_name] = e
    
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
