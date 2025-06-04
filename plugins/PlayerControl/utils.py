import platform
from enum import IntEnum

match platform.system():
    case "Windows":
        import win32api
        import win32con
        from pycaw.pycaw import AudioUtilities

        class PlayerCode(IntEnum):
            STOP = 0xB2
            PLAY_PAUSE = 0xB3
            NEXT_TRACK = 0xB0
            PREV_TRACK = 0xB1
            VOLUME_UP = 0xAF
            VOLUME_DOWN = 0xAE
            VOLUME_MUTE = 0xAD

        def send_press_key(key_code: PlayerCode):
            hwcode = win32api.MapVirtualKey(key_code, 0)
            win32api.keybd_event(key_code, hwcode, win32con.KEYEVENTF_EXTENDEDKEY, 0)

        def send_up_key(key_code: PlayerCode):
            hwcode = win32api.MapVirtualKey(key_code, 0)
            win32api.keybd_event(
                key_code,
                hwcode,
                win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP,
                0,
            )

        def send_key(key_code: PlayerCode):
            send_press_key(key_code)
            send_up_key(key_code)

        def is_audio_playing_windows():
            sessions = AudioUtilities.GetAllSessions()
            for session in sessions:
                if session.State and session.Process:
                    volume = session.SimpleAudioVolume
                    if volume.GetMute() == 0 and volume.GetMasterVolume() > 0:
                        return True
            return False

    case _:
        raise NotImplementedError
