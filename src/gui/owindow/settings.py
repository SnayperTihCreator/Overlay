from __future__ import annotations
import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFormLayout, QCheckBox
from PySide6.QtCore import Qt
from ldt import LDT

from gui.plugin_settings import PluginSettingTemplate

if TYPE_CHECKING:
    from .base import OWindow

logger = logging.getLogger(__name__)


class PluginSettingWindow(PluginSettingTemplate):
    formLayout: QFormLayout
    obj: OWindow
    
    def __init__(self, obj, name_plugin, parent=None):
        super().__init__(obj, name_plugin, parent)
        
        # UI translated to Simple English
        self.no_clicked = QCheckBox("Ignore Clicks (Transparent)")
        self.formLayout.addWidget(self.no_clicked)
        self.formLayout.setWidget(1, QFormLayout.ItemRole.SpanningRole, self.no_clicked)
        
        self.moved = QCheckBox("Movable")
        self.formLayout.addWidget(self.moved)
        self.formLayout.setWidget(2, QFormLayout.ItemRole.SpanningRole, self.moved)
        
        logger.debug(f"Settings window initialized for: {name_plugin}")
    
    def loader(self):
        try:
            super().loader()
            
            noClicked = bool(self.obj.windowFlags() & Qt.WindowType.WindowTransparentForInput)
            hasMoved = self.obj.hasMoved
            
            self.no_clicked.blockSignals(True)
            self.moved.blockSignals(True)
            
            self.no_clicked.setChecked(noClicked)
            self.moved.setChecked(hasMoved)
            
            self.no_clicked.blockSignals(False)
            self.moved.blockSignals(False)
            
            logger.debug(f"Loaded state for {self.save_name}: ClickThrough={noClicked}, Movable={hasMoved}")
        
        except Exception as e:
            logger.error(f"Failed to load settings state for {self.save_name}: {e}", exc_info=True)
    
    def send_data(self) -> LDT:
        try:
            ldt = super().send_data()
            ldt.set("hasMoved", self.moved.isChecked())
            ldt.set("notClicked", self.no_clicked.isChecked())
            return ldt
        except Exception as e:
            logger.error(f"Failed to save settings data for {self.save_name}: {e}", exc_info=True)
            return LDT()
