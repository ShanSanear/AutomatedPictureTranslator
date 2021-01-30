# DUMMY PROJECT
# Create script that:
# 1. Captures continously text from screen (best case - only when it changes or on demand)
# 2. Does OCR
# 3. Runs text and its fragments through google translate
# 3a. Bonus points - translates only the more obscure words
# 4. Uses some kind of GUI for this

from __future__ import annotations

import time

import cv2
import pyautogui

from typing import NamedTuple

import pytesseract

#TODO to be removed after adding Tesseract to PATH
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'


class ScreenshotSize(NamedTuple):
    width: int
    height: int


class ScreenPoint(NamedTuple):
    x: int
    y: int

    def __sub__(self, other: ScreenPoint):
        if not isinstance(other, ScreenPoint):
            raise ValueError("Incorrect other type: {}", other.__class__)
        return ScreenshotSize(
            width=self.x - other.x,
            height=self.y - other.y
        )


#TODO In general - move to class

def get_corners_of_region_to_translate():
    # TODO select screenshot points somehow (UI?)
    return ScreenPoint(x=748, y=914), ScreenPoint(x=1603, y=1139)


def capture_picture(top_left_corner: ScreenPoint, bottom_right_corner: ScreenPoint):
    size = bottom_right_corner - top_left_corner
    print(f"Capturing picture from {top_left_corner} of size {size}")
    time.sleep(2)
    return pyautogui.screenshot(region=(*top_left_corner, *size))


def process_picture_ocr(picture):
    custom_config = r'-l eng --psm 6'
    print(f"Picture to OCR: {picture}")
    raw_text = pytesseract.image_to_string(picture, config=custom_config)
    return ' '.join(raw_text.strip().split('\n'))


def translate_text(text_to_translate, source_language, target_language):
    # TODO use Google Translate API for this one
    print(f"Translating {text_to_translate} from {source_language} to {target_language}")
    translated_text = text_to_translate
    return translated_text


def cache_translation(translated_text):
    # TODO cache translations in SQLLite database to reduce lookup time
    pass


def display_translation(translated_text):
    # TODO this may be used by some window to be periodically updated
    print(f"Translation: {translated_text}")


def main():
    top_left, bottom_right = get_corners_of_region_to_translate()
    picture = capture_picture(top_left, bottom_right)
    text_to_translate = process_picture_ocr(picture)
    translated_text = translate_text(text_to_translate, 'en', 'pl')
    display_translation(translated_text)


if __name__ == '__main__':
    main()
