import zlib
from pathlib import Path
import os
import struct
import sys
from Crypto.Cipher import Blowfish

fileExts = dict()

importPath = r"D:\Program Files\Steam\steamapps\common\Monster Hunter Stories 2\nativeDX11x64\archive\mod\mo\mo016\em016/"

key = b"QZHaM;-5:)dV#"
cipher = Blowfish.new(key,Blowfish.MODE_ECB)

def writeUShort(file,val):
    file.write(struct.pack("H",val))

def writeUIntToByteArray(array,val):
    array.extend(struct.pack("I",val))

def jamcrc(string):
    return (zlib.crc32(str(string).encode()) ^ 0xffffffff) & 0x7fffffff

def padToECB(array):
    while (len(array) % Blowfish.block_size) != 0:
        array.extend([0x00])

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def endianness_reversal(data):
    return b''.join(map(lambda x: x[::-1],chunks(data, 4)))

def GenerateFileExtDict():
    #cfid, fppgr, bemtp, dfd, mkr, sdm, ecpd
    #gonna need a full filetype dump once exe is examined
    #if nativePC works like World, could just grab a list from procmon
    fileExts[".xfsa"] = jamcrc("rAIFSM") #aka .fsm
    fileExts[".lcm"] = jamcrc("rCameraList")
    fileExts[".xfsc"] = jamcrc("rCharacter")
    fileExts[".sbc"] = jamcrc("rCollision")
    fileExts[".clc"] = jamcrc("rColorLinkColor")
    fileExts[".cli"] = jamcrc("rColorLinkInfo")
    fileExts[".ean"] = jamcrc("rEffectAnim")
    fileExts[".efl"] = jamcrc("rEffectList")
    fileExts[".gui"] = jamcrc("rGUI")
    fileExts[".gfd"] = jamcrc("rGUIFont")
    fileExts[".gmd"] = jamcrc("rGUIMessage")
    fileExts[".xfsh"] = jamcrc("rHit2D")
    fileExts[".xfsl"] = jamcrc("rLayoutParameter")
    fileExts[".mod"] = jamcrc("rModel")
    fileExts[".lmt"] = jamcrc("rMotionList")
    fileExts[".pvi"] = jamcrc("rPartsVisibleInfo")
    fileExts[".prp"] = jamcrc("rPropParam")
    fileExts[".sdl"] = jamcrc("rScheduler")
    fileExts[".sbkr"] = jamcrc("rSoundBank")
    fileExts[".srqr"] = jamcrc("rSoundRequest")
    fileExts[".lopus"] = jamcrc("rSoundSourceADPCM") #this might be different on PC, as lopus is a Switch-exclusive ADPCM
    fileExts[".tex"] = jamcrc("rTexture")
    fileExts[".sgs"] = jamcrc("rSoundGuiSe")
    fileExts[".spoc"] = jamcrc("rSoundSeParamOffsetControl")
    fileExts[".pts"] = jamcrc("rSoundPelTiedSe")
    fileExts[".sar"] = jamcrc("rSoundAreaReverb")
    fileExts[".sss"] = jamcrc("rSoundSystemSetting")
    fileExts[".vjr"] = jamcrc("rVirtualJoint")

    fileExts[".mrl"] = 0x2749C8A8

def getExtension(hash):
    if hash in fileExts:
        return fileExts[hash]
    else:
        return int("0x"+hash.replace(".",""),16)

def exportString(array,string):
    nullsize = 128 - len(string)
    array.extend(string.encode('utf-8'))
    for i in range(nullsize):
        array.extend([0x00])

def appendArrayToOffset(array,offset):
    while len(array) < offset:
        array.extend([0x00])

class Entry:
    def __init__(self,name,extHash,compSize,decompSize,buffer):
        self.name = name
        self.extHash = extHash
        self.compSize = compSize
        self.decompSize = decompSize
        self.buffer = buffer
    
    def setOffset(self, offset):
        self.offset = offset

def writeArchive(outFile):
    outFileDir = Path(importPath).rglob("*.*")
    fileCount = len(list(outFileDir))
    outFile.write(b'ARCC') #just go ahead and write it out to the encrypted version
    writeUShort(outFile,7)
    writeUShort(outFile,fileCount)
    fileDec = bytearray()
    entries = []
    for path in Path(importPath).rglob("*.*"):
        name = str(Path(path).relative_to(importPath)).split(".")
        namePath = name[0]
        extHash = getExtension("."+name[1])
        print(namePath)
        inFile = open(path,'rb')
        uBuffer = inFile.read()
        decompSize = len(uBuffer)
        buffer = zlib.compress(uBuffer)
        compSize = len(buffer)
        entries.append(Entry(namePath,extHash,compSize,decompSize,buffer))
    currentOff = (4 + (fileCount * 0x90)) + (32768- ((4 + (fileCount * 0x90)) % 32768 )) #basically, just make sure it's far from the header
    for entry in entries:
        exportString(fileDec,entry.name)
        writeUIntToByteArray(fileDec,entry.extHash)
        writeUIntToByteArray(fileDec,entry.compSize)
        writeUIntToByteArray(fileDec, ((entry.decompSize) + 0x40000000))
        writeUIntToByteArray(fileDec, currentOff)
        entry.setOffset(currentOff)
        currentOff += entry.compSize
        #print(startingOff)
    for entry in entries:
        appendArrayToOffset(fileDec,entry.offset)
        fileDec.extend(entry.buffer)
    padToECB(fileDec)
    fileEnc = bytearray()
    fileEnc.extend(endianness_reversal(cipher.encrypt(endianness_reversal(fileDec))))
    outFile.write(fileEnc)



filename = input("Input Filename: ")
GenerateFileExtDict()
writeArchive(open(os.path.dirname(importPath)+filename,'wb'))