# Points to do:
# Translate only the more obscure words (how can you "measure" obscurity of word?)
# Uses some kind of GUI for this

from __future__ import annotations

import cv2
import numpy as np

import re
import time

import pyautogui

from typing import NamedTuple, List

import pytesseract
from PIL import Image

from googletrans import Translator

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# TODO to be removed after adding Tesseract to PATH
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

translator = Translator()
engine = create_engine("sqlite:///translation.db", echo=False)
session = sessionmaker(bind=engine)()
punctuation_regex = re.compile("[.,!:;]")


# TODO In general - move everything to class and modulize what is needed

def pil_to_cv2(image):
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)


def white_to_black_only(image):
    arr = pil_to_cv2(image)
    return Image.fromarray(np.where(arr == 255, 0, 255).astype('uint8'))

class Translations(Base):
    __tablename__ = 'translations'
    translation_id = Column(Integer, primary_key=True)
    source_language = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    text_to_translate = Column(String, nullable=False)
    translation = Column(String, nullable=False)


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


def cache_translation(text_to_translate, source_language, target_language, translation):
    translation = Translations(source_language=source_language, target_language=target_language,
                               text_to_translate=text_to_translate, translation=translation)
    session.add(translation)
    session.commit()


def translate_or_get_from_cache(text_to_translate, source_language, target_language):
    entry: Translations = session.query(Translations).filter(
        Translations.source_language.is_(source_language),
        Translations.text_to_translate.is_(text_to_translate),
        Translations.target_language.is_(target_language)
    ).first()
    if not entry:
        try:
            translator_response = translator.translate(text_to_translate, src=source_language, dest=target_language)
            cache_translation(text_to_translate, source_language, target_language, translator_response.text)
            return translator_response.text
        except TypeError as err:
            print(f"Error processing text: {text_to_translate}")
            print(f"Error: {err}")
            return ""
    return entry.translation


def get_corners_of_region_to_translate():
    # TODO select screenshot points somehow (UI?)
    return ScreenPoint(x=743, y=890), ScreenPoint(x=1603, y=1139)


def capture_picture(top_left_corner: ScreenPoint, bottom_right_corner: ScreenPoint) -> Image:
    size = bottom_right_corner - top_left_corner
    print(f"Capturing picture from {top_left_corner} of size {size}")
    time.sleep(2)
    return pyautogui.screenshot(region=(*top_left_corner, *size))


def process_picture_ocr(picture: Image) -> str:
    custom_config = r'-l eng --psm 6'
    print(f"Picture to OCR: {picture}")
    raw_text = pytesseract.image_to_string(picture, config=custom_config)
    return raw_text.strip().replace('\n', ' ')


def translate_text(text_to_translate: str, source_language: str, target_language: str) -> str:
    # TODO use Google Translate API for this one
    print(f"Translating {text_to_translate} from {source_language} to {target_language}")
    translated_text = translate_or_get_from_cache(text_to_translate, source_language, target_language)
    return translated_text


def translate_all_words(text_to_translate: str, source_language: str, target_language: str) -> List[str]:
    words = text_to_translate.split(' ')
    translations = []
    for word in words:
        text = translate_or_get_from_cache(punctuation_regex.sub("", word), source_language=source_language,
                                           target_language=target_language)
        translations.append(text)
    return translations


def display_translation(translated_text: str) -> None:
    # TODO this may be used by some window to be periodically updated
    print(f"Translation: {translated_text}")


def main() -> None:
    top_left, bottom_right = get_corners_of_region_to_translate()
    Base.metadata.create_all(engine)
    session.commit()
    while True:
        time.sleep(2)
        picture = capture_picture(top_left, bottom_right)
        text_to_translate = process_picture_ocr(white_to_black_only(picture))
        if not text_to_translate:
            text_to_translate = process_picture_ocr(picture)
        if not text_to_translate:
            continue
        translated_text = translate_text(text_to_translate, 'en', 'pl')
        print(translate_all_words(text_to_translate, 'en', 'pl'))
        display_translation(translated_text)


if __name__ == '__main__':
    main()
