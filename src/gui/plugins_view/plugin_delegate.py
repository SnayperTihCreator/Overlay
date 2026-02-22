from functools import lru_cache
import logging
from PySide6.QtCore import Qt, QSize, QRect, QEvent, Signal, QPoint
from PySide6.QtWidgets import QStyledItemDelegate, QApplication, QListView, QStyle, QMessageBox
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor

from gui.themes import ThemeController
from plugins.items import PluginItemRole, PluginItem

# Initialize logger for this module
logger = logging.getLogger(__name__)


class PluginDelegate(QStyledItemDelegate):
    itemClicked = Signal(PluginItem)
    contextMenuRun = Signal(QPoint)
    
    def __init__(self, list_view: QListView):
        super().__init__()
        self.listView = list_view
        self.listView.installEventFilter(self)
        logger.debug("PluginDelegate initialized")
    
    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.Type.ApplicationPaletteChange:
                logger.debug("Application palette changed, clearing pixmap cache")
                self.get_cached_pixmap.cache_clear()
                self.get_status_icon.cache_clear()
                self.listView.viewport().update()
        except Exception as e:
            logger.error(f"Error processing event filter: {e}", exc_info=True)
        
        return False  # Do not block the event
    
    @lru_cache(maxsize=32)
    def get_cached_pixmap(self, name: str, active: bool, dpr: float) -> QPixmap:
        try:
            # name is used to separate different icon types in cache
            img_name = "CCheckbox" if active else "UCheckbox"
            if name == "info":
                img_name = "ErrorInspect"  # Texture name in theme
            
            path = ThemeController().getPathImage(img_name)
            if not path:
                logger.warning(f"Image path not found for: {img_name}")
                return QPixmap()
            
            pixmap = QPixmap(path)
            size = int(48 * dpr) if name != "info" else int(32 * dpr)
            return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
        except Exception as e:
            logger.error(f"Failed to load cached pixmap '{name}': {e}", exc_info=True)
            return QPixmap()
    
    @lru_cache(maxsize=16)
    def get_status_icon(self, icon_type: QStyle.StandardPixmap, dpr: float) -> QPixmap:
        try:
            pixmap = QApplication.style().standardPixmap(icon_type)
            size = int(48 * dpr)
            return pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio,
                                 Qt.TransformationMode.SmoothTransformation)
        except Exception as e:
            logger.error(f"Failed to get status icon: {e}", exc_info=True)
            return QPixmap()
    
    def paint(self, painter: QPainter, option, index):
        try:
            self.initStyleOption(option, index)
            dpr = painter.device().devicePixelRatioF()
            
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            if index.data(PluginItemRole.IS_BAD):
                self.paintBadItem(painter, option, index, dpr)
            else:
                self.paintNormalItem(painter, option, index, dpr)
            
            painter.restore()
        except Exception as e:
            # Painting errors can flood the log, but we need to capture them
            logger.error(f"Error painting item at row {index.row()}: {e}", exc_info=True)
            painter.restore()
    
    def paintNormalItem(self, painter: QPainter, option, index, dpr):
        try:
            pluginName = index.data(Qt.ItemDataRole.DisplayRole)
            typePlugin = index.data(PluginItemRole.TYPE_ROLE)
            active = index.data(PluginItemRole.ACTIVE_ROLE)
            isClone = index.data(PluginItemRole.IS_DUPLICATE)
            
            # 1. Background and Border
            rect = option.rect.adjusted(2, 2, -2, -2)
            color_alt = ThemeController().color("altText")
            painter.setPen(QPen(color_alt, 1))
            painter.drawRoundedRect(rect, 12, 12)
            
            # 2. Checkbox (from cache)
            cb_pix = self.get_cached_pixmap("cb", active, dpr)
            cb_rect = QRect(option.rect.left() + 10, option.rect.top() + 11, 48, 48)
            painter.drawPixmap(cb_rect, cb_pix)
            
            # 3. Plugin Icon
            icon = index.data(Qt.ItemDataRole.DecorationRole) or index.data(PluginItemRole.ICON)
            if icon and not icon.isNull():
                icon_rect = QRect(option.rect.left() + 65, option.rect.top() + 11, 48, 48)
                painter.drawPixmap(icon_rect, icon.scaled(48 * dpr, 48 * dpr, Qt.AspectRatioMode.KeepAspectRatio,
                                                          Qt.TransformationMode.SmoothTransformation))
            
            # 4. Text
            painter.setPen(ThemeController().color("mainText"))
            font = option.font
            font.setBold(True)
            painter.setFont(font)
            
            if isClone and "_" in pluginName:
                pluginName, idClone = pluginName.rsplit("_", 1)
            else:
                idClone = ""
            
            name_rect = option.rect.adjusted(125, 5, -80, -20)
            painter.drawText(name_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, pluginName)
            
            # 5. Subtitle and Type
            painter.setFont(option.font)
            painter.setPen(color_alt)
            if idClone:
                clone_rect = option.rect.adjusted(125, 0, -10, -8)
                painter.drawText(clone_rect, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                                 f"ID: {idClone} (Clone)")
            
            type_rect = option.rect.adjusted(0, 0, -15, -8)
            painter.drawText(type_rect, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight, typePlugin)
        except Exception as e:
            logger.error(f"Error in paintNormalItem: {e}", exc_info=True)
    
    def paintBadItem(self, painter: QPainter, option, index, dpr):
        try:
            pluginName = index.data(Qt.ItemDataRole.DisplayRole)
            error = index.data(PluginItemRole.ERROR)
            rect = option.rect.adjusted(2, 2, -2, -2)
            
            painter.setPen(QPen(QColor("#f44336"), 2))
            painter.drawRoundedRect(rect, 12, 12)
            
            warn_icon = self.get_status_icon(QStyle.StandardPixmap.SP_MessageBoxWarning, dpr)
            painter.drawPixmap(option.rect.left() + 10, option.rect.top() + 11, warn_icon)
            
            painter.setPen(ThemeController().color("mainText"))
            painter.drawText(option.rect.adjusted(70, 5, -60, -20),
                             Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, pluginName)
            
            info_pix = self.get_cached_pixmap("info", False, dpr)
            info_rect = QRect(option.rect.right() - 45, option.rect.top() + 19, 32, 32)
            painter.drawPixmap(info_rect, info_pix)
            
            painter.setPen(QColor("#f44336"))
            painter.drawText(option.rect.adjusted(70, 0, -60, -8),
                             Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft,
                             f"Error: {type(error).__name__}")
        except Exception as e:
            logger.error(f"Error in paintBadItem: {e}", exc_info=True)
    
    def sizeHint(self, option, index):
        return QSize(option.rect.width(), 70)
    
    def editorEvent(self, event, model, option, index):
        try:
            if event.type() == QEvent.Type.MouseButtonPress:
                pos = event.pos()
                
                # Logic for BadItem (Info button)
                if index.data(PluginItemRole.IS_BAD):
                    info_rect = QRect(option.rect.right() - 45, option.rect.top() + 19, 32, 32)
                    if info_rect.contains(pos) and event.button() == Qt.MouseButton.LeftButton:
                        logger.debug(f"Info button clicked for bad plugin: {index.data(Qt.ItemDataRole.DisplayRole)}")
                        self.show_error_dialog(index)
                        return True
                
                # Logic for NormalItem (Checkbox)
                else:
                    cb_rect = QRect(option.rect.left() + 10, option.rect.top() + 11, 48, 48)
                    if cb_rect.contains(pos) and event.button() == Qt.MouseButton.LeftButton:
                        active = index.data(PluginItemRole.ACTIVE_ROLE)
                        model.setData(index, not active, PluginItemRole.ACTIVE_ROLE)
                        
                        plugin_data = index.data(PluginItemRole.SELF)
                        logger.info(f"Plugin '{plugin_data}' toggled to {'inactive' if active else 'active'}")
                        self.itemClicked.emit(plugin_data)
                        return True
                
                if event.button() == Qt.MouseButton.RightButton:
                    logger.debug("Context menu requested via mouse")
                    self.contextMenuRun.emit(event.pos())
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error handling editor event: {e}", exc_info=True)
            return False
    
    def show_error_dialog(self, index):
        """Displays a dialog with error details."""
        try:
            plugin_name = index.data(Qt.ItemDataRole.DisplayRole)
            error_obj = index.data(PluginItemRole.ERROR)
            
            logger.info(f"Showing error dialog for plugin: {plugin_name}")
            
            msg = QMessageBox(self.listView)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("Plugin Error")
            msg.setText(f"<b>{plugin_name}</b> failed to load.")
            msg.setInformativeText(f"Exception type: {type(error_obj).__name__}")
            msg.setDetailedText(str(error_obj))
            
            # Safe color access
            btn_color = ThemeController().color('altText').name()
            msg.setStyleSheet(
                f"QPushButton {{ background-color: {btn_color}; color: white; }}"
            )
            
            msg.exec()
        except Exception as e:
            logger.error(f"Failed to show error dialog: {e}", exc_info=True)
    
    def helpEvent(self, event, view, option, index):
        try:
            if index.data(PluginItemRole.IS_BAD):
                return False
            return super().helpEvent(event, view, option, index)
        except Exception as e:
            logger.error(f"Error in helpEvent: {e}", exc_info=True)
            return False