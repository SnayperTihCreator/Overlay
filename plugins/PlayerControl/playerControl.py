from PySide6.QtWidgets import QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor

from API import Config, DraggableWindow
from APIService.colorize import modulateIcon

from .utils import fakeInput, PlayerCode
from . import icons_rc


class PlayerControl(DraggableWindow):
    def __init__(self, parent=None):
        super().__init__(Config(__file__, "draggable_window"), parent)
        self.runs = True
        self.icons = None
        
        parent.registered_shortcut("play/pause media", "toggle_play", self)
        
        sizeIcon = QSize(1, 1) * self.config.icons.size
        
        self.box = QVBoxLayout()
        self.central_widget.setLayout(self.box)
        
        self.btn_play_pause = QPushButton()
        self.btn_play_pause.setIconSize(sizeIcon)
        self.btn_play_pause.pressed.connect(lambda: self.toggle_play_pause())
        
        self.btn_next_track = QPushButton()
        self.btn_next_track.setIconSize(sizeIcon)
        self.btn_next_track.pressed.connect(
            lambda: self.sender_media(PlayerCode.NEXT_TRACK)
        )
        
        self.btn_prev_track = QPushButton()
        self.btn_prev_track.setIconSize(sizeIcon)
        self.btn_prev_track.pressed.connect(
            lambda: self.sender_media(PlayerCode.PREV_TRACK)
        )
        
        self.btn_vol_up = QPushButton()
        self.btn_vol_up.setIconSize(sizeIcon)
        self.btn_vol_up.pressed.connect(
            lambda: self.sender_media1(PlayerCode.VOLUME_UP)
        )
        self.btn_vol_up.released.connect(
            lambda: self.sender_media2(PlayerCode.VOLUME_UP)
        )
        
        self.btn_vol_down = QPushButton()
        self.btn_vol_down.setIconSize(sizeIcon)
        self.btn_vol_down.pressed.connect(
            lambda: self.sender_media1(PlayerCode.VOLUME_DOWN)
        )
        self.btn_vol_down.released.connect(
            lambda: self.sender_media2(PlayerCode.VOLUME_DOWN)
        )
        
        self.btn_vol_mute = QPushButton()
        self.btn_vol_mute.setIconSize(sizeIcon)
        self.btn_vol_mute.pressed.connect(
            lambda: self.sender_media(PlayerCode.VOLUME_MUTE)
        )
        
        self.box.addWidget(self.btn_next_track)
        self.box.addWidget(self.btn_play_pause)
        self.box.addWidget(self.btn_prev_track)
        
        self.box.addWidget(self.btn_vol_up)
        self.box.addWidget(self.btn_vol_down)
        self.box.addWidget(self.btn_vol_mute)
        
        self.header = QPushButton()
        self.header.setIconSize(QSize(20, 20))
        self.header.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        self.box.insertWidget(0, self.header)
        self.updateIcons()
        
        self.playing = fakeInput.isPlayingMusic()
        self.set_state_play_pause(self.playing)
        
    def updateIcons(self):
        self.btn_play_pause.setIcon(self.getIcon("play", self.config.icons.modulate))
        self.btn_next_track.setIcon(self.getIcon("track_next", self.config.icons.modulate))
        self.btn_prev_track.setIcon(self.getIcon("track_prev", self.config.icons.modulate))
        self.btn_vol_up.setIcon(self.getIcon("volume_up", self.config.icons.modulate))
        self.btn_vol_down.setIcon(self.getIcon("volume_down", self.config.icons.modulate))
        self.btn_vol_mute.setIcon(self.getIcon("volume_mute", self.config.icons.modulate))
        self.header.setIcon(self.getIcon("header", self.config.icons.modulate))
    
    def shortcut_run(self, name):
        match name:
            case "toggle_play" if not self.runs:
                self.playing = not self.playing
                self.set_state_play_pause(self.playing)
        if hasattr(self, "runs") and self.runs:
            self.runs = False
    
    def set_state_play_pause(self, state):
        icon = self.getIcon("play" if not state else "pause", self.config.icons.modulate)
        self.btn_play_pause.setIcon(icon)
    
    def sender_media(self, key_code):
        fakeInput.send_key(key_code)
    
    def sender_media1(self, key_code):
        fakeInput.send_press_key(key_code)
    
    def sender_media2(self, key_code):
        fakeInput.send_up_key(key_code)
    
    def toggle_play_pause(self):
        self.runs = True
        fakeInput.send_key(PlayerCode.PLAY_PAUSE)
    
    @staticmethod
    def getIcon(name, color):
        return modulateIcon(QIcon(f":/player_control/{name}.png"), QColor(color))
    
    def reloadConfig(self):
        super().reloadConfig()
        self.updateIcons()
        
        
        
