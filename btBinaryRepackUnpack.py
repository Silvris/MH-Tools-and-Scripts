from pathlib import Path
import os
import zlib
import sys
import struct

def jamcrc(string):
    return (zlib.crc32(str(string).encode()) ^ 0xffffffff)

def writeUInt(file,val):
    file.write(struct.pack("I",val))

def readUInt(file):
    return struct.unpack("I",file.read(4))[0]

class File:
    def __init__(self,hash,data):
        self.hash = hash
        self.data = data

knownPaths = dict()
#only set the battleparm files manually, not the battleai
#we generate those using a for loop, for even greater compatibility
def generateHashes():
    knownPaths[jamcrc("battleparm\\HunterData.bin")] = "battleparm\\HunterData.bin"
    knownPaths[jamcrc("battleparm\\adjustData.bin")] = "battleparm\\adjustData.bin"
    knownPaths[jamcrc("battleparm\\MonsterData.bin")] = "battleparm\\MonsterData.bin"
    knownPaths[jamcrc("battleparm\\MonsterBaseData.bin")] = "battleparm\\MonsterBaseData.bin"
    knownPaths[jamcrc("battleparm\\OtomonData.bin")] = "battleparm\\OtomonData.bin"
    knownPaths[jamcrc("battleparm\\PartsData.bin")] = "battleparm\\PartsData.bin"
    knownPaths[jamcrc("battleparm\\PlayerData.bin")] = "battleparm\\PlayerData.bin"

    knownPaths[jamcrc("battleai\\testatel.bin")] = "battleai\\testatel.bin"
    knownPaths[jamcrc("battleai\\npcai.bin")] = "battleai\\npcai.bin"
    knownPaths[jamcrc("battleai\\StatusValue.bin")] = "battleai\\StatusValue.bin"
    knownPaths[jamcrc("battleai\\MonsterStatus.bin")] = "battleai\\MonsterStatus.bin"
    knownPaths[jamcrc("battleai\\otomonai.bin")] = "battleai\\otomonai.bin"
    for i in range(100000):
        knownPaths[jamcrc("battleai\\atelscrRush{0:0>5}.bin".format(i))] = "battleai\\atelscrRush{0:0>5}.bin".format(i)
    for i in range(100000):
        knownPaths[jamcrc("battleai\\atelscr{0:0>5}.bin".format(i))] = "battleai\\atelscr{0:0>5}.bin".format(i)

def getName(hash,type):
    if hash in knownPaths:
        return knownPaths[hash]
    else:
        name = ""
        if type == 0:
            name = "battleai\\"
        else:
            name = "battleparm\\"
        
        return name + str(hex(hash)[2:]) + ".bin"

def unpackBtBinary(inFile):
    dirName = os.path.basename(inFile.name).replace(".btb","") + "/"
    generateHashes()
    magic = inFile.read(4)
    assert magic == b"btb\x00"
    version = readUInt(inFile)
    assert version == 1
    for type in range(2):
        count = readUInt(inFile)
        for i in range(count):
            dataSize = readUInt(inFile)
            name = dirName + getName(readUInt(inFile),type)
            print(name)
            if os.path.dirname(name) != '':
                os.makedirs(os.path.dirname(name),exist_ok=True)
            fileData = inFile.read(dataSize)
            newFile = open(name,'wb')
            newFile.write(fileData)
            newFile.close()

def packBtBinary(importPath,outFile):
    generateHashes()
    entries = list()
    for path in Path(importPath).rglob("*"):
        if path.is_dir():
            middleList = list()
            for file in Path(path).rglob("*.bin"):
                name = str(Path(file).relative_to(importPath))
                if jamcrc(name) in knownPaths:
                    hash = jamcrc(name)
                else:
                    print(name)
                    #we cut it back open to retrieve the stored hash
                    hash = int("0x"+os.path.basename(name).replace(".bin",""),16)
                fp = open(file,'rb')
                data = fp.read()
                fp.close()
                middleList.append(File(hash,data))
            middleList.sort(key=lambda file: file.hash)
            entries.append(middleList)
    outFile.write(b"btb\x00")
    writeUInt(outFile,1)
    for entry in entries:
        writeUInt(outFile,len(entry))
        for file in entry:
            writeUInt(outFile,len(file.data))
            writeUInt(outFile,file.hash)
            outFile.write(file.data)
    outFile.close()




if __name__ == "__main__":

    for i, arg in enumerate(sys.argv):
        if i > 0:
            os.chdir(os.path.dirname(arg))
            if os.path.isdir(arg):
                packBtBinary(arg+"/",open(os.path.dirname(arg)+"/"+os.path.basename(arg)+"-new.btb",'wb'))
            else:
                unpackBtBinary(open(arg,'rb'))