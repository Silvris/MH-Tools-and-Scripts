import zlib
import os
import struct
import sys
from Crypto.Cipher import Blowfish

fileExts = dict()

key = b"QZHaM;-5:)dV#"
cipher = Blowfish.new(key,Blowfish.MODE_ECB)

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def endianness_reversal(data):
    return b''.join(map(lambda x: x[::-1],chunks(data, 4)))

def readUShort(file):
    return struct.unpack("H",file.read(2))[0]

def writeUShort(file,val):
    file.write(struct.pack("H",val))

def readUInt(file):
    return struct.unpack("I",file.read(4))[0]

def jamcrc(string):
    return (zlib.crc32(str(string).encode()) ^ 0xffffffff) & 0x7fffffff

def removeNulls(array):
    arr = bytearray()
    for i in range(len(array)):
        if array[i] != 0x00:
            arr.append(array[i])
    return bytes(arr)

def GenerateFileExtDict():
    #cfid, fppgr, bemtp, dfd, mkr, sdm, ecpd
    #gonna need a full filetype dump once exe is examined
    #if nativePC works like World, could just grab a list from procmon
    fileExts[jamcrc("rAIFSM")] = ".xfsa" #aka .fsm
    fileExts[jamcrc("rCameraList")] = ".lcm"
    fileExts[jamcrc("rCharacter")] = ".xfsc"
    fileExts[jamcrc("rCollision")] = ".sbc"
    fileExts[jamcrc("rColorLinkColor")] = ".clc"
    fileExts[jamcrc("rColorLinkInfo")] = ".cli"
    fileExts[jamcrc("rEffectAnim")] = ".ean"
    fileExts[jamcrc("rEffectList")] = ".efl"
    fileExts[jamcrc("rGUI")] = ".gui"
    fileExts[jamcrc("rGUIFont")] = ".gfd"
    fileExts[jamcrc("rGUIMessage")] = ".gmd"
    fileExts[jamcrc("rHit2D")] = ".xfsh"
    fileExts[jamcrc("rLayoutParameter")] = ".xfsl"
    fileExts[jamcrc("rModel")] = ".mod"
    fileExts[jamcrc("rMotionList")] = ".lmt"
    fileExts[jamcrc("rPartsVisibleInfo")] = ".pvi"
    fileExts[jamcrc("rPropParam")] = ".prp"
    fileExts[jamcrc("rScheduler")] = ".sdl"
    fileExts[jamcrc("rSoundBank")] = ".sbkr"
    fileExts[jamcrc("rSoundRequest")] = ".srqr"
    fileExts[jamcrc("rSoundSourceADPCM")] = ".lopus" #this might be different on PC, as lopus is a Switch-exclusive ADPCM
    fileExts[jamcrc("rTexture")] = ".tex"
    fileExts[jamcrc("rSoundGuiSe")] = ".sgs"
    fileExts[jamcrc("rSoundSeParamOffsetControl")] = ".spoc"
    fileExts[jamcrc("rSoundPelTiedSe")] = ".pts"
    fileExts[jamcrc("rSoundAreaReverb")] = ".sar"
    fileExts[jamcrc("rSoundSystemSetting")] = ".sss"
    fileExts[jamcrc("rVirtualJoint")] = ".vjr"

    #remainder of list stolen from Kuriimu source, almost definitely not all used by Stories, will be removed with proper list
    fileExts[0x22FA09] = ".hpe"
    fileExts[0x26E7FF] = ".ccl"
    fileExts[0x86B80F] = ".plexp"
    fileExts[0xFDA99B] = ".ntr"
    fileExts[0x2358E1A] = ".spkg"
    fileExts[0x2373BA7] = ".spn"
    fileExts[0x2833703] = ".efs"
    fileExts[0x315E81F] = ".sds"
    fileExts[0x437BCF2] = ".grw"
    fileExts[0x4B4BE62] = ".tmd"
    fileExts[0x525AEE2] = ".wfp"
    fileExts[0x5A36D08] = ".qif"
    fileExts[0x69A1911] = ".olp"
    fileExts[0x737E28B] = ".rst"
    fileExts[0x7437CCE] = ".base"
    fileExts[0x79B5F3E] = ".pci"
    fileExts[0x7B8BCDE] = ".fca"
    fileExts[0x7F768AF] = ".gii"
    fileExts[0x89BEF2C] = ".sap"
    fileExts[0xA74682F] = ".rnp"
    fileExts[0xC4FCAE4] = ".PlDefendParam"
    fileExts[0xD06BE6B] = ".tmn"
    fileExts[0xECD7DF4] = ".scs"
    fileExts[0x11C35522] = ".gr2"
    fileExts[0x12191BA1] = ".epv"
    fileExts[0x12688D38] = ".pjp"
    fileExts[0x12C3BFA7] = ".cpl"
    fileExts[0x133917BA] = ".mss"
    fileExts[0x14428EAE] = ".gce"
    fileExts[0x15302EF4] = ".lot"
    fileExts[0x157388D3] = ".itl"
    fileExts[0x15773620] = ".nmr"
    fileExts[0x167DBBFF] = ".stq"
    fileExts[0x1823137D] = ".mlm"
    fileExts[0x19054795] = ".nnl"
    fileExts[0x199C56C0] = ".ocl"
    fileExts[0x1B520B68] = ".zon"
    fileExts[0x1BCC4966] = ".srq"
    fileExts[0x1C2B501F] = ".atr"
    fileExts[0x1EB3767C] = ".spr"
    fileExts[0x2052D67E] = ".sn2"
    fileExts[0x215896C2] = ".statusparam"
    fileExts[0x2282360D] = ".jex"
    fileExts[0x22948394] = ".gui"
    fileExts[0x22B2A2A2] = ".PlNeckPos"
    fileExts[0x232E228C] = ".rev"
    fileExts[0x241F5DEB] = ".tex"
    fileExts[0x242BB29A] = ".gmd"
    fileExts[0x257D2F7C] = ".swm"
    fileExts[0x2749C8A8] = ".mrl"
    fileExts[0x271D08FE] = ".ssq"
    fileExts[0x272B80EA] = ".prp"
    fileExts[0x276DE8B7] = ".e2d"
    fileExts[0x2A37242D] = ".gpl"
    fileExts[0x2A4F96A8] = ".rbd"
    fileExts[0x2B0670A5] = ".map"
    fileExts[0x2B303957] = ".gop"
    fileExts[0x2B40AE8F] = ".equ"
    fileExts[0x2CE309AB] = ".joblvl"
    fileExts[0x2D12E086] = ".srd"
    fileExts[0x2D462600] = ".gfd"
    fileExts[0x30FC745F] = ".smx"
    fileExts[0x312607A4] = ".bll"
    fileExts[0x31B81AA5] = ".qr"
    fileExts[0x325AACA5] = ".shl"
    fileExts[0x32E2B13B] = ".edp"
    fileExts[0x33B21191] = ".esp"
    fileExts[0x354284E7] = ".lvl"
    fileExts[0x358012E8] = ".vib"
    fileExts[0x36019854] = ".bed"
    fileExts[0x39A0D1D6] = ".sms"
    fileExts[0x39C52040] = ".lcm"
    fileExts[0x3A947AC1] = ".cql"
    fileExts[0x3B350990] = ".qsp"
    fileExts[0x3BBA4E33] = ".qct"
    fileExts[0x3D97AD80] = ".amr"
    fileExts[0x3E356F93] = ".stc"
    fileExts[0x3E363245] = ".chn"
    fileExts[0x3FB52996] = ".imx"
    fileExts[0x4046F1E1] = ".ajp"
    fileExts[0x437662FC] = ".oml"
    fileExts[0x4509FA80] = ".itemlv"
    fileExts[0x456B6180] = ".cnsshake"
    fileExts[0x472022DF] = ".AIPlActParam"
    fileExts[0x48538FFD] = ".ist"
    fileExts[0x48C0AF2D] = ".msl"
    fileExts[0x49B5A885] = ".ssc"
    fileExts[0x4B704CC0] = ".mia"
    fileExts[0x4C0DB839] = ".sdl"
    fileExts[0x4CA26828] = ".bmse"
    fileExts[0x4E397417] = ".ean"
    fileExts[0x4E44FB6D] = ".fpe"
    fileExts[0x4EF19843] = ".nav"
    fileExts[0x4FB35A95] = ".aor"
    fileExts[0x50F3D713] = ".skl"
    fileExts[0x5175C242] = ".geo2"
    fileExts[0x51FC779F] = ".sbc"
    fileExts[0x522F7A3D] = ".fcp"
    fileExts[0x52DBDCD6] = ".rdd"
    fileExts[0x535D969F] = ".ctc"
    fileExts[0x5802B3FF] = ".ahc"
    fileExts[0x58A15856] = ".mod"
    fileExts[0x59D80140] = ".ablparam"
    fileExts[0x5A61A7C8] = ".fed"
    fileExts[0x5A7FEA62] = ".ik"
    fileExts[0x5B334013] = ".bap"
    fileExts[0x5EA7A3E9] = ".sky"
    fileExts[0x5F36B659] = ".way"
    fileExts[0x5F88B715] = ".epd"
    fileExts[0x60BB6A09] = ".hed"
    fileExts[0x6186627D] = ".wep"
    fileExts[0x619D23DF] = ".shp"
    fileExts[0x628DFB41] = ".gr2s"
    fileExts[0x63747AA7] = ".rpi"
    fileExts[0x63B524A7] = ".ltg"
    fileExts[0x64387FF1] = ".qlv"
    fileExts[0x65B275E5] = ".sce"
    fileExts[0x66B45610] = ".fsm"
    fileExts[0x671F21DA] = ".stp"
    fileExts[0x69A5C538] = ".dwm"
    fileExts[0x6D0115ED] = ".prt"
    fileExts[0x6D5AE854] = ".efl"
    fileExts[0x6DB9FA5F] = ".cmc"
    fileExts[0x6EE70EFF] = ".pcf"
    fileExts[0x6F302481] = ".plw"
    fileExts[0x6FE1EA15] = ".spl"
    fileExts[0x72821C38] = ".stm"
    fileExts[0x73850D05] = ".arc"
    fileExts[0x754B82B4] = ".ahs"
    fileExts[0x76820D81] = ".lmt"
    fileExts[0x76DE35F6] = ".rpn"
    fileExts[0x7808EA10] = ".rtex"
    fileExts[0x7817FFA5] = ".fbik_human"
    fileExts[0x7AA81CAB] = ".eap"
    fileExts[0x7BEC319A] = ".sps"
    fileExts[0x7DA64808] = ".qmk"
    fileExts[0x7E1C8D43] = ".pcs"
    fileExts[0x7E33A16C] = ".spc"
    fileExts[0x7E4152FF] = ".stg"
    fileExts[0x17A550D] = ".lom"
    fileExts[0x253F147] = ".hit"
    fileExts[0x39D71F2] = ".rvt"
    fileExts[0xDADAB62] = ".oba"
    fileExts[0x10C460E6] = ".msg"
    fileExts[0x176C3F95] = ".los"
    fileExts[0x19A59A91] = ".lnk"
    fileExts[0x1BA81D3C] = ".nck"
    fileExts[0x1ED12F1B] = ".glp"
    fileExts[0x1EFB1B67] = ".adh"
    fileExts[0x2447D742] = ".idm"
    fileExts[0x266E8A91] = ".lku"
    fileExts[0x2C4666D1] = ".smh"
    fileExts[0x2DC54131] = ".cdf"
    fileExts[0x30ED4060] = ".pth"
    fileExts[0x36E29465] = ".hkx"
    fileExts[0x38F66FC3] = ".seg"
    fileExts[0x430B4FF4] = ".ptl"
    fileExts[0x46810940] = ".egv"
    fileExts[0x4D894D5D] = ".cmi"
    fileExts[0x4E2FEF36] = ".mtg"
    fileExts[0x4F16B7AB] = ".hri"
    fileExts[0x50F9DB3E] = ".bfx"
    fileExts[0x5204D557] = ".shp"
    fileExts[0x538120DE] = ".eng"
    fileExts[0x557ECC08] = ".aef"
    fileExts[0x585831AA] = ".pos"
    fileExts[0x5898749C] = ".bgm"
    fileExts[0x60524FBB] = ".shw"
    fileExts[0x60DD1B16] = ".lsp"
    fileExts[0x758B2EB7] = ".cef"
    fileExts[0x7D1530C2] = ".sngw"
    fileExts[0x46FB08BA] = ".bmt"
    fileExts[0x285A13D9] = ".vzo"
    fileExts[0x4323D83A] = ".stex"
    fileExts[0x6A5CDD23] = ".occ"

