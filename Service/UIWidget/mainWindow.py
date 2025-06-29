import zipimport
import sys
import traceback

from PySide6.QtWidgets import (
    QMainWindow,
    QSystemTrayIcon,
    QListWidgetItem,
    QMenu
)
from PySide6.QtCore import Qt, QSettings, qDebug, QMargins, QEvent, Signal, QSize, qWarning
from PySide6.QtGui import QIcon, QKeyEvent, QAction, QColor

from uis.main_ui import Ui_MainWindow

from API import DraggableWindow, OverlayWidget, BackgroundWorkerManager, Config

from APIService import getAppPath, ToolsIniter, modulateIcon, QtResourceDescriptor

from Service.webSocket import AppServerControl
from Service.AnchorLayout import AnchorLayout
from Service.GlobalShortcutControl import HotkeyManager
from Service.pluginControl import PluginControl
from Service.core import ItemRole, flags

from .setting import SettingWidget

(getAppPath() / "configs").mkdir(exist_ok=True)
import Service.Loggins
import assets_rc


class Overlay(QMainWindow, Ui_MainWindow):
    handled_global_shortkey = Signal(str)
    
    def __init__(self):
        super().__init__(None, flags)
        self.setObjectName("OverlayMain")
        self.setupUi(self)
        
        if old_lay := self.centralwidget.layout():
            old_lay.deleteLater()
        
        self.config = Config(getAppPath() / "main.py", "apps")
        self.webSocketIn = AppServerControl(self.config.websockets.IN, self)
        self.webSocketIn.action_triggered.connect(self.handled_shortcut)
        
        self.box = AnchorLayout()
        self.centralwidget.setLayout(self.box)
        
        self.listPlugins.itemChanged.connect(self.updateStateItem)
        self.listPlugins.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listPlugins.customContextMenuRequested.connect(self.contextMenuItem)
        self.listPlugins.setIconSize(QSize(1, 1) * 32)
        
        self.settingWidget = SettingWidget(self)
        self.settingWidget.hide()
        
        self.addWidget(
            self.widgetListPlugin,
            [Qt.AnchorPoint.AnchorLeft, Qt.AnchorPoint.AnchorVerticalCenter],
            QMargins(20, 0, 0, 0),
        )
        self.addWidget(
            self.btnHide, [Qt.AnchorPoint.AnchorRight, Qt.AnchorPoint.AnchorTop]
        )
        self.addWidget(
            self.btnStopOverlay, [Qt.AnchorPoint.AnchorLeft, Qt.AnchorPoint.AnchorTop]
        )
        
        self.addWidget(
            self.btnSetting, [Qt.AnchorPoint.AnchorRight, Qt.AnchorPoint.AnchorBottom],
            QMargins(0, 0, 50, 50)
        )
        
        self.addWidget(
            self.settingWidget, [Qt.AnchorPoint.AnchorHorizontalCenter, Qt.AnchorPoint.AnchorVerticalCenter]
        )
        
        icon = modulateIcon(QIcon(":/main/setting.png"), QColor("#6a0497"))
        
        self.btnSetting.setIconSize(QSize(50, 50))
        self.btnSetting.setIcon(icon)
        self.btnSetting.setFixedSize(60, 60)
        
        self.btnStopOverlay.pressed.connect(self.stopOverlay)
        self.btnHide.pressed.connect(self.hideOverlay)
        self.btnSetting.pressed.connect(lambda: self.settingWidget.setVisible(not (self.settingWidget.isVisible())))
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        with QtResourceDescriptor.open(":/main/overlay.css") as file:
            self.setStyleSheet(file.read())
        self.hide()
        
        self.handled_global_shortkey.connect(self.handled_shortcut)
        
        self.input_bridge = HotkeyManager()
        self.registered_handler(self.config.shortkey.open, "toggle_show")
        self.input_bridge.start()
        
        self.tray = QSystemTrayIcon(QIcon(":/main/overlay.png"))
        self.initSystemTray()
        
        if str(getAppPath()) not in sys.path:
            sys.path.append(str(getAppPath()))
        
        self.tools_folder = ToolsIniter("tools")
        self.tools_folder.load()
        
        self.settings = QSettings("./configs/config.ini", QSettings.Format.IniFormat)
        
        self.windows: dict[str, DraggableWindow] = {}
        self.widgets: dict[str, OverlayWidget] = {}
        self.workers: dict[str, BackgroundWorkerManager] = {}
        
        self.shortcuts = {}
        
        self.dialogSettings = None
        
        self.updateDataPlugins()
        
        self.loadConfigs()
    
    def registered_handler(self, comb, name):
        self.input_bridge.add_hotkey(comb, self.handled_global_shortkey.emit, name)
    
    def registered_shortcut(self, comb, name, window):
        self.registered_handler(comb, name)
        self.shortcuts[name] = window
    
    def active_web_sockets(self):
        self.settingWidget.setOptions({"websoc": {"btn": True}})
        self.webSocketIn.start()
    
    def deactive_web_sockets(self):
        self.settingWidget.setOptions({"websoc": {"btn": False}})
        self.webSocketIn.quit()
    
    def loadConfigs(self):
        self.settings.beginGroup("windows")
        for win_name in self.settings.childGroups():
            items = self.listPlugins.findItems(win_name, Qt.MatchFlag.MatchContains)
            if items:
                self.listPlugins.takeItem(self.listPlugins.row(items[0]))
            try:
                win, item = DraggableWindow.dumper.loaded(self.settings, win_name, self)
                self.windows[item.text()] = win
                self.listPlugins.addItem(item)
            except ModuleNotFoundError:
                self.settings.endGroup()
                qWarning(f"Модуль(Окно) не найден: {win_name}")
        self.settings.endGroup()
        self.settings.beginGroup("widgets")
        for wid_name in self.settings.childGroups():
            items = self.listPlugins.findItems(wid_name, Qt.MatchFlag.MatchContains)
            if items:
                self.listPlugins.takeItem(self.listPlugins.row(items[0]))
            try:
                wid, item = OverlayWidget.dumper.loaded(self.settings, wid_name, self)
                self.widgets[item.text()] = wid
                self.listPlugins.addItem(item)
            except ModuleNotFoundError:
                self.settings.endGroup()
                qWarning(f"Модуль(Виджет) не найден: {wid_name}")
        self.settings.endGroup()
        
        self.settingWidget.restore_setting(self.settings)
    
    def saveConfigs(self):
        self.settings.clear()
        for item in self.listPlugins.findItems("", Qt.MatchFlag.MatchContains):
            if item.data(ItemRole.TYPE_NAME) not in ["Window", "Widget"]: return
            PluginControl.saveConfig(item, self.settings, {"windows": self.windows, "widgets": self.widgets})
        self.settingWidget.save_setting(self.settings)
    
    def initSystemTray(self):
        menu = QMenu()
        
        act_show_overlay = menu.addAction("Show overlay")
        act_show_overlay.triggered.connect(self.showOverlay)
        
        act_stop_overlay = menu.addAction("Stop overlay")
        act_stop_overlay.triggered.connect(self.stopOverlay)
        
        self.tray.setContextMenu(menu)
        
        self.tray.show()
        self.tray.showMessage(
            "Уведомление",
            "Программа запущена!",
            QSystemTrayIcon.MessageIcon.Information,
            1000,
        )
    
    def updateDataPlugins(self):
        self.listPlugins.clear()
        
        PACKAGES_DIR = getAppPath() / "plugins"
        
        if not PACKAGES_DIR.exists():
            PACKAGES_DIR.mkdir(exist_ok=True)
            (PACKAGES_DIR / "__init__.py").touch(exist_ok=True)
        
        for zip_pack in PACKAGES_DIR.glob("*.zip"):
            plugin_name = zip_pack.stem
            importer = zipimport.zipimporter(str(zip_pack))
            
            try:
                module = importer.load_module(plugin_name)
                pluginTypes = self.getModuleTypePlugin(module)
                if pluginTypes:
                    for pluginType in pluginTypes:
                        match pluginType:
                            case "Window":
                                item = DraggableWindow.dumper.overCreateItem(module, plugin_name)
                            case "Widget":
                                item = OverlayWidget.dumper.overCreateItem(module, plugin_name)
                        self.listPlugins.addItem(item)
                else:
                    qDebug(f"Пакет без инициализации: {plugin_name}")
                qDebug(f"Успешно импортирован пакет: {plugin_name}")
            except ImportError as e:
                trace = "".join(traceback.format_exception(e))
                qDebug(f"Ошибка импорта пакета {plugin_name}:\n {trace}")
    
    def hasCreateObj(self, name, type_name):
        match type_name:
            case "Window":
                return not bool(self.windows.get(name, False))
            case "Widget":
                return not bool(self.widgets.get(name, False))
    
    def getCreateObj(self, item):
        match item.data(ItemRole.TYPE_NAME):
            case "Window":
                return self.windows.get(item.text())
            case "Widget":
                return self.widgets.get(item.text())
    
    def updateStateItem(self, item: QListWidgetItem):
        stateVisible = item.checkState()
        is_obj_create = self.hasCreateObj(item.text(), item.data(ItemRole.TYPE_NAME))
        if is_obj_create:
            match item.data(ItemRole.TYPE_NAME):
                case "Window":
                    self.windows[item.text()] = DraggableWindow.dumper.overRunFunction(item.data(ItemRole.MODULE), self)
                case "Widget":
                    self.widgets[item.text()] = OverlayWidget.dumper.overRunFunction(item.data(ItemRole.MODULE), self)
        obj = self.getCreateObj(item)
        if stateVisible == Qt.CheckState.Checked:
            obj.show()
        elif stateVisible == Qt.CheckState.Unchecked:
            obj.hide()
    
    def contextMenuItem(self, pos):
        item = self.listPlugins.itemAt(pos)
        if item is None:
            return
        
        menu = QMenu()
        obj = self.getCreateObj(item)
        if obj is None:
            return
        
        actions: dict[str, QAction] = {}
        
        match item.data(ItemRole.TYPE_NAME):
            case "Window":
                actions = DraggableWindow.dumper.createActionMenu(menu, obj, item)
            case "Widget":
                actions = OverlayWidget.dumper.createActionMenu(menu, obj, item)
        
        act_settings = actions["settings"]
        act_settings.triggered.connect(lambda: self.onCreateSetting(item, obj))
        
        if "duplicate" in actions:
            act_duplicate = actions["duplicate"]
            act_duplicate.triggered.connect(lambda: self.duplicateWindowPlugin(item))
        
        if "delete_duplicate" in actions:
            act_delete_duplicate = actions["delete_duplicate"]
            act_delete_duplicate.triggered.connect(lambda: self.deleteDuplicateWindowPlugin(item, obj))
        
        menu.exec(self.listPlugins.mapToGlobal(pos))
    
    def onCreateSetting(self, item: QListWidgetItem, win: DraggableWindow | OverlayWidget):
        if self.dialogSettings is not None:
            self.box.removeWidget(self.dialogSettings)
            self.dialogSettings.deleteLater()
        
        self.dialogSettings = win.createSettingWidget(win, item.text(), self)
        if self.dialogSettings:
            self.box.addWidget(
                self.dialogSettings,
                [Qt.AnchorPoint.AnchorRight, Qt.AnchorPoint.AnchorVerticalCenter],
            )
            self.dialogSettings.loader()
            self.dialogSettings.show()
    
    def duplicateWindowPlugin(self, item):
        d_item = DraggableWindow.dumper.duplicate(item)
        self.listPlugins.addItem(d_item)
    
    def deleteDuplicateWindowPlugin(self, item, win):
        win.close()
        self.windows[item.text()].destroy()
        del self.windows[item.text()]
        self.listPlugins.takeItem(self.listPlugins.row(item))
    
    def handled_shortcut(self, name):
        match name:
            case "toggle_show":
                self.hideOverlay() if self.isVisible() else self.showOverlay()
            case _:
                if name in self.shortcuts:
                    self.shortcuts[name].shortcut_run(name)
        return True
    
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
    
    def event(self, event, /):
        if event == QEvent.Type.ShortcutOverride:
            print(event)
        return super().event(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            event.accept()
            self.stopOverlay()
        if event.key() == Qt.Key.Key_Backspace:
            event.accept()
            self.hideOverlay()
    
    def addWidget(self, widget, anchor=None, margins=None):
        self.box.addWidget(widget, anchor, margins)
    
    def hideOverlay(self):
        self.setWindowFlags(flags)
        self.hide()
        self.tray.show()
    
    def showOverlay(self):
        self.setWindowFlags(Qt.WindowType.Popup | flags)
        self.showFullScreen()
        self.tray.hide()
    
    def stopOverlay(self):
        self.webSocketIn.quit()
        self.close()
    
    def closeEvent(self, event, /):
        self.saveConfigs()
        self.settings.sync()
        self.input_bridge.stop()
        qApp.quit()
        return super().closeEvent(event)
