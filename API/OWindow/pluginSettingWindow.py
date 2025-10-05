from PySide6.QtWidgets import QFormLayout, QCheckBox, QWidget
from PySide6.QtCore import Qt

from API.PlugSetting import PluginSettingTemplate, SettingConfigData


class WindowConfigData(SettingConfigData):
    hasMoved: int
    notClicked: int


class PluginSettingWindow(PluginSettingTemplate):
    
    builderConfig = WindowConfigData
    formLayout: QFormLayout
    obj: QWidget
    
    def __init__(self, obj, name_plugin, parent=None):
        super().__init__(obj, name_plugin, parent)
        
        self.no_clicked = QCheckBox("Не кликабельный")
        self.formLayout.addWidget(self.no_clicked)
        self.formLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.no_clicked)
        
        self.moved = QCheckBox("Подвижный")
        self.formLayout.addWidget(self.moved)
        self.formLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.moved)
    
    def loader(self):
        super().loader()
        noClicked = bool(self.obj.windowFlags() & Qt.WindowType.WindowTransparentForInput)
        hasMoved = self.obj.hasMoved
        
        self.no_clicked.setChecked(noClicked)
        self.moved.setChecked(hasMoved)
    
    def send_data(self):
        data = super().send_data()
        
        return data | {
            "hasMoved": self.moved.checkState() == Qt.CheckState.Checked,
            "notClicked": self.no_clicked.checkState() == Qt.CheckState.Checked
        }
        
