from PySide6.QtCore import QUrl, Qt, qCritical, QEvent
from PySide6.QtGui import QPalette
from PySide6.QtQml import QQmlEngine
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtQuick import QQuickItem
from PySide6.QtWidgets import QApplication

from .base_window import DraggableWindow
from APIService.themeController import ThemeController

qApp: QApplication


class QmlDraggableWindow(DraggableWindow):
    central_widget: QQuickWidget
    
    def __init__(self, config, url, parent=None):
        super().__init__(config, parent)
        
        self.central_widget = QQuickWidget(self)
        self.central_widget.statusChanged.connect(self._onChangeStatus)
        self.loadPresetData()
        self.loadQmlContent(url)
        self.central_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        self.central_widget.setClearColor(Qt.GlobalColor.transparent)
        self.setCentralWidget(self.central_widget)
        
        self.loadConfig()
    
    def loadQmlContent(self, url: str):
        self.central_widget.setSource(QUrl(url))
    
    def _onChangeStatus(self, status):
        if status == QQuickWidget.Status.Error:
            for error in self.central_widget.errors():
                qCritical(str(error))
                
    def _loadPrivatePresetData(self):
        self.setContextProperty("mainTextColor", ThemeController().color("mainText"))
        self.setContextProperty("altTextColor", ThemeController().color("altText"))
        self.setContextProperty("baseColor", ThemeController().color("base"))
        alphaBaseColor = ThemeController().color("base")
        alphaBaseColor.setAlpha(128)
        self.setContextProperty("alphaBaseColor", alphaBaseColor)
    
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
    
    def reloadConfig(self):
        self.loadPresetData()
        super().reloadConfig()
