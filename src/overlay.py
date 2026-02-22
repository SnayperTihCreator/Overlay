import sys
import os
import builtins
import warnings
import asyncio

import qasync

warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
warnings.filterwarnings("ignore", category=DeprecationWarning, module="__main__")

from PySide6.QtCore import QTimer, qFatal
from PySide6.QtQuick import QQuickWindow, QSGRendererInterface
from qasync import QEventLoop

from core.service.print_manager import PrintManager
from core.metadata import metadata, version
from core.main_init import OpenManager
from core.application import OverlayApplication
from gui.themes import ThemeController, DefaultTheme
from gui.splash_screen import GifSplashScreen
from utils.fs import ToolsIniter, getAppPath
# noinspection PyUnresolvedReferences
import assets_rc
# noinspection PyUnresolvedReferences
import core.importers
# noinspection PyUnresolvedReferences
import core.logger


async def main():
    if sys.platform == "linux":
        os.environ["QT_QPA_PLATFORM"] = "xcb"
    
    QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.Software)
    app = OverlayApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    loop: asyncio.AbstractEventLoop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    tools_folder = ToolsIniter("tools")
    tools_folder.load()
    
    with OpenManager(), PrintManager() as pm:
        pm.show_caller_info(True)
        
        from gui.main_window import Overlay
        
        os.chdir(getAppPath())
        
        ThemeController().registerApp(app)
        ThemeController().setTheme(DefaultTheme())
        
        splash = GifSplashScreen(":/root/gif/loader.gif")
        splash.setStatus(version("App"), metadata("App").author)
        splash.show()
        app.processEvents()
        
        window = Overlay(splash)
        
        def on_finalized():
            try:
                builtins.windowOverlay = window
                splash.finish(window)
            except Exception as e:
                qFatal(f"Error on finalize: {e}")
                app.exit()
        
        window.finished_loading.connect(on_finalized)
        await asyncio.sleep(1)
        await window.ready()
        
        try:
            with loop:
                loop.run_forever()
        finally:
            pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except asyncio.CancelledError:
        sys.exit(0)
