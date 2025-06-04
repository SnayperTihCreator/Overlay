from enum import StrEnum
import socket

from PySide6.QtCore import qInfo
from pycaw.pycaw import AudioUtilities


class PlayerCode(StrEnum):
    STOP = "XF86AudioStop"
    PLAY_PAUSE = "XF86AudioPlay"
    NEXT_TRACK = "XF86AudioNext"
    PREV_TRACK = "XF86AudioPrev"
    VOLUME_UP = "XF86AudioRaiseVolume"
    VOLUME_DOWN = "XF86AudioLowerVolume"
    VOLUME_MUTE = "XF86AudioMute"


def send_message(key):
    """Отправляет клавишу на сервер."""
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    socket_path = "/tmp/keypress_socket.sock"

    try:
        sock.connect(socket_path)
        sock.sendall(key.encode("utf-8"))
    except Exception as e:
        qInfo(f"Ошибка отправки: {e}")
    finally:
        sock.close()

def send_press_key(key):
    send_message(f"press {key}")

def send_up_key(key):
    send_message(f"release {key}")

def send_key(key):
    send_press_key(key)
    send_up_key(key)

def is_audio_playing_windows():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.State and session.Process:
            volume = session.SimpleAudioVolume
            if volume.GetMute() == 0 and volume.GetMasterVolume() > 0:
                return True
    return False
