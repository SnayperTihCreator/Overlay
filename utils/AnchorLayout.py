from PySide6.QtWidgets import QLayout, QLayoutItem, QWidget, QSizePolicy
from PySide6.QtCore import Qt, QRect, QSize, QMargins, Signal, QEvent


class AnchorLayoutItem(QLayoutItem):
    def __init__(
        self,
        widget: QWidget,
        anchors: list[Qt.AnchorPoint] = None,
        margins: QMargins = None,
        minimum_size: QSize = None,
        maximum_size: QSize = None,
    ):
        super().__init__(Qt.AlignmentFlag.AlignCenter)

        self._anchors = anchors or [Qt.AnchorPoint.AnchorLeft, Qt.AnchorPoint.AnchorTop]
        self._margins = margins or QMargins(0, 0, 0, 0)
        self._minimum_size = minimum_size or QSize(0, 0)
        self._maximum_size = maximum_size or QSize(16777215, 16777215)
        self._widget = widget

        self._validate_anchors()

        if widget:
            widget.destroyed.connect(self._widget_destroyed)

    def _widget_destroyed(self):
        """Обработчик удаления виджета"""
        if self.layout():
            self.layout().invalidate()

    def _validate_anchors(self):
        if len(self._anchors) != 2:
            raise ValueError("Anchors must contain exactly 2 Qt.AnchorPoint values")

        horizontal_anchors = {Qt.AnchorLeft, Qt.AnchorRight, Qt.AnchorHorizontalCenter}
        vertical_anchors = {Qt.AnchorTop, Qt.AnchorBottom, Qt.AnchorVerticalCenter}

        if self._anchors[0] not in horizontal_anchors:
            raise ValueError(
                "First anchor must be horizontal (Left, Right or HorizontalCenter)"
            )

        if self._anchors[1] not in vertical_anchors:
            raise ValueError(
                "Second anchor must be vertical (Top, Bottom or VerticalCenter)"
            )

    def widget(self, /) -> QWidget:
        return self._widget

    # Properties for QML/PySide6 style access
    def anchors(self) -> list[Qt.AnchorPoint]:
        return self._anchors

    def setAnchors(self, anchors: list[Qt.AnchorPoint]):
        if self._anchors != anchors:
            self._anchors = anchors
            self._validate_anchors()
            self._update_layout()

    def margins(self) -> QMargins:
        return self._margins

    def setMargins(self, margins: QMargins):
        if self._margins != margins:
            self._margins = margins
            self._update_layout()

    def minimumSize(self) -> QSize:
        return self._minimum_size

    def setMinimumSize(self, size: QSize):
        if self._minimum_size != size:
            self._minimum_size = size
            self._update_layout()

    def maximumSize(self) -> QSize:
        return self._maximum_size

    def setMaximumSize(self, size: QSize):
        if self._maximum_size != size:
            self._maximum_size = size
            self._update_layout()

    def _update_layout(self):
        """Уведомляем лайаут об изменениях"""
        if self.layout():
            self.layout().invalidate()
        elif self.widget():
            self.widget().updateGeometry()


