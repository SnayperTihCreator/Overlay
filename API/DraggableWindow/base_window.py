import uuid

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMainWindow, QGraphicsColorizeEffect, QWidget
from PySide6.QtCore import Qt, QPoint, QTimer

from API.config import Config
from Common.core import APIBaseWidget
from API.PluginSetting import PluginSettingWindow

from ApiPlugins.windowPreloader import WindowPreLoader
from APIService.clamps import clampAllDesktop, clampAllDesktopP
from ColorControl.themeController import ThemeController


class DraggableWindow(QMainWindow, APIBaseWidget):
    dumper = WindowPreLoader()

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.setProperty("class", "DraggableWindow")
        self.uid = uuid.uuid4().hex

        self.config: Config = config
        # Настройки окна
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Window
        )

        self.baseflag = self.windowFlags()
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

    def updateData(self):
        self.reloading = False

    def loadConfig(self):
        width, height = self.config.window.width, self.config.window.height
        self.setFixedSize(width, height)
        
        ThemeController().register(self, f"plugin://{self.config.plugin_name}/{self.config.window.styleFile}", False)
        ThemeController().updateUid(self.uid)
        
        self.setWindowOpacity(self.config.window.opacity)

    def reloadConfig(self):
        self.reloading = True
        self.config.reload()

        self.loadConfig()

        self.updateData()
        
    def savesConfig(self):
        return {
            "hasMoved": int(self.hasMoved),
            "noClicked": int(self.windowFlags() & Qt.WindowType.WindowTransparentForInput),
            "position": [self.x(), self.y()]
        }
        
    def shortcut_run(self, name):
        pass

    def toggle_input(self, state):
        if not state:
            self.setWindowFlags(
                self.windowFlags() & ~Qt.WindowType.WindowTransparentForInput
            )
        else:
            self.setWindowFlags(self.baseflag | Qt.WindowType.WindowTransparentForInput)
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
        
    def keyPressEvent(self, event, /):
        if event.key() in [Qt.Key.Key_Escape, Qt.Key.Key_Backspace]:
            self.parent().keyPressEvent(event)
        return super().keyPressEvent(event)

    def restoreConfig(self, config):
        if not config:
            return
        visible = self.isVisible()
        self.toggle_input(config.noClicked)
        self.setVisible(visible)
        self.hasMoved = config.hasMoved
        try:
            x, y = config.position[0], config.position[1]
        except TypeError:
            x, y = config.position.x(), config.position.y()

        pos = clampAllDesktop(x, y, self.width(), self.height())
        self.setGeometry(pos.x(), pos.y(), self.width(), self.height())

    def highlightBorder(self):
        self.colorize_effect.setStrength(0.7)  # Интенсивность
        # Через 500 мс выключаем
        QTimer.singleShot(500, lambda: self.colorize_effect.setStrength(0))

    @classmethod
    def createSettingWidget(cls, window: "DraggableWindow", name_plugin: str, parent):
        return PluginSettingWindow(window, name_plugin, parent)
