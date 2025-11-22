from PySide6.QtCore import Qt, QSize, QRect, QEvent, Signal, QPoint
from PySide6.QtWidgets import QStyledItemDelegate, QApplication, QListView, QStyle
from PySide6.QtGui import QPixmap, QMouseEvent, QPainter, QPen, QColor, QFont

from ColorControl.themeController import ThemeController

from ApiPlugins.pluginItems import PluginItemRole, PluginItem
from .tooltip import ToolTipPlugin

qApp: QApplication


class PluginDelegate(QStyledItemDelegate):
    itemClicked = Signal(PluginItem)
    contextMenuRun = Signal(QPoint)
    
    def __init__(self, list):
        super().__init__()
        self.listView: QListView = list
        self._tooltip = None
    
    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        
        if index.data(PluginItemRole.BadItem):
            self.paintBadItem(painter, option, index)
        else:
            self.paintNormalItem(painter, option, index)
    
    def paintBadItem(self, painter: QPainter, option, index):
        pluginName: str = index.data(Qt.ItemDataRole.DisplayRole)
        error: Exception = index.data(PluginItemRole.Error)
        icon: QPixmap = qApp.style().standardPixmap(QStyle.StandardPixmap.SP_MessageBoxWarning).scaled(48, 48)
        
        rect = option.rect.adjusted(1, 1, -1, -1)
        painter.save()
        painter.setPen(QPen(QColor("#f00"), 4))
        painter.setBrush("#00000000")
        painter.drawRoundedRect(rect, 20, 20)
        painter.restore()
        
        icon_rect = option.rect.adjusted(48, 14, -option.rect.width() + 90, -14)
        painter.drawPixmap(icon_rect, icon)
        
        painter.save()
        font: QFont = option.font
        font.setPointSizeF(font.pointSizeF() * 1.25)
        painter.setFont(font)
        text_rect = option.rect.adjusted(100, 0, -100, 0)
        painter.setPen(ThemeController().color("mainText"))  # Зеленый цвет текста
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, pluginName)
        painter.restore()
        
        painter.setPen(ThemeController().color("altText"))  # Фиолетовый цвет текста
        textClone_rect = option.rect.adjusted(100, 0, 0, 0)
        painter.drawText(textClone_rect, Qt.AlignBottom | Qt.AlignLeft, f"Error: {type(error).__name__}")
    
    def paintNormalItem(self, painter, option, index):
        pluginName: str = index.data(Qt.ItemDataRole.DisplayRole)
        icon: QPixmap = index.data(Qt.ItemDataRole.DecorationRole)
        typePlugin: str = index.data(PluginItemRole.TypePluginRole)
        active: bool = index.data(PluginItemRole.ActiveRole)
        isClone: bool = index.data(PluginItemRole.Duplication)
        if not (icon and not icon.isNull()):
            icon = index.data(PluginItemRole.Icon)
        
        rect = option.rect.adjusted(1, 1, -1, -1)
        painter.save()
        painter.setPen(QPen(ThemeController().color("altText"), 4))
        painter.setBrush("#00000000")
        painter.drawRoundedRect(rect, 20, 20)
        painter.restore()
        
        icon_rect = option.rect.adjusted(48, 14, -option.rect.width() + 90, -14)
        painter.drawPixmap(icon_rect, icon)
        
        if isClone:
            pluginName, idClone = pluginName.rsplit("_", 1)
        else:
            idClone = ""
        
        painter.save()
        font: QFont = option.font
        font.setPointSizeF(font.pointSizeF()*1.25)
        painter.setFont(font)
        text_rect = option.rect.adjusted(100, 0, -1, 0)
        painter.setPen(ThemeController().color("mainText"))
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, pluginName)
        painter.restore()
        
        if isClone:
            textClone_rect = option.rect.adjusted(100, 0, -1, 0)
            painter.drawText(textClone_rect, Qt.AlignBottom | Qt.AlignLeft, f"id: {idClone}(Clone)")
        
        # Рисуем тип плагина (фиолетовый)
        type_rect = option.rect.adjusted(0, 0, -20, -3)
        painter.setPen(ThemeController().color("altText"))  # Фиолетовый цвет текста
        painter.drawText(type_rect, Qt.AlignBottom | Qt.AlignRight, typePlugin)
        
        # Рисуем чекбокс (в виде изображения)
        checkbox_rect = option.rect.adjusted(0, 14, -option.rect.width() + 48, -14)
        checkbox_img = ThemeController().getPathImage("CCheckbox" if active else "UCheckbox")
        pixmap = QPixmap(checkbox_img)
        pixmap = pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(checkbox_rect, pixmap)
    
    def sizeHint(self, option, index):
        # Фиксированная высота элемента, как в QML (60px)
        return QSize(option.rect.width(), 70)
    
    def createEditor(self, parent, option, index):
        return None
    
    def editorEvent(self, event, model, option, index):
        if index.data(PluginItemRole.BadItem):
            return super().editorEvent(event, model, option, index)
        checkbox_rect: QRect = option.rect.adjusted(0, 14, -option.rect.width() + 48, -14)
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
    
    def helpEvent(self, event, view, option, index):
        if event is None or not index.isValid():
            return False
        
        match event.type():
            case QEvent.Type.ToolTip if self.shouldToolTip(event, view, option, index):
                return True
            case QEvent.Type.ToolTip if not self.shouldToolTip(event, view, option, index):
                tooltip_data = index.data(Qt.ItemDataRole.ToolTipRole)
                tooltip = ToolTipPlugin(option.widget, tooltip_data)
                tooltip.move(event.globalPos() - QPoint(25, 20))
                tooltip.show()
                return True
        
        return super().helpEvent(event, view, option, index)
    
    def shouldToolTip(self, event, view, option, index):
        tooltip_rect: QRect = option.rect.adjusted(100, 0, -100, 0)
        return not tooltip_rect.contains(event.pos())
