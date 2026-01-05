import sys
import traceback
import typing
from typing import Optional, Iterator

from PySide6.QtWidgets import (
    QMainWindow,
    QSystemTrayIcon,
    QMenu, QApplication, QLabel
)
from PySide6.QtCore import Qt, qDebug, QMargins, QEvent, Signal, QSize, qWarning, QTimer, QEventLoop, qCritical
from PySide6.QtGui import QKeyEvent, QAction

from utils.fs import getAppPath
from core.loaders import PluginLoader, ThemeLoader, OverlayAddonsLoader
from core.config import Config
from core.cli import CLInterface
from core.settings import LDTSettings, TomlDriver
from core.cli_modules.theme_cli import ThemeCLI
from gui.owindow import OWindow
from gui.owidget import OWidget
from gui.plugin_settings import PluginSettingTemplate
from gui.themes import ThemeController
from gui.layouts.auchor_layout import AnchorLayout

from plugins.preloaders import PreLoader
from plugins.items import PluginItem, PluginBadItem
from core.service.websocket_server import AppServerControl
from core.metadata import version, metadata
from uis.main_ui import Ui_MainWindow
from core.hotkey_manager import HotkeyManager

if typing.TYPE_CHECKING:
    from gui.splash_screen import GifSplashScreen

from .settings_widget import SettingWidget, WebSocketState

(getAppPath() / "configs").mkdir(exist_ok=True)

qApp: QApplication

# noinspection PyUnresolvedReferences
import core.logger

PluginWidget: typing.TypeAlias = OWidget | OWindow