def getExtension(hash):
    if hash in fileExts:
        return fileExts[hash]
    else:
        return "." + str(hex(hash)[2:])

class Entry:
    def __init__(self,name,extHash,compSize,decompSize,offset):
        self.name = name
        self.extHash = extHash
        self.compSize = compSize
        self.decompSize = decompSize
        self.offset = offset

def extractARC(inFile,fileCount):
    entries = []
    for _ in range(fileCount):
        nameArray = inFile.read(128)
        nameArray = removeNulls(nameArray)
        eName = nameArray.decode("utf-8")
        eExt = readUInt(inFile)
        eComp = readUInt(inFile)
        eUncomp = readUInt(inFile)
        eOffset = readUInt(inFile)
        entries.append(Entry(eName,eExt,eComp,eUncomp,eOffset))
    for entry in entries:
        #deal with compression first
        inFile.seek(entry.offset)
        cFile = inFile.read(entry.compSize)
        dFile = zlib.decompress(cFile)
        #create name
        basePath = inFile.name.split('.')[0]+'/'
        dirPath = os.path.split(entry.name)[0]
        #print(dirPath, 1)
        if(dirPath != ''):
            os.makedirs(basePath+dirPath,exist_ok=True)
        finalName = basePath + entry.name + getExtension(entry.extHash)
        oFile = open(finalName,'wb')
        oFile.write(dFile)
        oFile.close()

def readARCC(inFile,fileCount):
    encFile = inFile.read()
    decFile = endianness_reversal(cipher.decrypt(endianness_reversal(encFile)))
    outFile = open(inFile.name+"-decrypt.arc",'wb')
    outFile.write(b"ARC\x00")
    writeUShort(outFile,7)
    writeUShort(outFile,fileCount)
    outFile.write(decFile)
    outFile.close()

def readARC(inFile):
    magic = inFile.read(4)
    assert readUShort(inFile) == 7
    fileCount = readUShort(inFile)
    if magic == b"ARCC":
        readARCC(inFile,fileCount)
    elif magic == b"ARC\x00":
        extractARC(inFile,fileCount)

if __name__ == "__main__":
    GenerateFileExtDict()
    for i, arg in enumerate(sys.argv):
        if i > 0:
            readARC(open(arg,'rb'))