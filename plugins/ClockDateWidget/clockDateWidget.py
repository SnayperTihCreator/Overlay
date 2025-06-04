from datetime import datetime

from PySide6.QtWidgets import QGridLayout, QLabel
from PySide6.QtCore import Qt

from API import Config, DraggableWindow


class ClockDateWidget(DraggableWindow):

    _weekname = [
        "Понедельник",
        "Вторник",
        "Среда",
        "Четверг",
        "Пятница",
        "Суббота",
        "Воскресенье",
    ]

    def __init__(self, parent=None):
        super().__init__(Config(__file__, "draggable_window"), parent)

        self.grid = QGridLayout(self.central_widget)

        self.timeLabel = QLabel("0:0:0")
        self.timeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.weekNameLabel = QLabel("Понедельник")
        self.weekNameLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dateLabel = QLabel("01/01/2025")
        self.dateLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.grid.addWidget(self.timeLabel, 0, 0, 1, 2)
        self.grid.addWidget(self.weekNameLabel, 1, 0)
        self.grid.addWidget(self.dateLabel, 1, 1)

        self._lastWeekName = ""
        self._lastDate = ""

        self.updateData()

        self.timerID = self.startTimer(500)

    def timerEvent(self, event, /):
        if event.id().value == self.timerID:
            self.updateData()

    def updateData(self):
        self.timeLabel.setText(self._getCurrentTime())

        date = self._getCurrentDate()
        if self._lastDate != date:
            self._lastDate = date
            self.dateLabel.setText(date)
        weekname = self._getCurrentWeekName()
        if self._lastWeekName != weekname:
            self._lastWeekName = weekname
            self.weekNameLabel.setText(weekname)

        super().updateData()

    def _getCurrentDate(self):
        return datetime.now().strftime(self.config.clockFormat.dateFormat)

    @classmethod
    def _getCurrentWeekName(cls):
        return cls._weekname[datetime.now().weekday()]

    def _getCurrentTime(self):
        return datetime.now().strftime(self.config.clockFormat.timeFormat)
