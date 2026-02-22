from __future__ import annotations
import logging
from typing import Optional

from shiboken6 import isValid
from PySide6.QtCore import QUrl, Qt, QEvent, QTimer
from PySide6.QtQml import QQmlEngine
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtQuick import QQuickItem
from PySide6.QtWidgets import QApplication

from gui.themes import ThemeController

from .base import OWindow

logger = logging.getLogger(__name__)

qApp: QApplication


class OQMLWindow(OWindow):
    central_widget: QQuickWidget
    
    def __init__(self, config, url, parent=None):
        super().__init__(config, parent)
        
        try:
            logger.debug("Initializing OQMLWindow...")
            
            # Initialize QQuickWidget
            central_widget = QQuickWidget(self)
            central_widget.statusChanged.connect(self._onChangeStatus)
            central_widget.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
            central_widget.setClearColor(Qt.GlobalColor.transparent)
            
            self.setCentralWidget(central_widget)
            self.central_widget = central_widget
            
            # Load content
            self.loadPresetData()
            self.loadQmlContent(url)
            
            QTimer.singleShot(0, self.load_config)
            
            logger.info("OQMLWindow initialized successfully")
        
        except Exception as e:
            logger.error(f"Failed to initialize OQMLWindow: {e}", exc_info=True)
    
    def loadQmlContent(self, url: str):
        try:
            logger.debug(f"Loading QML content from URL: {url}")
            self.central_widget.setSource(QUrl(url))
        except Exception as e:
            logger.error(f"Failed to load QML content: {e}", exc_info=True)
    
    def _onChangeStatus(self, status):
        try:
            if status == QQuickWidget.Status.Error:
                errors = self.central_widget.errors()
                for error in errors:
                    logger.error(f"QML Runtime Error: {error.toString()}")
                
                if errors:
                    logger.error("QML widget encountered errors during execution")
            elif status == QQuickWidget.Status.Ready:
                logger.debug("QML widget status: Ready")
        
        except Exception as e:
            logger.error(f"Error handling QML status change: {e}", exc_info=True)
    
    def _loadPrivatePresetData(self):
        """Safely inject colors into QML context"""
        try:
            if not isValid(self.central_widget):
                logger.warning("Central widget is invalid, skipping preset data load")
                return
            
            context = self.central_widget.rootContext()
            if context:
                theme = ThemeController()
                context.setContextProperty("mainTextColor", theme.color("mainText"))
                context.setContextProperty("altTextColor", theme.color("altText"))
                
                base_color = theme.color("base")
                context.setContextProperty("baseColor", base_color)
                
                alpha_color = theme.color("base")
                alpha_color.setAlpha(128)
                context.setContextProperty("alphaBaseColor", alpha_color)
                
                logger.debug("QML context properties (colors) updated")
            else:
                logger.warning("Root context not found for QQuickWidget")
        
        except Exception as e:
            logger.error(f"Failed to load private preset data: {e}", exc_info=True)
    
    def loadPresetData(self) -> Optional[QQmlEngine]:
        try:
            engine = self.central_widget.engine()
            self._loadPrivatePresetData()
            return engine
        except Exception as e:
            logger.error(f"Failed to load preset data: {e}", exc_info=True)
            return None
    
    def event(self, event: QEvent):
        try:
            if event.type() == QEvent.Type.ApplicationPaletteChange:
                logger.debug("Palette change detected, reloading presets")
                self._loadPrivatePresetData()
            return super().event(event)
        except Exception as e:
            logger.error(f"Error processing event {event.type()}: {e}", exc_info=True)
            return False
    
    def getRootQml(self) -> Optional[QQuickItem]:
        try:
            return self.central_widget.rootObject()
        except Exception as e:
            logger.error(f"Failed to get root QML object: {e}", exc_info=True)
            return None
    
    def setRootProperty(self, name, value):
        try:
            root = self.getRootQml()
            if root:
                root.setProperty(name, value)
            else:
                logger.warning(f"Cannot set property '{name}': Root QML object is None")
        except Exception as e:
            logger.error(f"Failed to set root property '{name}': {e}", exc_info=True)
    
    def setContextProperty(self, name, value):
        try:
            context = self.central_widget.rootContext()
            if context:
                context.setContextProperty(name, value)
            else:
                logger.warning(f"Cannot set context property '{name}': Root context is None")
        except Exception as e:
            logger.error(f"Failed to set context property '{name}': {e}", exc_info=True)
    
    def reload_config(self):
        try:
            logger.info("Reloading QML Window configuration")
            self.loadPresetData()
            super().reload_config()
        except Exception as e:
            logger.error(f"Failed to reload config: {e}", exc_info=True)