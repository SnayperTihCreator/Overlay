from typing import Self

from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Qt, Signal


class NonBlockingMessageBox(QMessageBox):
    """Неблокирующий QMessageBox с сигналами для результата."""
    result_signal = Signal(int)  # Сигнал с результатом (QMessageBox.StandardButton)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.WindowModality.NonModal)  # Неблокирующий режим
        self.finished.connect(self.emit_result)  # При закрытии испускаем сигнал
    
    def emit_result(self, result):
        self.result_signal.emit(result)
    
    # Статические методы (аналоги стандартных, но неблокирующие)
    
    @staticmethod
    def information(parent, title, text, /, buttons=QMessageBox.StandardButton.Ok, defaultButton=...):
        return NonBlockingMessageBox.show_message(
            parent, title, text, buttons, QMessageBox.Icon.Information, defaultButton
        )
    
    @staticmethod
    def question(parent, title, text, /, buttons=QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                 defaultButton=...):
        return NonBlockingMessageBox.show_message(
            parent, title, text, buttons, QMessageBox.Icon.Question, defaultButton
        )
    
    @staticmethod
    def warning(parent, title, text, /, buttons=QMessageBox.StandardButton.Ok, defaultButton=...) -> QMessageBox:
        return NonBlockingMessageBox.show_message(
            parent, title, text, buttons, QMessageBox.Icon.Warning, defaultButton
        )
    
    @staticmethod
    def critical(parent, title, text, /, buttons=QMessageBox.StandardButton.Ok, defaultButton=...):
        return NonBlockingMessageBox.show_message(
            parent, title, text, buttons, QMessageBox.Icon.Critical, defaultButton
        )
    
    @staticmethod
    def show_message(parent, title, text, buttons, icon, defaultButton):
        msg_box = NonBlockingMessageBox(parent)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setStandardButtons(buttons)
        msg_box.setIcon(icon)
        if defaultButton is not Ellipsis:
            msg_box.setDefaultButton(defaultButton)
        msg_box.show()
        return msg_box  # Возвращаем объект для подключения сигналов
