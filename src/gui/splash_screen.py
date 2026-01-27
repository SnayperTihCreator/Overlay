import copy
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QMovie, QColor, QPainter, QPixmap, QFont
from PySide6.QtWidgets import QSplashScreen, QApplication


class GifSplashScreen(QSplashScreen):
    def __init__(self, path, opacity=1.0, scale_factor=0.5):  # Добавили scale_factor
        super().__init__(QPixmap())
        
        self.movie = QMovie(path)
        self.movie.setCacheMode(QMovie.CacheAll)
        self.movie.jumpToFrame(0)
        
        self.text_color = QColor("#ffffff")
        self.text_font = QFont("Arial", 12)
        
        # РАСЧЕТ РАЗМЕРА: уменьшаем оригинальный размер GIF в scale_factor раз
        orig_size = self.movie.currentPixmap().size()
        self.scaled_size = orig_size * scale_factor
        self.setFixedSize(self.scaled_size)
        self.movie.setScaledSize(self.scaled_size)
        
        # ЦЕНТРИРОВАНИЕ
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        self.movie.frameChanged.connect(self.repaint)
        self.movie.start()
        
        self.setWindowOpacity(opacity)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        
        self.message = ""
        self._draw_texts = []
    
    def setStatus(self, text, author):
        """Обновляет текст состояния загрузки"""
        self.clearTexts()
        self.drawText(author, (20, 30), size=10, font="UNCAGE")
        self.drawText(text, (20, self.height() - 20))
        self.repaint()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, False)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.transparent)
        
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        
        pixmap = self.movie.currentPixmap()
        if not pixmap.isNull():
            painter.drawPixmap(self.rect(), pixmap)
        
        painter.setOpacity(1.0)
        for text, pos, color, size, font_name in self._draw_texts:
            painter.setPen(color or self.text_color)
            f = QFont(font_name) if font_name else self.text_font
            if size: f.setPointSize(size)
            painter.setFont(f)
            
            if isinstance(pos, QPoint):
                painter.drawText(pos, text)
            else:
                painter.drawText(pos[0], pos[1], text)
        
        painter.end()
    
    def setMessage(self, message, alignment=None, color=None):
        """Установка сообщения для отображения поверх анимации"""
        self.message = message
        if alignment:
            self.text_alignment = alignment
        if color:
            self.text_color = color
        self.repaint()
    
    def drawText(self, text, position, color=None, size=None, font=None):
        self._draw_texts.append((text, position, color, size, font))
    
    def clearTexts(self):
        self._draw_texts.clear()
    
    def setOpacity(self, opacity):
        """Установка уровня прозрачности (0.0 - полностью прозрачный, 1.0 - полностью непрозрачный)"""
        self.setWindowOpacity(opacity)
    
    def finish(self, main_window):
        self.movie.stop()
        super().finish(main_window)
