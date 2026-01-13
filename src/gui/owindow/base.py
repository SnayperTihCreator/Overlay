from __future__ import annotations
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


class OWindow(APIBaseWidget, ABC):
    dumper = WindowPreLoader()
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        self.overlay: Optional[Overlay] = parent
        
        self.flagsInstaller: FlagsInstaller = FlagsInstaller.bind(self)
        self.flagsInstaller.install(Qt.WindowType.Window)
        
        self.setObjectName(self.__class__.__name__)
        self.setProperty("class", "DraggableWindow")
        self.uid = uuid.uuid4().hex
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process)
        self.time_msec = 1000
        
        self.config: Config = config
        
        self.setGeometry(100, 100, 300, 200)
        
        self.box = QVBoxLayout(self)
        self.box.setContentsMargins(0, 0, 0, 0)
        self.box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.central_widget = QWidget()
        self.box.addWidget(self.central_widget)
        
        QTimer.singleShot(0, self.load_config)
        
        # Для перетаскивания
        self.hasMoved = True
        self.dragging = False
        self.reloading = False
        self.offset = QPoint()
        
        self.colorize_effect: Optional[QGraphicsColorizeEffect] = None
    
    def setCentralWidget(self, widget: QWidget):
        """Эмуляция QMainWindow для удобства плагинописцев"""
        if self.central_widget:
            self.central_widget.deleteLater()
        self.central_widget = widget
        self.box.addWidget(widget)
    
    def __process__(self):
        self.reloading = False
    
    def __ready__(self):
        ...
    
    def load_config(self):
        width, height = self.config.data.settings.window.width, self.config.data.settings.window.height
        self.setFixedSize(width, height)
        
        ThemeController().register(self, f"plugin://{self.config.name}/{self.config.data.settings.style_file}", False)
        ThemeController().updateUid(self.uid)
        
        self.setWindowOpacity(self.config.data.settings.window.opacity)
        
    def reload_config(self):
        self.reloading = True
        self.config.reload()
        self.load_config()
        self.process()
        
    def save_status(self) -> LDT:
        ldt = LDT()
        ldt.set("hasMoved", self.hasMoved)
        ldt.set("notClicked", bool(self.windowFlags() & Qt.WindowType.WindowTransparentForInput))
        ldt.set("position", self.pos())
        return ldt
    
    def load_status(self, status: LDT):
        visible = self.isVisible()
        self.toggle_input(status.get("notClicked", default=False))
        self.setVisible(visible)
        
        self.hasMoved = status.get("hasMoved", default=True)
        pos = clampAllDesktopP(status.get("position", default=QPoint(100, 100)), self.width(), self.height())
        self.setGeometry(pos.x(), pos.y(), self.width(), self.height())
    
    def shortcut_run(self, name):
        pass
    
    def toggle_input(self, state: bool):
        """Меняем флаги только если они реально отличаются"""
        current_flags = self.windowFlags()
        new_flags = current_flags
        
        if state:
            new_flags |= Qt.WindowType.WindowTransparentForInput
        else:
            new_flags &= ~Qt.WindowType.WindowTransparentForInput
        
        if current_flags != new_flags:
            self.setWindowFlags(new_flags)
            self.show()
    
    def mousePressEvent(self, event):
        if self.windowFlags() & Qt.WindowType.WindowTransparentForInput:
            return
        
        if (event.button() == Qt.MouseButton.LeftButton) and self.hasMoved:
            self.dragging = True
            self.offset = event.globalPosition().toPoint() - self.pos()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPosition().toPoint() - self.offset
            new_pos = clampAllDesktopP(new_pos, self.width(), self.height())
            self.move(new_pos)
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event):
        if event.key() in [Qt.Key.Key_Escape, Qt.Key.Key_Backspace]:
            self.parent().keyPressEvent(event)
        return super().keyPressEvent(event)
    
    def highlightBorder(self):
        if not hasattr(self, 'colorize_effect'):
            self.colorize_effect = QGraphicsColorizeEffect(self)
            self.colorize_effect.setColor(QColor(0, 255, 0))
            self.setGraphicsEffect(self.colorize_effect)
        self.colorize_effect.setStrength(0.7)  # Интенсивность
        QTimer.singleShot(500, lambda: self.colorize_effect.setStrength(0))
    
    def shortcut(self, key: str, uname: str):
        self.overlay.registered_shortcut(key, uname, self)
    
    @classmethod
    def createSettingWidget(cls, window: "OWindow", name_plugin: str, parent):
        return PluginSettingWindow(window, name_plugin, parent)
