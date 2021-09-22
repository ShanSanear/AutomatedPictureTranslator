from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import translation_processing
from picture_processing import PictureProcessing
from utils import CapturePosition

app = FastAPI()

picture_processing = PictureProcessing()


class Translation(BaseModel):
    sentence: str
    sentence_words: list[str]
    translated_sentence: str
    translated_words: list[str]


@app.get("/")
async def read_root():
    return {"Hello": "World!"}


@app.get("/translate")
async def translate_screen_part(position: CapturePosition):
    pic = picture_processing.capture_picture(top_left=position.top_left, size=position.size)
    sentence = picture_processing.process_picture_white_to_black(pic)
    if not sentence:
        sentence = picture_processing.process_picture_ocr(pic)
    if not sentence:
        raise HTTPException(status_code=404, detail="Couldn't translate right now")
    translated_sentence = translation_processing.translate_text(sentence, source_language='en', target_language='pl')
    sentence_words = translation_processing.get_single_words_to_translate(sentence)
    translated_words = translation_processing.translate_all_words(sentence_words, source_language='en',
                                                                  target_language='pl')
    return Translation(
        sentence=sentence,
        sentence_words=sentence_words,
        translated_sentence=translated_sentence,
        translated_words=translated_words
    )


@app.get("/item/{item_id}")
async def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}


def main():
    uvicorn.run("automated_picture_translator_api:app", port=8000, reload=True, access_log=False)


if __name__ == '__main__':
    main()
