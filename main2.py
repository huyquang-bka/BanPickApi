import pickle
from team_pick import *
from image_to_text import *
from Timer import *
from ReverseTime import reverse_time

ban_coords = {}
index = 0
with open("SpotFile/ban.csv", "r") as f:
    for line in f.read().split("\n")[:-1]:
        x, y, x2, y2 = list(map(int, line.split(",")))
        w = x2 - x
        h = y2 - y
        index += 1
        ban_coords[index] = [x, y, w, h]

with open("BanModel/clf.pkl", "rb") as f:
    clf = pickle.load(f)


window_handle = FindWindow(None, "Dota 2")
x_w, y_w, w_w, h_w = GetWindowRect(window_handle)

hero_mini_list = []
pickList = []
lastBanList = []
n = 0
print("start")

reserve_time_ls = []
time_first = []
turn = 0
isBan = False
present_time = 30
while True:
    if keyboard.is_pressed("g"):
        start = time.time()
        img = ImageGrab.grab(bbox=(x_w, y_w, w_w, h_w))
        img_np = np.array(img)
        frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        reserve_time_ls = reverse_time(frame)
        for index in range(1, 15):
            x, y, w, h = ban_coords[index]
            crop = frame[y:y + h, x:x + w]
            H, W, _ = crop.shape
            b, g, r = np.array(crop[5][W - 5], dtype=int)
            cv2.circle(crop, (W - 5, 5), 2, (255, 0, 0), 2)
            if b * g * r != 0:
                continue
            if img_to_text(crop):
                present_time = int(img_to_text(crop))
                isBan = True
                break
        for i in range(10):
            hero_mini_list = pick_phase(frame, hero_mini_list, pick_coords, i)
            if len(hero_mini_list) > 0:
                is_picked = True
            if len(hero_mini_list) == 2:
                pickList.append(hero_mini_list[-1])
                hero_mini_list = []
        break

radiant_time = int(reserve_time_ls[0][0]) * 60 + int(reserve_time_ls[0][1:])
dire_time = int(reserve_time_ls[1][0]) * 60 + int(reserve_time_ls[1][1:])

banList = []


nums_ban = [0, 4, 10, 14]
nums_pick = [4, 8, 10]
first_count = 0
count_pick = 15
is_picked = False
banned = 0
return_dict = {}
print(isBan)
print(pickList)
while True:
    count_pick += 1
    img = ImageGrab.grab(bbox=(x_w, y_w, w_w, h_w))
    img_np = np.array(img)
    frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    if list(frame[131][12]) == [179, 177, 175]:
        continue

    banList = []
    if isBan and banned < 14:
        for index in range(1, 15):
            x, y, w, h = ban_coords[index]
            crop = frame[y:y + h, x:x + w]
            H, W, _ = crop.shape
            b, g, r = np.array(crop[5][W-5], dtype=int)
            if b * g * r == 0:
                if present_time > 0:
                    present_time = int(img_to_text(crop))
                break
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            img = np.array(gray.flatten(), dtype=int)
            hero_name = clf.predict([img])[0]
            banList.append(hero_name.split("__")[0])
    if banList != lastBanList:
        print(banList)
        lastBanList = banList
    if not isBan:
        if int(present_time) > 0:
            present_time = get_time(frame, len(pickList))
        hero_mini_list = pick_phase(frame, hero_mini_list, pick_coords, len(pickList))
        if len(hero_mini_list) > 0:
            is_picked = True
        if len(hero_mini_list) == 2:
            pickList.append(hero_mini_list[-1])
            hero_mini_list = []
        if len(pickList) > n:
            print(pickList)
            n = len(pickList)
            print("*" * 50)


    banned = len(banList)
    picked = len(pickList)
    if banned in nums_ban:
        isBan = False
    if picked in nums_pick:
        isBan = True
    present_time = int(present_time)

    if present_time == 0:
        radiant_time, dire_time = reverse_time(frame)
    is_picked = False
    radiant_time_str = str(int(radiant_time / 60)) + ":" + str(int(radiant_time % 60))
    dire_time_str = str(int(dire_time / 60)) + ":" + str(int(dire_time % 60))
    print(present_time, radiant_time_str, dire_time_str, isBan)
    # return_dict["RT_radiant"] = radiant_time_str
    # return_dict["RT_dire"] = dire_time_str
    # return_dict["timeBP"] = "0:" + str(present_time) if present_time//10 >= 1 else "0:0" + str(present_time)



