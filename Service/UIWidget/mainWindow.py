import sys
import traceback
import typing

from PySide6.QtWidgets import (
    QMainWindow,
    QSystemTrayIcon,
    QMenu, QApplication, QLabel
)
from PySide6.QtCore import Qt, QSettings, qDebug, QMargins, QEvent, Signal, QSize, qWarning, QTimer
from PySide6.QtGui import QKeyEvent, QAction

from uis.main_ui import Ui_MainWindow

from API import OWindow, OWidget, BackgroundWorkerManager, Config, CLInterface

from PathControl import getAppPath
from PathControl.themeLoader import ThemeLoader
from PathControl.pluginLoader import PluginLoader
from PathControl.overlayAddonsLoader import OverlayAddonsLoader

from Service.webSocket import AppServerControl
from Service.metadata import version
from Service.AnchorLayout import AnchorLayout
from Service.GlobalShortcutControl import HotkeyManager
from ApiPlugins.preloader import PreLoader
from ApiPlugins.pluginItems import PluginItem
from API.PlugSetting import PluginSettingTemplate
from APIService.themeCLI import ThemeCLI

from ColorControl.themeController import ThemeController

from .setting import SettingWidget

(getAppPath() / "configs").mkdir(exist_ok=True)

qApp: QApplication

# noinspection PyUnresolvedReferences
import Service.Loggins

PluginWidget: typing.TypeAlias = OWidget | OWindow | BackgroundWorkerManager


