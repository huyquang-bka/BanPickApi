import cv2
import pytesseract
import re


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pick_time = {}
with open("SpotFile/pick_time.csv", "r") as f:
    for line in f.read().split("\n")[:-1]:
        x, y, w, h, index = list(map(int, line.split(",")))
        pick_time[index] = [x, y, w, h]


def sort_contours(cnts):
    reverse = False
    i = 0
    bounding_boxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, bounding_boxes) = zip(*sorted(zip(cnts, bounding_boxes),
                                         key=lambda b: b[1][i], reverse=reverse))
    return cnts


def get_time_pick(frame, turn_pick):
    x, y, w, h = pick_time[turn_pick + 1]
    crop = frame[y:y + h, x:x + w]
    crop = cv2.resize(crop, dsize=None, fx=3, fy=3)
    crop_copy = crop.copy()
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)[1]
    blur = cv2.medianBlur(binary, 3)
    # kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    # thre_mor = cv2.morphologyEx(blur, cv2.MORPH_DILATE, kernel3)
    # thre_mor_copy = thre_mor.copy()
    cont, _ = cv2.findContours(blur, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    count = 0
    timer = ""
    try:
        for c in sort_contours(cont)[2:]:
            (x_c, y_c, w_c, h_c) = cv2.boundingRect(c)
            height, width = gray.shape
            if height / h_c > 7 or height / h_c < 1.1:
                continue
            if y_c < 10 or h_c + y_c > height - 20:
                continue
            count += 1
            text = pytesseract.image_to_string(blur[y_c - 5:y_c + h_c + 5, x_c - 5:x_c + w_c + 5],
                                               config='--psm 13 --oem 1 -c tessedit_char_whitelist=0123456789',
                                               lang="eng")
            timer += re.sub("[\W_]+", "", text)
        if len(timer) >= 2:
            return timer[-2:]
    except:
        pass

    return "0"


def get_time_ban(frame):
    crop = cv2.resize(frame, dsize=None, fx=3, fy=3)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)[1]
    blur = cv2.medianBlur(binary, 3)
    try:
        text = pytesseract.image_to_string(blur,
                                           config='--psm 13 --oem 1 -c tessedit_char_whitelist=0123456789',
                                           lang="eng")
        if not re.sub("[\W_]+", "", text):
            return "00"
        return re.sub("[\W_]+", "", text)
    except:
        pass

    return "00"
