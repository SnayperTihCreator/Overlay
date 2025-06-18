import sys
import os

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from qt_material import apply_stylesheet

from Service.UIWidget.mainWindow import Overlay
from Service.PrintManager import PrintManager
from APIService import getAppPath
from API import Config

if __name__ == "__main__":
    if sys.platform == "linux":
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    app = QApplication(sys.argv)
    apply_stylesheet(
        app,
        theme="dark_purple.xml",
        extra={
            "font_size": "14px",
            "primaryColor": "#8b13a0",
            "primaryTextColor": "#45c016",
            "secondaryTextColor": "#9ad789",
        },
    )
    with PrintManager() as pm:
        pm.show_caller_info(True)
        pixmap = QPixmap(":/main/loader.png")
        splash = QSplashScreen(pixmap)
        splash.show()
        
        app.setQuitOnLastWindowClosed(False)
        window = Overlay()
        splash.finish(window)
        app.exec()
