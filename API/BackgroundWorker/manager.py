from PySide6.QtCore import QThread, QObject, Signal

from .worker import BackgroundWorker
from ..config import Config


class BackgroundWorkerManager(QObject):
    """
    Класс для управления фоновым работником.
    Создает и управляет отдельным потоком для worker'а.
    """

    body_returned = Signal(object)

    def __init__(self, config, worker_class=BackgroundWorker):
        super().__init__()
        self.config: Config = config
        self.worker = worker_class()
        self.thread = QThread()

        # Перемещаем worker в отдельный поток
        self.worker.moveToThread(self.thread)

        # Подключаем сигналы
        self.thread.started.connect(self.worker.start)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.body_returned.connect(self.body_returned.emit)

    def start(self):
        """Запускает фоновый worker"""
        if not self.thread.isRunning():
            self.thread.start()

    def stop(self):
        """Останавливает фоновый worker"""
        if self.thread.isRunning():
            self.worker.stop()  # Запрашиваем остановку
            self.thread.quit()  # Запрашиваем выход из цикла событий
            self.thread.wait()  # Ждем завершения потока

    def pause(self):
        """Приостанавливает работу"""
        if self.thread.isRunning():
            self.worker.pause()

    def resume(self):
        """Возобновляет работу после паузы"""
        if self.thread.isRunning():
            self.worker.resume()

    def is_running(self):
        """Проверяет, работает ли worker"""
        return self.thread.isRunning()

    def reloadConfig(self):
        self.config.reload()

    def savesConfig(self):
        return {}

    def restoreConfig(self, config):
        pass
