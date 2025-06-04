import threading

from PySide6.QtCore import qInfo, qCritical
from evdev import InputDevice, ecodes, list_devices

from .baseHotkeyHandler import BaseHotkeyHandler
from ._wayland_key_map import WaylandKeyMap


class WaylandHotkeyHandler(BaseHotkeyHandler):
    def __init__(self):
        super().__init__()
        self._device = self._find_keyboard()
        self._thread = None
    
    @staticmethod
    def _find_keyboard():
        """Находит устройство клавиатуры."""
        for path in list_devices():
            dev = InputDevice(path)
            if "keyboard" in dev.name.lower():
                return dev
        raise RuntimeError("Keyboard device not found!\nRun 'sudo usermod -aG input $USER' and reboot")
    
    def start(self):
        if not self._active and self._device:
            self._active = True
            self._thread = threading.Thread(target=self._listen, daemon=True)
            self._thread.start()
            qInfo("Wayland hotkey handler started")
    
    def stop(self):
        if self._active:
            self._active = False
            if self._thread:
                self._thread.join()
            qInfo("Wayland hotkey handler stopped")
    
    def _listen(self):
        pressed_keys = set()
        while self._active:
            try:
                event = self._device.read_one()
                if event and event.type == ecodes.EV_KEY:
                    key = WaylandKeyMap.get(event.code)
                    if key == WaylandKeyMap.VK_NONE:
                        continue
                        
                    if event.value == 1:  # Key down
                        pressed_keys.add(key.common_name)
                    elif event.value == 0:  # Key up
                        pressed_keys.discard(key.common_name)
                        
                    current_combo = self._normalize_combo('+'.join(pressed_keys))
                    self._trigger_callbacks(current_combo)
            except Exception as e:
                qCritical(f"Evdev error: {e}")