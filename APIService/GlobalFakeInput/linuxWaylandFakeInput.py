from evdev import UInput, ecodes as e
import pulsectl
import time

from .enums import BaseLinuxKey
from .baseHandlerFakeInput import BaseHandlerFakeInput

SYSTEM_PROCESSES = {
    "pulseaudio", "firefox", "chromium", "discord",
    "notify-send", "system-sounds", "alsa", "gnome-shell"
}


class LinuxWaylandFakeInput(BaseHandlerFakeInput):
    @classmethod
    def isPlayingMusic(cls):
        with pulsectl.Pulse("music-detector") as pulse:
            for sink_input in pulse.sink_input_list():
                # Если поток активен и не заглушён
                if sink_input.state == pulsectl.PulseStateEnum.running and sink_input.volume.value_flat > 0:
                    # Получаем имя приложения
                    app_name = sink_input.proplist.get("application.name", "").lower()
                    process_name = sink_input.proplist.get("process.name", "").lower()
                    
                    # Если это не системный процесс и звук есть → это музыка
                    if app_name not in SYSTEM_PROCESSES and process_name not in SYSTEM_PROCESSES:
                        return True
            return False
    
    @classmethod
    def send_key_press(cls, keycode: BaseLinuxKey):
        cls.send_key_state(keycode, 1)
    
    @classmethod
    def send_key_release(cls, keycode: BaseLinuxKey):
        cls.send_key_state(keycode, 0)

    @classmethod
    def send_key_state(cls, keycode: BaseLinuxKey, state):
        with UInput([], "OverlayKeyboard") as ui:
            ui.write(e.EV_KEY, keycode, state)
            ui.syn()
