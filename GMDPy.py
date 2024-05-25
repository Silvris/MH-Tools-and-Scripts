import struct
import sys

BIGENDIAN = False

def readUInt(file):
    if BIGENDIAN:
        return struct.unpack(">I",file.read(4))[0]
    else:
        return struct.unpack("I", file.read(4))[0]

def readUInt64(file):
    if BIGENDIAN:
        return struct.unpack("Q",file.read(8))[0]
    else:
        return struct.unpack(">Q", file.read(8))[0]

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
    magic = inFile.read(4)
    if BIGENDIAN:
        assert magic == b"DMG\x00"
    else:
        assert magic == b"GMD\x00"
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


if __name__ == "__main__":
    for i, path in enumerate(sys.argv):
        if i == 0:
            continue
        gmd = ReadGMDv2(open(path, 'rb'))
        output = open(path.replace(".gmd", ".csv"), 'w')
        output.writelines(["Key,Data\n", *[f"{key},{data}\n" for key, data in gmd.items()]])
        output.close()