class Overlay(QMainWindow, Ui_MainWindow):
    handled_global_shortkey = Signal(str)
    
    def __init__(self):
        self.defaultFlags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        super().__init__(None, self.defaultFlags)
        self.setObjectName("OverlayMain")
        self.setupUi(self)
        
        if old_lay := self.centralwidget.layout():
            old_lay.deleteLater()
        
        self.setMaximumSize(self.screen().size())
        
        self.config = Config.configApplication()
        self.webSocketIn = AppServerControl(self.config.data.websockets.IN, self)
        self.webSocketIn.action_triggered.connect(self.handler_websockets_shortcut)
        self.webSocketIn.call_cli.connect(self.cliRunner)
        
        self.box = AnchorLayout()
        self.centralwidget.setLayout(self.box)
        
        self.listPlugins.itemChecked.connect(self.updateStateItem)
        self.listPlugins.contextMenuRun.connect(self.contextMenuItem)
        self.listPlugins.setIconSize(QSize(1, 1) * 32)
        self.btnListUpdate.pressed.connect(self.notificationNotImpl)
        
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
        
        versionLabel = QLabel(version("App"), self)
        self.addWidget(
            versionLabel, [Qt.AnchorPoint.AnchorLeft, Qt.AnchorPoint.AnchorBottom],
            QMargins(0, 0, 100, 50)
        )
        
        self.btnSetting.setIconSize(QSize(50, 50))
        self.btnSetting.setFixedSize(60, 60)
        ThemeController().registerWidget(self.btnSetting, ":/root/icons/setting.png", "setIcon", "icon", True)
        ThemeController().updateWidget(self.btnSetting)
        
        self.btnStopOverlay.pressed.connect(self.close)
        self.btnHide.pressed.connect(self.hideOverlay)
        self.btnSetting.pressed.connect(lambda: self.settingWidget.setVisible(not (self.settingWidget.isVisible())))
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        folder_resource = getAppPath() / "resource"
        folder_resource.mkdir(exist_ok=True)
        
        ThemeController().register(self, "overlay/main.css")
        ThemeController().update()
        
        self.themeLoader = ThemeLoader()
        self.pluginLoader = PluginLoader()
        self.oaddons = OverlayAddonsLoader()
        
        self.hide()
        
        self.handled_global_shortkey.connect(self.handled_shortcut)
        
        hotkey_name = self.oaddons.find_platform_prefix("hotkey")
        self.input_bridge = HotkeyManager(self.oaddons, hotkey_name)
        self.registered_handler(self.config.data.shortkey.open, "toggle_show")
        self.input_bridge.start()
        
        self.tray = QSystemTrayIcon()
        ThemeController().registerWidget(self.tray, "icon:/main/overlay.svg", "setIcon", "icon", True)
        ThemeController().updateWidget(self.tray)
        self.initSystemTray()
        
        if str(getAppPath()) not in sys.path:
            sys.path.append(str(getAppPath()))
        
        self.settings = QSettings("./configs/settings.ini", QSettings.Format.IniFormat)
        
        self.widgets: dict[str, PluginWidget] = {}
        self.interface: dict[str, CLInterface] = {}
        
        self.shortcuts = {}
        
        self.dialogSettings: typing.Optional[PluginSettingTemplate] = None
    
    def ready(self):
        self.updateDataPlugins()
        self.loadConfigs()
        self.loadTheme()
    
    def registered_handler(self, comb, name):
        self.input_bridge.add_hotkey(comb, self.handled_global_shortkey.emit, name)
    
    def registered_shortcut(self, comb, name, window):
        self.registered_handler(comb, name)
        self.shortcuts[name] = window
    
    def cliRunner(self, uid, name_int, args):
        if name_int == "overlay_cli":
            self.webSocketIn.sendMassage(uid, " ".join(self.interface.keys()))
            return
        if name_int not in self.interface:
            self.webSocketIn.sendErrorState(uid, NameError(f"Not find interface {name_int}"))
            return
        interface: CLInterface = self.interface.get(name_int)
        result = interface.runner(args)
        self.webSocketIn.sendMassage(uid, result)
    
    def notificationNotImpl(self):
        self.tray.show()
        self.safe_show_notification(
            "Уведомление",
            "Данный функционал не реализован",
        )
        self.tray.hide()
    
    def safe_show_notification(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information):
        """Безопасный показ уведомления с учётом полноэкранного режима"""
        if self.isFullScreen():
            # Временный выход из полноэкранного режима
            self.showMaximized()
            self.tray.showMessage(title, message, icon, 2000)
            QTimer.singleShot(100, self.showFullScreen)
        else:
            self.tray.showMessage(title, message, icon, 2000)
    
    def active_web_sockets(self):
        self.settingWidget.setOptions({"websoc": {"btn": True}})
        self.webSocketIn.start()
    
    def deactivate_web_sockets(self):
        self.settingWidget.setOptions({"websoc": {"btn": False}})
        self.webSocketIn.quit()
    
    def loadTheme(self):
        self.interface["ThemeCLI"] = ThemeCLI(self.themeLoader)
        
        themeName = self.settings.value("theme", None)
        if themeName is None:
            return
        
        if themeName == "DefaultTheme":
            # noinspection PyUnresolvedReferences
            self.interface["ThemeCLI"].action_default_change()
        else:
            # noinspection PyUnresolvedReferences
            self.interface["ThemeCLI"].action_change(themeName)
    
    def loadConfigs(self):
        self.settings.beginGroup("windows")
        for win_name in self.settings.childGroups():
            qApp.processEvents()
            item = self.listPlugins.findItemBySaveName(win_name)
            if item is not None:
                self.listPlugins.remove(item)
            try:
                win, item = OWindow.dumper.loaded(self.settings, win_name, self)
                self.setWidgetMemory(item.save_name, win)
                self.listPlugins.addItem(item)
            except ModuleNotFoundError:
                self.settings.endGroup()
                qWarning(f"Модуль(Окно) не найден: {win_name}")
        self.settings.endGroup()
        self.settings.beginGroup("widgets")
        for wid_name in self.settings.childGroups():
            qApp.processEvents()
            item = self.listPlugins.findItemBySaveName(wid_name)
            if item:
                self.listPlugins.remove(item)
            try:
                wid, item = OWidget.dumper.loaded(self.settings, wid_name, self)
                self.setWidgetMemory(item.save_name, wid)
                self.listPlugins.addItem(item)
            except ModuleNotFoundError:
                self.settings.endGroup()
                qWarning(f"Модуль(Виджет) не найден: {wid_name}")
        self.settings.endGroup()
        
        self.settingWidget.restore_setting(self.settings)
    
    def saveConfigs(self):
        self.settings.clear()
        for item in self.listPlugins.items():
            if item.typeModule not in ["Window", "Widget"]:
                continue
            PreLoader.save(item, self.settings)
        PreLoader.saveConfigs()
        self.settingWidget.save_setting(self.settings)
        self.settings.setValue("theme", ThemeController().themeName())
        self.settings.sync()
        qDebug("Сохранение приложения")
    
    def initSystemTray(self):
        self.tray.setToolTip("Overlay")
        
        menu = QMenu()
        
        act_show_overlay = menu.addAction("Show overlay")
        act_show_overlay.triggered.connect(self.showOverlay)
        
        act_stop_overlay = menu.addAction("Stop overlay")
        act_stop_overlay.triggered.connect(self.close)
        
        self.tray.setContextMenu(menu)
        
        self.tray.show()
        self.tray.showMessage(
            "Уведомление",
            "Программа запущена!",
            QSystemTrayIcon.MessageIcon.Information,
            500,
        )
    
    def updateDataPlugins(self):
        self.listPlugins.clear()
        
        PreLoader.loadConfigs()
        self.pluginLoader.load()
        
        for plugin_name, module in self.pluginLoader.plugins.items():
            qApp.processEvents()
            if module is None:
                e = self.pluginLoader.getError(plugin_name)
                trace = "".join(traceback.format_exception(e))
                qDebug(f"Ошибка импорта пакета {plugin_name}:\n {trace}")
                continue
            pluginTypes = self.pluginLoader.getTypes(plugin_name)
            if pluginTypes:
                for pluginType in pluginTypes:
                    item = None
                    match pluginType:
                        case "Window":
                            item = OWindow.dumper.overCreateItem(module)
                        case "Widget":
                            item = OWidget.dumper.overCreateItem(module)
                    self.listPlugins.addItem(item)
            else:
                qDebug(f"Пакет без инициализации: {plugin_name}")
            qDebug(f"Успешно импортирован пакет: {plugin_name}")
    
    def updateStateItem(self, item: PluginItem):
        is_obj_create = item.widget is None
        if is_obj_create:
            item.build(self)
            item.widget.ready()
            # noinspection PyTypeChecker
            self.setWidgetMemory(item.save_name, item.widget)
        item.widget.dumper.activatedWidget(item.active, item.widget)
        if item.active:
            PreLoader.loadConfigInItem(item)
        PreLoader.save(item, self.settings)
        self.settings.sync()
    
    def setWidgetMemory(self, name: str, widget: PluginWidget):
        self.widgets[name] = widget
        if isinstance(widget, CLInterface):
            self.interface[name] = widget
    
    def onCreateSetting(self, item: PluginItem, win: OWindow | OWidget):
        if self.dialogSettings is not None:
            self.dialogSettings.saved_configs.disconnect(self.updateConfigsPlugins)
            self.box.removeWidget(self.dialogSettings)
            self.dialogSettings.deleteLater()
        
        self.dialogSettings = win.createSettingWidget(win, item.save_name, self)
        self.dialogSettings.saved_configs.connect(self.updateConfigsPlugins)
        if self.dialogSettings:
            self.box.addWidget(
                self.dialogSettings,
                [Qt.AnchorPoint.AnchorRight, Qt.AnchorPoint.AnchorVerticalCenter],
            )
            self.dialogSettings.loader()
            self.dialogSettings.show()
    
    def contextMenuItem(self, pos):
        item = self.listPlugins.itemAt(pos)
        if item is None:
            return
        
        menu = QMenu()
        obj = item.widget
        if obj is None:
            return
        
        actions: dict[str, QAction] = PreLoader.createMenu(menu, obj, item)
        
        act_settings = actions["settings"]
        act_settings.triggered.connect(lambda: self.onCreateSetting(item, obj))
        
        if "duplicate" in actions:
            act_duplicate = actions["duplicate"]
            act_duplicate.triggered.connect(lambda: self.duplicateWindowPlugin(item))
        
        if "delete_duplicate" in actions:
            act_delete_duplicate = actions["delete_duplicate"]
            act_delete_duplicate.triggered.connect(lambda: self.deleteDuplicateWindowPlugin(item, obj))
        
        menu.exec(self.listPlugins.viewport().mapToGlobal(pos))
    
    def updateConfigsPlugins(self):
        config = self.dialogSettings.obj.save_config().model_dump(mode="json")
        PreLoader.configs[self.dialogSettings.save_name] = config
        PreLoader.saveConfigs()
    
    def duplicateWindowPlugin(self, item: PluginItem):
        d_item = OWindow.dumper.duplicate(item)
        self.listPlugins.addItem(d_item)
    
    def deleteDuplicateWindowPlugin(self, item, win):
        win.close()
        self.widgets[item.save_name].destroy()
        del self.widgets[item.save_name]
        self.listPlugins.remove(item)
    
    def handled_shortcut(self, name):
        match name:
            case "toggle_show":
                self.hideOverlay() if self.isVisible() else self.showOverlay()
            case _:
                if name in self.shortcuts:
                    self.shortcuts[name].shortcut_run(name)
        return True
    
    def handler_websockets_shortcut(self, name, uid):
        try:
            self.handled_shortcut(name)
            self.webSocketIn.sendConfirmState(uid)
        except Exception as e:
            self.webSocketIn.sendErrorState(uid, e)
    
    def event(self, event, /):
        if event == QEvent.Type.ShortcutOverride:
            print(event)
        return super().event(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Escape:
            event.accept()
            self.close()
        if event.key() == Qt.Key.Key_Backspace:
            event.accept()
            self.hideOverlay()
    
    def addWidget(self, widget, anchor=None, margins=None):
        self.box.addWidget(widget, anchor, margins)
    
    def hideOverlay(self):
        self.setWindowFlags(self.defaultFlags)
        self.hide()
        self.tray.show()
    
    def showOverlay(self):
        self.setWindowFlags(Qt.WindowType.Popup | self.defaultFlags)
        self.showFullScreen()
        self.tray.hide()
    
    def stopOverlay(self):
        self.webSocketIn.quit()
        self.saveConfigs()
        self.settings.sync()
    
    def closeEvent(self, event, /):
        self.stopOverlay()
        self.input_bridge.stop()
        qApp.quit()
        return super().closeEvent(event)
