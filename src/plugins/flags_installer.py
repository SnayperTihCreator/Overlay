import weakref
from attrs import define, field
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from utils.system import getSystem


@define
class FlagsInstaller:
    _widget_ref: weakref.ReferenceType = field(repr=False)
    platform: str = field(init=False)
    window_system: str = field(init=False)
    
    def __attrs_post_init__(self):
        self.platform, self.window_system = getSystem()
    
    @property
    def widget(self) -> QWidget | None:
        return self._widget_ref()
    
    @classmethod
    def bind(cls, widget: QWidget):
        return cls(widget_ref=weakref.ref(widget))
    
    def install(self, base_flags: Qt.WindowType = Qt.WindowType.Widget):
        w = self.widget
        if not w: return
        
        if w.parent() is not None and not (base_flags & Qt.WindowType.Window):
            w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            w.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            return
        
        final_flags = (
                base_flags
                | Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
        )
        
        if self.platform == "win32":
            final_flags |= Qt.WindowType.Tool
        
        elif self.platform.startswith("linux"):
            if self.window_system == "x11":
                final_flags |= Qt.WindowType.X11BypassWindowManagerHint
                w.setAttribute(Qt.WidgetAttribute.WA_X11NetWmWindowTypeDock)
            elif self.window_system == "wayland":
                final_flags |= Qt.WindowType.ToolTip
        
        # Запрещаем фокус
        final_flags |= Qt.WindowType.WindowDoesNotAcceptFocus
        w.setWindowFlags(final_flags)
        
        # Атрибуты
        w.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        w.setFocusPolicy(Qt.FocusPolicy.NoFocus)
    
    def set_sticky(self, enabled: bool):
        """
        Переключает: отображать на всех рабочих столах (True) или только на текущем (False).
        Реализовано через переключение Bypass для Linux X11.
        """
        w = self.widget
        if not w: return
        
        current_flags = w.windowFlags()
        
        if self.platform.startswith("linux") and self.window_system == "x11":
            if enabled:
                current_flags |= Qt.WindowType.X11BypassWindowManagerHint
            else:
                current_flags &= ~Qt.WindowType.X11BypassWindowManagerHint
        
        w.setWindowFlags(current_flags)
        w.show()
    
    def toggle_input_transparency(self, enabled: bool):
        """Динамическое управление 'кликом насквозь'"""
        w = self.widget
        if not w: return
        
        current_flags = w.windowFlags()
        if enabled:
            current_flags |= Qt.WindowType.WindowTransparentForInput
        else:
            current_flags &= ~Qt.WindowType.WindowTransparentForInput
        
        w.setWindowFlags(current_flags)
        w.show()