from functools import lru_cache
from PySide6.QtCore import Qt, QSize, QRect, QEvent, Signal, QPoint, QCoreApplication
from PySide6.QtWidgets import QStyledItemDelegate, QApplication, QListView, QStyle, QMessageBox
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor

from ColorControl.themeController import ThemeController
from ApiPlugins.pluginItems import PluginItemRole, PluginItem


class PluginDelegate(QStyledItemDelegate):
    itemClicked = Signal(PluginItem)
    contextMenuRun = Signal(QPoint)
    
    def __init__(self, list_view: QListView):
        super().__init__()
        self.listView = list_view
        self.listView.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.ApplicationPaletteChange:
            self.get_cached_pixmap.cache_clear()
            self.get_status_icon.cache_clear()
            self.listView.viewport().update()
        return False  # Не блокируем событие дальше
    
    @lru_cache(maxsize=32)
    def get_cached_pixmap(self, name: str, active: bool, dpr: float) -> QPixmap:
        # name тут для разделения разных типов иконок в кэше
        img_name = "CCheckbox" if active else "UCheckbox"
        if name == "info": img_name = "ErrorInspect"  # Имя текстуры кнопки в теме
        
        path = ThemeController().getPathImage(img_name)
        if not path: return QPixmap()
        pixmap = QPixmap(path)
        size = int(48 * dpr) if name != "info" else int(32 * dpr)
        return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    @lru_cache(maxsize=16)
    def get_status_icon(self, icon_type: QStyle.StandardPixmap, dpr: float) -> QPixmap:
        pixmap = QApplication.style().standardPixmap(icon_type)
        size = int(48 * dpr)
        return pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    
    def paint(self, painter: QPainter, option, index):
        self.initStyleOption(option, index)
        dpr = painter.device().devicePixelRatioF()
        
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        
        if index.data(PluginItemRole.BadItem):
            self.paintBadItem(painter, option, index, dpr)
        else:
            self.paintNormalItem(painter, option, index, dpr)
        
        painter.restore()
    
    def paintNormalItem(self, painter: QPainter, option, index, dpr):
        pluginName = index.data(Qt.ItemDataRole.DisplayRole)
        typePlugin = index.data(PluginItemRole.TypePluginRole)
        active = index.data(PluginItemRole.ActiveRole)
        isClone = index.data(PluginItemRole.Duplication)
        
        # 1. Фон и рамка
        rect = option.rect.adjusted(2, 2, -2, -2)
        color_alt = ThemeController().color("altText")
        painter.setPen(QPen(color_alt, 1))
        painter.drawRoundedRect(rect, 12, 12)
        
        # 2. Чекбокс (из кэша)
        cb_pix = self.get_cached_pixmap("cb", active, dpr)
        cb_rect = QRect(option.rect.left() + 10, option.rect.top() + 11, 48, 48)
        painter.drawPixmap(cb_rect, cb_pix)
        
        # 3. Иконка плагина
        icon = index.data(Qt.ItemDataRole.DecorationRole) or index.data(PluginItemRole.Icon)
        if icon and not icon.isNull():
            icon_rect = QRect(option.rect.left() + 65, option.rect.top() + 11, 48, 48)
            painter.drawPixmap(icon_rect, icon.scaled(48 * dpr, 48 * dpr, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # 4. Текст
        painter.setPen(ThemeController().color("mainText"))
        font = option.font
        font.setBold(True)
        painter.setFont(font)
        
        if isClone and "_" in pluginName:
            pluginName, idClone = pluginName.rsplit("_", 1)
        else:
            idClone = ""
        
        name_rect = option.rect.adjusted(125, 5, -80, -20)
        painter.drawText(name_rect, Qt.AlignVCenter | Qt.AlignLeft, pluginName)
        
        # 5. Подзаголовок и Тип
        painter.setFont(option.font)
        painter.setPen(color_alt)
        if idClone:
            clone_rect = option.rect.adjusted(125, 0, -10, -8)
            painter.drawText(clone_rect, Qt.AlignBottom | Qt.AlignLeft, f"ID: {idClone} (Clone)")
        
        type_rect = option.rect.adjusted(0, 0, -15, -8)
        painter.drawText(type_rect, Qt.AlignBottom | Qt.AlignRight, typePlugin)
    
    def paintBadItem(self, painter: QPainter, option, index, dpr):
        pluginName = index.data(Qt.ItemDataRole.DisplayRole)
        error = index.data(PluginItemRole.Error)
        rect = option.rect.adjusted(2, 2, -2, -2)
        painter.setPen(QPen(QColor("#f44336"), 2))
        painter.drawRoundedRect(rect, 12, 12)
        warn_icon = self.get_status_icon(QStyle.StandardPixmap.SP_MessageBoxWarning, dpr)
        painter.drawPixmap(option.rect.left() + 10, option.rect.top() + 11, warn_icon)
        painter.setPen(ThemeController().color("mainText"))
        painter.drawText(option.rect.adjusted(70, 5, -60, -20), Qt.AlignVCenter | Qt.AlignLeft, pluginName)
        info_pix = self.get_cached_pixmap("info", False, dpr)
        info_rect = QRect(option.rect.right() - 45, option.rect.top() + 19, 32, 32)
        painter.drawPixmap(info_rect, info_pix)
        painter.setPen(QColor("#f44336"))
        painter.drawText(option.rect.adjusted(70, 0, -60, -8), Qt.AlignBottom | Qt.AlignLeft,
                         f"Error: {type(error).__name__}")
    
    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 70)
    
    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.Type.MouseButtonPress:
            pos = event.pos()
            
            # Логика для BadItem (кнопка Инфо)
            if index.data(PluginItemRole.BadItem):
                info_rect = QRect(option.rect.right() - 45, option.rect.top() + 19, 32, 32)
                if info_rect.contains(pos) and event.button() == Qt.MouseButton.LeftButton:
                    self.show_error_dialog(index)
                    return True
            
            # Логика для NormalItem (чекбокс)
            else:
                cb_rect = QRect(option.rect.left() + 10, option.rect.top() + 11, 48, 48)
                if cb_rect.contains(pos) and event.button() == Qt.MouseButton.LeftButton:
                    active = index.data(PluginItemRole.ActiveRole)
                    model.setData(index, not active, PluginItemRole.ActiveRole)
                    self.itemClicked.emit(index.data(PluginItemRole.Self))
                    return True
            
            if event.button() == Qt.MouseButton.RightButton:
                self.contextMenuRun.emit(event.pos())
                return True
        
        return False
    
    def show_error_dialog(self, index):
        """Вызов ванильного диалога с подробностями."""
        plugin_name = index.data(Qt.ItemDataRole.DisplayRole)
        error_obj = index.data(PluginItemRole.Error)
        
        msg = QMessageBox(self.listView)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Ошибка плагина")
        msg.setText(f"<b>{plugin_name}</b> не был загружен.")
        msg.setInformativeText(f"Тип исключения: {type(error_obj).__name__}")
        msg.setDetailedText(str(error_obj))
        msg.setStyleSheet(
            f"QPushButton {{ background-color: {ThemeController().color('altText').name()}; color: white; }}")
        
        msg.exec()
    
    def helpEvent(self, event, view, option, index):
        if index.data(PluginItemRole.BadItem):
            return False
        return super().helpEvent(event, view, option, index)