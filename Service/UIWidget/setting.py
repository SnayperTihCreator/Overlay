from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QWidget, QTreeWidgetItem, QVBoxLayout, QCheckBox

from uis.settings_ui import Ui_Setting


class SettingWidget(QWidget, Ui_Setting):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pageIds = {}
        self.treeWidget.itemClicked.connect(self.handler_item)
        
        self.initPageCommon()
        self.initPageWebSocket()
    
    # noinspection PyAttributeOutsideInit
    def initPageCommon(self):
        self.pageIds["Common"] = 0
    
    # noinspection PyAttributeOutsideInit
    def initPageWebSocket(self):
        self.pageIds["WebSockets"] = 1
        self.boxWebSocket = QVBoxLayout(self.pageWebSocket)
        self.pWebSocket_checkbox = QCheckBox("WebSocket")
        self.boxWebSocket.addWidget(self.pWebSocket_checkbox)
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
    
    def setOptions(self, data: dict):
        match data["websoc"]:
            case {"btn": state}:
                if self.pWebSocket_checkbox.isChecked() != state:
                    self.pWebSocket_checkbox.setChecked(state)
