import cv2
import pytesseract
import re
import cv2
import os
import numpy as np
from PIL import ImageGrab
import pytesseract
import re
from win32gui import *
import pyautogui
import time
import keyboard
import time

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
pick_2_coords_dire_1st = {}
with open("SpotFile/2team.csv", "r") as f:
    for line in f.read().split("\n")[:-1]:
        x, y, w, h, index = list(map(int, line.split(",")))
        pick_2_coords_dire_1st[index] = [x, y, w, h]

pick_coords_dire_1st = {}
with open("SpotFile/pick.csv", "r") as f:
    for line in f.read().split("\n")[:-1]:
        x, y, w, h, index = list(map(int, line.split(",")))
        pick_coords_dire_1st[index] = [x, y, w, h]


pick_2_coords_rad_1st = {}
with open("SpotFile/2team_rad_1st.csv", "r") as f:
    for line in f.read().split("\n")[:-1]:
        x, y, w, h, index = list(map(int, line.split(",")))
        pick_2_coords_rad_1st[index] = [x, y, w, h]

pick_coords_rad_1st = {}
with open("SpotFile/pick_rad_1st.csv", "r") as f:
    for line in f.read().split("\n")[:-1]:
        x, y, w, h, index = list(map(int, line.split(",")))
        pick_coords_rad_1st[index] = [x, y, w, h]

dire_turn = [0, 3, 5, 6, 8]

def sort_contours(cnts):
    reverse = False
    i = 0
    bounding_boxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, bounding_boxes) = zip(*sorted(zip(cnts, bounding_boxes),
                                         key=lambda b: b[1][i], reverse=reverse))
    return cnts


def pick_phase(frame, hero_mini_list, pick_coords, turn_pick):
    x, y, w, h = pick_coords[turn_pick + 1]
    crop = frame[y:y + h, x:x + w]
    crop = cv2.resize(crop, dsize=None, fx=3, fy=3)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)[1]
    blur = cv2.medianBlur(binary, 3)
    # kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    # thre_mor = cv2.morphologyEx(blur, cv2.MORPH_DILATE, kernel3)
    # thre_mor_copy = thre_mor.copy()
    cont, _ = cv2.findContours(blur, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    count = 0
    cont_dict = {}
    try:
        for c in sort_contours(cont):
            (x_c, y_c, w_c, h_c) = cv2.boundingRect(c)
            height, width = gray.shape
            if height / h_c > 3 or height / h_c < 1.2:
                continue
            if y_c < 10 or h_c + y_c > height - 10:
                continue
            count += 1
            cont_dict[count] = [x_c, y_c, w_c, h_c]
    except:
        pass


    # # Segment kí tự
    if count >= 2:
        x1, y1, w1, h1 = cont_dict[1]
        x2, y2, w2, h2 = cont_dict[count]
        digit_crop = blur[y1 - 2:y2 + h2 + 2, x1 - 2:x2 + w2 + 2]
        try:
            text = pytesseract.image_to_string(digit_crop,
                                               config='--psm 13 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                               lang="eng")
            hero = re.sub("[\W_]+", "", text)

            if len(hero_mini_list) == 2:
                return hero_mini_list

            if hero:
                hero_mini_list.append(hero)
                return hero_mini_list
        except:
            pass

    return []


def pick_phase_2_coord(frame, hero_mini_list, pick_2_coords, turn_pick):
    if turn_pick in dire_turn:
        x, y, w, h = pick_2_coords[2]
    else:
        x, y, w, h = pick_2_coords[1]
    crop = frame[y:y + h, x:x + w]
    crop = cv2.resize(crop, dsize=None, fx=3, fy=3)
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    binary = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY_INV)[1]
    blur = cv2.medianBlur(binary, 3)
    # kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    # thre_mor = cv2.morphologyEx(blur, cv2.MORPH_DILATE, kernel3)
    # thre_mor_copy = thre_mor.copy()
    cont, _ = cv2.findContours(blur, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    count = 0
    cont_dict = {}
    try:
        for c in sort_contours(cont):
            (x_c, y_c, w_c, h_c) = cv2.boundingRect(c)
            height, width = gray.shape
            if height / h_c > 3 or height / h_c < 1.2:
                continue
            if y_c < 10 or h_c + y_c > height - 10:
                continue
            count += 1
            cont_dict[count] = [x_c, y_c, w_c, h_c]
    except:
        pass


    # # Segment kí tự
    if count >= 2:
        x1, y1, w1, h1 = cont_dict[1]
        x2, y2, w2, h2 = cont_dict[count]
        digit_crop = blur[y1 - 2:y2 + h2 + 2, x1 - 2:x2 + w2 + 2]
        try:
            text = pytesseract.image_to_string(digit_crop,
                                               config='--psm 13 --oem 1 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                               lang="eng")
            hero = re.sub("[\W_]+", "", text)

            if len(hero_mini_list) == 2:
                return hero_mini_list

            if hero:
                hero_mini_list.append(hero)
                return hero_mini_list
        except:
            pass

    return []

