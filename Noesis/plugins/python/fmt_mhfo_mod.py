from inc_noesis import *
import rapi
import fnmatch
import os

#Originally by MHVuze, updated by Silvris

objectcount = 0
vertexoffsets = list(); vertexcounts = list()
faceoffsets = list(); faceblockcounts = list(); faceblocksubcounts = list()
uvoffsets = list(); normalsoffsets = list(); tanoffsets = list()
weightoffsets = list(); boneoffsets = list()
materialoffsets =list(); matmapoffsets = list()
matoffsets = list(); texoffsets = list()
coloroffsets = list()
materialOff = 0
materialCount = 0
textureOff = 0
textureCount = 0

#this is able to write out to the fmod format, however it should be noted that this is incredibly experimental and very much prone to not working in games other than Frontier (and crashing in Frontier)

def registerNoesisTypes():
    handle = noesis.register("Monster Hunter Frontier Models", ".fmod")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadFMOD)
    noesis.setTypeSharedModelFlags(handle,noesis.NMSHAREDFL_WANTTANGENTS4R)
    noesis.setHandlerWriteModel(handle, noepyWriteFMOD)
    #noesis.addOption(handle, "-fmot", "Load Animations from File", noesis.OPTFLAG_WANTARG) does nothing for now
    noesis.addOption(handle, "-noTex", "Skip Loading textures from PNG", noesis.OPTFLAG_WANTARG)
    noesis.logPopup()
    return 1

FMOD_HEADER = 0x00000001
FMOD_VERSION = 0x00000004
FSKL_HEADER = 0xC0000000

def noepyCheckType(data):
    if len(data) < 8:
        return 0
    bs = NoeBitStream(data)

    if bs.readInt() != FMOD_HEADER:
        return 0
    if bs.readInt() != FMOD_VERSION:
        return 0

    return 1

