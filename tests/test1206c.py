import asyncio
import sys

from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QTextEdit, QWidget


class WebSocketWorker(QObject):
    # Сигналы для обмена данными между потоками
    received_message = Signal(str)
    status_changed = Signal(str)
    finished = Signal()

    def __init__(self, url):
        super().__init__()
        self.url = url
        self._is_running = False

    async def _connect(self):
        try:
            async with websockets.connect(self.url) as ws:
                self.status_changed.emit("Подключено к серверу")
                self._is_running = True
                while self._is_running:
                    message = await ws.recv()
                    self.received_message.emit(f"Получено: {message}")
        except Exception as e:
            self.status_changed.emit(f"Ошибка: {e}")
        finally:
            self.status_changed.emit("Отключено")
            self.finished.emit()

    def start(self):
        self._is_running = True
        asyncio.run(self._connect())

    def stop(self):
        self._is_running = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebSocket + PySide6")
        self.setGeometry(100, 100, 400, 300)

        # Виджеты
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.button_connect = QPushButton("Подключиться")
        self.button_disconnect = QPushButton("Отключиться")
        self.button_send = QPushButton("Отправить сообщение")

        # Разметка
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.button_connect)
        layout.addWidget(self.button_disconnect)
        layout.addWidget(self.button_send)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Создаем поток и worker для WebSocket
        self.thread = QThread()
        self.ws_worker = WebSocketWorker("ws://localhost:8000")
        self.ws_worker.moveToThread(self.thread)

        # Подключаем сигналы
        self.ws_worker.received_message.connect(self.update_text)
        self.ws_worker.status_changed.connect(self.update_text)
        self.ws_worker.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)

        # Обработчики кнопок
        self.button_connect.clicked.connect(self.connect_websocket)
        self.button_disconnect.clicked.connect(self.disconnect_websocket)
        self.button_send.clicked.connect(self.send_message)

    @Slot(str)
    def update_text(self, text):
        self.text_edit.append(text)

    @Slot()
    def connect_websocket(self):
        self.thread.start()
        # Запускаем worker через QTimer, чтобы избежать прямого вызова из другого потока
        self.thread.started.connect(self.ws_worker.start)

    @Slot()
    def disconnect_websocket(self):
        self.ws_worker.stop()

    @Slot()
    def send_message(self):
        # В реальном приложении можно добавить QInputDialog для ввода сообщения
        asyncio.run(self._send_dummy_message())

    async def _send_dummy_message(self):
        try:
            async with websockets.connect("ws://localhost:8000") as ws:
                await ws.send("Привет от PySide6!")
        except Exception as e:
            self.text_edit.append(f"Ошибка отправки: {e}")


if __name__ == "__main__":
    import websockets  # Импортируем здесь, чтобы избежать ошибок в потоке

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())