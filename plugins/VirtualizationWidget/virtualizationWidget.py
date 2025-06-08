import sys
from collections import deque

from PySide6.QtGui import QLinearGradient, QBrush
from PySide6.QtWidgets import QVBoxLayout, QWidget, QComboBox, QPushButton, QFormLayout
from PySide6.QtCore import Qt, QTimer
from box import Box

from API import Config, DraggableWindow
from API.PluginSetting import PluginSettingWindow

import pyqtgraph as pg
import numpy as np
import pyaudio

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024  # Больше точек → лучше разрешение по частоте
SMOOTHING_WINDOW = 5  # Размер окна для скользящего среднего
SMOOTHING = 3

# Пороговые значения для определения наличия звука
SILENCE_THRESHOLD = 50  # Эмпирическое значение, можно настроить
SILENCE_DURATION = 15  # Количество кадров тишины перед выводом сообщения


class CustomPluginWindow(PluginSettingWindow):
    
    def __init__(self, obj, name_plugin, parent=None):
        super().__init__(obj, name_plugin, parent)
        self.p_audio = pyaudio.PyAudio()
        self.comboListDevice = QComboBox()
        self.listDevice = set()
        self.updateLoaderDevice()
        self.formLayout.addRow("Устройство", self.comboListDevice)
        
        self.btnUpdateDevice = QPushButton("Обновить устройства")
        self.btnUpdateDevice.pressed.connect(self.updateLoaderDevice)
        self.formLayout.addRow(self.btnUpdateDevice)
        # self.formLayout.setWidget(-1, QFormLayout.ItemRole.SpanningRole, self.btnUpdateDevice)
        
    def loader(self):
        super().loader()
        idx = self.comboListDevice.findData({"idx": self.obj.idx_device or 0}, Qt.ItemDataRole.UserRole, Qt.MatchFlag.MatchContains)
        self.comboListDevice.setCurrentIndex(idx)
    
    def updateLoaderDevice(self):
        self.comboListDevice.clear()
        self.listDevice.clear()
        for idx in range(self.p_audio.get_device_count()):
            info = self.p_audio.get_device_info_by_index(idx)
            if info["maxInputChannels"]<=0: continue
            name = info["name"].encode("cp1251").decode("utf-8")
            if name in self.listDevice: continue
            self.comboListDevice.addItem(name, {"idx":idx})
            self.listDevice.add(name)
            
    def send_data(self):
        data = super().send_data()
        idx = self.comboListDevice.currentIndex()
        uData = self.comboListDevice.itemData(idx, Qt.ItemDataRole.UserRole)
        return data|{"idx_device": uData["idx"]}


class Virtualization(DraggableWindow):
    def __init__(self, parent=None):
        super().__init__(Config(__file__, "draggable_window"), parent)
        
        self.idx_device = None
        self.stream = None
        
        # Инициализация PyAudio
        self.p = pyaudio.PyAudio()
        self.updateStream()
        
        pg.setConfigOptions(antialias=True, useNumba=True)
        
        # Настройка графика
        self.plot_widget = pg.PlotWidget()
        
        self.plot_widget.setMouseEnabled(x=False, y=False)  # Запрет перемещения по осям
        self.plot_widget.setMenuEnabled(False)  # Отключение контекстного меню
        self.plot_widget.setAspectLocked(False)  # Разрешить свободное соотношение сторон
        self.plot_widget.enableAutoRange(axis='xy')  # Автоподбор под размер виджета
        self.plot_widget.hideAxis("left")
        self.plot_widget.hideAxis("bottom")
        self.plot_widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
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
        
        self.updateData()
        
        # Таймер для обновления графика
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateData)
        self.timer.start(30)  # Обновление ~30 FPS
    
    def updateData(self):
        # Чтение аудиоданных
        if self.stream is None: return
        
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
        gradient.setCoordinateMode(QLinearGradient.CoordinateMode.ObjectMode)
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
        super().updateData()
    
    def closeEvent(self, event):
        # Очистка ресурсов
        self.timer.stop()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        event.accept()
    
    @classmethod
    def createSettingWidget(cls, window: "DraggableWindow", name_plugin: str, parent):
        return CustomPluginWindow(window, name_plugin, parent)
    
    def restoreConfig(self, config):
        super().restoreConfig(config)
        if isinstance(config.idx_device, Box) or config.idx_device <= 0: return
        self.idx_device = config.idx_device
        self.updateStream()
        
    def savesConfig(self):
        data = super().savesConfig()
        return data|{
            "idx_device": self.idx_device
        }
        
        
    def updateStream(self):
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        self.stream = self.p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
            input_device_index=self.idx_device,  # Подбери нужное устройство!
        )
        
        