using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Windows.Controls;
using System.Windows.Media;
using FMODMaterialEditor;

namespace FMODMaterialEditor.Classes
{
    class Material
    {
        FMODTypes type = FMODTypes.Material;
        uint header2;
        uint header1;

        public float set1x { get; set; } //base map factors?
        public float set1y { get; set; }
        public float set1z { get; set; }

        public float unknFl { get; set; } //base map alpha?

        public float set2x { get; set; } //emission?
        public float set2y { get; set; }
        public float set2z { get; set; }

        public float set3x { get; set; } //who knows
        public float set3y { get; set; }
        public float set3z { get; set; }
        public float set3w { get; set; }

        public uint unkn8 { get; set; } 
        public float unkn9 { get; set; } //constantly 50
        public List<uint> texList = new List<uint>();//gonna finish this part later

        public Material(BinaryReader br)
        {
            header2 = br.ReadUInt32();
            header1 = br.ReadUInt32();
            uint blockCount = br.ReadUInt32();
            set1x = br.ReadSingle();
            set1y = br.ReadSingle();
            set1z = br.ReadSingle();
            unknFl = br.ReadSingle();
            set2x = br.ReadSingle();
            set2y = br.ReadSingle();
            set2z = br.ReadSingle();
            set3x = br.ReadSingle();
            set3y = br.ReadSingle();
            set3z = br.ReadSingle();
            set3w = br.ReadSingle();
            unkn8 = br.ReadUInt32();
            unkn9 = br.ReadSingle();
            uint texCount = br.ReadUInt32();
            byte[] byteArray = br.ReadBytes(200);
            for(int i = 0; i < texCount; i++)
            {
                texList.Add(br.ReadUInt32());
            }
        }

        public void Write(BinaryWriter bw)
        {
            bw.Write(header2);
            bw.Write(header1);
            bw.Write(268 + (texList.Count * 4));
            bw.Write(set1x);
            bw.Write(set1y);
            bw.Write(set1z);
            bw.Write(unknFl);
            bw.Write(set2x);
            bw.Write(set2y);
            bw.Write(set2z);
            bw.Write(set3x);
            bw.Write(set3y);
            bw.Write(set3z);
            bw.Write(set3w);
            bw.Write(unkn8);
            bw.Write(unkn9);
            bw.Write(texList.Count);
            byte[] bytes = new byte[200];
            bw.Write(bytes);
            for(int i = 0; i < texList.Count; i++)
            {
                bw.Write(texList[i]);
            }
        }

        public int Length()
        {
            return 268 + (texList.Count * 4);
        }


    }
}