class Overlay(QMainWindow, Ui_MainWindow):
    handled_global_shortkey = Signal(str)
    finished_loading = Signal()
    
    def __init__(self, splash: "GifSplashScreen"):
        self.defaultFlags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint
        super().__init__(None, self.defaultFlags)
        self._load_generator: Optional[Iterator] = None
        self.setObjectName("OverlayMain")
        self.setupUi(self)
        
        if old_lay := self.centralwidget.layout():
            old_lay.deleteLater()
        
        self.themeLoader = ThemeLoader()
        self.pluginLoader = PluginLoader()
        self.oaddons = OverlayAddonsLoader()
        
        self.settings = LDTSettings(getAppPath()/"configs"/"settings.toml", TomlDriver())
        
        self.widgets: dict[str, PluginWidget] = {}
        self.interface: dict[str, CLInterface] = {}
        self._splash = splash
        
        self.shortcuts = {}
        self.loadTheme()
        
        self.setMaximumSize(self.screen().size())
        
        self.config = Config.configApplication()
        if not self.settings.contains("websockets.in"):
            self.settings.setValue("websockets.in", [8000, 8010])
        self.webSocketIn = AppServerControl(self.settings.value("websockets.in"), self)
        self.webSocketIn.action_triggered.connect(self.handler_websockets_shortcut)
        self.webSocketIn.call_cli.connect(self.cliRunner)
        
        self.box = AnchorLayout()
        self.centralwidget.setLayout(self.box)
        
        self.listPlugins.itemChecked.connect(self.updateStateItem)
        self.listPlugins.contextMenuRun.connect(self.contextMenuItem)
        self.listPlugins.setIconSize(QSize(1, 1) * 32)
        self.btnListUpdate.pressed.connect(self.notificationNotImpl)
        
        self.settingWidget = SettingWidget(self.themeLoader, self)
        self.settingWidget.webSocketToggled.connect(self._handler_settings_websocket)
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
        self.btnSetting.setToolTip("Настройки")
        ThemeController().registerWidget(self.btnSetting, ":/root/icons/setting.png", "setIcon", "icon", True)
        ThemeController().updateWidget(self.btnSetting)
        
        self.btnStopOverlay.pressed.connect(self.close)
        self.btnStopOverlay.setToolTip("Завершить работу Overlay")
        self.btnHide.pressed.connect(self.hideOverlay)
        self.btnHide.setToolTip("Скрыть Overlay")
        self.btnSetting.pressed.connect(lambda: self.settingWidget.setVisible(not (self.settingWidget.isVisible())))
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        
        folder_resource = getAppPath() / "resource"
        folder_resource.mkdir(exist_ok=True)
        
        ThemeController().register(self, "overlay/main.css")
        ThemeController().update()
        
        self.hide()
        
        self.handled_global_shortkey.connect(self.handled_shortcut)
        
        hotkey_name = self.oaddons.find_platform_prefix("hotkey")
        self.input_bridge = HotkeyManager(self.oaddons, hotkey_name)
        if not self.settings.contains("shortkey.open"):
            self.settings.setValue("shortkey.open", "shift+alt+o")
        self.registered_handler(self.settings.value("shortkey.open"), "toggle_show")
        self.input_bridge.start()
        
        self.tray = QSystemTrayIcon()
        ThemeController().registerWidget(self.tray, "icon:/main/overlay.svg", "setIcon", "icon", True)
        ThemeController().updateWidget(self.tray)
        self.initSystemTray()
        
        if str(getAppPath()) not in sys.path:
            sys.path.append(str(getAppPath()))
        
        self.dialogSettings: typing.Optional[PluginSettingTemplate] = None
    
    def ready(self):
        """Запуск пошаговой загрузки"""
        self._load_generator = self._ready_generator()
        self._process_next_step()
    
    def _handler_settings_websocket(self, state: bool):
        if state:
            self.active_web_sockets()
        else:
            self.deactivate_web_sockets()
    
    def _process_next_step(self):
        try:
            next(self._load_generator)
            QTimer.singleShot(10, self._process_next_step)
        except StopIteration:
            self.finished_loading.emit()
        except Exception as e:
            qCritical(f"Critical load error: \n{''.join(traceback.format_exception(e))}")
    
    def _ready_generator(self):
        """Собственно шаги загрузки с yield между ними"""
        self._splash.setStatus("Загрузка с resources", metadata("App").author)
        self.updateDataPlugins()
        yield
        self._splash.setStatus("Загрузка темы", metadata("App").author)
        self.loadTheme()
        yield
        
        for type_name, loader_cls in PreLoader.instances.items():
            group_name = f"{type_name}s"
            for target, item in loader_cls.load_group(group_name, self.settings, self):
                yield
                self._splash.setStatus(f"Загружается {item.save_name}", metadata("App").author)
                if target:
                    self.setWidgetMemory(item.save_name, target)
                if item:
                    self.listPlugins.addItem(item)
                yield
        
        self.settingWidget.restore_setting(self.settings)
        yield
    
    def registered_handler(self, comb, name):
        self.input_bridge.add_hotkey(comb, self.handled_global_shortkey.emit, name)
    
    def registered_shortcut(self, comb, name, window):
        self.registered_handler(comb, name)
        self.shortcuts[name] = window
    
    def cliRunner(self, uid, name_int, args):
        if name_int == "overlay_cli":
            self.webSocketIn.sendMassage(uid, "\n".join(
                f"* [green]{name}[/green]: [cyan]{inter.__docs_inter__}[/cyan]" for name, inter in
                self.interface.items()))
            return
        if name_int not in self.interface:
            self.webSocketIn.sendErrorState(uid, NameError(f"Not find interface {name_int}"))
            return
        try:
            interface: CLInterface = self.interface.get(name_int)
            result = interface.runner(args)
            self.webSocketIn.sendMassage(uid, result)
        except Exception as e:
            qWarning(f"Error: {''.join(traceback.format_exception(e))}")
            self.webSocketIn.sendErrorState(uid, e)
    
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
            self.showMaximized()
            self.tray.showMessage(title, message, icon, 2000)
            QTimer.singleShot(100, self.showFullScreen)
        else:
            self.tray.showMessage(title, message, icon, 2000)
    
    def active_web_sockets(self):
        self.settingWidget.setOptions(WebSocketState.ENABLED)
        self.webSocketIn.start()
    
    def deactivate_web_sockets(self):
        self.settingWidget.setOptions(WebSocketState.DISABLED)
        self.webSocketIn.quit()
    
    def loadTheme(self):
        theme_cli = self.interface["ThemeCLI"] = ThemeCLI(self.themeLoader)
        theme_name = self.settings.value("theme", None)
        if theme_name is None: return
        
        theme_cli.change(theme_name)
    
    def saveConfigs(self):
        PreLoader.clear(self.settings)
        for item in self.listPlugins.items():
            if item.module_type.lower() not in ["window", "widget"]:
                continue
            PreLoader.save(item, self.settings)
        PreLoader.saveConfigs()
        self.settingWidget.save_setting(self.settings)
        self.settings.setValue("theme", ThemeController().themeName())
        self.settings.sync()
        qDebug("Сохранение приложения")
    
    def initSystemTray(self):
        self.tray.setToolTip("Overlay" if getattr(sys, 'frozen', False) else "Overlay(Debug)")
        
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
    
    def is_plugin_loaded(self, module_name: str) -> bool:
        for item in self.listPlugins.items():
            QApplication.processEvents()
            if item.module.__name__ == module_name:
                return True
        return False
    
    def updateDataPlugins(self):
        PreLoader.loadConfigs()
        self.pluginLoader.load()
        
        for plugin_name, module in self.pluginLoader.plugins.items():
            QApplication.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 50)
            if module is None:
                e = self.pluginLoader.getError(plugin_name)
                item = PluginBadItem(plugin_name=plugin_name, error=e)
                item.show_info()
                self.listPlugins.addItem(item)
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
                    if item:
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
        if item.plugin_name:
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
        PreLoader.configs.setValue(self.dialogSettings.save_name, self.dialogSettings.obj.save_status())
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
    
    def event(self, event):
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
