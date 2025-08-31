import copy

from PySide6.QtCore import Qt
from PySide6.QtGui import QMovie, QColor, QPainter, QPixmap, QFont
from PySide6.QtWidgets import QSplashScreen, QApplication


class GifSplashScreen(QSplashScreen):
    def __init__(self, path, opacity=1.0):
        # Создаем QMovie для загрузки и управления GIF-анимацией
        self.image = QPixmap(":/root/icons/loader.png")
        super().__init__(self.image)
        self.movie = QMovie(path)
        
        self.movie.frameChanged.connect(lambda x: self.repaint())
        self.movie.start()
        
        self.setWindowOpacity(opacity)
        
        # Настройки для текста
        self.message = ""
        self.text_alignment = Qt.AlignBottom | Qt.AlignCenter
        self.text_color = QColor("#fff")  # Белый цвет по умолчанию
        self.text_font = QApplication.font()
        
        # Устанавливаем флаги окна для прозрачности
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self._draw_texts = []
    
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
    
    def paintEvent(self, event):
        # Создаем объект QPainter для рисования
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Получаем текущий кадр анимации
        pixmap = self.movie.currentPixmap().scaled(self.image.size())
        
        # Рисуем текущий кадр с учетом прозрачности
        painter.setOpacity(self.windowOpacity())
        painter.drawPixmap(0, 0, pixmap)
        
        # Рисуем текст поверх анимации
        if self.message:
            painter.setOpacity(1.0)  # Полная непрозрачность для текста
            painter.setFont(self.text_font)
            painter.setPen(self.text_color)
            
            # Получаем размеры области для текста
            text_rect = self.rect()
            text_rect.setHeight(text_rect.height() - 10)  # Отступ от нижнего края
            
            # Рисуем текст с выравниванием
            painter.drawText(text_rect, self.text_alignment, self.message)
        
        if self._draw_texts:
            for text, pos, color, size, fontName in self._draw_texts:
                if color is None: color = self.text_color
                if size is None: size = self.text_font.pointSize()
                font = copy.copy(self.text_font) if fontName is None else QFont(fontName)
                font.setPointSize(size)
                painter.setFont(font)
                painter.setPen(color)
                painter.drawText(*pos, text)
                
        painter.end()
        
    def clearTexts(self):
        self._draw_texts.clear()
    
    def setOpacity(self, opacity):
        """Установка уровня прозрачности (0.0 - полностью прозрачный, 1.0 - полностью непрозрачный)"""
        self.setWindowOpacity(opacity)
    
    def finish(self, main_window):
        # Останавливаем анимацию при завершении
        self.movie.stop()
        return super().finish(main_window)