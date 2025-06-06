import importlib
import sys
import traceback

from PySide6.QtWidgets import (
    QMainWindow,
    QSystemTrayIcon,
    QListWidgetItem,
    QMenu,
)
from PySide6.QtCore import Qt, QSettings, qDebug, QMargins, QEvent, Signal
from PySide6.QtGui import QIcon, QKeyEvent, QAction

from uis.main_ui import Ui_MainWindow
from utils import getAppPath
from utils.AnchorLayout import AnchorLayout

from GlobalShortcutControl import HotkeyManager
from API import DraggableWindow, OverlayWidget, BackgroundWorkerManager
from tools_folder import ToolsIniter
from pluginControl import PluginControl

from core import ItemRole, flags

(getAppPath() / "configs").mkdir(exist_ok=True)
import Loggins
import icons_rc


class Overlay(QMainWindow, Ui_MainWindow):
    handled_global_shortkey = Signal(str)
    
    def __init__(self):
        super().__init__(None, flags)
        self.setupUi(self)
        
        if old_lay := self.centralwidget.layout():
            old_lay.deleteLater()
        
        self.box = AnchorLayout()
        self.centralwidget.setLayout(self.box)
        
        self.listPlugins.itemChanged.connect(self.updateStateItem)
        self.listPlugins.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.listPlugins.customContextMenuRequested.connect(self.contextMenuItem)
        
        self.addWidget(
            self.listPlugins,
            [Qt.AnchorPoint.AnchorLeft, Qt.AnchorPoint.AnchorVerticalCenter],
            QMargins(20, 0, 0, 0),
        )
        self.addWidget(
            self.btnHide, [Qt.AnchorPoint.AnchorRight, Qt.AnchorPoint.AnchorTop]
        )
        self.addWidget(
            self.btnStopOverlay, [Qt.AnchorPoint.AnchorLeft, Qt.AnchorPoint.AnchorTop]
        )
        
        self.btnStopOverlay.pressed.connect(self.stopOverlay)
        self.btnHide.pressed.connect(self.hideOverlay)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")
        self.hide()
        
        self.handled_global_shortkey.connect(self.handeled_shortcut)
        
        self.input_bridge = HotkeyManager()
        self.registered_handler("shift+alt+o", "toggle_show")
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
    
    def loadConfigs(self):
        self.settings.beginGroup("windows")
        for win_name in self.settings.childGroups():
            print(win_name)
            items = self.listPlugins.findItems(win_name, Qt.MatchFlag.MatchContains)
            if items:
                self.listPlugins.takeItem(self.listPlugins.row(items[0]))
            win, item = DraggableWindow.dumper.loaded(self.settings, win_name, self)
            self.windows[item.text()] = win
            self.listPlugins.addItem(item)
        self.settings.endGroup()
        self.settings.beginGroup("widgets")
        for wid_name in self.settings.childGroups():
            items = self.listPlugins.findItems(wid_name, Qt.MatchFlag.MatchContains)
            if items:
                self.listPlugins.takeItem(self.listPlugins.row(items[0]))
            wid, item = OverlayWidget.dumper.loaded(self.settings, wid_name, self)
            self.widgets[item.text()] = wid
            self.listPlugins.addItem(item)
        self.settings.endGroup()
    
    def saveConfigs(self):
        self.settings.clear()
        for item in self.listPlugins.findItems("", Qt.MatchFlag.MatchContains):
            if item.data(ItemRole.TYPE_NAME) not in ["Window", "Widget"]: return
            PluginControl.saveConfig(item, self.settings, {"windows": self.windows, "widgets": self.widgets})
    
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
            3000,
        )
    
    def saveTypeWindow(self, item: QListWidgetItem):
        pass
    
    def updateDataPlugins(self):
        self.listPlugins.clear()
        
        PACKAGES_DIR = getAppPath() / "plugins"
        
        if not PACKAGES_DIR.exists():
            PACKAGES_DIR.mkdir(exist_ok=True)
            (PACKAGES_DIR / "__init__.py").touch(exist_ok=True)
        
        for package_dir in PACKAGES_DIR.iterdir():
            if package_dir.is_dir() and (package_dir / "__init__.py").exists():
                package_name = package_dir.name
                try:
                    module = importlib.import_module(f"plugins.{package_name}")
                    for pluginType in self.getModuleTypePlugin(module):
                        match pluginType:
                            case "Window":
                                item = DraggableWindow.dumper.overCreateItem(module, package_name)
                            case "Widget":
                                item = OverlayWidget.dumper.overCreateItem(module, package_name)
                        self.listPlugins.addItem(item)
                    qDebug(f"Успешно импортирован пакет: {package_name}")
                except ImportError as e:
                    trace = "".join(traceback.format_exception(e))
                    qDebug(f"Ошибка импорта пакета {package_name}:\n {trace}")
    
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
    
    def handeled_shortcut(self, name):
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
        self.close()
    
    def closeEvent(self, event, /):
        self.saveConfigs()
        self.settings.sync()
        self.input_bridge.stop()
        qApp.quit()
        return super().closeEvent(event)
