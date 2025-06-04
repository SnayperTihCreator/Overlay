from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMainWindow, QGraphicsColorizeEffect, QWidget
from PySide6.QtCore import Qt, QPoint, QTimer, qWarning
from qt_material import apply_stylesheet

from API.config import Config
from API.pluginSettringWidget import PluginSettingsWidget

from .dumper import DraggableWindowDumper
from utils import clampAllDesktopP, clampAllDesktop


class DraggableWindow(QMainWindow):
    dumper = DraggableWindowDumper()

    def __init__(self, config, parent=None):
        super().__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.setProperty("class", "DraggableWindow")

        self.config: Config = config
        # Настройки окна
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
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
        try:
            apply_stylesheet(
                self.central_widget,
                theme="dark_purple.xml",
                extra={
                    "font_size": "14px",
                    "primaryColor": "#8b13a0",
                    "primaryTextColor": "#41fd9f",
                    "secondaryTextColor": "#9ad789",
                },
                css_file=self.config.plugin_path() / self.config.window.styleFile,
            )
        except Exception as e:
            qWarning(str(e))

        self.setStyleSheet("border-radius: 20px")
        self.setWindowOpacity(self.config.window.opacity)

    def reloadConfig(self):
        self.reloading = True
        self.config.reload()

        self.loadConfig()

        self.updateData()
        
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

    def coordinatesWindow(self):
        if self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint:
            return 2
        if self.windowFlags() & Qt.WindowType.WindowStaysOnBottomHint:
            return 0
        return 1

    def setCoordinatesWindow(self, value):
        _position = [
            Qt.WindowType.WindowStaysOnBottomHint,
            Qt.WindowType.Window,
            Qt.WindowType.WindowStaysOnTopHint,
        ]
        pos = _position[self.coordinatesWindow()]
        if pos != value:
            if value == 1:
                return
            if 2 == value:
                self.setWindowFlags(
                    self.windowFlags() & ~Qt.WindowType.WindowStaysOnBottomHint
                )
                self.setWindowFlags(
                    self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint
                )
            else:
                self.setWindowFlags(
                    self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint
                )
                self.setWindowFlags(
                    self.windowFlags() | Qt.WindowType.WindowStaysOnBottomHint
                )

    def savesConfig(self):
        return {
            "TranspFI": int(bool(
                self.windowFlags() & Qt.WindowType.WindowTransparentForInput
            )),
            "mobility": self.hasMoved,
            "transparency": self.windowOpacity(),
            "coordinates": [self.x(), self.y()],
            "position": int(self.coordinatesWindow()),
        }

    def restoreConfig(self, config):
        if not config:
            return
        visible = self.isVisible()
        self.toggle_input(config.TranspFI)
        self.setVisible(visible)
        self.hasMoved = config.mobility
        self.setWindowOpacity(config.transparency)
        try:
            x, y = config.coordinates[0], config.coordinates[1]
        except TypeError:
            x, y = config.coordinates.x(), config.coordinates.y()

        pos = clampAllDesktop(x, y, self.width(), self.height())
        self.setGeometry(pos.x(), pos.y(), self.width(), self.height())
        self.setCoordinatesWindow(config.position)

    def highlightBorder(self):
        self.colorize_effect.setStrength(0.7)  # Интенсивность
        # Через 500 мс выключаем
        QTimer.singleShot(500, lambda: self.colorize_effect.setStrength(0))

    @classmethod
    def createSettingWidget(cls, window: "DraggableWindow", name_plugin: str, parent):
        return PluginSettingsWidget(window, name_plugin, parent)
