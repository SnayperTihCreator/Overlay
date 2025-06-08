from PySide6.QtWidgets import QFormLayout

from .pluginSettingTemplate import PluginSettingTemplate


class PluginSettingWidget(PluginSettingTemplate):
    formLayout: QFormLayout
    
    def __init__(self, obj, name_plugin, parent=None):
        super().__init__(obj, name_plugin, parent)