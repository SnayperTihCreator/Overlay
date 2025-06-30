from PySide6.QtCore import Qt, QObject, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QmlElement

app = QGuiApplication()
app.setAttribute(Qt.AA_UseSoftwareOpenGL)  # Важно для прозрачности

class PP(QObject):
    @Slot(str, result=type(None))
    def log(self, msg):
        print(msg)

def handler_error(errors):
    print(*errors, sep="\n")

printer = PP()
engine = QQmlApplicationEngine()
engine.rootContext().setContextProperty("PythonLog", printer)
engine.warnings.connect(handler_error)
engine.load("qml/main.qml")

app.exec()
