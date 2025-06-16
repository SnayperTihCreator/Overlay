import asyncio
import socket
from contextlib import closing

from PySide6.QtCore import Signal, QThread, qDebug
import websockets
from websockets.asyncio.server import serve


def find_free_port(start_port=8000, end_port=9000):
    """Находит первый свободный порт в заданном диапазоне"""
    for port in range(start_port, end_port + 1):
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            try:
                s.bind(('', port))
                s.close()
                return port
            except OSError:  # Порт занят
                continue
    raise ValueError(f"No free ports in range {start_port}-{end_port}")


class ServerWebSockets(QThread):
    message_received = Signal(str)
    
    def __init__(self, ports, parent=None):
        super().__init__(parent)
        self.free_port = find_free_port(*ports)
        self._is_running = False
    
    async def handle_connection(self, websocket):
        qDebug("Клиент подключен")
        try:
            async for message in websocket:
                qDebug(f"Получено: {message}")
                self.message_received.emit(message)
        except websockets.exceptions.ConnectionClosed:
            qDebug(f"Клиент отключился")
    
    async def run_server(self):
        async with serve(self.handle_connection, "localhost", self.free_port) as server:
            qDebug(f"Сервер запущен на ws://localhost:{self.free_port}")
            self.finished.connect(server.close)
            while self._is_running:
                await asyncio.sleep(0.1)
    
    def run(self, /):
        asyncio.run(self.run_server())
    
    def start(self, /, priority=QThread.Priority.InheritPriority):
        if not self._is_running:
            self._is_running = True
            super().start(priority)
    
    def quit(self, /):
        self._is_running = False
        super().quit()


class ClientWebSockets:
    def __init__(self, ports, parent=None):
        super().__init__(parent)
        self.free_port = find_free_port(ports)
    
    def send_message(self, message):
        asyncio.run(self.run_connect(message))
    
    async def run_connect(self, message):
        await self.asend_message(message)
    
    async def asend_message(self, message):
        async with websockets.connect(f"Сервер запущен на ws://localhost:{self.free_port}") as client:
            await client.send(message)
