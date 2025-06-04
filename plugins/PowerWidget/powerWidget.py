from PySide6.QtWidgets import QHBoxLayout, QWidget, QLabel
from PySide6.QtCore import Qt

import psutil

from API import Config, DraggableWindow

from .BatteryWidget import BatteryWidget


class PowerWidget(DraggableWindow):

    def __init__(self, parent=None):
        super().__init__(Config(__file__, "draggable_window"), parent)

        self.box = QHBoxLayout(self.central_widget)

        self.battery = BatteryWidget()
        self.powerLevelLabel = QLabel()
        self.powerLevelLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.powerLeftLabel = QLabel()
        self.powerLeftLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.box.addWidget(self.battery)
        self.box.addWidget(self.powerLevelLabel)
        self.box.addWidget(self.powerLeftLabel)

        self._lastPercent = ""
        self._lastLeftTime = ""

        self.updateData()
        self.timerID = self.startTimer(1000)

    def timerEvent(self, event, /):
        if event.id().value == self.timerID:
            self.updateData()

    def updateData(self):
        battery = psutil.sensors_battery()
        if battery is None:
            return

        percent = battery.percent
        if (percent != self._lastPercent) or self.reloading:
            self._lastPercent = percent
            self.powerLevelLabel.setText(
                self.config.powerFormat.unitFormat.replace("%u", str(percent))
            )
            self.battery.set_level(percent)
        timeLeft = (
            battery.secsleft
            if battery.secsleft != psutil.POWER_TIME_UNLIMITED
            else "Заряжается"
        )
        if (timeLeft != self._lastLeftTime) or self.reloading:
            self._lastLeftTime = timeLeft
            self.battery.set_charging(isinstance(timeLeft, str))
            if (not isinstance(timeLeft, str)) and (timeLeft // 3600) > 100_000:
                timeLeft = "Рассчитывается"
            self.powerLeftLabel.setText(
                f"{timeLeft if isinstance(timeLeft, str) else f'{timeLeft // 3600} ч {(timeLeft % 3600) // 60} мин'}"
            )

        super().updateData()
