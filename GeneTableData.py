import json
from GMDPy import ReadGMDv2
import os
import sys

os.chdir(os.path.dirname(sys.argv[0]))
geneTable = json.load(open("gene_table.gtb.json",'r'))["root"]["mpArray"]["mpArray"]
geneNames = ReadGMDv2(open("gene_name_eng.gmd",'rb'))
skillTable = json.load(open("skill_table.skt.json",'r'))["root"]["mpArray"]["mpArray"]
skillNames = ReadGMDv2(open("SkillName_eng.gmd",'rb'))
skillDesc = ReadGMDv2(open("SkillExp_eng.gmd",'rb'))

output = open("MHS2-Genes.csv",'w',encoding='utf-8')
output.write("GeneName\tGeneSize\tBingoType\tElementType\tReqLevel\tMaxUpgrade\tAssociatedSkill\tSkillDescription\tSkillCost\n")

def GetBingo(bingoVal):
    if bingoVal == 0:
        return "None"
    elif bingoVal == 1:
        return "Power"
    elif bingoVal == 2:
        return "Technique"
    elif bingoVal == 3:
        return "Speed"
    else:
        return "Invalid"

def GetElement(eleVal):
    if eleVal == 0:
        return "Element-less"
    elif eleVal == 1:
        return "Fire"
    elif eleVal == 2:
        return "Water"
    elif eleVal == 3:
        return "Thunder" 
    elif eleVal == 4:
        return "Ice"
    elif eleVal == 5:
        return "Dragon"
    else:
        return "Invalid"

#print(geneTable)
for gene in geneTable:
    try:
        skill = next(item for item in skillTable if item["mKeyString"] == "ID_BTL_SKILL_{0:0>3}".format(gene["mSkillID"]))
    except(StopIteration):
        skill = None
    if skill == None:
        if gene["mNameMessageId"] in geneNames:
            output.write("{geneName}\t{GeneSize}\t{BingoType}\t{Element}\t{ReqLevel}\t{MaxUpgrade}\t\t\t\n".format(geneName=geneNames[gene["mNameMessageId"]],GeneSize=gene["mGeneSize"],BingoType=GetBingo(gene["mBingoThreeType"]),Element=GetElement(gene["mBingoElementType"]),ReqLevel=gene["mOpenLevel"],MaxUpgrade=gene["mStrengthMaxLevel"]))
    else:
        output.write("{geneName}\t{GeneSize}\t{BingoType}\t{Element}\t{ReqLevel}\t{MaxUpgrade}\t{SkillName}\t{SkillDesc}\t{SkillCost}\n".format(geneName=geneNames[gene["mNameMessageId"]],GeneSize=gene["mGeneSize"],BingoType=GetBingo(gene["mBingoThreeType"]),Element=GetElement(gene["mBingoElementType"]),ReqLevel=gene["mOpenLevel"],MaxUpgrade=gene["mStrengthMaxLevel"],SkillName=skillNames[skill["mNameMessageId"]].replace("\r","\\r").replace("\n","\\n"),SkillDesc=skillDesc[skill["mExpMessageId"]].replace("\r","\\r").replace("\n","\\n"),SkillCost=skill["mGaugeCost"]))
