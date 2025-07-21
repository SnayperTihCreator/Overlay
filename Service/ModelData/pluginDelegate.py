from PySide6.QtCore import Qt, QSize, QRect, QEvent
from PySide6.QtWidgets import QStyledItemDelegate
from PySide6.QtGui import QPixmap, QPalette, QMouseEvent

from APIService.colorize import modulatePixmap

from .pluginModel import PluginItemRole


class PluginDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        self.initStyleOption(option, index)
        
        pluginName = index.data(Qt.ItemDataRole.DisplayRole)
        iconPath = index.data(PluginItemRole.IconPath)
        typePlugin = index.data(PluginItemRole.TypePluginRole)
        active = index.data(PluginItemRole.ActiveRole)
        
        if iconPath:
            icon = modulatePixmap(QPixmap(iconPath), option.palette.color(QPalette.ColorRole.ButtonText))
        else:
            icon = index.data(PluginItemRole.Icon)
        
        icon_rect = option.rect.adjusted(10, 14, -option.rect.width() + 58, -14)
        painter.drawPixmap(icon_rect, icon)
            
        # Рисуем основной текст (зеленый)
        text_rect = option.rect.adjusted(90, 0, -100, 0)
        painter.setPen(option.palette.color(QPalette.ColorRole.Text))  # Зеленый цвет текста
        painter.drawText(text_rect, Qt.AlignVCenter | Qt.AlignLeft, pluginName)
        
        # Рисуем тип плагина (фиолетовый)
        type_rect = option.rect.adjusted(0, 0, -20, -3)
        painter.setPen(option.palette.color(QPalette.ColorRole.ButtonText))  # Фиолетовый цвет текста
        painter.drawText(type_rect, Qt.AlignBottom | Qt.AlignRight, typePlugin)
        
        # Рисуем чекбокс (в виде изображения)
        checkbox_rect = option.rect.adjusted(0, 6, -option.rect.width()+48, -6)
        checkbox_img = ":/base/icons/c_checkbox.png" if active else ":/base/icons/u_checkbox.png"
        pixmap = QPixmap(checkbox_img).scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(checkbox_rect, pixmap)
    
    def sizeHint(self, option, index):
        # Фиксированная высота элемента, как в QML (60px)
        return QSize(option.rect.width(), 60)
    
    def createEditor(self, parent, option, index):
        return None
    
    def editorEvent(self, event, model, option, index):
        checkbox_rect: QRect = option.rect.adjusted(0, 6, -option.rect.width() + 48, -6)
        if isinstance(event, QMouseEvent) and event.type() == QEvent.Type.MouseButtonPress:
            if checkbox_rect.contains(event.pos()):
                active = index.data(PluginItemRole.ActiveRole)
                model.setData(index, not active, PluginItemRole.ActiveRole)
        return super().editorEvent(event, model, option, index)
        