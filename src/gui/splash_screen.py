import logging
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMovie, QColor, QPainter, QPixmap, QFont
from PySide6.QtWidgets import QSplashScreen, QApplication

# Initialize logger for this module
logger = logging.getLogger(__name__)


class GifSplashScreen(QSplashScreen):
    def __init__(self, path, opacity=1.0, scale_factor=0.5):
        super().__init__(QPixmap())
        
        try:
            logger.debug(f"Initializing GifSplashScreen with path: {path}")
            
            self.movie = QMovie(path)
            self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
            self.movie.jumpToFrame(0)
            
            if not self.movie.isValid():
                logger.error(f"Failed to load GIF for splash screen: {path}")
            
            self.text_color = QColor("#ffffff")
            self.text_font = QFont("Arial", 12)
            
            # Size calculation: scale original GIF size by scale_factor
            current_pixmap = self.movie.currentPixmap()
            if not current_pixmap.isNull():
                orig_size = current_pixmap.size()
                self.scaled_size = orig_size * scale_factor
            else:
                # Fallback size if pixmap is null
                logger.warning("Splash screen pixmap is null, using default size")
                self.scaled_size = QPixmap(400, 300).size()
            
            self.setFixedSize(self.scaled_size)
            self.movie.setScaledSize(self.scaled_size)
            
            # Centering on screen
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                x = (screen_geometry.width() - self.width()) // 2
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
            
            self.movie.frameChanged.connect(self.repaint)
            self.movie.start()
            
            self.setWindowOpacity(opacity)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.SplashScreen
            )
            self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
            
            self.message = ""
            self._draw_texts = []
            
            logger.info("Splash screen initialized successfully")
        
        except Exception as e:
            logger.critical(f"Critical error initializing splash screen: {e}", exc_info=True)
    
    def setStatus(self, text, author):
        """Updates the loading status text."""
        try:
            self.clearTexts()
            self.drawText(author, (20, 30), size=10, font="UNCAGE")
            self.drawText(text, (20, self.height() - 20))
            self.repaint()
        except Exception as e:
            logger.error(f"Failed to set status text: {e}", exc_info=True)
    
    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            try:
                # Render hints
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, False)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                
                # Clear background
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Source)
                painter.fillRect(self.rect(), Qt.GlobalColor.transparent)
                
                painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                
                # Draw GIF frame
                pixmap = self.movie.currentPixmap()
                if not pixmap.isNull():
                    painter.drawPixmap(self.rect(), pixmap)
                
                # Draw texts
                painter.setOpacity(1.0)
                for text, pos, color, size, font_name in self._draw_texts:
                    painter.setPen(color or self.text_color)
                    
                    f = QFont(font_name) if font_name else self.text_font
                    if size:
                        f.setPointSize(size)
                    painter.setFont(f)
                    
                    if isinstance(pos, QPoint):
                        painter.drawText(pos, text)
                    else:
                        painter.drawText(pos[0], pos[1], text)
            
            finally:
                painter.end()
        
        except Exception as e:
            # We log painting errors carefully as this runs frequently
            logger.error(f"Error painting splash screen: {e}", exc_info=True)
    
    def setMessage(self, message, alignment=None, color=None):
        """Sets a message to display on top of the animation."""
        try:
            self.message = message
            if alignment:
                self.text_alignment = alignment
            if color:
                self.text_color = color
            self.repaint()
        except Exception as e:
            logger.error(f"Failed to set message: {e}", exc_info=True)
    
    def drawText(self, text, position, color=None, size=None, font=None):
        try:
            self._draw_texts.append((text, position, color, size, font))
        except Exception as e:
            logger.error(f"Failed to add text to draw list: {e}", exc_info=True)
    
    def clearTexts(self):
        self._draw_texts.clear()
    
    def setOpacity(self, opacity):
        """Sets transparency level (0.0 - fully transparent, 1.0 - fully opaque)."""
        try:
            self.setWindowOpacity(opacity)
        except Exception as e:
            logger.error(f"Failed to set opacity: {e}", exc_info=True)
    
    def finish(self, main_window):
        try:
            logger.debug("Finishing splash screen")
            self.movie.stop()
            super().finish(main_window)
        except Exception as e:
            logger.error(f"Error finishing splash screen: {e}", exc_info=True)
