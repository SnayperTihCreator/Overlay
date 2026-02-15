from typing import Optional
import uuid
import logging

from PySide6.QtNetwork import QHostAddress
from PySide6.QtWebSockets import QWebSocketServer, QWebSocket
from PySide6.QtCore import QObject, Signal, Slot

from .webcontrol import find_free_port

logger = logging.getLogger(__name__)


class ServerWebSockets(QObject):
    message_received = Signal(str, str)
    
    def __init__(self, ports, parent=None):
        super().__init__(parent)
        self.free_port = find_free_port(ports[0], ports[1])
        
        self._server: Optional[QWebSocketServer] = None
        self.clients: dict[str, QWebSocket] = {}
    
    def start(self):
        self._server = QWebSocketServer("Overlay WebSockets", QWebSocketServer.SslMode.NonSecureMode)
        
        if not self._server.listen(QHostAddress("127.0.0.1"), self.free_port):
            err_code = self._server.error()
            err_msg = self._server.errorString()
            logger.error(f"Server failed to start. Code: {err_code}, Message: {err_msg}")
            return False
        
        url = self._server.serverUrl().toString()
        logger.info(f"Server started at: {url}")
        
        self._server.newConnection.connect(self.actNewConnection)
        return True
    
    def is_run(self):
        return self._server is not None
    
    def quit(self):
        if not self._server:
            return
        
        logger.info("Stopping server...")
        
        for uid, client in self.clients.items():
            try:
                client.close()
                client.deleteLater()
            except Exception as e:
                logger.warning(f"Error closing client {uid}: {e}")
        
        self.clients.clear()
        
        self._server.close()
        self._server.deleteLater()
        self._server = None
        
        logger.info("Server stopped.")
    
    @Slot()
    def actNewConnection(self):
        client = self._server.nextPendingConnection()
        if client:
            uid = uuid.uuid4().hex
            self.clients[uid] = client
            
            logger.info(f"New client connected. ID: {uid}")
            
            client.textMessageReceived.connect(lambda msg: self.actSendMessage(msg, uid))
            client.disconnected.connect(lambda: self.actDisconnectClient(uid))
    
    @Slot(str, str)
    def actSendMessage(self, msg: str, uid: str):
        logger.debug(f"Received message from {uid}: {msg}")
        self.message_received.emit(msg, uid)
    
    @Slot(str)
    def actDisconnectClient(self, uid: str):
        if uid in self.clients:
            client = self.clients[uid]
            del self.clients[uid]
            client.deleteLater()
            logger.info(f"Client disconnected. ID: {uid}")
    
    def sendConfirmState(self, uid: str):
        self.sendMassage(uid, "[bold green]Done[/bold green]")
    
    def sendErrorState(self, uid: str, e: Exception):
        logger.warning(f"Sending error state to client {uid}: {e}")
        self.sendMassage(uid, f"[bold red]Error {type(e).__name__}: {e}[/bold red]")
    
    def sendMassage(self, uid: str, msg: str):
        try:
            if uid in self.clients:
                self.clients[uid].sendTextMessage(msg)
            else:
                logger.warning(f"Cannot send message: Client {uid} not found.")
        except Exception as e:
            logger.error(f"Failed to send message to {uid}: {e}", exc_info=True)
