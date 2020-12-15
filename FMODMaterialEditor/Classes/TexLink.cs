using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Windows.Controls;

namespace FMODMaterialEditor.Classes
{
    class TexLink
    {
        public FMODTypes type = FMODTypes.TexLink;
        public uint header1 { get; set; }
        public uint header2 { get; set; }
        public uint blocksize = 268; //constant size among files
        public uint imageIdx { get; set; }
        public uint width { get; set; }
        public uint height { get; set; }

        public TexLink(BinaryReader br)
        {
            header1 = br.ReadUInt32();
            header2 = br.ReadUInt32();
            uint blockS = br.ReadUInt32();
            imageIdx = br.ReadUInt32();
            width = br.ReadUInt32();
            height = br.ReadUInt32();
            byte[] bytes = br.ReadBytes(244);
        }

        public TexLink()
        {
            header1 = 0;
            header2 = 1;
            imageIdx = 0;
            width = 256;
            height = 256;
        }

        public void Write(BinaryWriter bw)
        {
            bw.Write(header1);
            bw.Write(header2);
            bw.Write(blocksize);
            bw.Write(imageIdx);
            bw.Write(width);
            bw.Write(height);
            byte[] bytes = new byte[244];
            bw.Write(bytes);
        }
    }
}
