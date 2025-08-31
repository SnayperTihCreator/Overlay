from typing import Optional
import uuid

from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocketServer, QWebSocket
from PySide6.QtCore import QObject, Signal, Slot, qDebug, QUrl, qWarning
from rich.console import Console
from rich.text import Text

from .webControls import find_free_port


class ServerWebSockets(QObject):
    message_received = Signal(str, str)
    
    def __init__(self, ports, parent=None):
        super().__init__(parent)
        self.free_port = find_free_port(ports.begin, ports.end)
        
        self._server: Optional[QWebSocketServer] = None
        self.clients: dict[str, QWebSocket] = {}
        
        self._console = Console(record=True, )
    
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
    def actSendMessage(self, msg, uid):
        qDebug(f"Клиент прислал сообщение: {msg}")
        self.message_received.emit(msg, uid)
    
    @Slot(str)
    def actDisconnectClient(self, uid):
        client = self.clients[uid]
        if uid in self.clients:
            del self.clients[uid]
        client.deleteLater()
        qDebug("Клиент отключился")
        
    def sendConfirmState(self, uid):
        self._console.print(Text("True", "green"))
        self.sendMassage(uid, self._console.export_text(styles=True))
        
    def sendErrorState(self, uid, e):
        self._console.print(Text(f"Error: {e}", "Red"))
        self.sendMassage(uid, self._console.export_text(styles=True))
        
    def sendMassage(self, uid, msg):
        self.clients[uid].sendTextMessage(msg)
        
    def sendPrettyMsg(self, uid, msgs):
        self._console.print(Text.assemble(msgs))
        self.sendMassage(uid, self._console.export_text(styles=True))
        
