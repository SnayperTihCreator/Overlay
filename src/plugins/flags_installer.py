import logging
import weakref
from typing import Optional

from attrs import define, field
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget

from utils.system import getSystem

# Initialize logger for this module
logger = logging.getLogger(__name__)


@define
class FlagsInstaller:
    _widget_ref: weakref.ReferenceType = field(repr=False)
    platform: str = field(init=False)
    window_system: str = field(init=False)
    
    def __attrs_post_init__(self):
        try:
            self.platform, self.window_system = getSystem()
            logger.debug(f"FlagsInstaller initialized. System: {self.platform}, Window System: {self.window_system}")
        except Exception as e:
            logger.error(f"Failed to detect system info: {e}", exc_info=True)
            self.platform = "unknown"
            self.window_system = "unknown"
    
    @property
    def widget(self) -> Optional[QWidget]:
        return self._widget_ref()
    
    @classmethod
    def bind(cls, widget: QWidget):
        return cls(widget_ref=weakref.ref(widget))
    
    def install(self, base_flags: Qt.WindowType = Qt.WindowType.Widget):
        try:
            w = self.widget
            if not w:
                logger.warning("Cannot install flags: Widget reference is dead")
                return
            
            # If widget has a parent and is not explicitly a Window, treat as sub-widget
            if w.parent() is not None and not (base_flags & Qt.WindowType.Window):
                w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
                w.setFocusPolicy(Qt.FocusPolicy.NoFocus)
                logger.debug("Applied sub-widget attributes")
                return
            
            final_flags = (
                    base_flags
                    | Qt.WindowType.FramelessWindowHint
                    | Qt.WindowType.WindowStaysOnTopHint
            )
            
            # Platform specific adjustments
            if self.platform == "win32":
                final_flags |= Qt.WindowType.Tool
            
            elif self.platform.startswith("linux"):
                if self.window_system == "x11":
                    final_flags |= Qt.WindowType.X11BypassWindowManagerHint
                    # Note: WA_X11NetWmWindowTypeDock might not be available in all Qt builds/versions
                    if hasattr(Qt.WidgetAttribute, 'WA_X11NetWmWindowTypeDock'):
                        w.setAttribute(Qt.WidgetAttribute.WA_X11NetWmWindowTypeDock)
                elif self.window_system == "wayland":
                    final_flags |= Qt.WindowType.ToolTip
            
            # Disable focus
            final_flags |= Qt.WindowType.WindowDoesNotAcceptFocus
            w.setWindowFlags(final_flags)
            
            # Attributes
            w.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
            w.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            w.setFocusPolicy(Qt.FocusPolicy.NoFocus)
            
            logger.info(f"Window flags installed successfully for {w.objectName() or 'Widget'}")
        
        except Exception as e:
            logger.error(f"Failed to install window flags: {e}", exc_info=True)
    
    def set_sticky(self, enabled: bool):
        """
        Toggles visibility across all desktops (True) or only current (False).
        Implemented via BypassWindowManagerHint for Linux X11.
        """
        try:
            w = self.widget
            if not w:
                return
            
            current_flags = w.windowFlags()
            
            if self.platform.startswith("linux") and self.window_system == "x11":
                if enabled:
                    current_flags |= Qt.WindowType.X11BypassWindowManagerHint
                else:
                    current_flags &= ~Qt.WindowType.X11BypassWindowManagerHint
                
                w.setWindowFlags(current_flags)
                w.show()
                logger.debug(f"Sticky mode set to {enabled} (X11 Bypass)")
            else:
                logger.debug(f"Sticky mode not implemented for platform: {self.platform}")
        
        except Exception as e:
            logger.error(f"Failed to set sticky mode: {e}", exc_info=True)
    
    def toggle_input_transparency(self, enabled: bool):
        """Dynamic control of 'click-through' behavior."""
        try:
            w = self.widget
            if not w:
                return
            
            current_flags = w.windowFlags()
            if enabled:
                current_flags |= Qt.WindowType.WindowTransparentForInput
            else:
                current_flags &= ~Qt.WindowType.WindowTransparentForInput
            
            w.setWindowFlags(current_flags)
            w.show()
            
            logger.debug(f"Input transparency toggled to: {enabled}")
        
        except Exception as e:
            logger.error(f"Failed to toggle input transparency: {e}", exc_info=True)
