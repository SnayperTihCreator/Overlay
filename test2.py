import sys
from collections import deque

from tools_folder import ToolsIniter

ToolsIniter("tools").load()

from PySide6.QtGui import QLinearGradient, QBrush
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtCore import Qt

import pyqtgraph as pg
import numpy as np
import pyaudio

# Настройки аудио
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024  # Больше точек → лучше разрешение по частоте
SMOOTHING_WINDOW = 5  # Размер окна для скользящего среднего
SMOOTHING = 3

# Пороговые значения для определения наличия звука
SILENCE_THRESHOLD = 50  # Эмпирическое значение, можно настроить
SILENCE_DURATION = 15  # Количество кадров тишины перед выводом сообщения


audio = pyaudio.PyAudio()

for idx in range(audio.get_device_count()):
    info = audio.get_device_info_by_index(idx)
    print(idx, ":", info["name"].encode("cp1251").decode("utf8"), info["maxInputChannels"])
    print(info)


class AudioVisualizer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Анализатор спектра (0-1000)")
        self.setGeometry(100, 100, 800, 600)

        # Инициализация PyAudio
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=None,  # Подбери нужное устройство!
        )

        pg.setConfigOptions(useOpenGL=True, antialias=True, useNumba=True)

        # Настройка графика
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.hideAxis("left")
        self.plot_widget.hideAxis("bottom")
        self.plot_widget.setBackground(None)
        self.plot_widget.hideButtons()
        
        self.plot_widget.setXRange(
            0, RATE // 4
        )  # Ограничиваем диапазон частот (0-1000 Гц)
        self.plot_widget.setYRange(-1000, 1000)  # Амплитуда нормирована на 0-1000

        self.color_map = pg.ColorMap(
            [0.0, 0.5, 1.0],
            [
                pg.mkColor(0, 0, 255),  # Синий
                pg.mkColor(0, 255, 0),  # Зеленый
                pg.mkColor(255, 0, 0),  # Красный
            ],
        )

        # Линия для FFT
        self.fft_curve1 = self.plot_widget.plot(
            pen=None, fillLevel=0, brush=(255, 255, 255, 50)
        )
        self.fft_curve2 = self.plot_widget.plot(
            pen=None, fillLevel=0, brush=(255, 255, 255, 50)
        )

        # Данные для сглаживания
        self.smoothing_buffer = deque(maxlen=SMOOTHING)

        self.silence_counter = 0
        self.is_silent = False

        # Основной layout
        layout = QVBoxLayout()
        layout.addWidget(self.plot_widget)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Таймер для обновления графика
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(30)  # Обновление ~30 FPS

    def update_plot(self):
        # Чтение аудиоданных
        data = self.stream.read(CHUNK, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16)
        freqs = np.fft.fftfreq(CHUNK, 1 / RATE)[: CHUNK // 2]

        # Проверка уровня звука
        max_amplitude = np.max(np.abs(audio))
        is_currently_silent = max_amplitude < SILENCE_THRESHOLD

        if is_currently_silent:
            self.silence_counter += 1
            if self.silence_counter > SILENCE_DURATION:
                self.fft_curve1.setData(freqs, np.zeros(len(freqs)))
                self.fft_curve2.setData(freqs, np.zeros(len(freqs)))
                return
        else:
            self.silence_counter = 0

        # FFT
        fft = np.abs(np.fft.fft(audio)[: CHUNK // 2])

        # Нормализация амплитуды (0-1000)
        if np.max(fft) > 0:
            fft_normalized = (fft / np.max(fft)) * 1000
        else:
            fft_normalized = fft

        # Сглаживание (скользящее среднее)
        self.smoothing_buffer.append(fft_normalized)
        smoothed_fft = (
            np.mean(self.smoothing_buffer, axis=0)
            if self.smoothing_buffer
            else fft_normalized
        )

        colors = self.color_map.map(smoothed_fft / 1000, mode="qcolor")
        gradient = QLinearGradient(0, 0, 1, 0)
        gradient.setCoordinateMode(QLinearGradient.ObjectMode)
        for i, color in enumerate(colors):
            pos = i / len(colors)
            gradient.setColorAt(pos, color)

        # Обновление графика
        self.fft_curve1.setData(
            freqs, smoothed_fft, fillLevel=0, brush=QBrush(gradient)
        )
        self.fft_curve2.setData(
            freqs, -smoothed_fft, fillLevel=0, brush=QBrush(gradient)
        )

    def closeEvent(self, event):
        # Очистка ресурсов
        self.timer.stop()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioVisualizer()
    window.show()
    sys.exit(app.exec())
