import logging
import sys
import traceback
from datetime import datetime
import io

from contextvars import ContextVar

from PySide6.QtCore import (
    QtMsgType,
    qInstallMessageHandler,
    qCritical,
    QMessageLogContext,
)


def setup_exception_handler():
    def exception_handler(exc_type, exc_value, exc_traceback):
        # Игнорируем KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Формируем traceback
        error_trace = "".join(
            traceback.format_exception(exc_type, exc_value, exc_traceback)
        )

        # Записываем в файл
        qCritical(
            f"Unhandled exception:\n{error_trace}",
        )

        # Выводим в stderr
        sys.stderr.write(f"[!] Произошла ошибка (подробности в {handler.baseFilename}\n")

    sys.excepthook = exception_handler


logging.basicConfig(level=logging.CRITICAL, stream=io.StringIO())
logger = logging.getLogger("Qt")
logger.setLevel(logging.DEBUG)

date = datetime.now().strftime("%Y_%m_%d")
handler = logging.FileHandler(f"./configs/log{date}.log", "w", "utf-8")
handler.setLevel(logging.DEBUG)
logger.addHandler(handler)

formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s: %(lineno)d]",
    "%Y-%m-%d %H:%M:%S",
)
handler.setFormatter(formatter)


def qt_message_handler(mode: QtMsgType, context: QMessageLogContext, message):
    # frame = inspect.currentframe().f_back
    # func = frame.f_code.co_name
    # extra={"filename": frame.f_code.co_filename, "lineno": frame.f_lineno}
    if mode == QtMsgType.QtDebugMsg:
        logger.debug(message, stacklevel=2)
    elif mode == QtMsgType.QtInfoMsg:
        logger.info(message, stacklevel=2)
    elif mode == QtMsgType.QtWarningMsg:
        logger.warning(message, stacklevel=2)
    elif mode == QtMsgType.QtCriticalMsg:
        logger.error(message, stacklevel=2)
    elif mode == QtMsgType.QtFatalMsg:
        logger.critical(message, stacklevel=2)
    else:
        logger.debug(message, stacklevel=2)


# Установка обработчика Qt-сообщений
qInstallMessageHandler(qt_message_handler)
setup_exception_handler()
