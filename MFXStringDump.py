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

def readMfxStrings(file,outFile):
    assert file.read(4) == b'MFX\x00'
    assert file.read(2) == b'\x35\x00'
    assert file.read(2) == b'\x24\x00' #no point in struct for these
    file.read(8)
    stringTableOffset = struct.unpack("I",file.read(4))[0]
    #no need for the rest of the header
    file.seek(stringTableOffset)
    strings = []
    strings.append(readStringFromFile(file))# there's a blank string at the start, gonna not include it in the while and just add it manually
    rdStr = readStringFromFile(file)
    while(rdStr != ""):
        strings.append(rdStr)
        rdStr = readStringFromFile(file)
    for rdStr in strings:
        outFile.write("{string},{crc},{crc2},{jamcrc}\n".format(string=rdStr,crc=hex(zlib.crc32(rdStr.encode())),crc2=hex(zlib.crc32(rdStr.encode()) ^ 0xffffffff),jamcrc=hex((zlib.crc32(rdStr.encode()) ^ 0xffffffff) & 0x7fffffff)))

readMfxStrings(open(r"D:\roms\Switch\Switch Hacking\hactool\extracted\d8c8bddf350e7faa0216d053c28bed9b.nca\RomFs\nativeNX\system\app_shader\AppShaderPackage.mfx",'rb'),open(r"C:\Users\Owner\Documents\GitHub\MH-Tools-and-Scripts\MHGU_MFX_Strings.txt",'w',encoding='utf-8'))