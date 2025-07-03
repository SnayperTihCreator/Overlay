import sys
import traceback
import zipimport
from pathlib import Path
import types

from PySide6.QtGui import QGuiApplication, QIcon, QPixmap
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import Qt, QUrl, QObject, Slot, qDebug, Property, Signal

QGuiApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL)
app = QGuiApplication(sys.argv)
engineQml = QQmlApplicationEngine()

from plugins.ClockDateWidget import createWindow
from pluginModel import PluginDataModel, PluginItem

import assets_rc


class PythonLog(QObject):
    @Slot(str, result=type(None))
    def log(self, msg):
        print(repr(msg))


class WindowWrapper(QObject):
    def __init__(self):
        super().__init__()
        self.windows = []
    
    @Slot()
    def createWindow(self):
        window = createWindow(engineQml)
        self.windows.append(window)
        window.show()


class OverlayController(QObject):
    def __init__(self):
        super().__init__()
        self.pluginModel = PluginDataModel()
    
    def loadPlugins(self):
        """Загрузка плагинов из папки plugins"""
        plugins_dir = Path(__file__).parent / "plugins"
        plugins_dir.mkdir(exist_ok=True)
        
        for zip_pack in plugins_dir.glob("*.zip"):
            plugin_name = zip_pack.stem
            try:
                importer = zipimport.zipimporter(str(zip_pack))
                module = importer.load_module(plugin_name)
            
            except ImportError as e:
                trace = "".join(traceback.format_exception(e))
                qDebug(f"Ошибка импорта пакета {plugin_name}:\n {trace}")


def handler_error(errors):
    print(*errors, sep="\n")


plog = PythonLog()
windowControl = WindowWrapper()
overlayController = OverlayController()

item = PluginItem(types.ModuleType("ClockDateWidget"), "qrc:/ClockDateWidget/icon.png", "Window")
overlayController.pluginModel.addItem(item)


def print_errors(errors):
    print(*errors, sep="\n")


engineQml.warnings.connect(print_errors)
engineQml.rootContext().setContextProperty("plog", plog)
engineQml.rootContext().setContextProperty("WindowControl", windowControl)
engineQml.rootContext().setContextProperty("OverlayController", overlayController)
engineQml.rootContext().setContextProperty("pluginModel", overlayController.pluginModel)

engineQml.load(QUrl("qml/main.qml"))

app.exec()
