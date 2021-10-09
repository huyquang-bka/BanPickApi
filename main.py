import pickle
from team_pick import *
from image_to_text import *

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

reserve_time_coords = {}
with open("SpotFile/reserve_time.csv", "r") as f:
    for line in f.read().split("\n")[:-1]:
        x, y, w, h, index = map(int, line.split(","))
        reserve_time_coords[index] = [x, y, w, h]

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
while True:
    if keyboard.is_pressed("g"):
        start = time.time()
        img = ImageGrab.grab(bbox=(x_w, y_w, w_w, h_w))
        img_np = np.array(img)
        frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        for i in range(len(reserve_time_coords)):
            x, y, w, h = reserve_time_coords[i + 1]
            crop = frame[y:y + h, x:x + w]
            rv_time = img_to_text(crop)
            reserve_time_ls.append(rv_time)
            # print(rv_time)
            # cv2.imshow("Crop", cv2.resize(crop, dsize=None, fx=3, fy=3))
            # cv2.waitKey()
            # cv2.destroyAllWindows()

        for index in range(1, 15):
            turn += 1
            x, y, w, h = ban_coords[index]
            crop = frame[y:y + h, x:x + w]
            H, W, _ = crop.shape
            b, g, r = np.array(crop[5][W - 5], dtype=int)
            cv2.circle(crop, (W - 5, 5), 2, (255, 0, 0), 2)
            if b * g * r != 0:
                continue
            if img_to_text(crop):
                time_first = img_to_text(crop)
                isBan = True
                break
        break

radiant_time = int(reserve_time_ls[0][0]) * 60 + int(reserve_time_ls[0][1:])
dire_time = int(reserve_time_ls[1][0]) * 60 + int(reserve_time_ls[1][1:])
try:
    first_time = int(time_first[0]) * 60 + int(time_first[1:])
except:
    first_time = 0

nums_ban = [4, 10, 14]
nums_pick = [4, 8, 10]
first_count = 0
count_pick = 15
is_picked = False
banned = 0
while True:
    count_pick += 1
    start = time.time()
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
                banList.append("empty")
                continue
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            img = np.array(gray.flatten(), dtype=int)
            hero_name = clf.predict([img])[0]
            banList.append(hero_name.split("__")[0])
    if banList != lastBanList:
        print(banList)
        lastBanList = banList
        base_time = 30

    if not isBan and count_pick > 15:
        hero_mini_list = pick_phase(frame, hero_mini_list, pick_coords)
        if len(hero_mini_list) > 0:
            is_picked = True
        if len(hero_mini_list) == 4:
            pickList.append(hero_mini_list[-1])
            hero_mini_list = []
        if len(pickList) > n:
            print(pickList)
            n = len(pickList)
            print("*" * 50)
            base_time = 29
            count_pick = 0

    banned = len(banList) - banList.count("empty")
    picked = len(pickList)
    if banned in nums_ban:
        isBan = False
    if picked in nums_pick:
        isBan = True
    if first_count == 0:
        base_time = first_time
        first_count += 1
    if base_time > 0:
        base_time -= time.time() - start
    else:
        if isBan:
            if banned % 2 == 1:
                radiant_time -= time.time() - start
            else:
                dire_time -= time.time() - start
        elif isBan == False and is_picked == False:
            if picked in [0, 3, 5, 7, 8]:
                dire_time -= time.time() - start
            else:
                radiant_time -= time.time() - start
        base_time = 0
    is_picked = False
    radiant_time_str = str(int(radiant_time / 60)) + ":" + str(int(radiant_time % 60))
    dire_time_str = str(int(dire_time / 60)) + ":" + str(int(dire_time % 60))
    print(int(base_time), radiant_time_str, dire_time_str, isBan)
