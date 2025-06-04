import importlib
from pathlib import Path

from PySide6.QtWidgets import QVBoxLayout, QPushButton
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon

from API import Config, DraggableWindow, Backend


class PlayerControl(DraggableWindow):
    def __init__(self, parent=None):
        super().__init__(Config(__file__, "draggable_window"), parent)
        self.runs = True
        self.icons = None
        
        self.import_icons()
        
        self.backed = Backend(Path(__file__).parent, "utils")
        
        parent.registered_shortcut("play/pause media", "toggle_play", self)
        
        sizeIcon = QSize(1, 1) * self.config.icons.size
        
        self.box = QVBoxLayout()
        self.central_widget.setLayout(self.box)
        
        self.btn_play_pause = QPushButton(self.getIcon("play"), "")
        self.btn_play_pause.setIconSize(sizeIcon)
        self.btn_play_pause.pressed.connect(lambda: self.toggle_play_pause())
        
        self.btn_next_track = QPushButton(self.getIcon("track_next"), "")
        self.btn_next_track.setIconSize(sizeIcon)
        self.btn_next_track.pressed.connect(
            lambda: self.sender_media(self.backed.PlayerCode.NEXT_TRACK)
        )
        
        self.btn_prev_track = QPushButton(self.getIcon("track_prev"), "")
        self.btn_prev_track.setIconSize(sizeIcon)
        self.btn_prev_track.pressed.connect(
            lambda: self.sender_media(self.backed.PlayerCode.PREV_TRACK)
        )
        
        self.btn_vol_up = QPushButton(self.getIcon("volume_up"), "")
        self.btn_vol_up.setIconSize(sizeIcon)
        self.btn_vol_up.pressed.connect(
            lambda: self.sender_media1(self.backed.PlayerCode.VOLUME_UP)
        )
        self.btn_vol_up.released.connect(
            lambda: self.sender_media2(self.backed.PlayerCode.VOLUME_UP)
        )
        
        self.btn_vol_down = QPushButton(self.getIcon("volume_down"), "")
        self.btn_vol_down.setIconSize(sizeIcon)
        self.btn_vol_down.pressed.connect(
            lambda: self.sender_media1(self.backed.PlayerCode.VOLUME_DOWN)
        )
        self.btn_vol_down.released.connect(
            lambda: self.sender_media2(self.backed.PlayerCode.VOLUME_DOWN)
        )
        
        self.btn_vol_mute = QPushButton(self.getIcon("volume_mute"), "")
        self.btn_vol_mute.setIconSize(sizeIcon)
        self.btn_vol_mute.pressed.connect(
            lambda: self.sender_media(self.backed.PlayerCode.VOLUME_MUTE)
        )
        
        self.box.addWidget(self.btn_next_track)
        self.box.addWidget(self.btn_play_pause)
        self.box.addWidget(self.btn_prev_track)
        
        self.box.addWidget(self.btn_vol_up)
        self.box.addWidget(self.btn_vol_down)
        self.box.addWidget(self.btn_vol_mute)
        
        self.header = QPushButton(self.getIcon("header"), "")
        self.header.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        
        self.box.insertWidget(0, self.header)
        
        self.playing = self.backed.is_audio_playing_windows()
        self.set_state_play_pause(self.playing)
    
    def import_icons(self):
        match self.config.icons.theme:
            case "black" | "white" as theme:
                self.icons = importlib.import_module(f"plugins.PlayerControl.icons_rc_{theme}")
            case _:
                from . import icons_rc
                self.icons = icons_rc
    
    def shortcut_run(self, name):
        match name:
            case "toggle_play" if not self.runs:
                self.playing = not self.playing
                self.set_state_play_pause(self.playing)
        if hasattr(self, "runs") and self.runs:
            self.runs = False
    
    def set_state_play_pause(self, state):
        icon = self.getIcon("play" if not state else "pause")
        self.btn_play_pause.setIcon(icon)
    
    def sender_media(self, key_code):
        self.backed.send_key(key_code)
    
    def sender_media1(self, key_code):
        self.backed.send_press_key(key_code)
    
    def sender_media2(self, key_code):
        self.backed.send_up_key(key_code)
    
    def toggle_play_pause(self):
        self.runs = True
        self.backed.send_key(self.backed.PlayerCode.PLAY_PAUSE)
    
    def getIcon(self, name):
        return QIcon(f":/player_control/{name}.png")
    
    def reloadConfig(self):
        self.icons.qCleanupResources()
        super().reloadConfig()
        self.import_icons()
        self.icons.qInitResources()
        
        self.btn_play_pause.setIcon(self.getIcon("play"))
        self.btn_next_track.setIcon(self.getIcon("track_next"))
        self.btn_prev_track.setIcon(self.getIcon("track_prev"))
        self.btn_vol_up.setIcon(self.getIcon("volume_up"))
        self.btn_vol_down.setIcon(self.getIcon("volume_down"))
        self.btn_vol_mute.setIcon(self.getIcon("volume_mute"))
        self.header.setIcon(self.getIcon("header"))
