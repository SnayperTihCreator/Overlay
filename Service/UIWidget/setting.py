from functools import lru_cache

from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QWidget, QTreeWidgetItem, QCheckBox, QFormLayout, QComboBox

from uis.settings_ui import Ui_Setting
from ColorControl.themeController import ThemeController
from ColorControl.defaultTheme import DefaultTheme
from PathControl.themeLoader import ThemeLoader


class SettingWidget(QWidget, Ui_Setting):
    def __init__(self, loaderTheme: ThemeLoader, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pageIds = {}
        self.loaderTheme = loaderTheme
        self.defaultTheme = DefaultTheme()
        self.treeWidget.itemClicked.connect(self.handler_item)
        
        self.initPageCommon()
        self.initPageWebSocket()
    
    # noinspection PyAttributeOutsideInit
    def initPageCommon(self):
        self.pageIds["Common"] = self.stackedWidget.indexOf(self.pageCommon)
        self.boxCommon = QFormLayout(self.pageCommon)
        self.comboBoxSelectTheme = QComboBox()
        self.boxCommon.addRow("Тема", self.comboBoxSelectTheme)
        self.comboBoxSelectTheme.currentTextChanged.connect(self._handle_change_theme)
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
        self.pageIds["WebSockets"] = self.stackedWidget.indexOf(self.pageWebSocket)
        self.boxWebSocket = QFormLayout(self.pageWebSocket)
        self.pWebSocket_checkbox = QCheckBox("WebSocket")
        self.boxWebSocket.addRow(self.pWebSocket_checkbox)
        self.pWebSocket_checkbox.toggled.connect(self.checked_pws_active)
    
    def handler_item(self, item: QTreeWidgetItem, column):
        page = item.text(column)
        self.stackedWidget.setCurrentIndex(self.pageIds[page])
    
    def save_setting(self, setting: QSettings):
        setting.beginGroup("setting_overlay")
        try:
            setting.beginGroup("websockets")
            setting.setValue("active", int(self.pWebSocket_checkbox.isChecked()))
            setting.endGroup()
        finally:
            setting.endGroup()
    
    def restore_setting(self, setting: QSettings):
        setting.beginGroup("setting_overlay")
        try:
            setting.beginGroup("websockets")
            webActive = bool(int(setting.value("active", "0", str)))
            self.pWebSocket_checkbox.setChecked(webActive)
            setting.endGroup()
        finally:
            setting.endGroup()
    
    def checked_pws_active(self, state):
        if state:
            self.parent().active_web_sockets()
        else:
            self.parent().deactivate_web_sockets()
    
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
    
    def setOptions(self, data: dict):
        match data["websoc"]:
            case {"btn": state}:
                if self.pWebSocket_checkbox.isChecked() != state:
                    self.pWebSocket_checkbox.setChecked(state)
