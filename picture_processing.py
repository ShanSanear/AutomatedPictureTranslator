import cv2
import numpy as np
import pyautogui
import pytesseract
from PIL import Image

from utils import Communicate

# TODO to be removed after adding Tesseract to PATH

pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'


class PictureProcessing:
    def __init__(self, tesseract_lang: str = 'en', page_segmentation_mode: str = '6'):
        self._from_Language = tesseract_lang
        self._page_segmentation_mode = page_segmentation_mode
        self.communicate = Communicate()
        self.communicate.update_tesseract_psm.connect(self._set_page_segmentation_mode)

    @property
    def tesseract_config(self):
        return f'-l {self._from_Language} --psm {self._page_segmentation_mode}'

    def _set_page_segmentation_mode(self, val):
        self._page_segmentation_mode = val

    def process_picture_ocr(self, picture: Image) -> str:
        print(f"Picture to OCR: {picture}")
        raw_text = pytesseract.image_to_string(picture, config=self.tesseract_config)
        return raw_text.strip().replace('\n', ' ')

    def white_to_black_only(self, image):
        arr = self.pil_to_cv2(image)
        return Image.fromarray(np.where(arr == 255, 0, 255).astype('uint8'))

    @classmethod
    def pil_to_cv2(cls, image):
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    @classmethod
    def capture_picture(cls, bottom_right, top_left):
        size = bottom_right - top_left
        return pyautogui.screenshot(region=(*top_left, *size))

    def process_picture_white_to_black(self, image):
        img = self.white_to_black_only(image)
        return self.process_picture_ocr(img)
