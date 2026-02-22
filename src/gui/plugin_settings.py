from __future__ import annotations
import logging

from PySide6.QtCore import QPoint, Qt, Signal, Slot
from PySide6.QtWidgets import QWidget
from ldt import LDT

from core.config import Config
from core.common import APIBaseWidget
from uis.dialogSettingsTemplate_ui import Ui_Form
from utils.fs import getAppPath
from utils.system import open_file_manager

logger = logging.getLogger(__name__)


@LDT.serializer(QPoint)
def _(p: QPoint):
    try:
        return {"x": p.x(), "y": p.y()}
    except Exception as e:
        logger.error(f"Failed to serialize QPoint: {e}", exc_info=True)
        return {"x": 0, "y": 0}


@LDT.deserializer(QPoint)
def _(data: dict):
    try:
        return QPoint(data.get("x", 0), data.get("y", 0))
    except Exception as e:
        logger.error(f"Failed to deserialize QPoint: {e}", exc_info=True)
        return QPoint(0, 0)


class PluginSettingTemplate(QWidget, Ui_Form):
    """
    Generic settings widget for plugins, windows, etc.
    """
    
    saved_configs = Signal()
    
    def __init__(self, obj: APIBaseWidget, name_plugin: str, parent=None):
        """
        Initializes the settings widget.

        :param obj: The object whose settings are managed (must be subclass of APIBaseWidget)
        :param name_plugin: Plugin name in format "name_version"
        :param parent: Parent widget (default None)
        """
        super().__init__(parent, Qt.WindowType.Widget)
        
        try:
            logger.debug(f"Initializing settings for plugin: {name_plugin}")
            
            self.config: Config = Config("PluginSetting", "setting")
            self.setObjectName(self.__class__.__name__)
            self.setProperty("class", "OverlayWidget")
            self.setupUi(self)
            
            self.obj: APIBaseWidget = obj
            self.save_name = name_plugin
            
            # Format name: "plugin_1.0" -> "plugin(1.0)"
            try:
                if "_" in name_plugin:
                    formatted_name = "{0}({1})".format(*name_plugin.rsplit("_", 1))
                else:
                    formatted_name = name_plugin
                self.labelNamePlugin.setText(formatted_name)
            except Exception as e:
                logger.warning(f"Failed to format plugin name '{name_plugin}': {e}")
                self.labelNamePlugin.setText(name_plugin)
            
            self.btnOpenFolderPlugin.pressed.connect(self.openFolderPlugin)
            self.buttonBox.accepted.connect(self.confirming)
            self.buttonBox.rejected.connect(self.canceling)
            
            logger.info(f"Settings widget initialized for {self.save_name}")
        
        except Exception as e:
            logger.error(f"Critical error initializing PluginSettingTemplate: {e}", exc_info=True)
    
    @Slot()
    def openFolderPlugin(self):
        """
        Opens the file manager in the plugin folder.
        """
        try:
            if not self.obj or not self.obj.config:
                logger.warning("Cannot open folder: Object or Config is missing")
                return
            
            plugin_path = getAppPath() / "plugins" / f"{self.obj.config.name}.plugin"
            logger.info(f"Opening plugin folder: {plugin_path}")
            open_file_manager(plugin_path)
        
        except Exception as e:
            logger.error(f"Failed to open plugin folder: {e}", exc_info=True)
    
    @Slot()
    def confirming(self):
        """
        Slot to confirm setting changes.
        """
        try:
            logger.debug(f"Confirming changes for {self.save_name}")
            data = self.send_data()
            self.obj.load_status(data)
            self.saved_configs.emit()
            logger.info("Settings saved successfully")
        except Exception as e:
            logger.error(f"Failed to confirm settings changes: {e}", exc_info=True)
    
    @Slot()
    def canceling(self):
        """
        Slot to cancel setting changes.
        """
        try:
            logger.debug("Canceling changes, reloading previous state")
            self.loader()
        except Exception as e:
            logger.error(f"Failed to cancel changes: {e}", exc_info=True)
    
    def loader(self):
        """
        Loads the current values from the object into the UI.
        """
        try:
            if self.obj:
                self.spinBoxX.setValue(self.obj.x())
                self.spinBoxY.setValue(self.obj.y())
            else:
                logger.warning("Attempted to load settings but target object is None")
        except Exception as e:
            logger.error(f"Failed to load settings into UI: {e}", exc_info=True)
    
    def send_data(self) -> LDT:
        """
        Creates an LDT object with the current widget settings.

        :return: LDT with settings
        """
        try:
            ldt = LDT()
            position = QPoint(self.spinBoxX.value(), self.spinBoxY.value())
            ldt.set("position", position)
            return ldt
        except Exception as e:
            logger.error(f"Failed to generate settings data: {e}", exc_info=True)
            return LDT()
    
    def reload_config(self):
        """
        Reloads configuration and updates the interface.
        """
        try:
            logger.info("Reloading configuration...")
            self.config.reload()
            self.loader()
        except Exception as e:
            logger.error(f"Failed to reload config: {e}", exc_info=True)
