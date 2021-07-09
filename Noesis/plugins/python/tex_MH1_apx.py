from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register("Monster Hunter PS2 Decompressed Textures", ".apx")
    noesis.setHandlerTypeCheck(handle, texCheckType)
    noesis.setHandlerLoadRGBA(handle, texLoadAPX)
    noesis.setHandlerWriteRGBA(handle, texWriteAPX)
    handle = noesis.register("Monster Hunter PS2 Decompressed Texture Archive", ".ftex")
    noesis.setHandlerTypeCheck(handle, texCheckType)
    noesis.setHandlerLoadRGBA(handle, texLoadFTEX)
    noesis.logPopup()
    return 1

def texCheckType(data):
    return 1

def readAPX(data, off):
    bs = NoeBitStream(data)
    bs.seek(off)
    fileSize = bs.readUInt()
    totalPixels = bs.readUInt()
    paletteLength = bs.readUInt()
    bitDepth = bs.readUShort()
    width = bs.readUShort()
    height = bs.readUShort()
    paletteIndex = bs.readUShort()
    specialUnkn = bs.readUInt()
    NULL0 = bs.readUInt64()
    if bitDepth == 4:
        ImageData = []
        for i in range(totalPixels*2):
            ImageData.append(bs.readBits(4))
    else:
        ImageData = bs.readBytes(totalPixels)
    paletteData = bs.readBytes(paletteLength)

    #now to convert paletted data into RGBA
    RGBAData = []
    for i in range(len(ImageData)):
        RGBAData.append(paletteData[ImageData[i]*4])
        RGBAData.append(paletteData[(ImageData[i]*4)+1])
        RGBAData.append(paletteData[(ImageData[i]*4)+2])
        RGBAData.append(paletteData[(ImageData[i]*4)+3])
    return width, height, bytearray(RGBAData)

def texLoadAPX(data, texList):
    width, height, pix = readAPX(data,0)
    texList.append(NoeTexture("MHTex", width, height, pix, noesis.NOESISTEX_RGBA32))
    return 1

def texLoadFTEX(data, texList):
    bs = NoeBitStream(data)
    imageCount = bs.readUInt()
    imageOff = []
    imageSize = []
    for i in range(imageCount):
        imageOff.append(bs.readUInt())
        imageSize.append(bs.readUInt())
    print(bs.tell())
    for i in range(imageCount):
        width, height, pix = readAPX(data,imageOff[i])
        texList.append(NoeTexture("MHTex", width, height, pix, noesis.NOESISTEX_RGBA32))
    return 1

def compareColor(color1, color2):
    if(color1[0]==color2[0]):
        if(color1[1]==color2[1]):
            if(color1[2]==color2[2]):
                if(color1[3]==color2[3]):
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False

def texWriteAPX(data, width, height, bs):
    #first generate palette and pixel arrays
    paletteColors = [] #there might be an upper limit of 256 colors for this, but I do not actually know if that is the case
    pixels = []
    print(int(len(data)/4))
    for i in range(int(len(data)/4)):
        paletteColor = [data[(i*4)],data[(i*4)+1],data[(i*4)+2],data[(i*4)+3]]
        paletteExists = False
        for i in range(len(paletteColors)):
            if(compareColor(paletteColor,paletteColors[i])):
                paletteExists = True
                paletteIndex = i
        if(paletteExists):
            pixels.append(paletteIndex)
        else:
            paletteColors.append(paletteColor)
            paletteIndex = len(paletteColors)-1
            pixels.append(paletteIndex)
    #check size of palette colors, since the 256 limit does actually exist
    #because I forgot that a byte can only be 256 different values
    if(len(paletteColors) > 256):
        print("Too many colors! Reduce bit depth to 8 externally.")
        return 0
    #so now we should be able to write our file
    fileSize = 52 + len(pixels) + (len(paletteColors)*4)
    bs.writeInt(fileSize)
    bs.writeInt(len(pixels))
    bs.writeInt(len(paletteColors)*4)
    bs.writeShort(8) #just gonna go 8bpp
    bs.writeShort(width)
    bs.writeShort(height)
    bs.writeShort(1) #apparently it is always 1, might play around with it later
    bs.writeInt(65568)
    bs.writeInt64(0)
    bs.writeBytes(bytearray(pixels))
    for i in range(len(paletteColors)):
        bs.writeBytes(bytearray(paletteColors[i]))
    return 1