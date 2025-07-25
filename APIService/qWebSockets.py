from typing import Optional

from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocketServer
from PySide6.QtCore import QObject, Signal, Slot, qDebug, QUrl, qWarning

from .webControls import find_free_port


class ServerWebSockets(QObject):
    message_received = Signal(str)
    
    def __init__(self, ports, parent=None):
        super().__init__(parent)
        self.free_port = find_free_port(*ports)
        
        self._server: Optional[QWebSocketServer] = None
        self.clients = []
    
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
        for client in self.clients:
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
            self.clients.append(client)
            client.textMessageReceived.connect(self.actSendMessage)
            client.disconnected.connect(self.actDisconnectClient)
            
    @Slot(str)
    def actSendMessage(self, msg):
        qDebug(f"Клиент прислал сообщение: {msg}")
        self.message_received.emit(msg)
    
    @Slot()
    def actDisconnectClient(self):
        client = self.sender()
        if client in self.clients:
            self.clients.remove(client)
        client.deleteLater()
        qDebug("Клиент отключился")
