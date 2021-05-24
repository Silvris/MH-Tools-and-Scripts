using System;
using System.Collections.Generic;
using System.IO;
using System.Text;

namespace FMODMaterialEditor.Classes
{
    enum FMODTypes
    {
        Material,
        TexLink
    }//small enum used for logic within WPF
    class FMODFile
    {
        uint UnknData; //suspected hash but not needed for this
        byte[] geometryData; //we're not touching this aside from just keeping it in memory. Surprised List<byte[]> works tbh
        public List<Material> materials = new List<Material>();
        public List<TexLink> texLinks = new List<TexLink>();

        public FMODFile(BinaryReader br)
        {
            int fileType = br.ReadInt32();//should be 1
            int count = br.ReadInt32();//always 4, so I'm not running a for loop for it
            int fileSize = br.ReadInt32();//not important here, but important for writing
            int uType = br.ReadInt32();
            int uCount = br.ReadInt32();
            int uSize = br.ReadInt32();//should be 16
            UnknData = br.ReadUInt32();
            int gType = br.ReadInt32();
            int gCount = br.ReadInt32();
            int gSize = br.ReadInt32();
            br.BaseStream.Seek(-12,SeekOrigin.Current);
            geometryData = br.ReadBytes(gSize);//avoiding any further interpretation of this section, since it would take more effort than what is really required
            int mType = br.ReadInt32();
            int mCount = br.ReadInt32();
            int mSize = br.ReadInt32();
            for(int i = 0; i < mCount; i++)
            {
                Material material = new Material(br);
                materials.Add(material);
            }
            int tType = br.ReadInt32();
            int tCount = br.ReadInt32();
            int tSize = br.ReadInt32();
            for(int i = 0; i < tCount; i++)
            {
                texLinks.Add(new TexLink(br));
            }
        }

        public void Write(BinaryWriter bw)
        {
            int materialsLen = 0;
            for(int i = 0; i < materials.Count; i++)
            {
                materialsLen += materials[i].Length();
            }
            int totalFileLength = 12 + 16 + geometryData.Length + 12 + materialsLen + 12 + (268 * texLinks.Count);
            bw.Write(1);
            bw.Write(4);
            bw.Write(totalFileLength);
            bw.Write(0x20000);
            bw.Write(1);
            bw.Write(16);
            bw.Write(UnknData);
            bw.Write(geometryData);//now we just get to ignore any parsing for it
            bw.Write(9);
            bw.Write(materials.Count);
            bw.Write(materialsLen + 12);
            for(int i = 0; i < materials.Count; i++)
            {
                materials[i].Write(bw);
            }
            bw.Write(10);
            bw.Write(texLinks.Count);
            bw.Write((texLinks.Count * 268)+12);
            for(int i = 0; i < texLinks.Count; i++)
            {
                texLinks[i].Write(bw);
            }
        }
    }
}
