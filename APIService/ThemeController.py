from PySide6.QtWidgets import QApplication, QWidget


class MetaSingtools(type):
    _instance = None
    
    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


qApp: QApplication


class ThemeController(metaclass=MetaSingtools):
    def __init__(self):
        self.interface = {}
    
    def register(self, name: str, widget: QWidget):
        self.interface[name] = widget
    
    def registerApp(self, app: QApplication):
        self.interface["application"] = app
