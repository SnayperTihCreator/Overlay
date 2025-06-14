import sys
import os
from pathlib import Path
from functools import cache

from PySide6.QtCore import QRect, QPoint
from PySide6.QtWidgets import QApplication
import requests

from .openFolderExplorer import open_file_manager
from .dumper import Dumper
from .limit_called import limit_calls_per_day


@limit_calls_per_day(3)
def getCurrentWeather(city):
    api_key = os.environ.get("API_WEATHER")
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}&lang=ru"
    return requests.get(url).json()
    

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


@cache
def getAppPath():
    return (
        Path(sys.executable).parent
        if getattr(sys, "frozen", False)
        else Path(sys.argv[0]).parent
    )


__all__ = [
    "getAppPath",
    "getAllSizeDesktop",
    "clampAllDesktop",
    "clampAllDesktopP",
    "open_file_manager",
    "Dumper",
]
