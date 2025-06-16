from pycaw.pycaw import AudioUtilities
import win32api
import win32con
import time

from .enums import BaseWindowsKey
from .baseHandlerFakeInput import BaseHandlerFakeInput

SYSTEM_PROCESSES = ["explorer.exe", "svchost.exe", "System Sounds", "audiodg.exe"]
EVENT_PRESS = win32con.KEYEVENTF_EXTENDEDKEY
EVENT_RELEASE = win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP


class WindowsNativeFakeInput(BaseHandlerFakeInput):
    @classmethod
    def isPlayingMusic(cls):
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            if session.Process and session.State == 1:
                process_name = session.Process.name()
                volume = session.SimpleAudioVolume
                if (process_name not in SYSTEM_PROCESSES) and volume.GetMasterVolume() > 0:
                    return True
        return False
    
    @classmethod
    def send_press_key(cls, keycode: BaseWindowsKey):
        hwcode = win32api.MapVirtualKey(keycode, 0)
        win32api.keybd_event(keycode, hwcode, EVENT_PRESS, 0)
    
    @classmethod
    def send_release_key(cls, keycode: BaseWindowsKey):
        hwcode = win32api.MapVirtualKey(keycode, 0)
        win32api.keybd_event(keycode, hwcode, EVENT_RELEASE, 0)
