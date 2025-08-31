import sys
import os
import builtins
import warnings
from importlib import metadata

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="__main__")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from PathControl.storageControls import OpenManager
from Service.PrintManager import PrintManager
from Service.gifSplashScreen import GifSplashScreen
from ColorControl.themeController import ThemeController
from ColorControl.defaultTheme import DefaultTheme
# noinspection PyUnresolvedReferences
import Service.globalContext
# noinspection PyUnresolvedReferences
import PathControl.qtStorageControls
# noinspection PyUnresolvedReferences
import assets_rc
# noinspection PyUnresolvedReferences
import Service.metadatas

if __name__ == "__main__":
    if sys.platform == "linux":
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    app = QApplication(sys.argv)
    
    with OpenManager() as om, PrintManager() as pm:
        pm.show_caller_info(True)
        
        from Service.UIWidget.mainWindow import Overlay
        
        ThemeController().registerApp(app)
        ThemeController().setTheme(DefaultTheme())
        
        splash = GifSplashScreen(":/root/gif/loader.gif")
        splash.drawText(metadata.metadata("Overlay::App")["author"], (20, 30), size=10, font="UNCAGE")
        splash.drawText(metadata.version("Overlay::App"), (20, splash.height()-20))
        splash.show()
        
        app.setQuitOnLastWindowClosed(False)
        
        
        def load():
            window = Overlay()
            builtins.windowOverlay = window
            splash.finish(window)
        
        
        QTimer.singleShot(2500, load)
        
        app.exec()
