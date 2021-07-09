import zlib
import struct
def readStringFromFile(file):
    string = bytearray()
    currentByte = file.read(1)
    while(1):
        if currentByte == b'':
            return string.decode('utf-8')
            #this is python's method of EOF
        elif currentByte == b'\x00':
            return string.decode('utf-8')
        else:
            string.extend(currentByte)
        currentByte = file.read(1)

def readUShort(file):
    return struct.unpack("H",file.read(2))[0]

def readUInt(file):
    return struct.unpack("I",file.read(4))[0]

def readUInt64(file):
    return struct.unpack("Q",file.read(8))[0]

def jamcrc(string):
    return (zlib.crc32(str(string).encode()) ^ 0xffffffff) & 0x7fffffff

def mfxcrc(string,index):
    return (((zlib.crc32(str(string).encode()) ^ 0xffffffff) & 0x000fffff) << 12) + index

class MFXEntry:
    def __init__(self,name,index):
        self.name = name
        self.index = index

def readEntryMHS(inFile,strTableOff):
    nameOff = readUInt(inFile)
    string2 =readUInt(inFile) # string 2
    field8 = readUInt(inFile) # field_8
    field8c = readUInt(inFile) # field_8_c
    fieldc = readUInt(inFile) # field_C
    field10 = readUShort(inFile)
    index = readUShort(inFile)
    #we don't need the rest of the Entry, so end here
    #print(field8,fieldc,field10,index)
    inFile.seek(nameOff+strTableOff)
    name = readStringFromFile(inFile)
    return MFXEntry(name,index)

def readEntryMHGU(inFile,strTableOff):
    nameOff = readUInt(inFile)
    string2 =readUInt(inFile) # string 2
    field8 = readUInt(inFile) # field_8
    field8c = readUShort(inFile)
    index = readUShort(inFile)
    #we don't need the rest of the Entry, so end here
    #print(field8,fieldc,field10,index)
    inFile.seek(nameOff+strTableOff)
    name = readStringFromFile(inFile)
    return MFXEntry(name,index)

def readMfxStrings(file,outFile):
    assert file.read(4) == b'MFX\x00'
    assert file.read(1) == b'\x35'
    versionByte = file.read(1) #0x40 in Stories MFX, 0x00 in MHGU MFX
    assert file.read(2) == b'\x24\x00' #no point in struct for these
    file.read(4)
    entryCount = readUInt(file)
    stringTableOffset = readUInt(file)
    file.read(4)
    #no need for the rest of the header
    entries = []
    entryOffs = []
    if versionByte == b'\x40':
        for _ in range(entryCount):
            entryOffs.append(readUInt64(file))
        for offset in entryOffs:
            print(offset)
            file.seek(offset)
            entries.append(readEntryMHS(file,stringTableOffset))
    else:
        for _ in range(entryCount):
            entryOffs.append(readUInt(file))
        for offset in entryOffs:
            print(offset)
            file.seek(offset)
            entries.append(readEntryMHGU(file,stringTableOffset))

    for entry in entries:
        outFile.write("{string},{crc},{crc2},{jamcrc},{mfxcrc}\n".format(string=entry.name,crc=hex(zlib.crc32(entry.name.encode())),crc2=hex(zlib.crc32(entry.name.encode()) ^ 0xffffffff),jamcrc=hex(jamcrc(entry.name)),mfxcrc=hex(mfxcrc(entry.name,entry.index))))

readMfxStrings(open(r"D:\roms\Switch\Switch Hacking\hactool\extracted\d8c8bddf350e7faa0216d053c28bed9b.nca\RomFs\nativeNX\system\app_shader\AppShaderPackage.mfx",'rb'),open(r"C:\Users\Owner\Documents\GitHub\MH-Tools-and-Scripts\MHGU_MFX_Strings.txt",'w',encoding='utf-8'))