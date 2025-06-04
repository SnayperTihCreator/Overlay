from enum import IntEnum
from evdev import ecodes


class WaylandKeyMap(IntEnum):
    """Полный enum клавиш с общими и конкретными именами."""
    
    # Специальные значения
    VK_NONE = (-1, "none", "none")
    
    # Модификаторы (с общими именами)
    VK_LEFT_CTRL = (ecodes.KEY_LEFTCTRL, "ctrl", "left-ctrl")
    VK_RIGHT_CTRL = (ecodes.KEY_RIGHTCTRL, "ctrl", "right-ctrl")
    VK_LEFT_SHIFT = (ecodes.KEY_LEFTSHIFT, "shift", "left-shift")
    VK_RIGHT_SHIFT = (ecodes.KEY_RIGHTSHIFT, "shift", "right-shift")
    VK_LEFT_ALT = (ecodes.KEY_LEFTALT, "alt", "left-alt")
    VK_RIGHT_ALT = (ecodes.KEY_RIGHTALT, "alt", "right-alt")
    VK_LEFT_META = (ecodes.KEY_LEFTMETA, "meta", "left-meta")
    VK_RIGHT_META = (ecodes.KEY_RIGHTMETA, "meta", "right-meta")
    
    # Буквенные клавиши
    VK_A = (ecodes.KEY_A, "a", "a")
    VK_B = (ecodes.KEY_B, "b", "b")
    VK_C = (ecodes.KEY_C, "c", "c")
    VK_D = (ecodes.KEY_D, "d", "d")
    VK_E = (ecodes.KEY_E, "e", "e")
    VK_F = (ecodes.KEY_F, "f", "f")
    VK_G = (ecodes.KEY_G, "g", "g")
    VK_H = (ecodes.KEY_H, "h", "h")
    VK_I = (ecodes.KEY_I, "i", "i")
    VK_J = (ecodes.KEY_J, "j", "j")
    VK_K = (ecodes.KEY_K, "k", "k")
    VK_L = (ecodes.KEY_L, "l", "l")
    VK_M = (ecodes.KEY_M, "m", "m")
    VK_N = (ecodes.KEY_N, "n", "n")
    VK_O = (ecodes.KEY_O, "o", "o")
    VK_P = (ecodes.KEY_P, "p", "p")
    VK_Q = (ecodes.KEY_Q, "q", "q")
    VK_R = (ecodes.KEY_R, "r", "r")
    VK_S = (ecodes.KEY_S, "s", "s")
    VK_T = (ecodes.KEY_T, "t", "t")
    VK_U = (ecodes.KEY_U, "u", "u")
    VK_V = (ecodes.KEY_V, "v", "v")
    VK_W = (ecodes.KEY_W, "w", "w")
    VK_X = (ecodes.KEY_X, "x", "x")
    VK_Y = (ecodes.KEY_Y, "y", "y")
    VK_Z = (ecodes.KEY_Z, "z", "z")
    
    # Цифровые клавиши
    VK_0 = (ecodes.KEY_0, "0", "0")
    VK_1 = (ecodes.KEY_1, "1", "1")
    VK_2 = (ecodes.KEY_2, "2", "2")
    VK_3 = (ecodes.KEY_3, "3", "3")
    VK_4 = (ecodes.KEY_4, "4", "4")
    VK_5 = (ecodes.KEY_5, "5", "5")
    VK_6 = (ecodes.KEY_6, "6", "6")
    VK_7 = (ecodes.KEY_7, "7", "7")
    VK_8 = (ecodes.KEY_8, "8", "8")
    VK_9 = (ecodes.KEY_9, "9", "9")
    
    # Навигация
    VK_UP = (ecodes.KEY_UP, "up", "up")
    VK_DOWN = (ecodes.KEY_DOWN, "down", "down")
    VK_LEFT = (ecodes.KEY_LEFT, "left", "left")
    VK_RIGHT = (ecodes.KEY_RIGHT, "right", "right")
    VK_HOME = (ecodes.KEY_HOME, "home", "home")
    VK_END = (ecodes.KEY_END, "end", "end")
    VK_PAGE_UP = (ecodes.KEY_PAGEUP, "page up", "page-up")
    VK_PAGE_DOWN = (ecodes.KEY_PAGEDOWN, "page down", "page-down")
    VK_INSERT = (ecodes.KEY_INSERT, "insert", "insert")
    VK_DELETE = (ecodes.KEY_DELETE, "delete", "delete")
    
    # Управление
    VK_ENTER = (ecodes.KEY_ENTER, "enter", "enter")
    VK_ESC = (ecodes.KEY_ESC, "esc", "esc")
    VK_TAB = (ecodes.KEY_TAB, "tab", "tab")
    VK_BACKSPACE = (ecodes.KEY_BACKSPACE, "backspace", "backspace")
    VK_SPACE = (ecodes.KEY_SPACE, "space", "space")
    VK_CAPS_LOCK = (ecodes.KEY_CAPSLOCK, "caps lock", "caps-lock")
    VK_NUM_LOCK = (ecodes.KEY_NUMLOCK, "num lock", "num-lock")
    VK_SCROLL_LOCK = (ecodes.KEY_SCROLLLOCK, "scroll lock", "scroll-lock")
    VK_PRINT = (ecodes.KEY_PRINT, "print", "print")
    VK_PAUSE = (ecodes.KEY_PAUSE, "pause", "pause")
    VK_MENU = (ecodes.KEY_MENU, "menu", "menu")  # Клавиша контекстного меню
    
    # Цифры и операции
    VK_KP_0 = (ecodes.KEY_KP0, "num 0", "kp-0")
    VK_KP_1 = (ecodes.KEY_KP1, "num 1", "kp-1")
    VK_KP_2 = (ecodes.KEY_KP2, "num 2", "kp-2")
    VK_KP_3 = (ecodes.KEY_KP3, "num 3", "kp-3")
    VK_KP_4 = (ecodes.KEY_KP4, "num 4", "kp-4")
    VK_KP_5 = (ecodes.KEY_KP5, "num 5", "kp-5")
    VK_KP_6 = (ecodes.KEY_KP6, "num 6", "kp-6")
    VK_KP_7 = (ecodes.KEY_KP7, "num 7", "kp-7")
    VK_KP_8 = (ecodes.KEY_KP8, "num 8", "kp-8")
    VK_KP_9 = (ecodes.KEY_KP9, "num 9", "kp-9")
    VK_KP_ENTER = (ecodes.KEY_KPENTER, "num enter", "kp-enter")
    VK_KP_PLUS = (ecodes.KEY_KPPLUS, "num +", "kp-plus")
    VK_KP_MINUS = (ecodes.KEY_KPMINUS, "num -", "kp-minus")
    VK_KP_MULTIPLY = (ecodes.KEY_KPASTERISK, "num *", "kp-multiply")
    VK_KP_DIVIDE = (ecodes.KEY_KPSLASH, "num /", "kp-divide")
    VK_KP_DOT = (ecodes.KEY_KPDOT, "num .", "kp-dot")  # . на нампаде
    VK_KP_COMMA = (ecodes.KEY_KPCOMMA, "num ,", "kp-comma")  # , на нампаде
    
    # Управление медиа
    VK_VOLUME_UP = (ecodes.KEY_VOLUMEUP, "volume up", "volume-up")
    VK_VOLUME_DOWN = (ecodes.KEY_VOLUMEDOWN, "volume down", "volume-down")
    VK_VOLUME_MUTE = (ecodes.KEY_MUTE, "volume mute", "volume-mute")
    VK_PLAY_PAUSE = (ecodes.KEY_PLAYPAUSE, "play/pause media", "play-pause")
    VK_NEXT_TRACK = (ecodes.KEY_NEXTSONG, "next track", "next-track")
    VK_PREV_TRACK = (ecodes.KEY_PREVIOUSSONG, "previous track", "prev-track")
    VK_STOP = (ecodes.KEY_STOPCD, "stop media", "stop")
    VK_EJECT = (ecodes.KEY_EJECTCD, "eject", "eject")
    
    # Управление питанием
    VK_POWER = (ecodes.KEY_POWER, "power", "power")
    VK_SLEEP = (ecodes.KEY_SLEEP, "sleep", "sleep")
    VK_WAKE = (ecodes.KEY_WAKEUP, "wake", "wake")
    
    def __new__(cls, value, common_name, specific_name):
        obj = int.__new__(cls, value)
        obj._value_ = value
        obj.common_name = common_name
        obj.specific_name = specific_name
        return obj
    
    @classmethod
    def get(cls, key_code):
        """Находит клавишу по коду или возвращает VK_NONE."""
        try:
            return cls(key_code)
        except ValueError:
            return cls.VK_NONE