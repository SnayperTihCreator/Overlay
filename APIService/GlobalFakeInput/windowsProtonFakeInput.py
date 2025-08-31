import time

from APIService.webControls import ClientWebSockets
from API.config import Config

from .enums import BaseCommonKey
from .baseHandlerFakeInput import BaseHandlerFakeInput


class ClientProtonFakeInput(ClientWebSockets):
    def __init__(self, parent=None):
        self.config = Config.configApplication()
        super().__init__(self.config.data.websockets.OUT)
    
    def isPlayingMusic(self):
        self.send_message("check pmusic")
    
    def send_key_press(self, keycode: BaseCommonKey):
        self.send_message(f"press {keycode}")
    
    def send_key_release(self, keycode: BaseCommonKey):
        self.send_message(f"release {keycode}")


class WindowsProtonFakeInput(BaseHandlerFakeInput):
    clientFakeInput = ClientProtonFakeInput()
    
    @classmethod
    def send_key_press(cls, keycode):
        cls.clientFakeInput.send_key_press(keycode)
    
    @classmethod
    def send_key_release(cls, keycode):
        cls.clientFakeInput.send_key_press(keycode)
    
    @classmethod
    def isPlayingMusic(cls):
        return cls.clientFakeInput.isPlayingMusic()
    
    