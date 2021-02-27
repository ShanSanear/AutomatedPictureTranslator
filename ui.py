from __future__ import annotations

import sys
import time
from functools import partial
from typing import NamedTuple, List

import pyautogui
from PyQt5.QtCore import QRunnable, pyqtSlot, QThreadPool, QRect, QTimer, QAbstractTableModel, Qt
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QTableView

from picture_processing import process_picture_ocr, white_to_black_only
from translation_processing import translate_text, get_single_words_to_translate, translate_all_words


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


class Worker(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    @pyqtSlot()
    def run(self) -> None:
        self.fn(*self.args, **self.kwargs)


class TableModel(QAbstractTableModel):
    def __init__(self):
        super(TableModel, self).__init__()
        self._data = []
        self._header_labels = ["en", "pl"]

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        try:
            return len(self._data[0])
        except IndexError:
            return 0

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._header_labels[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def set_data(self, data: List[List[str]]):
        self._data = data
        self.layoutChanged.emit()


class SingleWordTranslations(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Single word translations")
        self.table = QTableView()
        self.table.verticalHeader().setDefaultSectionSize(50)
        self.table.horizontalHeader().setDefaultSectionSize(150)
        self.model = TableModel()
        self.table.setModel(self.model)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.table)


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main translations")
        self.thread_pool = QThreadPool()
        self.resize(300, 300)
        self.show_single_translations = QPushButton("CLICK FOR SINGLE")
        self.show_single_translations.clicked.connect(self.show_single_word_translations)
        self.toggle_translation_button = QPushButton("TURN ON TRANSLATION")
        self.toggle_translation_button.clicked.connect(self.toggle_translation)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label_field = QLabel("This will be translated text")
        self.set_top_left = QPushButton("TOP LEFT")
        self.set_bottom_right = QPushButton("BOTTOM RIGHT")
        self.top_left = ScreenPoint(0, 0)
        self.bottom_right = ScreenPoint(0, 0)
        self.set_top_left.clicked.connect(partial(self.get_mouse_position, 'top_left'))
        self.set_bottom_right.clicked.connect(partial(self.get_mouse_position, 'bottom_right'))
        self.current_screenshot = QPixmap()
        self.timer = QTimer()
        self.timer.timeout.connect(self._translation)
        self.label_field.setWordWrap(True)
        self.single_word_translation = SingleWordTranslations()
        self.single_word_translation.resize(400, 400)
        layout.addWidget(self.label_field)
        layout.addWidget(self.set_top_left)
        layout.addWidget(self.set_bottom_right)
        layout.addWidget(self.show_single_translations)
        layout.addWidget(self.toggle_translation_button)

    def toggle_translation(self):
        if self.timer.isActive():
            self.timer.stop()
            self.toggle_translation_button.setText("TURN ON TRANSLATION")
        else:
            self.timer.start(3000)
            self.toggle_translation_button.setText("TURN OFF TRANSLATION")

    def show_single_word_translations(self):
        self.single_word_translation.show()

    def get_mouse_position(self, variable_name_to_set):
        worker = Worker(self._get_mouse_position, 2, variable_name_to_set)
        self.thread_pool.start(worker)

    @property
    def rectangle_to_translate(self):
        return QRect(self.top_left, self.bottom_right)

    def capture_picture(self):
        size = self.bottom_right - self.top_left
        return pyautogui.screenshot(region=(*self.top_left, *size))

    def _get_mouse_position(self, timeout, variable_to_set):
        for i in range(timeout):
            time.sleep(1)
            print(i)
        print("getting position")
        p = QCursor.pos()
        setattr(self, variable_to_set, ScreenPoint(x=p.x(), y=p.y()))
        print(f"{self.bottom_right = }")
        print(f"{self.top_left = }")

    def do_translation(self):
        if self.top_left == (0, 0) or self.bottom_right == (0, 0):
            return
        pic = self.capture_picture()
        text_to_translate = process_picture_ocr(white_to_black_only(pic))
        if not text_to_translate:
            text_to_translate = process_picture_ocr(pic)
        if not text_to_translate:
            self.label_field.setText("Error processing translation")
            return
        translated_text = translate_text(text_to_translate, 'en', 'pl')
        self.label_field.setText(translated_text)
        single_words = get_single_words_to_translate(text_to_translate)
        translated_single_words = translate_all_words(single_words, 'en', 'pl')
        self.single_word_translation.model.set_data(list([org, trans] for org, trans in zip(
            single_words, translated_single_words
        )))

    def _translation(self):
        worker = Worker(self.do_translation)
        self.thread_pool.start(worker)


app = QApplication(sys.argv)

app.setStyleSheet("""
QLabel {
font-size: 25px;
font-style: bold;
border: 2px solid red;
}
QTableView {
font-size: 40px;
font-style: bold;
}
""")
window = MyApp()
window.show()
app.exec()
