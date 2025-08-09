from PySide6.QtCore import Qt, QSize, QRect, QEvent, Signal, QPoint
from PySide6.QtWidgets import QStyledItemDelegate, QApplication, QListView
from PySide6.QtGui import QPixmap, QPalette, QMouseEvent, QColor

from APIService.colorize import modulatePixmap
from APIService.themeController import ThemeController

from Service.pluginItems import PluginItemRole, PluginItem

qApp: QApplication


class PluginDelegate(QStyledItemDelegate):
    itemClicked = Signal(PluginItem)
    contextMenuRun = Signal(QPoint)
    
    def __init__(self, list):
        super().__init__()
        self.listView: QListView = list
    
    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        
        pluginName: str = index.data(Qt.ItemDataRole.DisplayRole)
        icon: QPixmap = index.data(Qt.ItemDataRole.DecorationRole)
        typePlugin: str = index.data(PluginItemRole.TypePluginRole)
        active: bool = index.data(PluginItemRole.ActiveRole)
        isClone: bool = index.data(PluginItemRole.Duplication)
        if not(icon and not icon.isNull()):
            icon = index.data(PluginItemRole.Icon)
        
        icon_rect = option.rect.adjusted(48, 14, -option.rect.width()+90, -14)
        painter.drawPixmap(icon_rect, icon)
        
        if isClone:
            pluginName, idClone = pluginName.rsplit("_", 1)
            pluginName+="(Clone)"
        else:
            idClone = ""
            
        # Рисуем основной текст (зеленый)
        text_rect = option.rect.adjusted(100, 0, -100, 0)
        painter.setPen(ThemeController().color("mainText"))  # Зеленый цвет текста
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, pluginName)
        
        if isClone:
            textClone_rect = option.rect.adjusted(100, 0, -option.rect.width()+200, 0)
            painter.drawText(textClone_rect, Qt.AlignBottom | Qt.AlignLeft, f"id: {idClone}")
        
        # Рисуем тип плагина (фиолетовый)
        type_rect = option.rect.adjusted(0, 0, -20, -3)
        painter.setPen(ThemeController().color("altText"))  # Фиолетовый цвет текста
        painter.drawText(type_rect, Qt.AlignBottom | Qt.AlignRight, typePlugin)
        
        # Рисуем чекбокс (в виде изображения)
        checkbox_rect = option.rect.adjusted(0, 14, -option.rect.width()+48, -14)
        checkbox_img = ":/base/icons/c_checkbox.png" if active else ":/base/icons/u_checkbox.png"
        pixmap: QPixmap = ThemeController().getImage(checkbox_img, "pixmap", True)
        pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(checkbox_rect, pixmap)
    
    def sizeHint(self, option, index):
        # Фиксированная высота элемента, как в QML (60px)
        return QSize(option.rect.width(), 70)
    
    def createEditor(self, parent, option, index):
        return None
    
    def editorEvent(self, event, model, option, index):
        checkbox_rect: QRect = option.rect.adjusted(0, 6, -option.rect.width() + 48, -6)
        if isinstance(event, QMouseEvent) and event.type() == QEvent.Type.MouseButtonPress:
            if checkbox_rect.contains(event.pos()) and event.button() == Qt.MouseButton.LeftButton:
                active = index.data(PluginItemRole.ActiveRole)
                model.setData(index, not active, PluginItemRole.ActiveRole)
                self.itemClicked.emit(index.data(PluginItemRole.Self))
                return True
            elif event.button() == Qt.MouseButton.RightButton:
                self.contextMenuRun.emit(event.pos())
                return True
        return super().editorEvent(event, model, option, index)
        