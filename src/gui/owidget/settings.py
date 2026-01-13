from PySide6.QtWidgets import QFormLayout
from ldt import LDT

from gui.plugin_settings import PluginSettingTemplate



class PluginSettingWidget(PluginSettingTemplate):
    formLayout: QFormLayout
    
    def __init__(self, obj, name_plugin, parent=None):
        super().__init__(obj, name_plugin, parent)
    
    def send_data(self):
        ldt = LDT()
        ldt.set("position", self.obj.pos())
        return ldt
