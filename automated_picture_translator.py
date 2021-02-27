# Points to do:
# Translate only the more obscure words (how can you "measure" obscurity of word?)
# Uses some kind of GUI for this

from __future__ import annotations

import time

import pyautogui

from typing import NamedTuple

import pytesseract
from PIL import Image

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from picture_processing import process_picture_ocr, white_to_black_only
from translation_processing import translate_text, translate_all_words, get_single_words_to_translate

Base = declarative_base()
# TODO to be removed after adding Tesseract to PATH
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

engine = create_engine("sqlite:///translation.db", echo=False)
session = sessionmaker(bind=engine)()


# TODO In general - move everything to class and modulize what is needed


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


def get_corners_of_region_to_translate():
    # TODO select screenshot points somehow (UI?)
    # return ScreenPoint(x=743, y=890), ScreenPoint(x=1603, y=1139)
    # return ScreenPoint(x=987,y=408), ScreenPoint(x=2128,y=639)
    #return ScreenPoint(x=693, y=981), ScreenPoint(x=1631,y=1197)
    return ScreenPoint(x=513,y=1016), ScreenPoint(x=1814,y=1293)


def capture_picture(top_left_corner: ScreenPoint, bottom_right_corner: ScreenPoint) -> Image:
    size = bottom_right_corner - top_left_corner
    print(f"Capturing picture from {top_left_corner} of size {size}")
    time.sleep(2)
    return pyautogui.screenshot(region=(*top_left_corner, *size))


def display_translation(translated_text: str) -> None:
    # TODO this may be used by some window to be periodically updated
    print(f"Translation: {translated_text}")


def main() -> None:
    top_left, bottom_right = get_corners_of_region_to_translate()
    Base.metadata.create_all(engine)
    session.commit()
    time_between_checks = 5
    while True:
        time.sleep(time_between_checks)
        picture = capture_picture(top_left, bottom_right)
        text_to_translate = process_picture_ocr(white_to_black_only(picture))
        if not text_to_translate:
            text_to_translate = process_picture_ocr(picture)
        if not text_to_translate:
            continue
        translated_text = translate_text(text_to_translate, 'en', 'pl')
        words = get_single_words_to_translate(text_to_translate)
        print(translate_all_words(words, 'en', 'pl'))
        display_translation(translated_text)


if __name__ == '__main__':
    main()
