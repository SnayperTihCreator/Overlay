import asyncio
import sys
import typing
import logging
from typing import Optional, Iterator

from PySide6.QtWidgets import (
    QMainWindow,
    QSystemTrayIcon,
    QMenu, QApplication, QLabel
)
from PySide6.QtCore import Qt, QMargins, QEvent, Signal, QSize, QTimer, QCoreApplication
from PySide6.QtGui import QKeyEvent, QAction
from ldt import NexusStore, extra

from core.application import OverlayApplication
from utils.fs import getAppPath
from core.loaders import PluginLoader, ThemeLoader, OverlayAddonsLoader
from core.config import Config
from core.cli import CLInterface
from core.cli_modules.theme_cli import ThemeCLI
from gui.owindow import OWindow
from gui.owidget import OWidget
from gui.plugin_settings import PluginSettingTemplate
from gui.themes import ThemeController
from gui.layouts.auchor_layout import AnchorLayout
from plugins.flags_installer import FlagsInstaller

from plugins.preloaders import PreLoader
from plugins.items import PluginItem, PluginBadItem
from core.service.websocket_server import AppServerControl
from core.metadata import version, metadata
from uis.main_ui import Ui_MainWindow
from core.hotkey_manager import HotkeyManager

if typing.TYPE_CHECKING:
    from gui.splash_screen import GifSplashScreen

from .settings_widget import SettingWidget, WebSocketState

# Initialize logger
logger = logging.getLogger(__name__)

(getAppPath() / "configs").mkdir(exist_ok=True)

qApp: QApplication



PluginWidget: typing.TypeAlias = OWidget | OWindow


