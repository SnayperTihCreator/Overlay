import sys
import subprocess
import os
from enum import StrEnum
import socket
import shutil

from evdev import UInput, ecodes


class PlayerCode(StrEnum):
    STOP = ("XF86AudioStop", 166)
    PLAY_PAUSE = ("XF86AudioPlay", 164)
    NEXT_TRACK = ("XF86AudioNext", 163)
    PREV_TRACK = ("XF86AudioPrev", 165)
    VOLUME_UP = ("XF86AudioRaiseVolume", 115)
    VOLUME_DOWN = ("XF86AudioLowerVolume", 114)
    VOLUME_MUTE = ("XF86AudioMute", 113)
    
    def __new__(cls, keysyms, keycode):
        obj = str.__new__(cls, keysyms)
        obj._value_ = keysyms
        obj.keycode = keycode
        return obj

def detect_display_server():
    return os.environ["XDG_SESSION_TYPE"]


def emulate_key(command):
    state, key = command.split(maxsplit=1)
    key = PlayerCode(key)
    """Эмулирует нажатие клавиши в Linux."""
    is_wayland = os.environ["XDG_SESSION_TYPE"] == "wayland"
    try:
        if is_wayland:
            state = 1 if state == "press" else 0
            with UInput() as ui:
                ui.write(ecodes.EV_KEY, key.keycode, state)
        else:
            state = "keydown" if state == "press" else "keyup"
            subprocess.run(["xdotool", state, key], check=True)
    except subprocess.CalledProcessError as e:
        print("Ошибка эмуляции:", e)


def run_server():
    display_server = detect_display_server()
    print(f"Сервер запущен ({display_server.upper()}). Ожидание команд...")

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    socket_path = "/tmp/keypress_socket.sock"

    # Удаляем старый сокет, если он есть
    try:
        os.unlink(socket_path)
    except FileNotFoundError:
        pass

    sock.bind(socket_path)
    sock.listen(1)

    while True:
        conn, _ = sock.accept()
        try:
            data = conn.recv(1024).decode().strip()
            if data:
                print(f"Получена команда: {data}")
                emulate_key(data)
        finally:
            conn.close()

if __name__ == "__main__":
    run_server()