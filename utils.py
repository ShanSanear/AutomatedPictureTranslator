from __future__ import annotations

from typing import NamedTuple

from PyQt5.QtCore import QRunnable, pyqtSlot, QObject, pyqtSignal


class Singleton(type(QObject), type):
    def __init__(cls, name, bases, dict):
        super().__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self) -> None:
        self.fn(*self.args, **self.kwargs)


class Communicate(QObject, metaclass=Singleton):
    translate_signal = pyqtSignal()
    update_tesseract_psm = pyqtSignal(str)
    update_tesseract_language = pyqtSignal(str)


class MenuSignals(QObject, metaclass=Singleton):
    tesseract_config_signal = pyqtSignal()


class ScreenshotSize(NamedTuple):
    width: int
    height: int


class ScreenPoint(NamedTuple):
    x: int
    y: int

    def __sub__(self, other: ScreenPoint) -> ScreenshotSize:
        if not isinstance(other, ScreenPoint):
            raise ValueError("Incorrect other type: {}", other.__class__)
        return ScreenshotSize(
            width=self.x - other.x,
            height=self.y - other.y
        )
