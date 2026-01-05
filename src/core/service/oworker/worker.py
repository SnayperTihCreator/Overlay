import time

from PySide6.QtCore import QObject, Signal, Slot


class BackgroundWorker(QObject):
    """
    Класс для фоновой работы, который можно запускать и останавливать.
    Не блокирует основное приложение.
    """

    # Сигнал для отправки данных в основное приложение
    body_returned = Signal(object)
    # Сигнал для уведомления о завершении работы
    finished = Signal()

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._pause_event = False

    @Slot()
    def start(self):
        """Запускает фоновую работу"""
        self._is_running = True
        self._pause_event = False
        self.run()

    @Slot()
    def stop(self):
        """Останавливает фоновую работу"""
        self._is_running = False

    @Slot()
    def pause(self):
        """Приостанавливает фоновую работу"""
        self._pause_event = True

    @Slot()
    def resume(self):
        """Возобновляет фоновую работу после паузы"""
        self._pause_event = False

    def run(self):
        """Основной рабочий цикл"""
        while self._is_running:
            if self._pause_event:
                time.sleep(0.1)  # Небольшая задержка при паузе
                continue

            # Здесь выполняется полезная работа
            result = self.do_work()

            # Отправляем результат в основное приложение
            self.body_returned.emit(result)

            # Небольшая задержка для имитации работы
            time.sleep(0.5)

        # Уведомляем о завершении работы
        self.finished.emit()

    def do_work(self):
        """
        Переопределите этот метод для выполнения полезной работы.
        Возвращаемое значение будет отправлено через сигнал data_ready.
        """
        return f"Background work at {time.strftime('%H:%M:%S')}"
