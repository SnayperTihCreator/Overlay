from APIService.GlobalFakeInput import *


class PlayerCode(BaseCommonKey):
    STOP = "STOP"
    PLAY_PAUSE = "PLAY_PAUSE"
    NEXT_TRACK = "NEXT_TRACK"
    PREV_TRACK = "PREV_TRACK"
    VOLUME_UP = "VOLUME_UP"
    VOLUME_DOWN = "VOLUME_DOWN"
    VOLUME_MUTE = "VOLUME_MUTE"


class WinPlayerCode(BaseWindowsKey):
    STOP = 0xB2
    PLAY_PAUSE = 0xB3
    NEXT_TRACK = 0xB0
    PREV_TRACK = 0xB1
    VOLUME_UP = 0xAF
    VOLUME_DOWN = 0xAE
    VOLUME_MUTE = 0xAD


class LinuxPlayerCode(BaseLinuxKey):
    STOP = ("XF86AudioStop", 166)
    PLAY_PAUSE = ("XF86AudioPlay", 164)
    NEXT_TRACK = ("XF86AudioNext", 163)
    PREV_TRACK = ("XF86AudioPrev", 165)
    VOLUME_UP = ("XF86AudioRaiseVolume", 115)
    VOLUME_DOWN = ("XF86AudioLowerVolume", 114)
    VOLUME_MUTE = ("XF86AudioMute", 113)
    
    
fakeInput = EmitterFakeInput(PlayerCode, WinPlayerCode, LinuxPlayerCode)
