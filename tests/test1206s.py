import sys
import asyncio
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTextEdit, QWidget
from PySide6.QtCore import QObject, Signal, Slot, QThread
import websockets.asyncio.server as aserve
from websockets import exceptions as exc


class WebSocketWorker(QThread):
    message_received = Signal(str)
    server_started = Signal(str)
    finished = Signal()
    
    def __init__(self, host="localhost", port=8765):
        super().__init__()
        self.host = host
        self.port = port
        self._is_running = False
    
    async def handle_connection(self, websocket):
        self.message_received.emit("Клиент подключился")
        await websocket.send("Ok")
        try:
            async for message in websocket:
                self.message_received.emit(f"Получено: {message}")
        except exc.ConnectionClosed:
            self.message_received.emit("Клиент отключился")
    
    async def run_server(self):
        self._is_running = True
        async with aserve.serve(self.handle_connection, self.host, self.port) as server:
            self.server_started.emit(f"Сервер запущен на ws://{self.host}:{self.port}")
            await server.serve_forever()
        self.finished.emit()
    
    def stop(self):
        self._is_running = False
    
    def run(self, /):
        asyncio.run(self.run_server())


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WebSocket Server (PySide6 + QThread)")
        self.setGeometry(100, 100, 500, 400)
        
        self.setup_ui()
        self.setup_websocket_server()
    
    def setup_ui(self):
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        
        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def setup_websocket_server(self):
        # Создаем и настраиваем поток
        self.worker = WebSocketWorker()
        
        # Подключаем сигналы
        self.worker.message_received.connect(self.text_edit.append)
        self.worker.server_started.connect(self.text_edit.append)
        
        # Запускаем поток при старте приложения
        self.worker.start()
    
    def closeEvent(self, event):
        """Обработчик закрытия окна - останавливаем сервер"""
        self.worker.stop()
        self.thread.quit()
        self.thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())