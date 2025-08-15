import sys
import os
import builtins

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap

import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

from PathControl.storageControls import OpenManager
from Service.PrintManager import PrintManager
from ColorControl.themeController import ThemeController
from ColorControl.defaultTheme import DefaultTheme
# noinspection PyUnresolvedReferences
import Service.globalContext
# noinspection PyUnresolvedReferences
import PathControl.qtStorageControls
# noinspection PyUnresolvedReferences
import assets_rc

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
