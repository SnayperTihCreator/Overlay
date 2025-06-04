import sys
import subprocess
import os
from enum import StrEnum

from PySide6.QtCore import QObject, Slot
from PySide6.QtWidgets import QApplication
from PySide6.QtNetwork import QLocalServer


class PlayerCode(StrEnum):
    STOP = "XF86AudioStop", 166
    PLAY_PAUSE = "XF86AudioPlay", 164
    NEXT_TRACK = "XF86AudioNext", 163
    PREV_TRACK = "XF86AudioPrev", 165
    VOLUME_UP = "XF86AudioRaiseVolume", 115
    VOLUME_DOWN = "XF86AudioLowerVolume", 114
    VOLUME_MUTE = "XF86AudioMute", 113
    
    def __new__(cls, keysyms, keycode):
        obj = object.__new__(cls)
        obj._value_ = keysyms
        obj.keycode = keycode


class KeyEmulatorServer(QObject):
    def __init__(self):
        super().__init__()
        self.server = QLocalServer()
        self.server.newConnection.connect(self.handle_client)
        
        # Удаляем старый сокет, если он есть
        QLocalServer.removeServer("keypress_socket")
        
        if not self.server.listen("keypress_socket"):
            print("Ошибка запуска сервера:", self.server.errorString())
            sys.exit(1)
        
        print("Сервер запущен. Ожидание подключений...")
    
    @Slot()
    def handle_client(self):
        conn = self.server.nextPendingConnection()
        conn.readyRead.connect(lambda: self.read_data(conn))
        conn.disconnected.connect(conn.deleteLater)
    
    def read_data(self, conn):
        data = conn.readAll().data().decode().strip()
        if data:
            print("Получена команда:", data)
            self.emulate_key(data)
            conn.write(b"OK")  # Отправляем подтверждение
    
    def emulate_key(self, command):
        state, key = command.split(maxsplit=1)
        key = PlayerCode(key)
        """Эмулирует нажатие клавиши в Linux."""
        is_wayland = os.environ["XDG_SESSION_TYPE"] == "wayland"
        try:
            if is_wayland:
                state = "1" if state == "press" else "0"
                subprocess.run(["ydotool", "key", f"{key.keycode}:{state}"], check=True)
            else:
                state = "keydown" if state == "press" else "keyup"
                subprocess.run(["xdotool", state, key], check=True)
        except subprocess.CalledProcessError as e:
            print("Ошибка эмуляции:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    server = KeyEmulatorServer()
    sys.exit(app.exec())
