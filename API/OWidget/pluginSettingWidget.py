from PySide6.QtWidgets import QFormLayout

from API.PlugSetting import PluginSettingTemplate, SettingConfigData


class WidgetConfigData(SettingConfigData): ...


class PluginSettingWidget(PluginSettingTemplate):
    formLayout: QFormLayout
    
    def __init__(self, obj, name_plugin, parent=None):
        super().__init__(obj, name_plugin, parent)
        
    def send_data(self):
        return {"position": self.obj.pos()}
