import sys
import os
import builtins

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap, QFontDatabase, QFont, QPalette, QColor

import Service.globalContext
from APIService.storageControls import OpenManager
import APIService.qtStorageControls
from Service.PrintManager import PrintManager

if __name__ == "__main__":
    if sys.platform == "linux":
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    app = QApplication(sys.argv)
        
    with OpenManager() as om, PrintManager() as pm:
        pm.show_caller_info(True)
        
        from Service.UIWidget.mainWindow import Overlay
        idx = QFontDatabase.addApplicationFont(":/base/fonts/MarckScript.ttf")
        # print(QFontDatabase.applicationFontFamilies(idx))
        
        with open("qt://root/css/main.css") as file:
            app.setStyleSheet(file.read())
            
            app.setFont(QFont("Marck Script", 14, 900))
            
            palette = app.palette()
            palette.setColor(QPalette.ColorRole.Text, QColor("#009b34"))
            app.setPalette(palette)
            
            pixmap = QPixmap(":/root/icons/loader.png")
            splash = QSplashScreen(pixmap)
            splash.show()
            
            app.setQuitOnLastWindowClosed(False)
            window = Overlay()
            builtins.windowOverlay = window
            splash.finish(window)
            app.exec()
