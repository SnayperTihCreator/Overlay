from PySide6.QtWidgets import QListView

from .pluginModel import PluginDataModel, ClonePluginItem, PluginItemRole, PluginItem
from .pluginDelegate import PluginDelegate


class PluginList(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_data = PluginDataModel()
        self.setModel(self.model_data)
        self.setItemDelegate(PluginDelegate())
    
    def clear(self):
        self.model_data.clear()
        
    def addItem(self, item: PluginItem):
        if item:
            self.model_data.addItem(item)