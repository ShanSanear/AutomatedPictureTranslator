import cv2
import numpy as np
import pyautogui
import pytesseract
from PIL import Image

# TODO to be removed after adding Tesseract to PATH
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'


class PictureProcessing:
    tesseract_config = '-l eng --psm 6'

    def __init__(self, tesseract_config: str = '-l eng --psm 6'):
        self.tesseract_config = tesseract_config

    @classmethod
    def process_picture_ocr(cls, picture: Image) -> str:
        custom_config = r'-l eng --psm 6'
        print(f"Picture to OCR: {picture}")
        raw_text = pytesseract.image_to_string(picture, config=custom_config)
        return raw_text.strip().replace('\n', ' ')

    @classmethod
    def white_to_black_only(cls, image):
        arr = cls.pil_to_cv2(image)
        return Image.fromarray(np.where(arr == 255, 0, 255).astype('uint8'))

    @classmethod
    def pil_to_cv2(cls, image):
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    @classmethod
    def capture_picture(cls, bottom_right, top_left):
        size = bottom_right - top_left
        return pyautogui.screenshot(region=(*top_left, *size))

    @classmethod
    def process_picture_white_to_black(cls, image):
        img = cls.white_to_black_only(image)
        return cls.process_picture_ocr(img)