def processBlock(btype, bcount, bsize, bs):
    if btype == 0x20000:
        print("Unknown block of type 0x{:X} with {} entries. Size: 0x{:X}. Data offset: 0x{:X}".format(btype, bcount, bsize, bs.tell()))
        print("Byte 1: {}, Byte 2: {}, Byte 3: {}, Byte 4: {}".format(bs.readByte(), bs.readByte(), bs.readByte(), bs.readByte()))
    elif btype == 2:
        global objectcount
        objectcount = bcount
        #print("Main block with {} objects. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, bs.tell()))
    elif btype == 4:
        print("Object block with {} sub blocks. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, bs.tell()))
    elif btype == 5:
        pos = bs.tell()
        #print("Face block with {} sub blocks. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        faceoffsets.append(pos)
        faceblockcounts.append(bcount)
    elif btype == 0x030000:
        pos = bs.tell()
        #print("Face index buffer type 0x030000 with {} tristrips. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        bs.readBytes(bsize - 12) # skip
    elif btype == 0x040000:
        pos = bs.tell()
        #print("Face index buffer type 0x040000 with {} tristrips. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        bs.readBytes(bsize - 12) # skip
    elif btype == 0x050000:
        pos = bs.tell()
        #print("Material remap table with {} materials. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        materialoffsets.append(pos)
        bs.readBytes(bsize - 12)  # skip
    elif btype == 0x060000:
        pos = bs.tell()
        #print("Material index buffer with {} tristrips. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        matmapoffsets.append(pos)
        bs.readBytes(bsize - 12)  # skip
    elif btype == 0x070000:
        pos = bs.tell()
        #print("Vertex buffer with {} vertices. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        vertexoffsets.append(pos)
        vertexcounts.append(bcount)
        bs.readBytes(bsize - 12) # skip
    elif btype == 0x080000:
        pos = bs.tell()
        #print("Normals buffer with {} normals. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        normalsoffsets.append(pos)
        bs.readBytes(bsize - 12) # skip
    elif btype == 0x0A0000:
        pos = bs.tell()
        #print("UV buffer with {} UV mappings. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        uvoffsets.append(pos)
        bs.readBytes(bsize - 12) # skip
    elif btype == 0x0B0000:
        pos = bs.tell()
        #print("Vertex Color buffer with {} vertex mappings. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        coloroffsets.append(pos)
        bs.readBytes(bsize - 12) # skip
    elif btype == 0x0C0000:
        pos = bs.tell()
        #print("Weight buffer with {} weight mappings. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        weightoffsets.append(pos)
        bs.readBytes(bsize - 12) # skip
    elif btype == 0x100000:
        pos = bs.tell()
        #print("Bone remap table with {} bones. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount, bsize, pos))
        boneoffsets.append(pos)
        bs.readBytes(bsize - 12) # skip
    elif btype == 0x120000:
        pos = bs.tell()
        #print("Tangents buffer with {} tangents. Size: 0x{:X}. Data offset: 0x{:X}".format(bcount,bsize,pos))
        tanoffsets.append(pos)
        bs.readBytes(bsize - 12) # skip
    elif btype == 0x9:
        global materialOff, materialCount
        pos = bs.tell()
        #print("Material block of type 0x{:x} with {} materials. Size: 0x{:X}. Data offset: 0x{:X}".format(btype, bcount,bsize, bs.tell()))
        materialOff = pos
        materialCount = bcount
        bs.readBytes(bsize-12) # skip
    elif btype == 0xA:
        global textureOff, textureCount
        pos = bs.tell()
        #print("Texture block of type 0x{:x} with {} textures. Size: 0x{:X}. Data offset: 0x{:X}".format(btype, bcount,bsize, bs.tell()))
        textureOff = pos
        textureCount = bcount
        bs.readBytes(bsize-12) # skip
    else:
        print("Unknown block of type 0x{:X} with {} entries. Size: 0x{:X}. Data offset: 0x{:X}".format(btype, bcount, bsize, bs.tell()))
        bs.readBytes(bsize - 12) # skip

def createMaterialTexList(bs,to,tc,mo,mc):

    # Add materials and textures
    texList = []
    matList = []
    rapi.rpgSetMaterial("test")
    texIDs = []
    matDiffs = []
    matNorm = []
    matSpecs = []
    #read textures first
    bs.seek(to)
    for i in range(tc):
        head1 = bs.readUInt()
        head2 = bs.readUInt()
        blockS = bs.readUInt()
        imageID = bs.readUInt()
        width = bs.readUInt()
        height = bs.readUInt()
        bs.readBytes(244)
        texIDs.append(imageID)

    bs.seek(mo)
    for i in range(mc):
        # this is all probably important but not that important for reading
        bs.readUInt()
        bs.readUInt()
        bs.readUInt()
        bs.readFloat()
        bs.readFloat()
        bs.readFloat()
        bs.readFloat()
        bs.readFloat()
        bs.readFloat()
        bs.readFloat()
        bs.readFloat()
        bs.readFloat()
        bs.readFloat()
        bs.readFloat()
        bs.readUInt()
        bs.readFloat()
        texCount = bs.readUInt()
        bs.readBytes(200)
        texLinks = []
        for _ in range(texCount):
            texLinks.append(bs.readUInt())
        if(len(texLinks) > 0):
            matDiffs.append(texIDs[texLinks[0]])
        else:
            matDiffs.append(None)
        if (len(texLinks) > 1):
            matNorm.append(texIDs[texLinks[1]])
            matSpecs.append(texIDs[texLinks[2]])
        else:
            matNorm.append(None)
            matSpecs.append(None)

    skipTex = False
    if noesis.optWasInvoked("-noTex"):
        print("Skipping Texture Loading")
        skipTex = True
    else:
        pngs = []
        for root, dirnames, filenames in os.walk(noesis.getSelectedDirectory()):
            for filename in fnmatch.filter(filenames, '*.png'):
                pngs.append(os.path.join(root, filename))
            
        if (len(pngs) == 0):
            for root, dirnames, filenames in os.walk(os.path.dirname(noesis.getSelectedDirectory())):
                for filename in fnmatch.filter(filenames, '*.png'):
                    pngs.append(os.path.join(root, filename))
        
        for i in range(len(pngs)):
            path = pngs[i]
            tex = rapi.loadExternalTex(path)
            tex.name = pngs[i]
            texList.append(tex)


    for i in range(mc):
        material = NoeMaterial("Material.%03i"%i, "")
        if matDiffs[i] != None and skipTex == False:
            material.setTexture(pngs[matDiffs[i]])
        if matNorm[i] != None and skipTex == False:
            material.setNormalTexture(pngs[matNorm[i]])
        if matSpecs[i] != None and skipTex == False:
            material.setSpecularTexture(pngs[matSpecs[i]])
        material.setFlags(noesis.NMATFLAG_SPEC_UV1,0) # second arg is shading off bool
        matList.append(material)
    matoffsets = list()
    texoffsets = list()
    
    return texList, matList
        

def noepyLoadFMOD(data, mdlList):
    bs = NoeBitStream(data)
    if bs.readInt() != FMOD_HEADER:
        return 0
    if bs.readInt() != FMOD_VERSION:
        return 0

    pos = 0
    
    filesize = bs.readUInt() # total
    
    typeBlock = bs.readInt()
    countBlock = bs.readInt()
    sizeBlock = bs.readInt()
    processBlock(typeBlock, countBlock, sizeBlock, bs)
    
    while pos < filesize:
        for i in range(countBlock):
            pos = bs.tell()
            if pos < filesize:
                typeBlock = bs.readInt()
                countBlock = bs.readInt()
                sizeBlock = bs.readInt()
                processBlock(typeBlock, countBlock, sizeBlock, bs)

    ctx = rapi.rpgCreateContext()
    global textureOff, textureCount, materialOff, materialCount
    texList, matList = createMaterialTexList(bs,textureOff,textureCount,materialOff,materialCount)
    for meshi in range(objectcount):
        # Add vertices
        bs.seek(vertexoffsets[meshi])
        vertexbuffer = bs.readBytes(vertexcounts[meshi] * 12)
        rapi.rpgBindPositionBufferOfs(vertexbuffer, noesis.RPGEODATA_FLOAT, 12, 0)
        
        # Add normals
        global normalsoffsets
        bs.seek(normalsoffsets[meshi] - 8)
        normalscount = bs.readInt()
        bs.readInt() # skip
        normalsbuffer = bs.readBytes(normalscount * 12)
        rapi.rpgBindNormalBufferOfs(normalsbuffer, noesis.RPGEODATA_FLOAT, 12, 0)
        
        # Add tangents (is it necessary?)
        global tanoffsets
        if len(tanoffsets) > 0:
            bs.seek(tanoffsets[meshi] - 8)
            tangentcount = bs.readInt()
            bs.readInt() #blocksize
            tangentbuffer = bs.readBytes(tangentcount*16)
            rapi.rpgBindTangentBuffer(tangentbuffer, noesis.RPGEODATA_FLOAT, 16)

        # Add UVs
        bs.seek(uvoffsets[meshi] - 8)
        uvcount = bs.readInt()
        bs.readInt() # skip
        uvbuffer = bs.readBytes(uvcount * 8)
        rapi.rpgBindUV1BufferOfs(uvbuffer, noesis.RPGEODATA_FLOAT, 8, 0)

        # Add Vertex Color (possible)
        global coloroffsets
        bs.seek(coloroffsets[meshi] - 8)
        colorcount = bs.readUInt()
        bs.readUInt() #blocksize
        colorbuffer = bs.readBytes(colorcount*16)
        rapi.rpgBindColorBuffer(colorbuffer, noesis.RPGEODATA_FLOAT, 16, 4)

        # Add Bone Remap
        global boneoffsets
        if(len(boneoffsets) > 0):
            bs.seek(boneoffsets[meshi] - 8)
            boneCount = bs.readInt()
            bs.readInt() #blockSize
            bones = list()
            for i in range(boneCount):
                bone = bs.readInt()
                bones.append(bone)
            rapi.rpgSetBoneMap(bones)
        else:
            #there's no bone remap
            dummy = 1+1 #just to please noesis
            
        
        # Add Weights
        global weightoffsets
        if len(weightoffsets) > 0:
            weightValues = bytes()
            weightBones = bytes()
            bs.seek(weightoffsets[meshi] - 8)
            weightcount = bs.readInt()
            bs.readInt() #blocksize
            for i in range(weightcount):
                paircount = bs.readInt()
                for j in range(paircount):
                    weightBone = bs.readUInt()
                    weightValue = bs.readFloat()
                    weightBones += noePack("i", weightBone)
                    weightValues += noePack("f", weightValue/100)
                for k in range(4-paircount):
                    weightBone = 0
                    weightValue = 0.0
                    weightBones += noePack("i", weightBone)
                    weightValues += noePack("f", weightValue)
            rapi.rpgBindBoneIndexBufferOfs(weightBones,noesis.RPGEODATA_UINT, 16, 0, 4)
            rapi.rpgBindBoneWeightBufferOfs(weightValues,noesis.RPGEODATA_FLOAT, 16, 0, 4)
        
        # Add skeleton
        bins = []
        for root, dirnames, filenames in os.walk(noesis.getSelectedDirectory()):
            for filename in fnmatch.filter(filenames, '*.fskl'):
                bins.append(os.path.join(root, filename))
        
        boneList = []
        if len(bins) > 0:
            dataSkl = []
            with open(bins[0], mode='rb') as file:
                dataSkl = file.read()
                bsSkl = NoeBitStream(dataSkl)
                if bsSkl.readUInt() == FSKL_HEADER:
                    # slightly adapted from https://github.com/m2jean/mhfu-ios-pmo-plugin
                    blockCount = bsSkl.readUInt() - 1
                    #print("Skeleton file with {} sections found.".format(blockCount))
                    filesizeSkl = bsSkl.readUInt()
                    
                    blockType = bsSkl.readUInt()
                    blockCount1 = bsSkl.readUInt()
                    blockLen = bsSkl.readUInt()
                    for i in range(blockCount1):
                        dummy = bsSkl.readUInt()
                    
                    
                    
                    sklidxList = []
                    posList = []
                    for i in range(blockCount):
                        blockTyp = bsSkl.readUInt()
                        assert blockTyp == 0x40000001 or 0x40000002
                        assert bsSkl.readUInt() == 0x1
                        assert bsSkl.readUInt() == 0x10C
                        nodei = bsSkl.readInt()
                        parent = bsSkl.readInt()
                        lchild = bsSkl.readInt()
                        rsibling = bsSkl.readInt()

                        bsSkl.readBytes(4*8)
                        mat43 = []
                        for _ in range(3):
                            mat43.append(bsSkl.readFloat())
                        bsSkl.readFloat()
                        bsSkl.readBytes(16*12)

                        if parent == -1:
                            pos = (0,0,0)
                        else:
                            pos = posList[parent].vec3
                            sklidxList += (nodei, parent, parent)
                        
                        transform = list(pos)
                        transform[0] += mat43[0]
                        transform[1] += mat43[1]
                        transform[2] += mat43[2]
                        #print(mat43, transform)
                        posList.append(NoeVec3(transform))
                        
                        finMatrix = NoeQuat().toMat43()
                        finMatrix[3] = NoeVec3(transform)
                        boneList.append(NoeBone(i, "Bone.%03i"%i, finMatrix, None, parent))

        #create material remap and material map
        global materialoffsets, matmapoffsets
        bs.seek(materialoffsets[meshi]-8)
        matRemap = []
        remapCount = bs.readUInt()
        bs.readUInt()
        for _ in range(remapCount):
            matRemap.append(bs.readUInt())

        matMap = []
        bs.seek(matmapoffsets[meshi]-8)
        stripCount = bs.readUInt()
        bs.readUInt()
        for _ in range(stripCount):
            matMap.append(matRemap[bs.readUInt()])


        # Add faces
        bs.seek(faceoffsets[meshi])
        stripIndex = 0
        for j in range(faceblockcounts[meshi]):
            faceblocktype = bs.readInt()
            facesubblockcount = bs.readInt()
            blocksize = bs.readInt()
            
            for i in range(facesubblockcount):
                rapi.rpgSetMaterial("Material.%03i"%matMap[stripIndex])
                facecount = bs.readUInt()
                # not sure what's up with these counts i.e. wf521, em098
                if facecount > 0x80000000:
                    #print("WARNING: Face count is abnormal with {}. Fake adjusted.".format(facecount))
                    facecount = facecount - 0x80000000
                #print("Mesh {} face index {} block count: {} at offset 0x{:X}".format(meshi, i, facecount, bs.tell()))
                facebuffer = bs.readBytes(facecount * 4)
                rapi.rpgCommitTriangles(facebuffer, noesis.RPGEODATA_UINT, facecount, noesis.RPGEO_TRIANGLE_STRIP, 1)
                stripIndex += 1
        
        matRemap = []
        matMap = []
    mdl = rapi.rpgConstructModel()
    mdl.setModelMaterials(NoeModelMaterials(texList, matList))
    mdl.setBones(boneList)
    mdlList.append(mdl)
    rapi.rpgReset()
    
    rapi.rpgClearBufferBinds()
    # reset global variables
    rapi.rpgOptimize()
    global objectcount
    global vertexoffsets; global vertexcounts
    global faceoffsets; global faceblocksubcounts; global faceblockcounts
    global uvoffsets; global tanoffsets
    objectcount = 0
    vertexoffsets = list(); vertexcounts = list()
    faceoffsets = list(); faceblockcounts = list(); faceblocksubcounts = list()
    uvoffsets = list(); normalsoffsets = list(); tanoffsets = list()
    weightoffsets = list(); boneoffsets = list()
    materialoffsets =list(); matmapoffsets = list()
    matoffsets = list(); texoffsets = list()
    coloroffsets = list()
    materialOff = 0
    materialCount = 0
    textureOff = 0
    textureCount = 0
    
    return 1

def WriteFirstBlock(bs):
    bs.writeInt(0x20000)
    bs.writeInt(1)
    bs.writeInt(16)
    bs.writeInt(235409152) #I think this might actually be a hash, but it doesn't actually need it to be correct
    return 16

def writeStrips(strips, type1, bs):
    bs.writeInt(type1)
    bs.writeInt(len(strips))
    stripBlockLen = 12
    off = bs.tell()
    bs.writeInt(0)
    for strip in strips:
        bs.writeInt(len(strip))
        for face in strip:
            bs.writeInt(face)
        stripBlockLen += (4 + (4*len(strip)))
    returnPlace = bs.tell()
    bs.seek(off)
    bs.writeInt(stripBlockLen)
    bs.seek(returnPlace)
    return stripBlockLen

def writeFaceBlock(mesh, bs):
    #export faces
    strips = rapi.createTriStrip(mesh.indices,0xFFFF)
    newStrips = []
    newStrip = []
    for i in range(len(strips)):
        if strips[i] != 65535:
            newStrip.append(strips[i])
        else:
            newStrips.append(newStrip)
            newStrip = []
    strips1 =[]
    strips2 = []
    stripCount = len(newStrips)
    #cursed time
    stripSplit = len(newStrips) - (len(newStrips)/4)
    for i in range(len(newStrips)):
        if i > stripSplit:
            strips1.append(newStrips[i])
        else:
            strips2.append(newStrips[i])
    #I do not know the reason for this, but it is present in every single file
    bs.writeInt(5)
    bs.writeInt(2)
    faceBlockLenOff = bs.tell()
    bs.writeInt(0)
    faceBlockLen = 12
    faceBlockLen += writeStrips(strips1, 0x30000, bs)
    faceBlockLen += writeStrips(strips2, 0x40000, bs)
    returnPlace = bs.tell()
    bs.seek(faceBlockLenOff)
    bs.writeInt(faceBlockLen)
    bs.seek(returnPlace)
    return faceBlockLen, stripCount

def writeMatRemap(mdl,mesh,bs):
    bs.writeInt(0x50000)
    bs.writeInt(1)
    off = bs.tell()
    bs.writeInt(0)
    length = 12
    #this is actually rather simple because of Noesis limitations
    #Noesis does not allow a NoeMesh to have more than one material
    mat = []
    for material in mdl.modelMats.matList:
        if material.name == mesh.matName and mdl.modelMats.matList.index(material) not in mat:
            mat.append(mdl.modelMats.matList.index(material))
    for i in range(len(mat)):
        bs.writeInt(mat[i])
        length += 4
    returnPlace = bs.tell()
    bs.seek(off)
    bs.writeInt(length)
    bs.seek(returnPlace)
    return length

def writeMatMap(strips, bs):
    bs.writeInt(0x60000)
    bs.writeInt(strips)
    length = 12 + (strips*4)
    bs.writeInt(length)
    #see matRemap
    for _ in range(strips):
        bs.writeInt(0) #this is technically wrong but I'm not fixing it atm
    return length

def writePositions(mesh,bs):
    bs.writeInt(0x70000)
    bs.writeInt(len(mesh.positions))
    length = 12 + (len(mesh.positions)*12)
    bs.writeInt(length)
    for position in mesh.positions:
        bs.writeFloat(position[0])
        bs.writeFloat(position[1])
        bs.writeFloat(position[2])
    return length

def writeNormals(mesh,bs):
    bs.writeInt(0x80000)
    bs.writeInt(len(mesh.normals))
    length = 12 + (len(mesh.normals)*12)
    bs.writeInt(length)
    for normal in mesh.normals:
        bs.writeFloat(normal[0])
        bs.writeFloat(normal[1])
        bs.writeFloat(normal[2])
    return length

def writeUVs(mesh,bs):
    bs.writeInt(0xA0000)
    bs.writeInt(len(mesh.uvs))
    length = 12 + (len(mesh.uvs)*8)
    bs.writeInt(length)
    for uv in mesh.uvs:
        bs.writeFloat(uv[0])
        bs.writeFloat(uv[1])
    return length

def writeVertColor(mesh,bs):
    bs.writeInt(0xB0000)
    if(len(mesh.colors) > 0):
        bs.writeInt(len(mesh.colors))
        length = 12 + (len(mesh.colors)*16)
        bs.writeInt(length)
        for color in mesh.colors:
            bs.writeFloat(color[0])
            bs.writeFloat(color[1])
            bs.writeFloat(color[2])
            bs.writeFloat(color[3])
    else:
        bs.writeInt(len(mesh.positions))
        length = 12 + (len(mesh.positions)*16)
        bs.writeInt(length)
        for _ in range(len(mesh.positions)):
            bs.writeFloat(255)
            bs.writeFloat(255)
            bs.writeFloat(255)
            bs.writeFloat(255)
    return length

def writeWeightBoneRemap(mesh,bs):
    boneRemap = []
    for weight in mesh.weights:
        for index in weight.indices:
            if index not in boneRemap:
                boneRemap.append(index)
    bs.writeInt(0xC0000)
    bs.writeInt(len(mesh.weights))
    offset = bs.tell()
    length = 12
    bs.writeInt(0)
    for weight in mesh.weights:
        bs.writeInt(weight.numWeights())
        length += ((weight.numWeights()*8)+4)
        for i in range(weight.numWeights()):
            bs.writeInt(boneRemap.index(weight.indices[i]))
            bs.writeFloat(weight.weights[i]*100)
    returnPlace = bs.tell()
    bs.seek(offset)
    bs.writeInt(length)
    bs.seek(returnPlace)
    # now write bone remap
    bs.writeInt(0x100000)
    bs.writeInt(len(boneRemap))
    boneLen = 12 + (4*len(boneRemap))
    bs.writeInt(boneLen)
    for bone in boneRemap:
        bs.writeInt(bone)
    return length+boneLen

def writeTangents(mesh,bs):
    print(mesh.tangents[0][0])
    bs.writeInt(0x120000)
    bs.writeInt(len(mesh.tangents))
    length = 12 + (16 * len(mesh.tangents))
    bs.writeInt(length)
    for tangent in mesh.tangents:
        print(tangent)
        bs.writeFloat(float(tangent[0]))
        bs.writeFloat(float(tangent[1]))
        bs.writeFloat(float(tangent[2]))
        bs.writeFloat(float(tangent[3]))

def WriteMeshBlock(mdl, bs):
    bs.writeInt(2)
    bs.writeInt(len(mdl.meshes))
    meshBlockLenOff = bs.tell()
    bs.writeInt(0)
    meshBlockLen = 12
    #still can't write it
    #seperate the meshes into mesh groups, mainly for the purpose of merging meshes
    for mesh in mdl.meshes:
        bs.writeInt(4)
        #determine what all needs to be exported
        blockCount = 1 #faces
        blockCount += 1 #vertices
        blockCount += 1 #normals
        blockCount += 1 #UVs
        blockCount += 1 #VertColor
        if len(mesh.weights) > 0:
            blockCount += 2
        if len(mesh.tangents) > 0:
            blockCount += 1 #may not matter since Noesis auto-generates tangents
        blockCount += 1 #material remap
        blockCount += 1 #material map
        bs.writeInt(blockCount)
        meshLenOff = bs.tell()
        bs.writeInt(0)
        #this one actually gets solved quicker
        meshLen = 12
        faceLen, stripCount = writeFaceBlock(mesh,bs)
        meshLen += faceLen
        meshLen += writeMatRemap(mdl,mesh,bs)
        meshLen += writeMatMap(stripCount, bs)
        meshLen += writePositions(mesh,bs)
        meshLen += writeNormals(mesh,bs)
        meshLen += writeUVs(mesh,bs)
        meshLen += writeVertColor(mesh,bs)
        meshLen += writeWeightBoneRemap(mesh,bs)
        meshLen += writeTangents(mesh,bs) #little iffy on this one
        returnPlace = bs.tell()
        bs.seek(meshLenOff)
        bs.writeInt(meshLen)
        bs.seek(returnPlace)
        meshBlockLen += meshLen
    returnPlace = bs.tell()
    bs.seek(meshBlockLenOff)
    bs.writeInt(meshBlockLen)
    bs.seek(returnPlace)
    return meshBlockLen
        
def writeMaterialTexture(mdl,bs):
    textureRemap = []
    #the texture gathering method for this model can catch a lot of extra textures, so this filters accounted textures to only those used by materials
    for material in mdl.modelMats.matList:
        if material.texName is not "" and material.texName not in textureRemap:
            textureRemap.append(material.texName)
        if hasattr(material,"nrmTexName"):
            if material.nrmTexName not in textureRemap:
                textureRemap.append(material.nrmTexName)
        if hasattr(material,"specTexName"):
            if material.specTexName not in textureRemap:
                textureRemap.append(material.specTexName)
    textureRemap.sort()
    #writing material block
    bs.writeInt(0x9)
    bs.writeInt(len(mdl.modelMats.matList))
    matOff = bs.tell()
    bs.writeInt(0)
    matLen = 12
    for material in mdl.modelMats.matList:
        bs.writeInt(2)
        bs.writeInt(1)
        mLen = bs.tell()
        bs.writeInt(0)
        #these float groups are separate until more testing is done to know what they all are
        for _ in range(3):
            bs.writeFloat(1)
        bs.writeFloat(0)
        for _ in range(3):
            bs.writeFloat(1)
        for _ in range(4):
            bs.writeFloat(1)
        bs.writeFloat(0)
        bs.writeFloat(50)
        #need to see what textures are being used
        texCount = 0
        l = 268
        if material.texName is not "":
            texCount += 1
            l += 4
        if hasattr(material,"nrmTexName"):
            texCount += 1
            l += 4
        if hasattr(material,"specTexName"):
            texCount += 1
            l += 4
        bs.writeInt(texCount)
        buffer = []
        for _ in range(200):
            buffer.append(0)
        bs.writeBytes(bytes(buffer))
        if(texCount > 2):
            bs.writeInt(textureRemap.index(material.texName))
            bs.writeInt(textureRemap.index(material.nrmTexName))
            bs.writeInt(textureRemap.index(material.specTexName))
        elif(texCount > 1):
            bs.writeInt(textureRemap.index(material.texName))
            bs.writeInt(textureRemap.index(material.nrmTexName))
        elif(texCount > 0):
            bs.writeInt(textureRemap.index(material.texName))
        returnPlace = bs.tell()
        bs.seek(mLen)
        bs.writeInt(l)
        bs.seek(returnPlace)
        matLen += l
    returnPlace = bs.tell()
    bs.seek(matOff)
    bs.writeInt(matLen)
    bs.seek(returnPlace)
    #now write texture block
    bs.writeInt(0xA)
    bs.writeInt(len(textureRemap))
    texLen = 12 + (len(textureRemap)*268)
    bs.writeInt(texLen)
    for texture in textureRemap:
        bs.writeInt(0)
        bs.writeInt(1)
        bs.writeInt(268)
        texIndex = textureRemap.index(texture)
        bs.writeInt(texIndex)
        tex = rapi.loadExternalTex(texture)
        bs.writeInt(tex.width)
        bs.writeInt(tex.height)
        buffer = []
        for _ in range(244):
            buffer.append(0)
        bs.writeBytes(bytes(buffer))
    return matLen+texLen


def noepyWriteFMOD(mdl,bs):
    #write mainBlock and first block
    bs.writeInt(1)
    bs.writeInt(4)
    fileSizeOff = bs.tell()
    bs.writeInt(0)
    fileSize = 12
    #can't really write this yet, so save location and write later
    fileSize += WriteFirstBlock(bs)
    #now write mesh data
    fileSize += WriteMeshBlock(mdl,bs)
    fileSize += writeMaterialTexture(mdl,bs)
    bs.seek(fileSizeOff)
    bs.writeInt(fileSize)
    return 1