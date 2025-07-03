from PySide6.QtQuick import QQuickWindow
from PySide6.QtCore import QUrl
from PySide6.QtQml import QQmlComponent, QQmlEngine

from attrs import define, field


@define
class WrapperWindow:
    engine: QQmlEngine = field()
    component: QQmlComponent = field()
    _window: QQuickWindow = field(init=False, repr=False)
    
    def show(self):
        if self.component.isReady():
            self._window = self.component.create()


def factoryWindow(prefix, engine):
    window = QQmlComponent(engine, QUrl(f"qrc:/{prefix}/main.qml"))
    return WrapperWindow(engine, window)