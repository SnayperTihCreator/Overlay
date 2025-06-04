import platform

if platform.system() == "Windows":
    from .initer import initer
    initer()

from .playerControl import PlayerControl


def createWindow(parent):
    return PlayerControl(parent)

