import threading
import select
from time import sleep
from PySide6.QtCore import qInfo, qCritical
from evdev import InputDevice, ecodes, list_devices
from .baseHotkeyHandler import BaseHotkeyHandler
from ._wayland_key_map import WaylandKeyMap


class WaylandHotkeyHandler(BaseHotkeyHandler):
    def __init__(self):
        super().__init__()
        self._device = None
        self._thread = None
        self._poll = select.poll()
        self._active = False
        self._debounce_time = 0.05  # 50ms debounce time
        self._last_event_time = 0
    
    @staticmethod
    def _find_keyboard():
        """Находит устройство клавиатуры с оптимизацией поиска."""
        devices = [InputDevice(path) for path in list_devices()]
        for dev in devices:
            if "keyboard" in dev.name.lower():
                return dev
            dev.close()  # Закрываем неиспользуемые устройства
        raise RuntimeError(
            "Keyboard device not found!\n"
            "Run 'sudo usermod -aG input $USER' and reboot"
        )
    
    def start(self):
        if not self._active:
            try:
                self._device = self._find_keyboard()
                self._poll.register(self._device, select.POLLIN)
                self._active = True
                self._thread = threading.Thread(
                    target=self._listen,
                    daemon=True,
                    name="HotkeyListener"
                )
                self._thread.start()
                qInfo("Wayland hotkey handler started")
            except Exception as e:
                qCritical(f"Failed to start hotkey handler: {e}")
    
    def stop(self):
        if self._active:
            self._active = False
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=1)
            if self._device:
                self._poll.unregister(self._device)
                self._device.close()
            qInfo("Wayland hotkey handler stopped")
    
    def _listen(self):
        pressed_keys = set()
        last_combo = ""
        
        while self._active:
            try:
                # Используем poll с таймаутом для снижения CPU нагрузки
                events = self._poll.poll(100)  # 100ms timeout
                if not events:
                    continue
                
                event = self._device.read_one()
                if not event or event.type != ecodes.EV_KEY:
                    continue
                
                # Дебаунс событий
                current_time = event.timestamp()
                if current_time - self._last_event_time < self._debounce_time:
                    continue
                self._last_event_time = current_time
                
                key = WaylandKeyMap.get(event.code)
                if key == WaylandKeyMap.VK_NONE:
                    continue
                
                # Обновляем состояние клавиш
                if event.value == 1:  # Key down
                    pressed_keys.add(key.common_name)
                elif event.value == 0:  # Key up
                    pressed_keys.discard(key.common_name)
                elif event.value == 2:  # Key hold
                    continue  # Игнорируем удержание для экономии
                
                current_combo = self._normalize_combo('+'.join(pressed_keys))
                
                # Триггерим колбэки только при изменении комбинации
                if current_combo != last_combo:
                    self._trigger_callbacks(current_combo)
                    last_combo = current_combo
            
            except (IOError, OSError) as e:
                qCritical(f"Device error: {e}")
                sleep(1)  # Пауза при ошибках ввода/вывода
                if self._active:
                    self.stop()
                    self.start()
                break
            except Exception as e:
                qCritical(f"Unexpected error: {e}")
                sleep(1)