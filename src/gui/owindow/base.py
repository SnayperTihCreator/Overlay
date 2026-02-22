from __future__ import annotations
import logging
import uuid
from abc import ABC
from typing import Optional, TYPE_CHECKING

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGraphicsColorizeEffect, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QPoint, QTimer

from core.common import APIBaseWidget
from core.config import Config
from plugins.flags_installer import FlagsInstaller
from plugins.preloaders import WindowPreLoader
from gui.utils import clampAllDesktopP
from gui.themes import ThemeController
from ldt import LDT

from .settings import PluginSettingWindow

if TYPE_CHECKING:
    from gui.main_window import Overlay

# Initialize logger for this module
logger = logging.getLogger(__name__)


class OWindow(APIBaseWidget, ABC):
    dumper = WindowPreLoader()
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        self.overlay: Optional[Overlay] = parent
        self.config: Config = config
        
        # Unique ID generation
        self.uid = uuid.uuid4().hex
        
        try:
            logger.debug(f"Initializing OWindow (UID: {self.uid})")
            
            self.flagsInstaller: FlagsInstaller = FlagsInstaller.bind(self)
            self.flagsInstaller.install(Qt.WindowType.Window)
            
            self.setObjectName(self.__class__.__name__)
            self.setProperty("class", "DraggableWindow")
            
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.process)
            self.time_msec = 1000
            
            self.setGeometry(100, 100, 300, 200)
            
            self.box = QVBoxLayout(self)
            self.box.setContentsMargins(0, 0, 0, 0)
            self.box.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.central_widget = QWidget()
            self.box.addWidget(self.central_widget)
            
            # Dragging state
            self.hasMoved = True
            self.dragging = False
            self.reloading = False
            self.offset = QPoint()
            
            self.colorize_effect: Optional[QGraphicsColorizeEffect] = None
            
            QTimer.singleShot(0, self.load_config)
            
            logger.info("OWindow initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize OWindow: {e}", exc_info=True)
    
    def setCentralWidget(self, widget: QWidget):
        """Эмуляция QMainWindow для удобства плагинописцев"""
        try:
            if self.central_widget:
                self.central_widget.deleteLater()
            self.central_widget = widget
            self.box.addWidget(widget)
            logger.debug("Central widget set for OWindow")
        except Exception as e:
            logger.error(f"Failed to set central widget: {e}", exc_info=True)
    
    def __process__(self):
        self.reloading = False
    
    def __ready__(self):
        ...
    
    def load_config(self):
        try:
            logger.debug(f"Loading configuration for OWindow (UID: {self.uid})")
            width, height = self.config.data.settings.window.width, self.config.data.settings.window.height
            self.setFixedSize(width, height)
            
            style_path = f"plugin://{self.config.name}/{self.config.data.settings.style_file}"
            ThemeController().register(self, style_path, False)
            ThemeController().updateUid(self.uid)
            
            self.setWindowOpacity(self.config.data.settings.window.opacity)
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}", exc_info=True)
    
    def reload_config(self):
        try:
            logger.info("Reloading configuration...")
            self.reloading = True
            self.config.reload()
            self.load_config()
            self.process()
        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}", exc_info=True)
    
    def save_status(self) -> LDT:
        try:
            ldt = LDT()
            ldt.set("hasMoved", self.hasMoved)
            ldt.set("notClicked", bool(self.windowFlags() & Qt.WindowType.WindowTransparentForInput))
            ldt.set("position", self.pos())
            return ldt
        except Exception as e:
            logger.error(f"Failed to save status: {e}", exc_info=True)
            return LDT()
    
    def load_status(self, status: LDT):
        try:
            visible = self.isVisible()
            self.toggle_input(status.get("notClicked", default=False))
            self.setVisible(visible)
            
            self.hasMoved = status.get("hasMoved", default=True)
            pos = clampAllDesktopP(status.get("position", default=QPoint(100, 100)), self.width(), self.height())
            self.setGeometry(pos.x(), pos.y(), self.width(), self.height())
            logger.debug("Status loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load status: {e}", exc_info=True)
    
    def shortcut_run(self, name):
        pass
    
    def toggle_input(self, state: bool):
        """Меняем флаги только если они реально отличаются"""
        try:
            current_flags = self.windowFlags()
            new_flags = current_flags
            
            if state:
                new_flags |= Qt.WindowType.WindowTransparentForInput
            else:
                new_flags &= ~Qt.WindowType.WindowTransparentForInput
            
            if current_flags != new_flags:
                self.setWindowFlags(new_flags)
                self.show()
                logger.debug(f"Input transparency toggled to: {state}")
        except Exception as e:
            logger.error(f"Failed to toggle input state: {e}", exc_info=True)
    
    def mousePressEvent(self, event):
        try:
            if self.windowFlags() & Qt.WindowType.WindowTransparentForInput:
                return
            
            if (event.button() == Qt.MouseButton.LeftButton) and self.hasMoved:
                self.dragging = True
                self.offset = event.globalPosition().toPoint() - self.pos()
            super().mousePressEvent(event)
        except Exception as e:
            logger.error(f"Error in mouse press event: {e}", exc_info=True)
    
    def mouseMoveEvent(self, event):
        try:
            if self.dragging:
                new_pos = event.globalPosition().toPoint() - self.offset
                new_pos = clampAllDesktopP(new_pos, self.width(), self.height())
                self.move(new_pos)
            super().mouseMoveEvent(event)
        except Exception as e:
            # Logging in move event can flood logs, so we log critical errors only once per drag usually,
            # but for now we stick to the rule.
            self.dragging = False
            logger.error(f"Error in mouse move event: {e}", exc_info=True)
    
    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self.dragging = False
            super().mouseReleaseEvent(event)
        except Exception as e:
            logger.error(f"Error in mouse release event: {e}", exc_info=True)
    
    def keyPressEvent(self, event):
        try:
            if event.key() in [Qt.Key.Key_Escape, Qt.Key.Key_Backspace]:
                if self.parent():
                    self.parent().keyPressEvent(event)
            return super().keyPressEvent(event)
        except Exception as e:
            logger.error(f"Error in key press event: {e}", exc_info=True)
            return super().keyPressEvent(event)
    
    def highlightBorder(self):
        try:
            if self.colorize_effect is None:
                self.colorize_effect = QGraphicsColorizeEffect(self)
                self.colorize_effect.setColor(QColor(0, 255, 0))
                self.setGraphicsEffect(self.colorize_effect)
            self.colorize_effect.setStrength(0.7)  # Интенсивность
            QTimer.singleShot(500, lambda: self.colorize_effect.setStrength(0))
        except Exception as e:
            logger.error(f"Failed to highlight border: {e}", exc_info=True)
    
    def shortcut(self, key: str, uname: str):
        try:
            if self.overlay:
                self.overlay.registered_shortcut(key, uname, self)
                logger.debug(f"Registered shortcut: {key} ({uname})")
            else:
                logger.warning("Attempted to register shortcut but overlay is None")
        except Exception as e:
            logger.error(f"Failed to register shortcut: {e}", exc_info=True)
    
    @classmethod
    def createSettingWidget(cls, window: "OWindow", name_plugin: str, parent):
        try:
            return PluginSettingWindow(window, name_plugin, parent)
        except Exception as e:
            logger.error(f"Failed to create setting widget for plugin '{name_plugin}': {e}", exc_info=True)
            return None
