import sys
import os
import builtins

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap, QPalette, QColor

import Service.globalContext
from APIService.storageControls import OpenManager
import APIService.qtStorageControls
from Service.PrintManager import PrintManager
from APIService.themeController import ThemeController
from Service.defaultTheme import DefaultTheme

if __name__ == "__main__":
    if sys.platform == "linux":
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    app = QApplication(sys.argv)
        
    with OpenManager() as om, PrintManager() as pm:
        pm.show_caller_info(True)
        
        from Service.UIWidget.mainWindow import Overlay
        
        ThemeController().currentTheme = DefaultTheme()
        ThemeController().registerApp(app)
        ThemeController().updateApp()
        
        pixmap = QPixmap(":/root/icons/loader.png")
        splash = QSplashScreen(pixmap)
        splash.show()
        
        app.setQuitOnLastWindowClosed(False)
        window = Overlay()
        builtins.windowOverlay = window
        splash.finish(window)
        app.exec()
