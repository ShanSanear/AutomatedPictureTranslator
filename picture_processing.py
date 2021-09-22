import cv2
import numpy as np
import pyautogui
import pytesseract
from PIL import Image

from utils import Communicate

# TODO to be removed after adding Tesseract to PATH

pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'


class PictureProcessing:
    _from_language = 'eng'
    _page_segmentation_mode = '6'
    tesseract_config = f'-l {_from_language} --psm {_page_segmentation_mode}'

    def __init__(self):
        self.communicate = Communicate()
        self.communicate.update_tesseract_psm.connect(self._set_page_segmentation_mode)

    def _set_page_segmentation_mode(self, val):
        print(f"Set page segmentation mode: {val}")
        self._page_segmentation_mode = val

    @classmethod
    def process_picture_ocr(cls, picture: Image) -> str:
        print(f"Picture to OCR: {picture}")
        raw_text = pytesseract.image_to_string(picture, config=cls.tesseract_config)
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
    def capture_picture_in_black_and_white(cls, bottom_right, top_left):
        size = bottom_right - top_left
        ss = pyautogui.screenshot(region=(*top_left, *size))
        return cls.process_picture_white_to_black(ss)

    @classmethod
    def process_picture_white_to_black(cls, image):
        img = cls.white_to_black_only(image)
        return cls.process_picture_ocr(img)
