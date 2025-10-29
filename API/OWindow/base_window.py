import uuid
from abc import ABC

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMainWindow, QGraphicsColorizeEffect, QWidget
from PySide6.QtCore import Qt, QPoint, QTimer
from pydantic import BaseModel

from API.config import Config
from Common.core import APIBaseWidget

from ApiPlugins.windowPreloader import WindowPreLoader
from APIService.clamps import clampAllDesktopP
from ColorControl.themeController import ThemeController

from .pluginSettingWindow import PluginSettingWindow, WindowConfigData


class OWindow(QMainWindow, APIBaseWidget, ABC):
    _config_data_ = WindowConfigData
    
    dumper = WindowPreLoader()
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        
        self.setObjectName(self.__class__.__name__)
        self.setProperty("class", "DraggableWindow")
        self.uid = uuid.uuid4().hex
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process)
        self.time_msec = 1000
        
        self.config: Config = config
        # Настройки окна
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Window
        )
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setGeometry(100, 100, 300, 200)
        
        self.central_widget = QWidget()
        self.setObjectName("CentralWidget")
        self.setCentralWidget(self.central_widget)
        
        # Устанавливаем размер из конфига
        self.loadConfig()
        
        # Для перетаскивания
        self.hasMoved = True
        self.dragging = False
        self.reloading = False
        self.offset = QPoint()
        
        self.colorize_effect = QGraphicsColorizeEffect(self)
        self.colorize_effect.setColor(QColor(0, 255, 0))  # Зеленый
        self.colorize_effect.setStrength(0)  # Изначально выключен
        self.setGraphicsEffect(self.colorize_effect)
    
    def __process__(self):
        self.reloading = False
        
    def __ready__(self): ...
    
    def loadConfig(self):
        width, height = self.config.data.window.width, self.config.data.window.height
        self.setFixedSize(width, height)
        
        ThemeController().register(self, f"plugin://{self.config.name}/{self.config.data.window.styleFile}", False)
        ThemeController().updateUid(self.uid)
        
        self.setWindowOpacity(self.config.data.window.opacity)
    
    def reloadConfig(self):
        self.reloading = True
        self.config.reload()
        
        self.loadConfig()
        
        self.process()
    
    def __save_config__(self) -> dict:
        return dict(
            hasMoved=self.hasMoved,
            notClicked=bool(self.windowFlags() & Qt.WindowType.WindowTransparentForInput),
            position=self.pos()
        )
    
    def save_config(self) -> BaseModel:
        return self._config_data_(**self.__save_config__())
    
    def restore_config(self, config: dict):
        self.__restore_config__(self._config_data_(**config))
    
    def __restore_config__(self, config: BaseModel):
        if not config: return
        visible = self.isVisible()
        self.toggle_input(config.notClicked)
        self.setVisible(visible)
        self.hasMoved = config.hasMoved
        pos = clampAllDesktopP(config.position, self.width(), self.height())
        self.setGeometry(pos.x(), pos.y(), self.width(), self.height())
    
    def shortcut_run(self, name):
        pass
    
    def toggle_input(self, state):
        if not state:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowTransparentForInput
            )
        else:
            self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowTransparentForInput)
        self.show()
    
    def mousePressEvent(self, event):
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
        self.colorize_effect.setStrength(0.7)  # Интенсивность
        # Через 500 мс выключаем
        QTimer.singleShot(500, lambda: self.colorize_effect.setStrength(0))
    
    def shortcut(self, key: str, uname: str):
        self.parent().registered_shortcut(key, uname, self)
    
    @classmethod
    def createSettingWidget(cls, window: "OWindow", name_plugin: str, parent):
        return PluginSettingWindow(window, name_plugin, parent)
