from enum import StrEnum
import os

from PySide6.QtCore import qDebug


def is_running_under_proton():
    # Проверяем специфичные для Proton переменные
    proton_env_vars = [
        "STEAM_COMPAT_DATA_PATH",
        "SteamAppId",
        "SteamGameId",
        "PROTON_",
    ]
    
    for var in proton_env_vars:
        if var in os.environ:
            return True
    
    # Дополнительная проверка на Wine
    if "WINEPREFIX" in os.environ or os.path.exists("/proc/sys/fs/binfmt_misc/Wine"):
        return True
    
    return False


class PlayerCode(StrEnum):
    STOP = "STOP"
    PLAY_PAUSE = "PLAY_PAUSE"
    NEXT_TRACK = "NEXT_TRACK"
    PREV_TRACK = "PREV_TRACK"
    VOLUME_UP = "VOLUME_UP"
    VOLUME_DOWN = "VOLUME_DOWN"
    VOLUME_MUTE = "VOLUME_MUTE"


if is_running_under_proton():
    from plugins.PlayerControl import _utils_win32_proton as utils_win32
else:
    from plugins.PlayerControl import _utils_win32_native as utils_win32


def send_press_key(key_code: PlayerCode):
    utils_win32.send_press_key(getattr(utils_win32.PlayerCode, key_code))


def send_up_key(key_code: PlayerCode):
    utils_win32.send_up_key(getattr(utils_win32.PlayerCode, key_code))


def send_key(key_code: PlayerCode):
    utils_win32.send_key(getattr(utils_win32.PlayerCode, key_code))


def is_audio_playing_windows():
    return utils_win32.is_audio_playing_windows()
