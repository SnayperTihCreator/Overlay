import sys
import traceback
import zipimport
from pathlib import Path
import types

from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import Qt, QUrl, QObject, Slot, qDebug, Property, Signal
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import QStringListModel

from fs import open_fs

QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseSoftwareOpenGL)
app = QApplication(sys.argv)
engineQml = QQmlApplicationEngine()

from APIService.storageControls import OpenManager
from APIService.tools_folder import ToolsIniter

import Service.globalContext
import Service.Loggins
from Service.PrintManager import PrintManager
from Service.ModelData import PluginDataModel, PluginItem
from Service.GlobalShortcutControl import HotkeyManager

import assets_rc

OpenManager().enable()

from QmlService.providers import PluginImageProvider, ModulateImageProvider
from QmlApi.legacyController import LegacyController

engineQml.addImageProvider("plugins", PluginImageProvider())
engineQml.addImageProvider("modul", ModulateImageProvider())


class PythonLog(QObject):
    @Slot(str, result=type(None))
    def log(self, msg):
        print(repr(msg))


class OverlayController(QObject):
    visibleChanged = Signal()
    handledGlobalShortkey = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.pluginModel = PluginDataModel()
        self.settingModelPy = QStringListModel(
            [
                "Common",
                "WebSockets"
            ]
        )
        self.toolsIniter = ToolsIniter()
        self.input_bridge = HotkeyManager()
        self.handledGlobalShortkey.connect(self.handled_shortcut)
        
        self.registered_handler("shift+alt+o", "toggle_show")
        self.shortcuts = {}
        
        self.toolsIniter.load()
        self.legacyRender = self.initLegacyRender()
        
        self.loadPlugins()
    
    def initLegacyRender(self):
        return LegacyController(self, engineQml)
    
    def handled_shortcut(self, name):
        match name:
            case "toggle_show":
                self.visibleChanged.emit()
    
    def registered_shortcut(self, comb, name, window):
        self.registered_handler(comb, name)
        self.shortcuts[name] = window
    
    def registered_handler(self, comb, name):
        self.input_bridge.add_hotkey(comb, self.handledGlobalShortkey.emit, name)
    
    def loadPlugins(self):
        """Загрузка плагинов из папки plugins"""
        plugins_dir = Path(__file__).parent / "plugins"
        plugins_dir.mkdir(exist_ok=True)
        
        for zip_pack in plugins_dir.glob("*.zip"):
            plugin_name = zip_pack.stem
            try:
                importer = zipimport.zipimporter(str(zip_pack))
                module = importer.load_module(plugin_name)
                for typePlugin in self.getModuleTypePlugin(module):
                    item = PluginItem(module, f"image://plugins/{module.__name__}/icon.png", typePlugin, self.legacyRender)
                    self.pluginModel.addItem(item)
            except ImportError as e:
                trace = "".join(traceback.format_exception(e))
                qDebug(f"Ошибка импорта пакета {plugin_name}:\n {trace}")
    
    @staticmethod
    def getModuleTypePlugin(module):
        result = []
        if hasattr(module, "createWindow"):
            result.append("Window")
        if hasattr(module, "createWidget"):
            result.append("Widget")
        if hasattr(module, "createWorker"):
            result.append("Worker")
        return result
    
    pluginsModeDataChanged = Signal()
    
    def get_pluginsModeData(self):
        return self.pluginModel
    
    pluginsModeData = Property(QObject, get_pluginsModeData, notify=pluginsModeDataChanged)
    
    settingModelChanged = Signal()
    
    def get_settingModel(self):
        return self.settingModelPy
    
    settingModel = Property(QObject, get_settingModel, notify=settingModelChanged)


def handler_error(errors):
    print(*errors, sep="\n")


plog = PythonLog()
overlayController = OverlayController()


def print_errors(errors):
    print(*errors, sep="\n")


engineQml.warnings.connect(print_errors)
engineQml.rootContext().setContextProperty("plog", plog)
engineQml.rootContext().setContextProperty("OverlayController", overlayController)

engineQml.load(QUrl("qml/main.qml"))
with PrintManager() as pm:
    pm.show_caller_info(True)
    app.exec()
