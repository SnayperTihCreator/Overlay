from PySide6.QtGui import QIcon, QPixmap, QPainter, QImage, QColor
from PySide6.QtCore import Qt, QSize


def modulateIcon(icon: QIcon, color: QColor) -> QIcon:
    """
    Modulates (tints) a QIcon with the specified color while preserving alpha channel.

    Args:
        icon: The icon to be tinted
        color: The color to apply

    Returns:
        A new QIcon with the color applied
    """
    if icon.isNull() or not color.isValid():
        return icon
    
    # Get the first available size
    size = icon.availableSizes()[0] if icon.availableSizes() else QSize(16, 16)
    pixmap = icon.pixmap(size)
    
    # Create new pixmap with same size
    tinted_pixmap = QPixmap(pixmap.size())
    tinted_pixmap.fill(Qt.transparent)
    
    # Draw original icon with color overlay
    painter = QPainter(tinted_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted_pixmap.rect(), color)
    painter.end()
    
    return QIcon(tinted_pixmap)


def modulatePixmap(pixmap: QPixmap, color: QColor) -> QPixmap:
    """
    Modulates (tints) a QPixmap with the specified color while preserving alpha channel.

    Args:
        pixmap: The pixmap to be tinted
        color: The color to apply

    Returns:
        A new QPixmap with the color applied
    """
    if pixmap.isNull() or not color.isValid():
        return pixmap
    
    tinted_pixmap = QPixmap(pixmap.size())
    tinted_pixmap.fill(Qt.transparent)
    
    painter = QPainter(tinted_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.drawPixmap(0, 0, pixmap)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted_pixmap.rect(), color)
    painter.end()
    
    return tinted_pixmap


def modulateImage(image: QImage, color: QColor) -> QImage:
    """
    Modulates (tints) a QImage with the specified color while preserving alpha channel.

    Args:
        image: The image to be tinted
        color: The color to apply

    Returns:
        A new QImage with the color applied
    """
    if image.isNull() or not color.isValid():
        return image
    
    tinted_image = QImage(image.size(), QImage.Format_ARGB32)
    tinted_image.fill(Qt.transparent)
    
    painter = QPainter(tinted_image)
    painter.setCompositionMode(QPainter.CompositionMode_Source)
    painter.drawImage(0, 0, image)
    painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    painter.fillRect(tinted_image.rect(), color)
    painter.end()
    
    return tinted_image