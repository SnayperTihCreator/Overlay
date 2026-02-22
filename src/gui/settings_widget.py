import logging
from enum import IntEnum
from functools import lru_cache

from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QTreeWidgetItem, QCheckBox, QFormLayout, QComboBox, QLabel
from ldt import NexusStore

from gui.themes import ThemeController, DefaultTheme
from core.loaders import ThemeLoader
from core.application import OverlayApplication
from uis.settings_ui import Ui_Setting

logger = logging.getLogger(__name__)


class WebSocketState(IntEnum):
    ENABLED = True
    DISABLED = False


class SettingWidget(QWidget, Ui_Setting):
    webSocketToggled = Signal(bool)
    
    def __init__(self, loaderTheme: ThemeLoader, parent=None):
        super().__init__(parent)
        try:
            logger.debug("Initializing SettingWidget...")
            self.setupUi(self)
            self.pageIds = {}
            self.loaderTheme = loaderTheme
            self.defaultTheme = DefaultTheme()
            
            self.treeWidget.itemClicked.connect(self.handler_item)
            
            # Setup Tree Items
            pageCommon = self.treeWidget.topLevelItem(0)
            pageCommon.setData(0, Qt.ItemDataRole.UserRole, 0)
            
            pageWebSocket = self.treeWidget.topLevelItem(1)
            pageWebSocket.setData(0, Qt.ItemDataRole.UserRole, 1)
            
            # Initialize Pages
            self.initPageCommon()
            self.initPageWebSocket()
            
            OverlayApplication.INSTANCE().bind_translate(self)
            logger.info("SettingWidget initialized successfully")
        
        except Exception as e:
            logger.critical(f"Failed to initialize SettingWidget: {e}", exc_info=True)
    
    def retranslate(self):
        try:
            header = self.treeWidget.headerItem()
            header.setText(0, OverlayApplication.text("settings.title"))
            
            pageCommon = self.treeWidget.topLevelItem(0)
            pageCommon.setText(0, OverlayApplication.text("settings.page.common.title"))
            
            try:
                labelCBST: QLabel = self.boxCommon.labelForField(self.comboBoxSelectTheme)
                if labelCBST:
                    labelCBST.setText(OverlayApplication.text("settings.page.common.theme"))
                
                labelCBSL: QLabel = self.boxCommon.labelForField(self.comboBoxSelectLang)
                if labelCBSL:
                    labelCBSL.setText(OverlayApplication.text("settings.page.common.lang"))
            except AttributeError:
                logger.debug("UI attributes missing during retranslate (fast init)")
            
            pageWebSocket = self.treeWidget.topLevelItem(1)
            pageWebSocket.setText(0, OverlayApplication.text("settings.page.websocket.title"))
        
        except Exception as e:
            logger.error(f"Error during retranslation: {e}", exc_info=True)
    
    # noinspection PyAttributeOutsideInit
    def initPageCommon(self):
        try:
            self.pageIds[0] = self.stackedWidget.indexOf(self.pageCommon)
            self.boxCommon = QFormLayout(self.pageCommon)
            
            self.comboBoxSelectTheme = QComboBox()
            # Note: "Тема" might be replaced by retranslate later
            self.boxCommon.addRow("Theme", self.comboBoxSelectTheme)
            self.comboBoxSelectTheme.currentTextChanged.connect(self._handle_change_theme)
            
            self.comboBoxSelectLang = QComboBox()
            self.boxCommon.addRow("Lang", self.comboBoxSelectLang)
            
            self.comboBoxSelectLang.addItems(OverlayApplication.supported_langs())
            self.comboBoxSelectLang.setCurrentText(OverlayApplication.get_current_lang())
            self.comboBoxSelectLang.currentTextChanged.connect(OverlayApplication.set_language)
            
            self.initComboBoxSelectTheme()
        except Exception as e:
            logger.error(f"Failed to initialize Common Page: {e}", exc_info=True)
    
    def initComboBoxSelectTheme(self):
        try:
            self.comboBoxSelectTheme.clear()
            themes = set()
            
            # Load themes from loader
            for themeInfo in self.loaderTheme.list():
                themes.add(themeInfo.nameTheme)
            
            themes.add("DefaultTheme")
            
            currentThemeName = ThemeController().themeName()
            self.comboBoxSelectTheme.addItems(list(themes))
            
            if currentThemeName:
                self.comboBoxSelectTheme.setCurrentText(currentThemeName)
        
        except Exception as e:
            logger.error(f"Failed to populate theme combo box: {e}", exc_info=True)
    
    # noinspection PyAttributeOutsideInit
    def initPageWebSocket(self):
        try:
            self.pageIds[1] = self.stackedWidget.indexOf(self.pageWebSocket)
            self.boxWebSocket = QFormLayout(self.pageWebSocket)
            self.pWebSocket_checkbox = QCheckBox("WebSocket")
            self.boxWebSocket.addRow(self.pWebSocket_checkbox)
            self.pWebSocket_checkbox.toggled.connect(self.checked_pws_active)
        except Exception as e:
            logger.error(f"Failed to initialize WebSocket Page: {e}", exc_info=True)
    
    def handler_item(self, item: QTreeWidgetItem, column):
        try:
            page = item.data(0, Qt.ItemDataRole.UserRole)
            if page is not None and page in self.pageIds:
                self.stackedWidget.setCurrentIndex(self.pageIds[page])
            else:
                logger.warning(f"Unknown page ID for item: {item.text(0)}")
        except Exception as e:
            logger.error(f"Error handling tree item click: {e}", exc_info=True)
    
    def save_setting(self, setting: NexusStore):
        try:
            logger.info("Saving settings...")
            with setting.group_context("settings"):
                with setting.group_context("websockets"):
                    setting.setValue("active", self.pWebSocket_checkbox.isChecked())
        except Exception as e:
            logger.error(f"Failed to save settings: {e}", exc_info=True)
    
    def restore_setting(self, setting: NexusStore):
        try:
            logger.debug("Restoring settings...")
            with setting.group_context("settings"):
                with setting.group_context("websockets"):
                    self.pWebSocket_checkbox.setChecked(setting.value("active", False))
        except Exception as e:
            logger.error(f"Failed to restore settings: {e}", exc_info=True)
    
    def checked_pws_active(self, state):
        try:
            self.webSocketToggled.emit(state)
            logger.info(f"WebSocket state toggled: {state}")
        except Exception as e:
            logger.error(f"Error emitting WebSocket toggle signal: {e}", exc_info=True)
    
    def _handle_change_theme(self, text):
        try:
            if text == "DefaultTheme":
                ThemeController().setTheme(self.defaultTheme)
                logger.info("Switched to DefaultTheme")
                return
            
            if not text:
                return
            
            theme = self._get_file_theme(text)
            if theme:
                ThemeController().setTheme(theme)
                logger.info(f"Switched to theme: {text}")
            else:
                logger.warning(f"Could not load theme: {text}")
        
        except Exception as e:
            logger.error(f"Failed to change theme to '{text}': {e}", exc_info=True)
    
    @lru_cache(128)
    def _get_file_theme(self, text):
        try:
            themeType = self.loaderTheme.loadTheme(text)
            return themeType()
        except Exception as e:
            logger.error(f"Failed to load theme file '{text}': {e}", exc_info=True)
            return None
    
    def showEvent(self, event, /):
        try:
            self.initComboBoxSelectTheme()
        except Exception as e:
            logger.error(f"Error in showEvent: {e}", exc_info=True)
        return super().showEvent(event)
    
    def setOptions(self, option: IntEnum):
        try:
            match option:
                case WebSocketState.ENABLED if not self.pWebSocket_checkbox.isChecked():
                    self.pWebSocket_checkbox.blockSignals(True)
                    self.pWebSocket_checkbox.setChecked(True)
                    self.pWebSocket_checkbox.blockSignals(False)
                    logger.debug("WebSocket option forced to ENABLED")
                
                case WebSocketState.DISABLED if self.pWebSocket_checkbox.isChecked():
                    self.pWebSocket_checkbox.blockSignals(True)
                    self.pWebSocket_checkbox.setChecked(False)
                    self.pWebSocket_checkbox.blockSignals(False)
                    logger.debug("WebSocket option forced to DISABLED")
        except Exception as e:
            logger.error(f"Failed to set options: {e}", exc_info=True)
