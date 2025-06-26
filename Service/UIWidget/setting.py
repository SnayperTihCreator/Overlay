from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QTreeWidgetItem

from uis.settings_ui import Ui_Setting


class SettingWidget(QWidget, Ui_Setting):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.pws_activateCheckBox.toggled.connect(self.checkes_pws_active)
        self.allHide()
        self.treeWidget.itemClicked.connect(self.handler_item)
    
    def allHide(self):
        for child in self.frame.children():
            if isinstance(child, QWidget):
                child.hide()
    
    def handler_item(self, item: QTreeWidgetItem, column):
        self.allHide()
        obj: QWidget = getattr(self, f"page{item.text(column)}")
        obj.show()
        
    def checkes_pws_active(self, state):
        if state:
            self.parent().active_web_sockets()
        else:
            self.parent().deactive_web_sockets()
            
            
    def setOptions(self, data: dict):
        match data["websoc"]:
            case {"btn": state}:
                if self.pws_activateCheckBox.isChecked() != state:
                    self.pws_activateCheckBox.setChecked(state)
                    