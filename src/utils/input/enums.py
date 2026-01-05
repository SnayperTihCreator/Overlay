from enum import StrEnum, IntEnum


class BaseCommonKey(StrEnum):
    pass


class BaseWindowsKey(IntEnum):
    pass


class BaseLinuxKey(StrEnum):
    def __new__(cls, keysyms, keycode):
        obj = str.__new__(cls, keysyms)
        obj._value_ = keysyms
        obj.keycode = keycode
        return obj


__all__ = ["BaseCommonKey", "BaseWindowsKey", "BaseLinuxKey"]
