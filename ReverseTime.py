from image_to_text import img_to_text

reserve_time_coords = {}
with open("SpotFile/reserve_time.csv", "r") as f:
    for line in f.read().split("\n")[:-1]:
        x, y, w, h, index = map(int, line.split(","))
        reserve_time_coords[index] = [x, y, w, h]


def reverse_time(frame):
    reserve_time_ls = []
    for i in range(len(reserve_time_coords)):
        x, y, w, h = reserve_time_coords[i + 1]
        crop = frame[y:y + h, x:x + w]
        rv_time = img_to_text(crop)
        rv_time = rv_time[0] + rv_time[-2:]
        reserve_time_ls.append(rv_time)
    return reserve_time_ls
