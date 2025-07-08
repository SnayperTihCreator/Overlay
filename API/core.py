from box import Box

from APIService.dumper import Dumper


class APIBaseWidget:
    dumper: Dumper
    
    def reloadConfig(self):
        raise NotImplementedError
    
    def savesConfig(self):
        return {}
    
    def restoreConfig(self, config: Box):
        raise NotImplementedError
    
    @classmethod
    def createSettingWidget(cls, obj: "APIBaseWidget", name_plugin, parent: "Overlay"):
        raise NotImplementedError
