from PIL import Image
import sys
import os
import numpy as np
import json

def recolorWhite(img,pixdata,color):
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            if pixdata[x, y] == (255, 255, 255, 255):
                pixdata[x, y] = (color[0], color[1], color[2], 255)


def changeColor(im, color):

    data = np.array(im)

    r1, g1, b1 = 255, 255, 255 # Original value
    r2, g2, b2 = color[0], color[1], color[2] # Value that we want to replace it with

    red, green, blue = data[:,:,0], data[:,:,1], data[:,:,2]
    mask = (red == r1) & (green == g1) & (blue == b1)
    data[:,:,:3][mask] = [r2, g2, b2]
    
    im = Image.fromarray(data)
    
    return im

def get_concat_h(im1, im2):
    dst = Image.new('RGBA', (im1.width + im2.width, im1.height),(0,0,0,0))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (im1.width, 0))
    return dst

os.chdir(os.path.dirname(sys.argv[0]))
outputDir = r"eggs/"
os.makedirs(outputDir,exist_ok=True)
colors = json.load(open("egg_base_color.ebc.json",'r'))["root"]["mpArray"]["mpArray"]
unqPattern = json.load(open("egg_unique_pattern.eup.json",'r'))["root"]["mpArray"]["mpArray"]
buddies = json.load(open("buddyPath.bdypa.json",'r'))["root"]["mpArray"]["mpArray"]
baseInfo = json.load(open("monster_base_info.mbi.json",'r'))["root"]["mpArray"]["mpArray"]

egg1 = Image.open("cmn_eggicon01_ID.tga")
egg2 = Image.open("cmn_eggicon02_ID.tga")

raceToPattern = {
    1: 0,
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 5,
    7: 6,
    8: 7,
    11: 8,
    13: 9,
    14: 10,
    15: 11
}

baseCrop = (0,416,208,501)
outCrop = (208,416,416,501)
transCrop = (43,25,212,232)
patternCrop = [
    (0,0,170,208),
    (170,0,340,208),
    (340,0,510,208),
    (510,0,680,208),
    (680,0,850,208),
    (850,0,1020,208),
    (0,208,170,416),
    (170,208,340,416),
    (340,208,510,416),
    (510,208,680,416),
    (680,208,850,416),
    (850,208,1020,416)
]
outHalf = egg1.crop(outCrop)
outHalf = outHalf.transpose(Image.ROTATE_270)
outline = get_concat_h(outHalf,outHalf.transpose(Image.FLIP_LEFT_RIGHT))
outline = changeColor(outline,(0,0,0))
#outline.show()
eggOver = egg2.crop(transCrop)

halfEgg = egg1.crop(baseCrop)
halfEgg = halfEgg.transpose(Image.ROTATE_270)
baseEgg = get_concat_h(halfEgg,halfEgg.transpose(Image.FLIP_LEFT_RIGHT))
#baseEgg.show()


#baseEgg.show()

for i in range(len(buddies)):
    if buddies[i]["mBaseMonsterID[0]"] != 0:
        monster = next(item for item in baseInfo if item["mID"] == buddies[i]["mBaseMonsterID[0]"])
        monsterRace = monster["mMonsterRace"]
        try:
            uniquePattern = next(item for item in unqPattern if item["mMonsterRace"] == i)
        except(StopIteration):
            uniquePattern = None
        if uniquePattern != None:
            monsterRace = 15 #this will fail in the future, but it works for now
        try:
            eggColor = next(item for item in colors if item["mMonsterRace"] == i)
        except:
            print(buddies[i]["mKeyString"])
            eggColor = None
        if eggColor != None:
            baseColor = [eggColor["mBase[0]"],eggColor["mBase[1]"],eggColor["mBase[2]"]]
            patternColor = [eggColor["mPattern[0]"],eggColor["mPattern[1]"],eggColor["mPattern[2]"]]
            newEgg = baseEgg
            eggPattern = egg1.crop(patternCrop[raceToPattern[monsterRace]])
            newEgg = changeColor(newEgg,baseColor)
            eggPattern = changeColor(eggPattern,patternColor)
            newEgg.paste(eggPattern,(0,0),eggPattern)
            newEgg.paste(eggOver,(0,0),eggOver)
            newEgg.paste(outline,(0,0),outline)
            #newEgg.show()
            newEgg.save(outputDir+"egg-{}.png".format(i))

