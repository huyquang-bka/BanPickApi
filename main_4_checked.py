import pickle
from team_pick import *
from image_to_text import *
from ReverseTime2 import *
from Timer import *
from HeroName import *


ban_coords_dire_1st = {}
ban_coords_rad_1st = {}

index = 0
with open("SpotFile/ban.csv", "r") as f:
    for line in f.read().split("\n")[:-1]:
        x, y, x2, y2 = list(map(int, line.split(",")))
        w = x2 - x
        h = y2 - y
        index += 1
        ban_coords_dire_1st[index] = [x, y, w, h]
        if index % 2 == 1:
            ban_coords_rad_1st[index+1] = [x, y, w, h]
        else:
            ban_coords_rad_1st[index-1] = [x, y, w, h]


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
banList = []
present_time = 30
nums_ban = [4, 10, 14]
nums_pick = [4, 8, 10]
return_dict = {}
while True:
    if keyboard.is_pressed("g"):
        s = time.time()
        img = ImageGrab.grab(bbox=(x_w, y_w, w_w, h_w))
        img_np = np.array(img)
        frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        reserve_time_ls = reverse_time(frame)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if gray_frame[578][1639] > 100:
            ban_coords = ban_coords_rad_1st
            pick_2_coords = pick_2_coords_rad_1st
            pick_coords = pick_coords_rad_1st
        else:
            ban_coords = ban_coords_dire_1st
            pick_2_coords = pick_2_coords_dire_1st
            pick_coords = pick_coords_dire_1st
        for index in range(1, 15):
            x, y, w, h = ban_coords[index]
            crop = frame[y:y + h, x:x + w]
            H, W, _ = crop.shape
            b, g, r = np.array(crop[5][W - 5], dtype=int)
            if b * g * r == 0:
                present_time = int(get_time_ban(crop))
                break
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            img = np.array(gray.flatten(), dtype=int)
            hero_name = clf.predict([img])[0]
            banList.append(hero_name.split("__")[0])
        if len(banList) in nums_ban:
            isBan = False
        else:
            isBan = True
        for i in range(10):
            hero_mini_list = pick_phase(frame, hero_mini_list, pick_coords, i)
            if len(hero_mini_list) > 0:
                pickList.append(get_true_hero_name(hero_mini_list[-1]))
                hero_mini_list = []

        if not isBan:
            for i in range(10):
                present_time = int(get_time_pick(frame, len(pickList)))
        break


radiant_time_str, dire_time_str = reserve_time_ls
present_time = present_time - (time.time() - s)
first_count = 0
count_pick = 15
is_picked = False
banned = 0
first_count = True
print(banList)
print(pickList)
print(reserve_time_ls, present_time)
while True:
    start = time.time()
    img = ImageGrab.grab(bbox=(x_w, y_w, w_w, h_w))
    img_np = np.array(img)
    frame = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
    if list(frame[131][12]) == [179, 177, 175]:
        continue

    if isBan and banned < 14:
        banList = []
        for index in range(1, 15):
            x, y, w, h = ban_coords[index]
            crop = frame[y:y + h, x:x + w]
            H, W, _ = crop.shape
            b, g, r = np.array(crop[5][W-5], dtype=int)
            if b * g * r == 0:
                break
            gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
            img = np.array(gray.flatten(), dtype=int)
            hero_name = clf.predict([img])[0]
            banList.append(hero_name.split("__")[0])
    if banList != lastBanList:
        print(banList)
        lastBanList = banList
        base_time = 29


    if not isBan:
        if len(pickList) < 6 or len(pickList) == 9:
            hero_mini_list = pick_phase_2_coord(frame, hero_mini_list, pick_2_coords, len(pickList))
        else:
            hero_mini_list = pick_phase(frame, hero_mini_list, pick_coords, len(pickList))
        if len(hero_mini_list) > 0:
            is_picked = True
        if len(hero_mini_list) == 2:
            print(hero_mini_list[-1])
            hero_append = get_true_hero_name(hero_mini_list[-1])
            print(hero_mini_list[-1])
            hero_mini_list = []
            if hero_append not in pickList:
                pickList.append(hero_append)
        if len(pickList) > n:
            print(pickList)
            n = len(pickList)
            print("*" * 50)
            if len(pickList) <= 6:
                base_time = 27
            else:
                base_time = 24


    banned = len(banList)
    picked = len(pickList)
    if banned in nums_ban:
        isBan = False
    if picked in nums_pick and isBan is False:
        if nums_ban.index(banned) == nums_pick.index(picked):
            isBan = True
    if first_count:
        base_time = present_time
        first_count = False
    if base_time > 0:
        base_time -= time.time() - start
    else:
        radiant_time_str, dire_time_str = reverse_time(frame)
        base_time = 0
    is_picked = False
    return_dict["RT_radiant"] = radiant_time_str
    return_dict["RT_dire"] = dire_time_str
    return_dict["timeBP"] = "0:" + str(int(base_time)) if base_time//10 >= 1 else "0:0" + str(int(base_time))


    print(banList, pickList, isBan)
    for i in range(4):
        index = f"0{i+1}"
        try:
            return_dict[f"turn_{index}"] = banList[i] + ".png"
        except:
            return_dict[f"turn_{index}"] = "empty.png"
        index = f"0{i+5}"
        try:
            return_dict[f"turn_{index}"] = pickList[i] + ".mov"
        except:
            return_dict[f"turn_{index}"] = "empty.png"

    for i in range(4, 10):
        index = f"0{i+5}" if i + 5 < 10 else str(i + 5)
        try:
            return_dict[f"turn_{index}"] = banList[i] + ".png"
        except:
            return_dict[f"turn_{index}"] = "empty.png"

    for i in range(10, 14):
        index = str(i + 9)
        try:
            return_dict[f"turn_{index}"] = banList[i] + ".png"
        except:
            return_dict[f"turn_{index}"] = "empty.png"

    for i in range(4, 8):
        try:
            return_dict[f"turn_{i + 11}"] = pickList[i] + ".mov"
        except:
            return_dict[f"turn_{i + 11}"] = "empty.png"

    for i in range(8, 10):
        try:
            return_dict[f"turn_{i + 15}"] = pickList[i] + ".mov"
        except:
            return_dict[f"turn_{i + 15}"] = "empty.png"

    print(return_dict)
    json_object = json.dumps(return_dict)

    # Writing to sample.json
    for i in range(5):
        with open(f"ApiFile/dota_status_{i}.json", "w+") as outfile:
            outfile.write(json_object)
    print(time.time() - start)