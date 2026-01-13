from PySide6.QtCore import QPoint, Qt, Signal, Slot
from PySide6.QtWidgets import QWidget
from ldt import LDT

from core.config import Config
from core.common import APIBaseWidget
from uis.dialogSettingsTemplate_ui import Ui_Form
from utils.fs import getAppPath
from utils.system import open_file_manager



@LDT.serializer(QPoint)
def _(p: QPoint):
    return {"x": p.x(), "y": p.y()}


@LDT.deserializer(QPoint)
def _(data: dict):
    return QPoint(data["x"], data["y"])


class PluginSettingTemplate(QWidget, Ui_Form):
    """
    Общий виджет настроек виджетов, окон и т.д.
    """
    
    saved_configs = Signal()
    
    def __init__(self, obj, name_plugin: str, parent=None):
        """
        Инициализирует виджет настроек.

        :param obj: объект, чьи настройки управляются виджетом (должен быть подклассом APIBaseWidget)
        :type obj: APIBaseWidget
        :param name_plugin: имя плагина в формате "имя_версии"
        :type name_plugin: str
        :param parent: родительский виджет (по умолчанию None)
        :type parent: QWidget, optional
        """
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
    
    @Slot()
    def openFolderPlugin(self):
        """
        Открывает файловый менеджер в папке плагина.
        """
        open_file_manager(getAppPath() / "plugins" / f"{self.obj.config.name}.plugin")
    
    @Slot()
    def confirming(self):
        """
        Слот для подтверждения изменений настроек.
        """
        self.obj.load_status(self.send_data())
        self.saved_configs.emit()
    
    @Slot()
    def canceling(self):
        """
        Слот для отмены изменений настроек.
        """
        self.loader()
    
    def loader(self):
        """
        Загружает текущие значения объекта.
        """
        self.spinBoxX.setValue(self.obj.x())
        self.spinBoxY.setValue(self.obj.y())
    
    def send_data(self) -> LDT:
        """
        Формирует LDT с текущими настройками виджета.

        :return: LDT с настройками
        :rtype: LDT
        """
        ldt = LDT()
        ldt.set("position", QPoint(self.spinBoxX.value(), self.spinBoxY.value()))
        return ldt
    
    def reload_config(self):
        """
        Перезагружает конфигурацию и обновляет интерфейс.
        """
        self.config.reload()
        self.loader()
