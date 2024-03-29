from __future__ import annotations

import sys
import time
from functools import partial
from pathlib import Path

from PyQt5.QtCore import QThreadPool, QRect, QTimer
from PyQt5.QtGui import QCursor, QPixmap, QTextOption
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QMainWindow, \
    QMenuBar, QMenu, QAction

from picture_processing import PictureProcessing
from popups import SettingsPopup, SingleWordTranslations
from translation_processing import translate_text, get_single_words_to_translate, translate_all_words
from utils import Worker, Communicate, ScreenPoint, MenuSignals


class AutomatedPictureTranslator(QWidget):
    # noinspection PyUnresolvedReferences
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

        self.translation = QTextEdit("This will be translated text")
        self.translation.setReadOnly(True)
        self.set_top_left = QPushButton("TOP LEFT")
        self.set_bottom_right = QPushButton("BOTTOM RIGHT")
        self.top_left = ScreenPoint(x=501, y=1012)
        self.bottom_right = ScreenPoint(x=1656, y=1265)
        self.set_top_left.clicked.connect(partial(self.get_mouse_position, 'top_left'))
        self.set_bottom_right.clicked.connect(partial(self.get_mouse_position, 'bottom_right'))
        self.current_screenshot = QPixmap()
        self.translation.setWordWrapMode(QTextOption.WordWrap)
        self.single_word_translation = SingleWordTranslations()
        self.single_word_translation.resize(400, 400)
        layout.addWidget(self.translation)
        layout.addWidget(self.set_top_left)
        layout.addWidget(self.set_bottom_right)
        layout.addWidget(self.show_single_translations)
        layout.addWidget(self.toggle_translation_button)
        self.communicate = Communicate()
        self.communicate.translate_signal.connect(self.do_translation)
        self.translate_timer = QTimer()
        self.translate_timer.timeout.connect(self.communicate.translate_signal.emit)
        self.left_mouse_button_clicked = False
        self.picture_processing = PictureProcessing()

    def toggle_translation(self):
        if self.translate_timer.isActive():
            self.translate_timer.stop()
            self.toggle_translation_button.setText("TURN ON TRANSLATION")
        else:
            self.translate_timer.start(3000)
            self.toggle_translation_button.setText("TURN OFF TRANSLATION")

    def show_single_word_translations(self):
        self.single_word_translation.show()

    def get_mouse_position(self, variable_name_to_set: str):
        worker = Worker(self._get_mouse_position, 2, variable_name_to_set)
        self.thread_pool.start(worker)

    @property
    def rectangle_to_translate(self):
        return QRect(self.top_left, self.bottom_right)

    def _get_mouse_position(self, timeout: int, variable_to_set: str):
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
        size = self.bottom_right - self.top_left
        pic = self.picture_processing.capture_picture(self.top_left, size)
        text_to_translate = self.picture_processing.process_picture_white_to_black(pic)
        if not text_to_translate:
            text_to_translate = self.picture_processing.process_picture_ocr(pic)
        if not text_to_translate:
            self.translation.setPlainText("Error processing translation")
            return
        if len(text_to_translate) > 500:
            self.translation.setPlainText("Text to be translated too long")
            return
        translated_text = translate_text(text_to_translate, 'en', 'pl')
        self.translation.setPlainText(translated_text)
        single_words = get_single_words_to_translate(text_to_translate)
        translated_single_words = translate_all_words(single_words, 'en', 'pl')
        self.single_word_translation.model.set_data(list([org, trans] for org, trans in zip(
            single_words, translated_single_words
        )))


class APT(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setCentralWidget(AutomatedPictureTranslator())
        self.menu_bar = QMenuBar(self)
        file_menu = QMenu("&File", self)
        self.menu_bar.addMenu(file_menu)
        self.settings_menu = QAction("Settings...", self)
        self.menu_signals = MenuSignals()
        self.settings_menu.triggered.connect(self.menu_signals.show_config_signal)
        self.menu_signals.show_config_signal.connect(self.show_settings_popup)
        file_menu.addAction(self.settings_menu)
        self.setMenuBar(self.menu_bar)
        self.communicate = Communicate()
        self.settings_popup = SettingsPopup()

    def show_settings_popup(self):
        self.settings_popup.show()
        print("Showing tesseract options...")
        self.communicate.update_tesseract_psm.emit('6')
        print("Set tesseract config...")


app = QApplication(sys.argv)

app.setStyleSheet(Path('app_style.qss').read_text(encoding='utf-8'))
window = APT()
window.show()
app.exec()
