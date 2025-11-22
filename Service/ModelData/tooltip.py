from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QToolTip
from PySide6.QtCore import Qt, QTimer


class ToolTipPlugin(QWidget):
    def __init__(self, parent, data):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint |
                            Qt.WindowType.Window | Qt.WindowType.WindowDoesNotAcceptFocus |
                            Qt.WindowType.BypassWindowManagerHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.box = QVBoxLayout(self)
        
        self.title_lbl = QLabel(data[0])
        self.title_lbl.setStyleSheet(f"color: {data[1]}")
        self.box.addWidget(self.title_lbl)
        
        self.adjustSize()
        
    def leaveEvent(self, event):
        QTimer.singleShot(1500, self.deleteLater)
        self.hide()
        super().leaveEvent(event)
