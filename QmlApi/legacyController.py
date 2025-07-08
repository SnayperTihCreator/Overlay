from typing import Optional

from PySide6.QtCore import QObject, Signal, Qt, QEvent
from PySide6.QtGui import QPixmap, QPainter, QMouseEvent, QHoverEvent
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem, QQuickPaintedItem
from PySide6.QtQuickWidgets import QQuickWidget
class WidgetWrapper(QQuickPaintedItem):
    """
    Класс-обертка для встраивания QWidget в QML сценарий.
    Наследуется от QQuickPaintedItem и поддерживает:
    - Отрисовку виджета
    - Передачу событий мыши и клавиатуры
    - Динамическое изменение размера
    """
    
    # Сигнал, когда виджет изменяет свой размер
    widgetSizeChanged = Signal(int, int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._widget = None
        self._pixmap = QPixmap()
        
        # Настройки для корректной работы событий и отрисовки
        self.setAcceptedMouseButtons(Qt.AllButtons)
        self.setAcceptHoverEvents(True)
        self.setFlag(QQuickPaintedItem.ItemHasContents, True)
        self.setFlag(QQuickPaintedItem.ItemAcceptsInputMethod, True)
    
    def setWidget(self, widget: QWidget):
        """ Установка виджета для отображения """
        if self._widget == widget:
            return
        
        if self._widget:
            self._widget.removeEventFilter(self)
        
        self._widget = widget
        if self._widget:
            self._widget.installEventFilter(self)
            self._widget.setAttribute(Qt.WA_DontCreateNativeAncestors)
            self._widget.setAttribute(Qt.WA_NativeWindow)
            
            # Настройка прозрачности
            self._widget.setAttribute(Qt.WA_TranslucentBackground)
            self._widget.setAutoFillBackground(True)
            
            # Обновляем размеры при изменении виджета
            self._updateWidgetSize()
    
    def widget(self) -> QWidget:
        """ Получение текущего виджета """
        return self._widget
    
    def _updateWidgetSize(self):
        """ Обновление размера виджета в соответствии с размером QQuickItem """
        if not self._widget:
            return
        
        # Устанавливаем размер виджета
        size = self.size().toSize()
        if size.isValid() and not size.isEmpty():
            self._widget.resize(size)
            self.update()
    
    def eventFilter(self, obj, event):
        """ Фильтр событий для виджета """
        if obj == self._widget:
            if event.type() == QEvent.Resize:
                # При изменении размера виджета обновляем отображение
                self.update()
                self.widgetSizeChanged.emit(event.size().width(), event.size().height())
            elif event.type() == QEvent.UpdateRequest:
                self.update()
        return super().eventFilter(obj, event)
    
    def paint(self, painter: QPainter):
        """ Отрисовка виджета на QPainter """
        if not self._widget or not self._widget.isVisible():
            return
        
        # Создаем pixmap с контентом виджета
        size = self.size().toSize()
        if size.isEmpty():
            return
        
        if self._pixmap.size() != size:
            self._pixmap = QPixmap(size)
        
        self._pixmap.fill(Qt.transparent)
        self._widget.render(self._pixmap)
        painter.drawPixmap(0, 0, self._pixmap)
    
    def geometryChange(self, newGeometry, oldGeometry):
        """ Обработка изменения геометрии """
        super().geometryChange(newGeometry, oldGeometry)
        self._updateWidgetSize()
    
    # Далее идут методы для передачи событий от QML к виджету
    
    def mousePressEvent(self, event):
        if self._widget:
            pos = event.position().toPoint()
            self._sendMouseEvent(event, QEvent.MouseButtonPress, pos)
        event.accept()
    
    def mouseMoveEvent(self, event):
        if self._widget:
            pos = event.position().toPoint()
            self._sendMouseEvent(event, QEvent.MouseMove, pos)
        event.accept()
    
    def mouseReleaseEvent(self, event):
        if self._widget:
            pos = event.position().toPoint()
            self._sendMouseEvent(event, QEvent.MouseButtonRelease, pos)
        event.accept()
    
    def hoverMoveEvent(self, event):
        if self._widget:
            pos = event.position().toPoint()
            self._sendMouseEvent(event, QEvent.HoverMove, pos)
        event.accept()
    
    def keyPressEvent(self, event):
        if self._widget:
            QApplication.sendEvent(self._widget, event)
        event.accept()
    
    def keyReleaseEvent(self, event):
        if self._widget:
            QApplication.sendEvent(self._widget, event)
        event.accept()
    
    def _sendMouseEvent(self, originalEvent, eventType, pos):
        """ Создание и отправка события мыши в виджет """
        if not self._widget:
            return
        
        # Преобразование координат и кнопок мыши
        button = originalEvent.button()
        buttons = originalEvent.buttons()
        modifiers = originalEvent.modifiers()
        
        # Создание события
        event = QEvent(eventType)
        if eventType in (QEvent.MouseButtonPress, QEvent.MouseButtonRelease, QEvent.MouseMove):
            event = QMouseEvent(
                eventType,
                pos,
                button,
                buttons,
                modifiers
            )
        elif eventType == QEvent.HoverMove:
            event = QHoverEvent(
                pos,
                pos - originalEvent.sceneDelta().toPoint(),
                modifiers
            )
        
        # Отправка события в виджет
        QApplication.sendEvent(self._widget, event)

class LegacyController(QWidget):
    def __init__(self, overlayHandler, engine):
        super().__init__()
        self.overlayHandler = overlayHandler
        self.engine: QQmlApplicationEngine = engine
        self.legacyApp = QWidget()
        with open("qt://root/css/main.css") as css:
            self.legacyApp.setStyleSheet(css.read())
        self.setParent(self.legacyApp)
        with open("qt://root/css/overlay.css") as css:
            self.setStyleSheet(css.read())
        self.widgets = []
        self.container: Optional[QQuickItem] = None
    
    def initContainer(self):
        if self.container is not None: return
        root = self.engine.rootObjects()[0]
        for item in root.findChildren(QObject):
            if item.objectName() == "win":
                self.container = item
                break
    
    def addWidget(self, widget, anchor=None, margins=None):
        self.initContainer()
        if self.container:
            gwidget = WidgetWrapper(self.container)
            gwidget.setWidget(widget)
            self.widgets.append(gwidget)
    
    def __getattr__(self, item):
        match item:
            case "registered_shortcut":
                return self.overlayHandler.registered_shortcut