class AnchorLayout(QLayout):
    layoutChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: list[AnchorLayoutItem] = []
        self._dirty = False

    def addItem(self, item):
        self._items.append(item)
        item.widget().installEventFilter(self)  # Отслеживаем изменения виджета
        self.invalidate()

    def addWidget(self, w, anchors=None, margins=None):
        item = AnchorLayoutItem(w, anchors, margins, w.minimumSize(), w.maximumSize())
        self.addItem(item)

    def removeWidget(self, w, /):
        for item in self._items:
            if item.widget() == w:
                self._items.remove(item)
                item.widget().removeEventFilter(self)
                self.invalidate()
                break

    def eventFilter(self, obj, event):
        """Автоматическое обновление при изменениях виджетов"""
        if event.type() in {
            QEvent.Type.Resize,
            QEvent.Type.Polish,
            QEvent.Type.LayoutRequest,
            QEvent.Type.Show,
            QEvent.Type.Hide,
        }:
            self.invalidate()
        return super().eventFilter(obj, event)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            item = self._items.pop(index)
            if item.widget():
                item.widget().removeEventFilter(self)
            self.invalidate()
            return item
        return None

    def invalidate(self):
        """Помечаем лайаут как нуждающийся в обновлении"""
        super().invalidate()
        self._dirty = True
        self.layoutChanged.emit()

    def setGeometry(self, rect: QRect):
        """Переопределяем setGeometry с автоматическим обновлением"""
        if self._dirty or rect != self.geometry():
            super().setGeometry(rect)
            self._doLayout(rect)
            self._dirty = False

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        min_size = QSize()

        for item in self._items:
            if isinstance(item, AnchorLayoutItem):
                min_size = min_size.expandedTo(item.minimumSize())

        margins = self.contentsMargins()
        min_size += QSize(
            margins.left() + margins.right(), margins.top() + margins.bottom()
        )
        return min_size

    def _doLayout(self, rect: QRect):
        """Оптимизированный расчет позиций"""
        if not self._items:
            return

        contents = self.contentsRect()
        if contents.isEmpty():
            return

        # Группируем элементы для оптимизации
        anchor_groups = {}
        for item in self._items:
            if isinstance(item, AnchorLayoutItem):
                widget = item.widget()
                if widget and widget.isVisible():
                    key = (item.anchors()[0], item.anchors()[1])
                    anchor_groups.setdefault(key, []).append(item)

        # Обрабатываем группы элементов
        for (h_anchor, v_anchor), items in anchor_groups.items():
            for item in items:
                widget = item.widget()
                if not widget:
                    continue

                margins = item.margins()
                min_size = item.minimumSize()
                max_size = item.maximumSize()
                size_hint = widget.sizeHint()
                policy = widget.sizePolicy()

                # Вычисляем геометрию
                x, y, width, height = 0, 0, 0, 0

                # Горизонтальные вычисления
                if h_anchor == Qt.AnchorLeft:
                    x = contents.left() + margins.left()
                    width = size_hint.width()
                    if policy.horizontalPolicy() == QSizePolicy.Policy.Expanding:
                        width = contents.right() - margins.right() - x
                elif h_anchor == Qt.AnchorRight:
                    x = contents.right() - margins.right() - size_hint.width()
                    width = size_hint.width()
                    if policy.horizontalPolicy() == QSizePolicy.Policy.Expanding:
                        width = (
                            x + size_hint.width() - (contents.left() + margins.left())
                        )
                        x = contents.left() + margins.left()
                elif h_anchor == Qt.AnchorHorizontalCenter:
                    x = contents.left() + (contents.width() - size_hint.width()) // 2
                    width = size_hint.width()
                    if policy.horizontalPolicy() == QSizePolicy.Policy.Expanding:
                        width = contents.width() - margins.left() - margins.right()
                        x = contents.left() + margins.left()

                # Вертикальные вычисления
                if v_anchor == Qt.AnchorTop:
                    y = contents.top() + margins.top()
                    height = size_hint.height()
                    if policy.verticalPolicy() == QSizePolicy.Policy.Expanding:
                        height = contents.bottom() - margins.bottom() - y
                elif v_anchor == Qt.AnchorBottom:
                    y = contents.bottom() - margins.bottom() - size_hint.height()
                    height = size_hint.height()
                    if policy.verticalPolicy() == QSizePolicy.Policy.Expanding:
                        height = (
                            y + size_hint.height() - (contents.top() + margins.top())
                        )
                        y = contents.top() + margins.top()
                elif v_anchor == Qt.AnchorVerticalCenter:
                    y = contents.top() + (contents.height() - size_hint.height()) // 2
                    height = size_hint.height()
                    if policy.verticalPolicy() == QSizePolicy.Policy.Expanding:
                        height = contents.height() - margins.top() - margins.bottom()
                        y = contents.top() + margins.top()

                # Применяем ограничения размеров
                width = max(min(width, max_size.width()), min_size.width())
                height = max(min(height, max_size.height()), min_size.height())

                # Корректируем позиции после изменения размеров
                if h_anchor == Qt.AnchorRight:
                    x = contents.right() - margins.right() - width
                elif h_anchor == Qt.AnchorHorizontalCenter:
                    x = contents.left() + (contents.width() - width) // 2

                if v_anchor == Qt.AnchorBottom:
                    y = contents.bottom() - margins.bottom() - height
                elif v_anchor == Qt.AnchorVerticalCenter:
                    y = contents.top() + (contents.height() - height) // 2

                # Устанавливаем новую геометрию
                widget.setGeometry(QRect(x, y, width, height))
