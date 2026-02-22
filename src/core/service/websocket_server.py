import logging
from PySide6.QtCore import Signal

from core.network import QServerWebSockets

# Setup logger
logger = logging.getLogger(__name__)


class AppServerControl(QServerWebSockets):
    action_triggered = Signal(str, str)
    call_cli = Signal(str, str, list)
    
    def __init__(self, ports, parent=None):
        super().__init__(ports, parent)
        self.message_received.connect(self.handle_message)
        logger.info("AppServerControl initialized.")
    
    def handle_message(self, message: str, uid):
        command_parts = message.strip().split(" ")
        
        match command_parts:
            case ["action", name]:
                logger.info(f"Action triggered: '{name}' (Client: {uid})")
                self.action_triggered.emit(name, uid)
            
            case ["cli", interface, *args]:
                logger.info(f"CLI call: '{interface}', Args: {args}")
                self.call_cli.emit(uid, interface, args)
            
            case ["print", *text_parts]:
                text = " ".join(text_parts)
                logger.info(f"Remote print request: {text}")
                self.sendConfirmState(uid)
            
            case _:
                logger.warning(f"Unknown command format: '{message}' (Client: {uid})")
