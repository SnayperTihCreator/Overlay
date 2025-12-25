from PySide6.QtWidgets import QLayout, QLayoutItem, QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect, QSize, QMargins, Signal, QEvent


class AnchorLayoutItem(QLayoutItem):
    def __init__(
            self,
            widget: QWidget,
            anchors: list[Qt.AnchorPoint] = None,
            margins: QMargins = None,
            min_size: QSize = None,
            max_size: QSize = None,
            relative_x: float = None,  # Процент от ширины (0.0 - 1.0)
            relative_y: float = None  # Процент от высоты (0.0 - 1.0)
    ):
        super().__init__(Qt.AlignmentFlag.AlignCenter)
        self._widget = widget
        self._anchors = anchors or [Qt.AnchorPoint.AnchorLeft, Qt.AnchorPoint.AnchorTop]
        self._margins = margins or QMargins(0, 0, 0, 0)
        self._min_size = min_size or QSize(0, 0)
        self._max_size = max_size or QSize(16777215, 16777215)
        self.relative_x = relative_x
        self.relative_y = relative_y
        
        self._validate_anchors()
        if widget:
            widget.destroyed.connect(self._widget_destroyed)
    
    def _widget_destroyed(self):
        if self.layout():
            self.layout().invalidate()
    
    def _validate_anchors(self):
        if len(self._anchors) != 2:
            raise ValueError("Exactly 2 anchors required [Horizontal, Vertical]")
    
    def widget(self) -> QWidget:
        return self._widget
    
    def anchors(self) -> list[Qt.AnchorPoint]:
        return self._anchors
    
    def margins(self) -> QMargins:
        return self._margins
    
    def minimumSize(self) -> QSize:
        return self._min_size
    
    def maximumSize(self) -> QSize:
        return self._max_size
    
    def _update_layout(self):
        if self.layout():
            self.layout().invalidate()
        elif self.widget():
            self.widget().updateGeometry()


class AnchorLayout(QLayout):
    layoutChanged = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[AnchorLayoutItem] = []
        self._dirty = True
    
    def addItem(self, item: AnchorLayoutItem):
        self._items.append(item)
        if item.widget():
            if self.parentWidget():
                item.widget().setParent(self.parentWidget())
            item.widget().installEventFilter(self)
        self.invalidate()
    
    def addWidget(self, w, anchors=None, margins=None, rel_x=None, rel_y=None):
        item = AnchorLayoutItem(w, anchors, margins, w.minimumSize(), w.maximumSize(), rel_x, rel_y)
        self.addItem(item)
    
    def takeAt(self, index):
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            if item.widget():
                item.widget().removeEventFilter(self)
            self.invalidate()
            return item
        return None
    
    def eventFilter(self, obj, event):
        if event.type() in {QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.LayoutRequest}:
            self.invalidate()
        return super().eventFilter(obj, event)
    
    def invalidate(self):
        super().invalidate()
        self._dirty = True
        self.layoutChanged.emit()
    
    def setGeometry(self, rect: QRect):
        if self._dirty or rect != self.geometry():
            super().setGeometry(rect)
            self._doLayout(rect)
            self._dirty = False
    
    def _doLayout(self, rect: QRect):
        contents = self.contentsRect()
        if contents.isEmpty(): return
        
        for item in self._items:
            widget = item.widget()
            if not widget or not widget.isVisible(): continue
            
            # Расчет X
            x, w = self._calculate_axis(
                anchor=item.anchors()[0],
                margin_low=item.margins().left(),
                margin_high=item.margins().right(),
                container_size=contents.width(),
                container_start=contents.left(),
                hint=widget.sizeHint().width(),
                min_s=item.minimumSize().width(),
                max_s=item.maximumSize().width(),
                is_expanding=(widget.sizePolicy().horizontalPolicy() == QSizePolicy.Policy.Expanding),
                percent=item.relative_x
            )
            
            # Расчет Y
            y, h = self._calculate_axis(
                anchor=item.anchors()[1],
                margin_low=item.margins().top(),
                margin_high=item.margins().bottom(),
                container_size=contents.height(),
                container_start=contents.top(),
                hint=widget.sizeHint().height(),
                min_s=item.minimumSize().height(),
                max_s=item.maximumSize().height(),
                is_expanding=(widget.sizePolicy().verticalPolicy() == QSizePolicy.Policy.Expanding),
                percent=item.relative_y
            )
            
            widget.setGeometry(QRect(x, y, w, h))
    
    @staticmethod
    def _calculate_axis(anchor, margin_low, margin_high, container_size,
                        container_start, hint, min_s, max_s, is_expanding, percent):
        # 1. Размер
        raw_size = container_size - margin_low - margin_high if is_expanding else hint
        final_size = max(min(raw_size, max_s), min_s)
        
        # 2. Позиция
        pos = container_start
        if percent is not None:
            pos += int(container_size * percent) + margin_low - margin_high
        else:
            if anchor in {Qt.AnchorPoint.AnchorLeft, Qt.AnchorPoint.AnchorTop}:
                pos += margin_low
            elif anchor in {Qt.AnchorPoint.AnchorRight, Qt.AnchorPoint.AnchorBottom}:
                pos += container_size - margin_high - final_size
            else:
                pos += (container_size - final_size) // 2 + (margin_low - margin_high)
        
        return pos, final_size
    
    def count(self):
        return len(self._items)
    
    def itemAt(self, i):
        return self._items[i] if 0 <= i < len(self._items) else None
    
    def minimumSize(self):
        s = QSize(0, 0)
        for i in self._items: s = s.expandedTo(i.minimumSize())
        m = self.contentsMargins()
        return s + QSize(m.left() + m.right(), m.top() + m.bottom())
