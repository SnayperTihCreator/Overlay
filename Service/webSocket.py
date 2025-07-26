from PySide6.QtCore import Signal

from APIService.qWebSockets import ServerWebSockets


class AppServerControl(ServerWebSockets):
    action_triggered = Signal(str, str)
    
    def __init__(self, ports, parent=None):
        super().__init__(ports, parent)
        self.message_received.connect(self.handle_message)
    
    def handle_message(self, message, uid):
        match message.split(" "):
            case ["action", name]:
                self.action_triggered.emit(name, uid)
            case ["print", message]:
                print(message)
                self.sendConfirmState(uid)
