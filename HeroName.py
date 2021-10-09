import json

f = open("jsonFile/heroes.json", "r")
data = json.load(f)

heroes_list = list(data.values())
hero_ids = dict()
IngameNameDict = {}
for hero in heroes_list:
    hero_name = hero["name"].split("hero_")[1]
    hero_name_ingame = hero["localized_name"]
    hero_name_ingame = hero_name_ingame.replace("-", "").upper()
    hero_name_ingame = hero_name_ingame.replace(" ", "").upper()
    IngameNameDict[hero_name_ingame] = hero_name


def get_true_hero_name(name):
    if name in IngameNameDict.keys():
        return IngameNameDict[name]
    for ingameName in sorted(IngameNameDict.keys(), key= lambda x: len(x), reverse=True):
        count = 0
        for digit in name:
            if digit in ingameName:
                count += 1
            if len(ingameName) - count > 2:
                break
        if len(ingameName) - count > 2:
            continue
        return IngameNameDict[ingameName]



