from box import Box
from PySide6.QtWidgets import QWidget


class APIBaseWidget():
    dumper: "Dumper"
    
    def reloadConfig(self):
        raise NotImplementedError
    
    def savesConfig(self):
        return {}
    
    def restoreConfig(self, config: Box):
        raise NotImplementedError
    
    @classmethod
    def createSettingWidget(cls, obj: "APIBaseWidget", name_plugin, parent: "Overlay"):
        raise NotImplementedError
    