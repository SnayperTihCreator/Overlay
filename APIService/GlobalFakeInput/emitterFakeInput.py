from functools import cache

from APIService.platformCurrent import getSystem
from .enums import BaseCommonKey, BaseWindowsKey, BaseLinuxKey


class EmitterFakeInput:
    def __init__(self, c_keycode: type[BaseCommonKey], w_keycode: type[BaseWindowsKey], l_keycode: type[BaseLinuxKey]):
        self.c_keycode = c_keycode
        self.w_keycode = w_keycode
        self.l_keycode = l_keycode
        self.platform, self.windowed = getSystem()
        match [self.platform, self.windowed]:
            case ["win32", "native"]:
                from .windowsNativeFakeInput import WindowsNativeFakeInput
                self.handler = WindowsNativeFakeInput()
            case ["win32", "proton"]:
                from .windowsProtonFakeInput import WindowsProtonFakeInput
                self.handler = WindowsProtonFakeInput()
            case ["linux", "wayland"]:
                from .linuxWaylandFakeInput import LinuxWaylandFakeInput
                self.handler = LinuxWaylandFakeInput()
            case ["linux", "x11"]:
                from .linuxX11FakeInput import LinuxX11FakeInput
                self.handler = LinuxX11FakeInput()
    
    @cache
    def _get_keycode_enum(self, keycode: BaseCommonKey):
        if isinstance(keycode, int):
            return keycode
        if isinstance(keycode, BaseLinuxKey):
            return keycode
        if isinstance(keycode, BaseWindowsKey):
            return keycode
        
        match [self.platform, self.windowed]:
            case ["win32", "native"]:
                return getattr(self.w_keycode, keycode.value)
            case ["win32", "proton"]:
                return keycode
            case ["linux", window]:
                return getattr(self.l_keycode, keycode.value).keycode
    
    def send_key_press(self, keycode: BaseCommonKey):
        keycode = self._get_keycode_enum(keycode)
        self.handler.send_key_press(keycode)
    
    def send_key_release(self, keycode: BaseCommonKey):
        keycode = self._get_keycode_enum(keycode)
        self.handler.send_key_release(keycode)
    
    def send_key(self, keycode: BaseCommonKey):
        keycode = self._get_keycode_enum(keycode)
        self.send_key_press(keycode)
        self.send_key_release(keycode)
    
    def isPlayingMusic(self):
        return self.handler.isPlayingMusic()