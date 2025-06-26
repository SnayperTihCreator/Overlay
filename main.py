import sys
import os
import builtins

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap

from Service.UIWidget.mainWindow import Overlay
from Service.PrintManager import PrintManager
from APIService import QtResourceDescriptor
from API import Config

if __name__ == "__main__":
    if sys.platform == "linux":
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    app = QApplication(sys.argv)
    with QtResourceDescriptor.open(":/main/main.css") as file:
        app.setStyleSheet(file.read())
    with PrintManager() as pm:
        pm.show_caller_info(True)
        pixmap = QPixmap(":/main/loader.png")
        splash = QSplashScreen(pixmap)
        splash.show()
        
        app.setQuitOnLastWindowClosed(False)
        window = Overlay()
        builtins.windowOverlay = window
        splash.finish(window)
        app.exec()
