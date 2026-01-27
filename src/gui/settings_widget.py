import asyncio
from enum import IntEnum

from methodtools import lru_cache
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import QWidget, QTreeWidgetItem, QCheckBox, QFormLayout, QComboBox, QLabel
from ldt import NexusStore

from gui.themes import ThemeController, DefaultTheme
from core.loaders import ThemeLoader
from core.application import OverlayApplication
from uis.settings_ui import Ui_Setting


class WebSocketState(IntEnum):
    ENABLED = True
    DISABLED = False


class SettingWidget(QWidget, Ui_Setting):
    webSocketToggled = Signal(bool)
    
    def __init__(self, loaderTheme: ThemeLoader, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pageIds = {}
        self.loaderTheme = loaderTheme
        self.defaultTheme = DefaultTheme()
        self.treeWidget.itemClicked.connect(self.handler_item)
        
        pageCommon = self.treeWidget.topLevelItem(0)
        pageCommon.setData(0, Qt.ItemDataRole.UserRole, 0)
        
        pageWebSocket = self.treeWidget.topLevelItem(1)
        pageWebSocket.setData(0, Qt.ItemDataRole.UserRole, 1)
        
        self.initPageCommon()
        self.initPageWebSocket()
        OverlayApplication.INSTANCE().bind_translate(self)
        
    def retranslate(self):
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
            print("speed init")
        
        pageWebSocket = self.treeWidget.topLevelItem(1)
        pageWebSocket.setText(0, OverlayApplication.text("settings.page.websocket.title"))
    
    # noinspection PyAttributeOutsideInit
    def initPageCommon(self):
        self.pageIds[0] = self.stackedWidget.indexOf(self.pageCommon)
        self.boxCommon = QFormLayout(self.pageCommon)
        
        self.comboBoxSelectTheme = QComboBox()
        self.boxCommon.addRow("Тема", self.comboBoxSelectTheme)
        self.comboBoxSelectTheme.currentTextChanged.connect(self._handle_change_theme)
        
        self.comboBoxSelectLang = QComboBox()
        self.boxCommon.addRow("Lang", self.comboBoxSelectLang)
        
        self.comboBoxSelectLang.addItems(OverlayApplication.supported_langs())
        self.comboBoxSelectLang.setCurrentText(OverlayApplication.get_current_lang())
        self.comboBoxSelectLang.currentTextChanged.connect(OverlayApplication.set_language)
        
        self.initComboBoxSelectTheme()
    
    def initComboBoxSelectTheme(self):
        self.comboBoxSelectTheme.clear()
        themes = set()
        for themeInfo in self.loaderTheme.list():
            themes.add(themeInfo.nameTheme)
        themes.add("DefaultTheme")
        currentThemeName = ThemeController().themeName()
        self.comboBoxSelectTheme.addItems(list(themes))
        self.comboBoxSelectTheme.setCurrentText(currentThemeName)
    
    # noinspection PyAttributeOutsideInit
    def initPageWebSocket(self):
        self.pageIds[1] = self.stackedWidget.indexOf(self.pageWebSocket)
        self.boxWebSocket = QFormLayout(self.pageWebSocket)
        self.pWebSocket_checkbox = QCheckBox("WebSocket")
        self.boxWebSocket.addRow(self.pWebSocket_checkbox)
        self.pWebSocket_checkbox.toggled.connect(self.checked_pws_active)
    
    def handler_item(self, item: QTreeWidgetItem, column):
        page = item.data(0, Qt.ItemDataRole.UserRole)
        self.stackedWidget.setCurrentIndex(self.pageIds[page])
    
    def save_setting(self, setting: NexusStore):
        with setting.group_context("settings"):
            with setting.group_context("websockets"):
                setting.setValue("active", self.pWebSocket_checkbox.isChecked())
    
    def restore_setting(self, setting: NexusStore):
        with setting.group_context("settings"):
            with setting.group_context("websockets"):
                self.pWebSocket_checkbox.setChecked(setting.value("active", False))
    
    def checked_pws_active(self, state):
        self.webSocketToggled.emit(state)
    
    def _handle_change_theme(self, text):
        if text == "DefaultTheme":
            ThemeController().setTheme(self.defaultTheme)
            return
        if not text:
            return
        theme = self._get_file_theme(text)
        ThemeController().setTheme(theme)
    
    @lru_cache(128)
    def _get_file_theme(self, text):
        themeType = self.loaderTheme.loadTheme(text)
        return themeType()
    
    def showEvent(self, event, /):
        self.initComboBoxSelectTheme()
        return super().showEvent(event)
    
    def setOptions(self, option: IntEnum):
        match option:
            case WebSocketState.ENABLED if not self.pWebSocket_checkbox.isChecked():
                self.pWebSocket_checkbox.blockSignals(True)
                self.pWebSocket_checkbox.setChecked(True)
                self.pWebSocket_checkbox.blockSignals(False)
            case WebSocketState.DISABLED if self.pWebSocket_checkbox.isChecked():
                self.pWebSocket_checkbox.blockSignals(True)
                self.pWebSocket_checkbox.setChecked(False)
                self.pWebSocket_checkbox.blockSignals(False)
