import struct

def readUInt(file):
    return struct.unpack("I",file.read(4))[0]

def readUInt64(file):
    return struct.unpack("Q",file.read(8))[0]

def readNullTerminatedString(file):
    currentByte = file.read(1)
    string = bytearray()
    while(1):
        if currentByte == b'':
            return ""
            #this is python's method of EOF
        elif currentByte == b'\x00':
            return string.decode('utf-8')
        else:
            string.extend(currentByte)
        currentByte = file.read(1)

def readAtOffset(file,offset):
    #print(offset)
    retAdd = file.tell()
    file.seek(offset)
    string = readNullTerminatedString(file)
    file.seek(retAdd)
    return string

class LabelEntry:
    def __init__(self,offset,sectionID):
        self.offset = offset
        self.sectionID = sectionID

def ReadGMDv2(inFile):
    assert inFile.read(4) == b"GMD\x00"
    assert readUInt(inFile) == 66306
    inFile.read(4) #language
    inFile.read(8) #hash + null
    LabelCount = readUInt(inFile)
    SectionCount = readUInt(inFile)
    LabelSize = readUInt(inFile)
    SectionSize = readUInt(inFile)
    NameSize = readUInt(inFile)
    Name = readNullTerminatedString(inFile)
    entries = list()
    for _ in range(LabelCount):
        sectionID = readUInt(inFile)
        inFile.read(12)#2 hashes (likely one for label and section) and CDCDCDCD filler
        LabelOffset = readUInt64(inFile)
        inFile.read(8)#"ListLink"
        entries.append(LabelEntry(LabelOffset,sectionID))
    for _ in range(0x100):
        inFile.read(8)#legitimately don't understand what these are for
    labelOffset = inFile.tell()
    inFile.seek(labelOffset+LabelSize)
    sections = list()
    for _ in range(SectionCount):
        sections.append(readNullTerminatedString(inFile))
    GMDOut = dict()
    for label in entries:
        GMDOut[readAtOffset(inFile,labelOffset+label.offset)] = sections[label.sectionID]
    
    return GMDOut

