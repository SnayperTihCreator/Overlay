from PySide6.QtCore import Signal

from APIService.qWebSockets import ServerWebSockets


class AppServerControl(ServerWebSockets):
    action_triggered = Signal(str, str)
    call_cli = Signal(str, str, list)
    
    def __init__(self, ports, parent=None):
        super().__init__(ports, parent)
        self.message_received.connect(self.handle_message)
    
    def handle_message(self, message:str, uid):
        match message.strip().split(" "):
            case ["action", name]:
                self.action_triggered.emit(name, uid)
            case ["cli", interface, *args]:
                self.call_cli.emit(uid, interface, args)
            case ["print", message]:
                print(message)
                self.sendConfirmState(uid)
