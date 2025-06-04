import sys

from PySide6.QtWidgets import QApplication, QSplashScreen
from PySide6.QtGui import QPixmap
from qt_material import apply_stylesheet

from UIWidget.mainWindow import Overlay

if __name__ == "__main__":
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
    
    pixmap = QPixmap(":/main/loader.png")
    splash = QSplashScreen(pixmap)
    splash.show()
    
    app.setQuitOnLastWindowClosed(False)
    window = Overlay()
    splash.finish(window)
    app.exec()