class Overlay(QMainWindow, Ui_MainWindow):
    handled_global_shortkey = Signal(str)
    finished_loading = Signal()
    
    def __init__(self, splash: "GifSplashScreen"):
        super().__init__()
        
        try:
            logger.info("Initializing Overlay Window...")
            
            self.flagsInstaller = FlagsInstaller.bind(self)
            self.flagsInstaller.install(Qt.WindowType.Window)
            
            self._load_generator: Optional[Iterator] = None
            self.setObjectName("OverlayMain")
            self.setupUi(self)
            
            # Clean up existing layout if present
            if old_lay := self.centralwidget.layout():
                old_lay.deleteLater()
            
            # Initialize Loaders
            self.themeLoader = ThemeLoader()
            self.pluginLoader = PluginLoader()
            self.oaddons = OverlayAddonsLoader()
            
            # Settings Setup
            settings_path = getAppPath() / "configs" / "settings.toml"
            logger.debug(f"Loading settings from {settings_path}")
            self.settings = NexusStore(settings_path, extra.TomlDriver())
            self.settings.sync()
            
            lang = self.settings.value("language", "en")
            OverlayApplication.set_language(lang)
            
            self.widgets: dict[str, PluginWidget] = {}
            self.interface: dict[str, CLInterface] = {}
            self._splash = splash
            self.shortcuts = {}
            
            self.setMaximumSize(self.screen().size())
            
            # Config & WebSockets
            self.config = Config.configApplication()
            if not self.settings.contains("websockets.in"):
                self.settings.setValue("websockets.in", [8000, 8010])
            
            self.webSocketIn = AppServerControl(self.settings.value("websockets.in"), self)
            self.webSocketIn.action_triggered.connect(self.handler_websockets_shortcut)
            self.webSocketIn.call_cli.connect(self.cliRunner)
            
            # Layout Setup
            self.box = AnchorLayout()
            self.centralwidget.setLayout(self.box)
            
            self.listPlugins.itemChecked.connect(self.updateStateItem)
            self.listPlugins.contextMenuRun.connect(self.contextMenuItem)
            self.listPlugins.setIconSize(QSize(1, 1) * 32)
            self.btnListUpdate.pressed.connect(self.notificationNotImpl)
            
            # Settings Widget
            self.settingWidget = SettingWidget(self.themeLoader, self)
            self.settingWidget.webSocketToggled.connect(self._handler_settings_websocket)
            self.settingWidget.hide()
            
            # Add Widgets to Layout
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
            
            # Configure Buttons
            self.btnSetting.setIconSize(QSize(50, 50))
            self.btnSetting.setFixedSize(60, 60)
            self.btnSetting.setToolTip("Settings")
            ThemeController().registerWidget(self.btnSetting, ":/root/icons/setting.png", "setIcon", "icon", True)
            ThemeController().updateWidget(self.btnSetting)
            
            self.btnStopOverlay.pressed.connect(self.close)
            self.btnStopOverlay.setToolTip("Exit Overlay")
            
            self.btnHide.pressed.connect(self.hideOverlay)
            self.btnHide.setToolTip("Hide Overlay")
            
            self.btnSetting.pressed.connect(lambda: self.settingWidget.setVisible(not (self.settingWidget.isVisible())))
            
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            
            # Resources
            folder_resource = getAppPath() / "resource"
            folder_resource.mkdir(exist_ok=True)
            
            ThemeController().register(self, "overlay/main.css")
            
            self.hide()
            
            # Hotkeys
            self.handled_global_shortkey.connect(self.handled_shortcut)
            self.input_bridge = HotkeyManager()
            
            if not self.settings.contains("shortkey.open"):
                self.settings.setValue("shortkey.open", "shift+alt+o")
            
            self.registered_handler(self.settings.value("shortkey.open"), "toggle_show")
            self.input_bridge.start()
            
            # Tray Icon
            self.tray = QSystemTrayIcon()
            ThemeController().registerWidget(self.tray, "icon:/main/overlay.svg", "setIcon", "icon", True)
            ThemeController().updateWidget(self.tray)
            self.initSystemTray()
            
            if str(getAppPath()) not in sys.path:
                sys.path.append(str(getAppPath()))
            
            self.dialogSettings: typing.Optional[PluginSettingTemplate] = None
            logger.info("Overlay initialization complete")
        
        except Exception as e:
            logger.critical(f"Failed to initialize Overlay: {e}", exc_info=True)
    
    async def update_status(self, text, **context):
        try:
            self._splash.setStatus(await OverlayApplication.atext(text, **context), metadata("App").author)
            for _ in range(20):
                QCoreApplication.processEvents()
                await asyncio.sleep(0.02)
            await asyncio.sleep(0.01)
        except Exception as e:
            logger.error(f"Error updating status: {e}", exc_info=True)
    
    async def ready(self):
        """Sequential loading process"""
        try:
            logger.info("Starting async resource loading...")
            await self.update_status("screen.load_resource")
            
            await asyncio.to_thread(PreLoader.loadConfigs)
            await asyncio.to_thread(self.pluginLoader.load)
            
            await self.updateDataPlugins()
            await asyncio.sleep(0.02)
            
            await self.update_status("screen.load_theme")
            self.loadTheme()
            await asyncio.sleep(0.02)
            
            for type_name, loader_cls in PreLoader.instances.items():
                group_name = f"{type_name}s"
                for target, item in loader_cls.load_group(group_name, self.settings, self):
                    await asyncio.sleep(0.02)
                    await self.update_status("screen.load_plugin", plugin_name=item.save_name)
                    if target:
                        self.setWidgetMemory(item.save_name, target)
                    if item:
                        self.listPlugins.addItem(item)
                    await asyncio.sleep(0.01)
            
            self.settingWidget.restore_setting(self.settings)
            await asyncio.sleep(0.01)
            
            logger.info("Loading finished successfully")
            self.finished_loading.emit()
        
        except Exception as e:
            logger.critical(f"Critical load error: {e}", exc_info=True)
    
    def _handler_settings_websocket(self, state: bool):
        if state:
            self.active_web_sockets()
        else:
            self.deactivate_web_sockets()
    
    def registered_handler(self, comb, name):
        try:
            self.input_bridge.add_hotkey(comb, self.handled_global_shortkey.emit, name)
            logger.debug(f"Registered hotkey handler: {name} ({comb})")
        except Exception as e:
            logger.error(f"Failed to register hotkey {name}: {e}", exc_info=True)
    
    def registered_shortcut(self, comb, name, window):
        self.registered_handler(comb, name)
        self.shortcuts[name] = window
    
    def cliRunner(self, uid, name_int, args):
        try:
            if name_int == "overlay_cli":
                msg = "\n".join(
                    f"* [green]{name}[/green]: [cyan]{inter.__docs_inter__}[/cyan]"
                    for name, inter in self.interface.items()
                )
                self.webSocketIn.sendMassage(uid, msg)
                return
            
            if name_int not in self.interface:
                error = NameError(f"Interface not found: {name_int}")
                self.webSocketIn.sendErrorState(uid, error)
                return
            
            interface: CLInterface = self.interface.get(name_int)
            result = interface.runner(args)
            self.webSocketIn.sendMassage(uid, result)
        
        except Exception as e:
            logger.warning(f"CLI Runner Error: {e}", exc_info=True)
            self.webSocketIn.sendErrorState(uid, e)
    
    def notificationNotImpl(self):
        self.tray.show()
        self.safe_show_notification(
            "Notification",
            "This functionality is not implemented yet.",
        )
        self.tray.hide()
    
    def safe_show_notification(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information):
        """Safe notification showing considering full-screen mode"""
        try:
            if self.isFullScreen():
                self.showMaximized()
                self.tray.showMessage(title, message, icon, 2000)
                QTimer.singleShot(100, self.showFullScreen)
            else:
                self.tray.showMessage(title, message, icon, 2000)
        except Exception as e:
            logger.error(f"Failed to show notification: {e}", exc_info=True)
    
    def active_web_sockets(self):
        try:
            self.settingWidget.setOptions(WebSocketState.ENABLED)
            self.webSocketIn.start()
            logger.info("WebSockets activated")
        except Exception as e:
            logger.error(f"Failed to activate WebSockets: {e}", exc_info=True)
    
    def deactivate_web_sockets(self):
        try:
            self.settingWidget.setOptions(WebSocketState.DISABLED)
            self.webSocketIn.quit()
            logger.info("WebSockets deactivated")
        except Exception as e:
            logger.error(f"Failed to deactivate WebSockets: {e}", exc_info=True)
    
    def loadTheme(self):
        try:
            self.interface["ThemeCLI"] = ThemeCLI(self.themeLoader)
            theme_name = self.settings.value("theme")
            if theme_name is None:
                return
            
            logger.info(f"Loading theme: {theme_name}")
            theme_cli: ThemeCLI = self.interface["ThemeCLI"]
            theme_cli.change(theme_name)
        except Exception as e:
            logger.error(f"Failed to load theme: {e}", exc_info=True)
    
    def saveConfigs(self):
        try:
            logger.info("Saving application configuration...")
            PreLoader.clear(self.settings)
            
            for item in self.listPlugins.items():
                if item.module_type.lower() not in ["window", "widget"]:
                    continue
                PreLoader.save(item, self.settings)
            
            PreLoader.saveConfigs()
            self.settingWidget.save_setting(self.settings)
            self.settings.setValue("theme", ThemeController().themeName())
            self.settings.setValue("language", OverlayApplication.get_current_lang())
            self.settings.sync()
            logger.info("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}", exc_info=True)
    
    def initSystemTray(self):
        try:
            self.tray.setToolTip("Overlay" if getattr(sys, 'frozen', False) else "Overlay(Debug)")
            
            menu = QMenu()
            
            act_show_overlay = menu.addAction("Show overlay")
            act_show_overlay.triggered.connect(self.showOverlay)
            
            act_stop_overlay = menu.addAction("Stop overlay")
            act_stop_overlay.triggered.connect(self.close)
            
            self.tray.setContextMenu(menu)
            self.tray.show()
            self.tray.showMessage(
                "Notification",
                "Program started!",
                QSystemTrayIcon.MessageIcon.Information,
                500,
            )
        except Exception as e:
            logger.error(f"Failed to initialize System Tray: {e}", exc_info=True)
    
    async def updateDataPlugins(self):
        await asyncio.sleep(0.05)
        logger.info("Importing plugins...")
        for i, (plugin_name, module) in enumerate(self.pluginLoader.plugins.items()):
            self._load_single_plugin(plugin_name, module)
            if i % 5 == 0:
                QCoreApplication.processEvents()
                await asyncio.sleep(0)
    
    def _load_single_plugin(self, plugin_name, module):
        try:
            if module is None:
                e = self.pluginLoader.getError(plugin_name)
                logger.error(f"Plugin load error '{plugin_name}': {e}")
                item = PluginBadItem(plugin_name=plugin_name, error=e)
                item.show_info()
                self.listPlugins.addItem(item)
                return
            
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
                logger.debug(f"Successfully imported package: {plugin_name}")
            else:
                logger.warning(f"Package without initialization: {plugin_name}")
        except Exception as e:
            logger.error(f"Error loading single plugin '{plugin_name}': {e}", exc_info=True)
    
    def updateStateItem(self, item: PluginItem):
        try:
            is_obj_create = item.widget is None
            if is_obj_create:
                logger.debug(f"Building widget for: {item.save_name}")
                item.build(self)
                item.widget.ready()
                self.setWidgetMemory(item.save_name, item.widget)
            
            item.widget.dumper.activatedWidget(item.active, item.widget)
            
            if item.active:
                PreLoader.loadConfigInItem(item)
            
            if item.plugin_name:
                PreLoader.save(item, self.settings)
                self.settings.sync()
        
        except Exception as e:
            logger.error(f"Failed to update state for item '{item.save_name}': {e}", exc_info=True)
    
    def setWidgetMemory(self, name: str, widget: PluginWidget):
        self.widgets[name] = widget
        if isinstance(widget, CLInterface):
            self.interface[name] = widget
    
    def onCreateSetting(self, item: PluginItem, win: OWindow | OWidget):
        try:
            logger.info(f"Opening settings for: {item.save_name}")
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
        except Exception as e:
            logger.error(f"Failed to create settings window: {e}", exc_info=True)
    
    def contextMenuItem(self, pos):
        try:
            item = self.listPlugins.itemAt(pos)
            if item is None:
                return
            
            menu = QMenu()
            obj = item.widget
            if obj is None:
                logger.warning(f"Cannot open context menu: Widget is None for {item}")
                return
            
            actions: dict[str, QAction] = PreLoader.createMenu(menu, obj, item)
            
            if "settings" in actions:
                act_settings = actions["settings"]
                act_settings.triggered.connect(lambda: self.onCreateSetting(item, obj))
            
            if "duplicate" in actions:
                act_duplicate = actions["duplicate"]
                act_duplicate.triggered.connect(lambda: self.duplicateWindowPlugin(item))
            
            if "delete_duplicate" in actions:
                act_delete_duplicate = actions["delete_duplicate"]
                act_delete_duplicate.triggered.connect(lambda: self.deleteDuplicateWindowPlugin(item, obj))
            
            menu.exec(self.listPlugins.viewport().mapToGlobal(pos))
        except Exception as e:
            logger.error(f"Error in context menu: {e}", exc_info=True)
    
    def updateConfigsPlugins(self):
        try:
            if self.dialogSettings:
                PreLoader.configs.setValue(self.dialogSettings.save_name, self.dialogSettings.obj.save_status())
                PreLoader.saveConfigs()
        except Exception as e:
            logger.error(f"Failed to update plugin configs: {e}", exc_info=True)
    
    def duplicateWindowPlugin(self, item: PluginItem):
        try:
            logger.info(f"Duplicating plugin: {item.save_name}")
            d_item = OWindow.dumper.duplicate(item)
            self.listPlugins.addItem(d_item)
        except Exception as e:
            logger.error(f"Failed to duplicate plugin: {e}", exc_info=True)
    
    def deleteDuplicateWindowPlugin(self, item, win):
        try:
            logger.info(f"Deleting duplicate plugin: {item.save_name}")
            win.close()
            if item.save_name in self.widgets:
                self.widgets[item.save_name].destroy()
                del self.widgets[item.save_name]
            self.listPlugins.remove(item)
        except Exception as e:
            logger.error(f"Failed to delete duplicate: {e}", exc_info=True)
    
    def handled_shortcut(self, name):
        try:
            match name:
                case "toggle_show":
                    self.hideOverlay() if self.isVisible() else self.showOverlay()
                case _:
                    if name in self.shortcuts:
                        self.shortcuts[name].shortcut_run(name)
            return True
        except Exception as e:
            logger.error(f"Shortcut handler error '{name}': {e}", exc_info=True)
            return False
    
    def handler_websockets_shortcut(self, name, uid):
        try:
            self.handled_shortcut(name)
            self.webSocketIn.sendConfirmState(uid)
        except Exception as e:
            logger.error(f"WebSocket shortcut error: {e}", exc_info=True)
            self.webSocketIn.sendErrorState(uid, e)
    
    def event(self, event):
        if event == QEvent.Type.ShortcutOverride:
            # Removed direct print, using debug level only if needed
            # logger.debug(f"ShortcutOverride event: {event}")
            pass
        return super().event(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        try:
            if event.key() == Qt.Key.Key_Escape:
                event.accept()
                self.close()
            if event.key() == Qt.Key.Key_Backspace:
                event.accept()
                self.hideOverlay()
        except Exception as e:
            logger.error(f"Key press event error: {e}", exc_info=True)
    
    def addWidget(self, widget, anchor=None, margins=None):
        self.box.addWidget(widget, anchor, margins)
    
    def hideOverlay(self):
        logger.debug("Hiding overlay")
        self.hide()
        self.tray.show()
    
    def showOverlay(self):
        try:
            logger.debug("Showing overlay")
            self.flagsInstaller.install(Qt.WindowType.Popup | Qt.WindowType.Window)
            screen_geometry = self.screen().geometry()
            self.setGeometry(screen_geometry)
            self.setFixedSize(screen_geometry.size())
            self.show()
            self.tray.hide()
            self.raise_()
        except Exception as e:
            logger.error(f"Failed to show overlay: {e}", exc_info=True)
    
    def stopOverlay(self):
        try:
            logger.info("Stopping overlay services...")
            self.webSocketIn.quit()
            self.saveConfigs()
            self.settings.sync()
        except Exception as e:
            logger.error(f"Error stopping overlay: {e}", exc_info=True)
    
    def closeEvent(self, event, /):
        logger.info("Closing application...")
        self.stopOverlay()
        self.input_bridge.stop()
        qApp.quit()
        return super().closeEvent(event)
