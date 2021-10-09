import cv2
import pytesseract
import re
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

reserve_time_coords = {}
with open("SpotFile/reserve_time.csv", "r") as f:
    for line in f.read().split("\n")[:-1]:
        x, y, w, h, index = map(int, line.split(","))
        reserve_time_coords[index] = [x, y, w, h]


def sort_contours(cnts):
    reverse = False
    i = 0
    bounding_boxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, bounding_boxes) = zip(*sorted(zip(cnts, bounding_boxes),
                                         key=lambda b: b[1][i], reverse=reverse))
    return cnts


def img_to_text(frame):
    crop = cv2.resize(frame, dsize=None, fx=3, fy=3)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)[1]
    blur = cv2.medianBlur(binary, 3)
    try:
        text1 = pytesseract.image_to_string(blur,
                                           config='--psm 13 --oem 1 -c tessedit_char_whitelist=0123456789',
                                           lang="eng")

        if not re.sub("[\W_]+", "", text1):
            return "00"
        return re.sub("[\W_]+", "", text1)
    except:
        pass

    return "00"




