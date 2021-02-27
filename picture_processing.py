import cv2
import numpy as np
import pytesseract
from PIL import Image

# TODO to be removed after adding Tesseract to PATH
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'


def process_picture_ocr(picture: Image) -> str:
    custom_config = r'-l eng --psm 6'
    print(f"Picture to OCR: {picture}")
    raw_text = pytesseract.image_to_string(picture, config=custom_config)
    return raw_text.strip().replace('\n', ' ')


def white_to_black_only(image):
    arr = pil_to_cv2(image)
    return Image.fromarray(np.where(arr == 255, 0, 255).astype('uint8'))


def pil_to_cv2(image):
    return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
