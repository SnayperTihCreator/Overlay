from PySide6.QtWidgets import QListView
from PySide6.QtCore import Signal, QPoint

from plugins.items import PluginItemRole, PluginItem

from .plugin_model import PluginDataModel
from .plugin_delegate import PluginDelegate


class PluginList(QListView):
    itemChecked = Signal(PluginItem)
    contextMenuRun = Signal(QPoint)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model_data = PluginDataModel()
        self.delegate = PluginDelegate(self)
        self.setModel(self.model_data)
        self.setItemDelegate(self.delegate)
        self.delegate.itemClicked.connect(self.itemChecked.emit)
        self.delegate.contextMenuRun.connect(self.contextMenuRun.emit)
    
    def clear(self):
        self.model_data.clear()
    
    def addItem(self, item: PluginItem):
        if item:
            self.model_data.addItem(item)
    
    def itemAt(self, pos: QPoint) -> PluginItem:
        idx = self.indexAt(pos)
        return self.model().data(idx, PluginItemRole.SELF)
    
    def remove(self, item: PluginItem):
        idx = self.model_data.findIndexItem(item)
        self.model_data.removeItem(idx)
    
    def items(self) -> list[PluginItem]:
        return self.model_data.items()
    
    def findItemBySaveName(self, saveName):
        objs = [item for item in self.model_data.items() if isinstance(item, PluginItem) and item.save_name == saveName]
        if objs:
            return objs[0]
        return None
