import json
import os
import sys

os.chdir(os.path.dirname(sys.argv[0]))
baseInfo = json.load(open("monster_base_info.mbi.json",'r'))["root"]["mpArray"]["mpArray"]
outFile = open("MonsterBaseInfo.txt",'w')

for monster in baseInfo:
    outFile.write(monster["mKeyString"])
    outFile.write("\n")