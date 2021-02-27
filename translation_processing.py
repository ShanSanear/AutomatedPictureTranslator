import re
from typing import List

from googletrans import Translator
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine("sqlite:///translation.db", echo=False)
session = sessionmaker(bind=engine)()

ERROR_TRANSLATING = "error"

translator = Translator()
punctuation_regex = re.compile("[.,!:;]")


def translate_text(text_to_translate: str, source_language: str, target_language: str) -> str:
    # TODO use Google Translate API for this one
    print(f"Translating {text_to_translate} from {source_language} to {target_language}")
    translated_text = translate_or_get_from_cache(text_to_translate, source_language, target_language)
    return translated_text


def get_single_words_to_translate(sentence: str) -> List[str]:
    return [punctuation_regex.sub("", word) for word in sentence.split(' ')]


def translate_all_words(words_to_translate: List[str], source_language: str, target_language: str) -> List[str]:
    translations = []
    for word in words_to_translate:
        text = translate_or_get_from_cache(punctuation_regex.sub("", word), source_language=source_language,
                                           target_language=target_language)
        translations.append(text)
    return translations


class Translations(Base):
    __tablename__ = 'translations'
    translation_id = Column(Integer, primary_key=True)
    source_language = Column(String, nullable=False)
    target_language = Column(String, nullable=False)
    text_to_translate = Column(String, nullable=False)
    translation = Column(String, nullable=False)


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
            return cache_translation(text_to_translate, source_language, target_language, ERROR_TRANSLATING)
    return entry.translation
