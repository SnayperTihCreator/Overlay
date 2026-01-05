from __future__ import annotations
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFormLayout, QCheckBox
from PySide6.QtCore import Qt

from gui.plugin_settings import PluginSettingTemplate

if TYPE_CHECKING:
    from .base import OWindow


class PluginSettingWindow(PluginSettingTemplate):
    formLayout: QFormLayout
    obj: OWindow
    
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
        ldt = super().send_data()
        ldt.set("hasMoved", self.moved.isChecked())
        ldt.set("notClicked", self.no_clicked.isChecked())
        return ldt
