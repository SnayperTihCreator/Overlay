from PySide6.QtWidgets import QApplication, QWidget
from abc import ABC, ABCMeta


class Meta(type(QWidget), ABCMeta): ...


class Widget(QWidget, ABC, metaclass=Meta): ...
