import sys
import os
import builtins
import warnings

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="__main__")

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, qFatal
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface
from pyi18n.loaders import PyI18nYamlLoader

from Service.PrintManager import PrintManager
from Service.metadata import metadata, version
from Service.gifSplashScreen import GifSplashScreen
from Service.internalization import CustomPyI18n
from ColorControl.themeController import ThemeController
from ColorControl.defaultTheme import DefaultTheme
from PathControl.tools_folder import ToolsIniter
from PathControl import getAppPath
from MinTools import OpenManager
# noinspection PyUnresolvedReferences
import assets_rc
# noinspection PyUnresolvedReferences
import Service.importer_overlayaddons

if __name__ == "__main__":
    if sys.platform == "linux":
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.Software)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    tools_folder = ToolsIniter("tools")
    tools_folder.load()
    
    with OpenManager() as om, PrintManager() as pm:
        pm.show_caller_info(True)
        
        from Service.UIWidget.mainWindow import Overlay
        
        os.chdir(getAppPath())
        
        ThemeController().registerApp(app)
        ThemeController().setTheme(DefaultTheme())
        
        splash = GifSplashScreen(":/root/gif/loader.gif")
        splash.drawText(metadata("App").author, (20, 30), size=10, font="UNCAGE")
        splash.drawText(version("App"), (20, splash.height() - 20))
        splash.show()
        
        window = Overlay()
        
        
        def load():
            try:
                window.ready()
                builtins.windowOverlay = window
                splash.finish(window)
            except Exception as e:
                qFatal(f"Error {type(e)}: {e}")
                app.exit()
                
        
        
        QTimer.singleShot(2500, load)
        
        app.exec()
