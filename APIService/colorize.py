from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QColor, QPixmap, QPainter


def tint_icon(icon: QIcon, color: QColor) -> QIcon:
    # Получаем пиксельную карту иконки
    pixmap = icon.pixmap(icon.availableSizes()[0])  # Берём первый доступный размер
    
    # Создаём новую пиксельную карту с тем же размером
    tinted_pixmap = QPixmap(pixmap.size())
    tinted_pixmap.fill(Qt.transparent)  # Прозрачный фон
    
    # Рисуем исходную иконку с наложением цвета
    painter = QPainter(tinted_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted_pixmap.rect(), color)
    painter.end()
    
    return QIcon(tinted_pixmap)