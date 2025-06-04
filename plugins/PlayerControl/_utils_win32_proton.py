from enum import StrEnum

from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtNetwork import QLocalSocket
from pycaw.pycaw import AudioUtilities


class PlayerCode(StrEnum):
    STOP = "XF86AudioStop"
    PLAY_PAUSE = "XF86AudioPlay"
    NEXT_TRACK = "XF86AudioNext"
    PREV_TRACK = "XF86AudioPrev"
    VOLUME_UP = "XF86AudioRaiseVolume"
    VOLUME_DOWN = "XF86AudioLowerVolume"
    VOLUME_MUTE = "XF86AudioMute"


class KeySenderClient(QObject):
    response_received = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.socket = QLocalSocket()
        self.socket.connected.connect(self.on_connected)
        self.socket.readyRead.connect(self.on_ready_read)
        self.socket.errorOccurred.connect(self.on_error)
    
    def send_message(self, key):
        """Отправляет клавишу на сервер."""
        if self.socket.state() != QLocalSocket.LocalSocketState.ConnectedState:
            self.socket.connectToServer("keypress_socket")
        
        if self.socket.waitForConnected(1000):
            self.socket.write(key.encode("utf-8"))
            self.socket.waitForBytesWritten(1000)
        else:
            self.response_received.emit("Ошибка подключения")
    
    def send_press_key(self, key: PlayerCode):
        self.send_message(f"press {key}")
    
    def send_release_key(self, key: PlayerCode):
        self.send_message(f"release {key}")
    
    def send_key(self, key: PlayerCode):
        self.send_press_key(key)
        self.socket.waitForBytesWritten(1000)
        self.send_release_key(key)
    
    @Slot()
    def on_connected(self):
        print("Подключено к серверу")
    
    @Slot()
    def on_ready_read(self):
        response = self.socket.readAll().data().decode()
        self.response_received.emit(f"Ответ сервера: {response}")
    
    @Slot()
    def on_error(self, error):
        self.response_received.emit(f"Ошибка: {self.socket.errorString()}")


_keySenderClient = KeySenderClient()

send_press_key = _keySenderClient.send_press_key
send_up_key = _keySenderClient.send_release_key
send_key = _keySenderClient.send_key


def is_audio_playing_windows():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.State and session.Process:
            volume = session.SimpleAudioVolume
            if volume.GetMute() == 0 and volume.GetMasterVolume() > 0:
                return True
    return False
