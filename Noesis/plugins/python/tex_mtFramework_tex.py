from inc_noesis import *
import rapi
import struct
import subprocess

"""
Noesis Script for extracting textures from games using MT Framework. 
Originally intended for Monster Hunter 3 Ultimate, Monster Hunter Explore, and Monster Hunter Generations Ultimate, so any other formats may have issues
"""
Debug = True
bigEndian = False

def registerNoesisTypes():
    handle = noesis.register("MT Framework TEX", ".tex")
    noesis.setHandlerTypeCheck(handle, texCheckType)
    noesis.setHandlerLoadRGBA(handle, texLoadARGB)
    noesis.logPopup()
    return 1


def texCheckType(data):
    bs = NoeBitStream(data)
    fileMagic = bs.readUInt()
    if fileMagic == 5784916:
        print("MT Framework Texture found.")
        return 1
    elif fileMagic == 1413830656:
        print("Big Endian MT Framework Texture found.")
        return 1
    elif fileMagic == 542655828:
        print("Mobile MT Framework Texture found.")
        return 1
    else:
        print("Fatal Error: Unknown file magic: " + str(hex(fileMagic) + " expected 0x584554!"))
        return 0
"""
def ConvertYCbCr2RGB(y,cb,cr):
    assert len(y) == len(cb)
    assert len(y) == len(cr)
    pixCount = len(y)
    r = []
    g = []
    b = []
    for i in range(pixCount):
        yCoeff = 255/219
        crCoeff = (255/224)*1.402
        cbCoeff = (255/224)*1.772
        gbRatio = 0.114/0.587
        grRatio = 0.299/0.587
        red = y[i] -3.94e-5*cb[i] +1.14 *cr[i]
        green = y[i] -0.394*cb[i] -0.581*cr[i]
        blue = y[i] +2.032*cb[i] -4.81e-4*cr[i]
        #red = yCoeff*(y[i]-16) + crCoeff*(cr[i]-128)
        #green = yCoeff*(y[i]-16) - cbCoeff*gbRatio*(cb[i]-128) - crCoeff*grRatio*(cr[i]-128)
        #blue = yCoeff*(y[i]-16) + cbCoeff*(cb[i]-128)
        #red = y[i] + ((cr[i]-128)*1.402)
        #green = y[i] - ((cb[i]-128)*0.344136) - (0.714136*(cr[i]-128))
        #blue = y[i] + ((cb[i]-128)*1.772)
        red += 1
        green += 1
        blue += 1
        if red < 0: red += 256
        if green < 0: green += 256
        if blue < 0: blue += 256
        if red > 255: red = 255
        if green > 255: green = 255
        if blue > 255: blue = 255
        r.append(red)
        g.append(green)
        b.append(blue)
    return r, g, b
"""
def texLoadARGB(data, texList):
    bs = NoeBitStream(data)
    magic = bs.readUInt()
    if magic == 5784916 or magic == 1413830656:
        bigEndian = False
        if magic == 1413830656:
            bigEndian = True
            bs.setEndian(NOE_BIGENDIAN)
            bs.setByteEndianForBits(NOE_BIGENDIAN)
        Version = bs.readBits(12)
        if Version == 16:
            print("Monster Hunter World textures not supported! Use Jodo's Texture Converter on Nexus Mods.")
            return 0
        unkn1 = bs.readBits(12)
        unused1 = bs.readBits(4)
        alphaFlags = bs.readBits(4)
        MipMapCount = bs.readBits(6)
        Width = bs.readBits(13)
        Height = bs.readBits(13)
        unkn2 = bs.readByte()
        Format = bs.readByte()
        unkn3 = bs.readUShort()
        Length = Width*Height
        if Version == 160 or Version == 163:
            Length = bs.readUInt()
        if Debug:
            print("Endian: {endian}".format(endian="Big" if bigEndian else "Little"))
            print("Version: {}".format(Version))
            print("Format: {}".format(Format))
            print("Width: {}".format(Width))
            print("Height: {}".format(Height))
            print("Length: {}".format(Length))
        MipOffsets = []
        if Version == 158:
            #DMC4SE
            for i in range(MipMapCount):
                MipOffsets.append(bs.readUInt())
            if Format == 19:
                pix = rapi.imageDecodeDXT(bs.readBytes(int(Length/2)),Width,Height,noesis.FOURCC_DXT1)
            elif Format == 20:
                pix = rapi.imageDecodeDXT(bs.readBytes(Length),Width,Height,noesis.FOURCC_DXT3)
            elif Format == 23:
                pix = rapi.imageDecodeDXT(bs.readBytes(Length),Width,Height,noesis.FOURCC_DXT5)
            elif Format == 25:
                pix = rapi.imageDecodeDXT(bs.readBytes(int(Length/2)),Width,Height,noesis.FOURCC_BC4)
            elif Format == 31:
                pix = rapi.imageDecodeDXT(bs.readBytes(Length),Width,Height,noesis.FOURCC_BC5)
            else:
                print(Format)
            texList.append(NoeTexture("MTFTex", Width, Height, pix, noesis.NOESISTEX_RGBA32))
        if Version == 160:
            for i in range(MipMapCount):
                MipOffsets.append(bs.readUInt())
            #Switch - GU
            if Format == 7:
                blockWidth = blockHeight = 1
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, 4, maxBlockHeight)
                pix = rapi.imageDecodeRaw(pix,Width,Height,"b8g8r8a8",2)
            elif Format == 19:
                blockWidth = blockHeight = 4
                blockSize = 8
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, blockSize, maxBlockHeight)
                pix = rapi.imageDecodeDXT(pix,Width,Height,noesis.FOURCC_DXT1)
            elif Format == 23:
                blockWidth = blockHeight = 4
                blockSize = 16
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, blockSize, maxBlockHeight)
                pix = rapi.imageDecodeDXT(pix, Width, Height, noesis.FOURCC_DXT5)
            elif Format == 25:
                blockWidth = blockHeight = 4
                blockSize = 8
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, blockSize, maxBlockHeight)
                pix = rapi.imageDecodeDXT(pix,Width,Height,noesis.FOURCC_ATI1)
            elif Format == 31:
                blockWidth = blockHeight = 4
                blockSize = 16
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, blockSize, maxBlockHeight)
                pix = rapi.imageDecodeDXT(pix,Width,Height,noesis.FOURCC_ATI2)
            else:
                print(Format)
            texList.append(NoeTexture("MTFTex", Width, Height, pix, noesis.NOESISTEX_RGBA32))
        if Version == 163:
            #MHS 2
            for i in range(MipMapCount):
                MipOffsets.append(bs.readUInt())
            currentOff = bs.tell()
            bs.seek(currentOff + MipOffsets[0])
            if Format == 7:
                blockWidth = blockHeight = 1
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, 4, maxBlockHeight)
                pix = rapi.imageDecodeRaw(pix,Width,Height,"b8g8r8a8",2)
            elif Format == 9:
                blockWidth = blockHeight = 1
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, 4, maxBlockHeight)
                pix = rapi.imageDecodeRaw(pix,Width,Height,"r8g8b8a8",2)
            elif Format == 19:
                blockWidth = blockHeight = 4
                blockSize = 8
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, blockSize, maxBlockHeight)
                pix = rapi.imageDecodeDXT(pix,Width,Height,noesis.FOURCC_DXT1)
            elif Format == 20:
                blockWidth = blockHeight = 4
                blockSize = 8
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, blockSize, maxBlockHeight)
                pix = rapi.imageDecodeDXT(pix,Width,Height,noesis.FOURCC_BC1)
            elif Format == 23:
                blockWidth = blockHeight = 4
                blockSize = 16
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, blockSize, maxBlockHeight)
                pix = rapi.imageDecodeDXT(pix, Width, Height, noesis.FOURCC_DXT5)
            elif Format == 25:
                blockWidth = blockHeight = 4
                blockSize = 8
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, blockSize, maxBlockHeight)
                pix = rapi.imageDecodeDXT(pix,Width,Height,noesis.FOURCC_ATI1)
            elif Format == 31:
                blockWidth = blockHeight = 4
                blockSize = 16
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, blockSize, maxBlockHeight)
                pix = rapi.imageDecodeDXT(pix,Width,Height,noesis.FOURCC_ATI2)
            elif Format == 55:
                blockWidth = blockHeight = 4
                blockSize = 16
                WidthInBlocks = (Width + (blockWidth - 1)) // blockWidth
                HeightInBlocks = (Height + (blockHeight - 1)) // blockHeight
                maxBlockHeight = rapi.callExtensionMethod("untile_blocklineargob_blockheight", Height, 4)
                pix = rapi.callExtensionMethod("untile_blocklineargob", bs.readBytes(Length), WidthInBlocks, HeightInBlocks, blockSize, maxBlockHeight)
                pix = rapi.imageDecodeDXT(pix,Width,Height,noesis.FOURCC_BC7)
            else:
                print(Format)
            texList.append(NoeTexture("MTFTex", Width, Height, pix, noesis.NOESISTEX_RGBA32))
        if Version == 165:
            #3DS v2 | Wii U
            if bigEndian:
                #adapted loosely from Zaramot's script
                gtxTex = (b'\x47\x66\x78\x32\x00\x00\x00\x20\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x0A\x00\x00\x00\x9C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01')
                gtxWidth = struct.pack(">I", Width)
                gtxheight = struct.pack(">I", Height)
                gtxTex += gtxWidth
                gtxTex += gtxheight
                gtxTex += (b'\x00\x00\x00\x01\x00\x00\x00\x01')
                if Format == 11:
                    ddsFmt = noesis.FOURCC_BC1
                    type = struct.pack(">I", 49)
                    gtxFmt =  struct.pack(">I", 0xC40003FF)
                    pixelInfo = struct.pack(">II", 4096, 256)
                    ddsSize = (Width * Height * 4) // 8
                    ddsData = bs.readBytes(ddsSize)
                elif Format == 12:
                    ddsFmt = noesis.FOURCC_BC2
                    type = struct.pack(">I", 50)
                    gtxFmt =  struct.pack(">I", 0xCC0003FF)
                    pixelInfo = struct.pack(">II", 8192, 256)
                    ddsSize = (Width * Height * 8) // 8
                    
                    ddsData = bs.readBytes(ddsSize)
                else:
                    print("Unknown format {}".format(Format))
                    return 0
                gtxTex += type
                gtxTex += (b'\x00\x00\x00\x00\x00\x00\x00\x01')
                gtxTex += struct.pack(">I", ddsSize)
                gtxTex += (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\x0D\x00\x00')
                gtxTex += pixelInfo
                gtxTex += (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x01\x02\x03\x1F\xF8\x7F\x21')
                gtxTex += gtxFmt
                gtxTex += (b'\x06\x88\x84\x00\x00\x00\x00\x00\x80\x00\x00\x10\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x0B')
                gtxTex += struct.pack(">I", ddsSize)
                gtxTex += (b'\x00\x00\x00\x00\x00\x00\x00\x00')
                gtxTex += ddsData
                gtxTex += (b'\x42\x4C\x4B\x7B\x00\x00\x00\x20\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
                ddsName = rapi.getLocalFileName(rapi.getInputName())
                dstFilePath = rapi.getDirForFilePath(rapi.getInputName()) + ddsName + ".gtx"
                newfile = open(dstFilePath,'wb')
                newfile.write(gtxTex)
                newfile.close()
                subprocess.Popen([noesis.getScenesPath() + 'TexConv2.bat', dstFilePath]).wait()
                try:
                        texData = rapi.loadIntoByteArray(dstFilePath + ".dds")
                        texture = rapi.loadTexByHandler(texData, ".dds")
                except:
                    texture = NoeTexture(str(len(self.texList)), 0, 0, None, noesis.NOESISTEX_RGBA32)
                texture.name = ddsName
                texList.append(texture)
            else:
                print("3DS MT Framework Textures not supported! Use Kukkii from the Kuriimu suite.")

        return 1
    elif magic == 542655828:
        #MHXR Mobile MT
        Version = bs.readBits(16)
        unkn1 = bs.readBits(8)
        Format = bs.readBits(8)
        MipMapCount = bs.readBits(6)
        R1 = bs.readBits(2)
        unused1 = bs.readBits(24)
        Width = bs.readBits(13)
        Height = bs.readBits(13)
        unkn4 = bs.readBits(2)
        unkn5 = bs.readBits(4) #these could be part of the same thing, but I doubt it
        assert Version == 9 #according to https://github.com/IcySon55/Kuriimu/blob/master/src/image/image_mt/MobileMTTexSupport.cs this whole structure should be mostly inverted, so unless this file is somehow Big Endian, we need version check
        #noticed that any other version of the format also uses version 9, so there will be problems
        #also, only works with iOS textures. Android uses BC but has some issues within the data. The two are identical header-wise
        #even Gunpla Warfare uses version 9, so look out for that as well apparently
        if Format == 4:
            #PVRTC4
            length = int(Width*Height/2)
            pix = rapi.imageDecodePVRTC(bs.readBytes(length), Width, Height, 4)
        elif Format ==0x10:
            #ABGR16
            length = Width*Height*2
            pix = rapi.imageDecodeRaw(bs.readBytes(length), Width, Height, "a4b4g4r4")
        elif Format == 0x20:
            #ABGR32
            length = Width*Height*4
            pix = rapi.imageDecodeRaw(bs.readBytes(length), Width, Height, "a8b8g8r8")
        else:
            print("Invalid Format {}".format(Format))
            return 0
        texList.append(NoeTexture("MobileMTFTex", Width, Height, pix, noesis.NOESISTEX_RGBA32))
        return 1
    else:
        return 0

