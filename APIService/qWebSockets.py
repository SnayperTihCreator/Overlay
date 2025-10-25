from typing import Optional
import uuid

from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocketServer, QWebSocket
from PySide6.QtCore import QObject, Signal, Slot, qDebug, qWarning

from .webControls import find_free_port


class ServerWebSockets(QObject):
    message_received = Signal(str, str)
    
    def __init__(self, ports, parent=None):
        super().__init__(parent)
        self.free_port = find_free_port(ports.begin, ports.end)
        
        self._server: Optional[QWebSocketServer] = None
        self.clients: dict[str, QWebSocket] = {}
    
    def start(self):
        self._server = QWebSocketServer("Overlay WebSockets", QWebSocketServer.SslMode.NonSecureMode)
        if not self._server.listen(QHostAddress("127.0.0.1"), self.free_port):
            qWarning(f"Сервер не запущен\nОшибка: {self._server.error()}: {self._server.errorString()}")
            return False
        qDebug(f"Сервер запущен на: {self._server.serverUrl().toString()}")
        
        self._server.newConnection.connect(self.actNewConnection)
        return True
    
    def is_run(self):
        return self._server is not None
    
    def quit(self):
        if not self._server:
            return
        
        qDebug("Остановка сервера...")
        
        # Закрываем все клиентские подключения
        for client in self.clients.values():
            client.close()
            client.deleteLater()
        
        self.clients.clear()
        
        # Останавливаем сервер
        self._server.close()
        self._server.deleteLater()
        self._server = None
        
        qDebug(f"Сервер остановлен")
    
    @Slot()
    def actNewConnection(self):
        client = self._server.nextPendingConnection()
        if client:
            qDebug(f"Клиент подключился:")
            uid = uuid.uuid4().hex
            self.clients[uid] = client
            client.textMessageReceived.connect(lambda msg: self.actSendMessage(msg, uid))
            client.disconnected.connect(lambda: self.actDisconnectClient(uid))
    
    @Slot(str, str)
    def actSendMessage(self, msg: str, uid: str):
        qDebug(f"Клиент прислал сообщение: {msg}")
        self.message_received.emit(msg, uid)
    
    @Slot(str)
    def actDisconnectClient(self, uid: str):
        client = self.clients[uid]
        if uid in self.clients:
            del self.clients[uid]
        client.deleteLater()
        qDebug("Клиент отключился")
    
    def sendConfirmState(self, uid: str):
        self.sendMassage(uid, "[bold green]Done[/bold green]")
    
    def sendErrorState(self, uid: str, e: Exception):
        self.sendMassage(uid, f"[bold red]Error {type(e).__name__}: {e}[/bold red]")
    
    def sendMassage(self, uid: str, msg: str):
        self.clients[uid].sendTextMessage(msg)
