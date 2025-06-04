from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QColor, QPainter, QPen, QPolygon, QBrush, QLinearGradient


class BatteryWidget(QWidget):
    def __init__(self, level=65, is_charging=False, parent=None):
        super().__init__(parent)
        self.level = level
        self.is_charging = is_charging
        self.animation_phase = 0  # Для анимации мигания
        self.setFixedSize(100, 40)

        # Таймер для анимации зарядки
        self.animation_timer = QTimer(self)
        self.animation_timer.timeout.connect(self.update_animation)
        if self.is_charging:
            self.animation_timer.start(500)  # Обновление каждые 500 мс

    def set_level(self, level):
        self.level = max(0, min(100, level))
        self.update()

    def set_charging(self, is_charging):
        if self.is_charging != is_charging:
            self.is_charging = is_charging
            if is_charging:
                self.animation_timer.start(200)
            else:
                self.animation_timer.stop()
                self.animation_phase = 0
            self.update()

    def update_animation(self):
        self.animation_phase = (self.animation_phase + 1) % 4
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Кабель зарядки (если подключен)
        if self.is_charging:
            # Кабель
            cable_gradient = QLinearGradient(
                0, self.height() // 2, 20, self.height() // 2
            )
            cable_gradient.setColorAt(0, QColor(100, 100, 100))
            cable_gradient.setColorAt(1, QColor(180, 180, 180))
            painter.setPen(QPen(QBrush(cable_gradient), 3))
            painter.drawLine(0, self.height() // 2, 15, self.height() // 2)

            # Вилка (стилизованная)
            plug_color = QColor(80, 80, 80)
            painter.setBrush(QBrush(plug_color))
            painter.setPen(QPen(plug_color.darker(), 1))
            plug_points = QPolygon(
                [
                    QPoint(10, self.height() // 2 - 8),
                    QPoint(2, self.height() // 2),
                    QPoint(10, self.height() // 2 + 8),
                ]
            )
            painter.drawPolygon(plug_points)

        # Корпус батарейки (с тенью и градиентом)
        body_rect = self.rect().adjusted(20, 5, -20, -5)
        body_gradient = QLinearGradient(body_rect.topLeft(), body_rect.topRight())
        body_gradient.setColorAt(0, QColor(220, 220, 220))
        body_gradient.setColorAt(1, QColor(250, 250, 250))
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.setBrush(QBrush(body_gradient))
        painter.drawRoundedRect(body_rect, 7, 7)

        # Контакт (металлический эффект)
        contact_rect = self.rect().adjusted(self.width() - 20, 10, -5, -10)
        contact_gradient = QLinearGradient(
            contact_rect.topLeft(), contact_rect.bottomLeft()
        )
        contact_gradient.setColorAt(0, QColor(180, 180, 180))
        contact_gradient.setColorAt(1, QColor(220, 220, 220))
        painter.setPen(QPen(QColor(100, 100, 100), 1))
        painter.setBrush(QBrush(contact_gradient))
        painter.drawRect(contact_rect)

        # Заливка уровня заряда
        if self.level > 0:
            fill_width = max(5, int((body_rect.width() - 6) * self.level / 100))
            fill_rect = body_rect.adjusted(
                3, 3, -(body_rect.width() - fill_width - 3), -3
            )

            # Градиент заливки
            fill_gradient = QLinearGradient(fill_rect.topLeft(), fill_rect.topRight())
            if self.is_charging:
                # Анимированный градиент при зарядке
                if self.animation_phase == 0:
                    fill_gradient.setColorAt(0, QColor(70, 170, 255))
                    fill_gradient.setColorAt(1, QColor(120, 210, 255))
                else:
                    fill_gradient.setColorAt(0, QColor(100, 190, 255))
                    fill_gradient.setColorAt(1, QColor(150, 230, 255))
            elif self.level < 15:
                fill_gradient.setColorAt(0, QColor(255, 70, 70))
                fill_gradient.setColorAt(1, QColor(255, 120, 120))
            elif self.level < 40:
                fill_gradient.setColorAt(0, QColor(255, 180, 50))
                fill_gradient.setColorAt(1, QColor(255, 220, 80))
            else:
                fill_gradient.setColorAt(0, QColor(70, 220, 70))
                fill_gradient.setColorAt(1, QColor(120, 255, 120))

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(fill_gradient))
            painter.drawRoundedRect(fill_rect, 5, 5)
