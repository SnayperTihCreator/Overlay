from PySide6.QtCore import QRect, QPoint
from PySide6.QtWidgets import QApplication


def getAllSizeDesktop() -> QRect:
    screens = QApplication.screens()
    global_rect = QRect()
    for screen in screens:
        global_rect = global_rect.united(screen.availableGeometry())
    return global_rect


def clampAllDesktop(x, y, w, h) -> QPoint:
    global_rect = getAllSizeDesktop()
    x = max(global_rect.left(), min(x, global_rect.right() - w))
    y = max(global_rect.top(), min(y, global_rect.bottom() - h))
    return QPoint(x, y)


def clampAllDesktopP(point: QPoint, w, h) -> QPoint:
    global_rect = getAllSizeDesktop()
    x = max(global_rect.left(), min(point.x(), global_rect.right() - w))
    y = max(global_rect.top(), min(point.y(), global_rect.bottom() - h))
    return QPoint(x, y)


__all__ = ["clampAllDesktop", "clampAllDesktopP", "getAllSizeDesktop"]