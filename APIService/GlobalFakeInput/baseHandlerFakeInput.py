
class BaseHandlerFakeInput:
    @classmethod
    def send_key_press(cls, keycode): ...
    
    @classmethod
    def send_key_release(cls, keycode): ...
    
    @classmethod
    def isPlayingMusic(cls): ...