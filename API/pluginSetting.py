from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtWidgets import QWidget
from pydantic import BaseModel, field_serializer, field_validator, ConfigDict

from PathControl import getAppPath
from PathControl.openFolderExplorer import open_file_manager
from API.config import Config
from Common.core import APIBaseWidget
from uis.dialogSettingsTemplate_ui import Ui_Form


class SettingConfigData(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
    
    position: QPoint
    
    # noinspection PyNestedDecorators
    @field_validator("position", mode="before")
    @classmethod
    def check_position(cls, value):
        match value:
            case QPoint() as point:
                return point
            case [x, y]:
                return QPoint(x, y)
            case (x, y):
                return QPoint(x, y)
            case _:
                raise ValueError(f"Данный объект не представить как точку {value!r}")
    
    @field_serializer("position", when_used="json")
    def serialize_position(self, position: QPoint):
        return [position.x(), position.y()]


class PluginSettingTemplate(QWidget, Ui_Form):
    saved_configs = Signal()
    
    def __init__(self, obj, name_plugin: str, parent=None):
        super().__init__(parent, Qt.WindowType.Widget)
        self.config: Config = Config("PluginSetting", "setting")
        self.setObjectName(self.__class__.__name__)
        self.setProperty("class", "OverlayWidget")
        self.setupUi(self)
        
        self.obj: APIBaseWidget = obj
        self.save_name = name_plugin
        name_plugin = "{0}({1})".format(*name_plugin.rsplit("_", 1))
        self.labelNamePlugin.setText(name_plugin)
        
        self.btnOpenFolderPlugin.pressed.connect(self.openFolderPlugin)
        self.buttonBox.accepted.connect(self.confirming)
        self.buttonBox.rejected.connect(self.canceling)
    
    def openFolderPlugin(self):
        open_file_manager(getAppPath() / "plugins" / f"{self.obj.config.name}.plugin")
    
    def confirming(self):
        self.obj.restore_config(self.send_data())
        self.saved_configs.emit()
    
    def canceling(self):
        self.loader()
    
    def loader(self):
        self.spinBoxX.setValue(self.obj.x())
        self.spinBoxY.setValue(self.obj.y())
    
    def send_data(self):
        return {
            "position": QPoint(self.spinBoxX.value(), self.spinBoxY.value())
        }
    
    def reloadConfig(self):
        self.config.reload()
        self.loader()
    