import logging
from PySide6.QtWidgets import QFormLayout
from ldt import LDT

from gui.plugin_settings import PluginSettingTemplate

logger = logging.getLogger(__name__)


class PluginSettingWidget(PluginSettingTemplate):
    formLayout: QFormLayout
    
    def __init__(self, obj, name_plugin, parent=None):
        logger.debug(f"Creating settings widget for plugin: {name_plugin}")
        super().__init__(obj, name_plugin, parent)
    
    def send_data(self) -> LDT:
        try:
            ldt = LDT()
            ldt.set("position", self.obj.pos())
            return ldt
        except Exception as e:
            logger.error(f"Error saving settings data for {self.name_plugin}: {e}", exc_info=True)
            return LDT()
