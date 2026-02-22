import logging
from PySide6.QtGui import QIcon, QPixmap, QPainter, QImage, QColor
from PySide6.QtCore import Qt, QSize

# Initialize logger for this module
logger = logging.getLogger(__name__)


def modulateIcon(icon: QIcon, color: QColor) -> QIcon:
    """
    Modulates (tints) a QIcon with the specified color while preserving alpha channel.

    Args:
        icon: The icon to be tinted
        color: The color to apply

    Returns:
        A new QIcon with the color applied
    """
    try:
        if icon.isNull():
            return icon
        
        if not color.isValid():
            logger.warning("Invalid color provided for icon modulation")
            return icon
        
        # Get the first available size
        size = icon.availableSizes()[0] if icon.availableSizes() else QSize(16, 16)
        pixmap = icon.pixmap(size)
        
        # Create new pixmap with same size
        tinted_pixmap = QPixmap(pixmap.size())
        tinted_pixmap.fill(Qt.GlobalColor.transparent)
        
        # Draw original icon with color overlay
        painter = QPainter(tinted_pixmap)
        try:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            painter.drawPixmap(0, 0, pixmap)
            
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            painter.fillRect(tinted_pixmap.rect(), color)
        finally:
            painter.end()
        
        return QIcon(tinted_pixmap)
    
    except Exception as e:
        logger.error(f"Failed to modulate icon: {e}", exc_info=True)
        return icon


def modulatePixmap(pixmap: QPixmap, color: QColor) -> QPixmap:
    """
    Modulates (tints) a QPixmap with the specified color while preserving alpha channel.

    Args:
        pixmap: The pixmap to be tinted
        color: The color to apply

    Returns:
        A new QPixmap with the color applied
    """
    try:
        if pixmap.isNull():
            return pixmap
        
        if not color.isValid():
            logger.warning("Invalid color provided for pixmap modulation")
            return pixmap
        
        tinted_pixmap = QPixmap(pixmap.size())
        tinted_pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(tinted_pixmap)
        try:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            painter.drawPixmap(0, 0, pixmap)
            
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            painter.fillRect(tinted_pixmap.rect(), color)
        finally:
            painter.end()
        
        return tinted_pixmap
    
    except Exception as e:
        logger.error(f"Failed to modulate pixmap: {e}", exc_info=True)
        return pixmap


def modulateImage(image: QImage, color: QColor) -> QImage:
    """
    Modulates (tints) a QImage with the specified color while preserving alpha channel.

    Args:
        image: The image to be tinted
        color: The color to apply

    Returns:
        A new QImage with the color applied
    """
    try:
        if image.isNull():
            return image
        
        if not color.isValid():
            logger.warning("Invalid color provided for image modulation")
            return image
        
        tinted_image = QImage(image.size(), QImage.Format.Format_ARGB32)
        tinted_image.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(tinted_image)
        try:
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
            painter.drawImage(0, 0, image)
            
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            painter.fillRect(tinted_image.rect(), color)
        finally:
            painter.end()
        
        return tinted_image
    
    except Exception as e:
        logger.error(f"Failed to modulate image: {e}", exc_info=True)
        return image


__all__ = ["modulateIcon", "modulateImage", "modulatePixmap"]
