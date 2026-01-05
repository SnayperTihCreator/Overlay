from shiboken6 import isValid
from PySide6.QtCore import QUrl, Qt, qCritical, QEvent, QTimer
from PySide6.QtQml import QQmlEngine
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtQuick import QQuickItem
from PySide6.QtWidgets import QApplication

from gui.themes import ThemeController

from .base import OWindow

qApp: QApplication


class OQMLWindow(OWindow):
    central_widget: QQuickWidget
    
    def __init__(self, config, url, parent=None):
        
        super().__init__(config, parent)
        central_widget = QQuickWidget(self)
        
        central_widget.statusChanged.connect(self._onChangeStatus)
        central_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        central_widget.setClearColor(Qt.GlobalColor.transparent)
        
        self.setCentralWidget(central_widget)
        self.central_widget = central_widget
        
        self.loadPresetData()
        self.loadQmlContent(url)
        
        QTimer.singleShot(0, self.load_config)
    
    def loadQmlContent(self, url: str):
        self.central_widget.setSource(QUrl(url))
    
    def _onChangeStatus(self, status):
        if status == QQuickWidget.Status.Error:
            for error in self.central_widget.errors():
                qCritical(str(error))
    
    def _loadPrivatePresetData(self):
        """Безопасно прокидываем цвета в QML"""
        if not isValid(self.central_widget):
            return
        
        context = self.central_widget.rootContext()
        if context:
            theme = ThemeController()
            context.setContextProperty("mainTextColor", theme.color("mainText"))
            context.setContextProperty("altTextColor", theme.color("altText"))
            
            base_color = theme.color("base")
            context.setContextProperty("baseColor", base_color)
            
            # Создаем копию для альфа-канала, чтобы не испортить основной цвет в теме
            alpha_color = theme.color("base")
            alpha_color.setAlpha(128)
            context.setContextProperty("alphaBaseColor", alpha_color)
    
    def loadPresetData(self) -> QQmlEngine:
        engine = self.central_widget.engine()
        
        self._loadPrivatePresetData()
        
        return engine
    
    def event(self, event: QEvent):
        if event.type() == QEvent.Type.ApplicationPaletteChange:
            self._loadPrivatePresetData()
        return super().event(event)
    
    def getRootQml(self) -> QQuickItem:
        return self.central_widget.rootObject()
    
    def setRootProperty(self, name, value):
        if self.getRootQml():
            self.getRootQml().setProperty(name, value)
    
    def setContextProperty(self, name, value):
        if self.central_widget.rootContext():
            self.central_widget.rootContext().setContextProperty(name, value)
    
    def reload_config(self):
        self.loadPresetData()
        super().reload_config()
