using System;
using System.IO;
using System.Windows.Forms;

namespace FMOD2AMH
{
    class Program
    {
        static void fmod2amh()
        {
            byte[] fmodBin = null;
            byte[] fsklBin = null;
            OpenFileDialog fmod = new OpenFileDialog();
            fmod.Filter = "Monster Hunter PS2 Model (.fmod)|*.fmod";
            fmod.Title = "Select your fmod file:";
            if (fmod.ShowDialog() == DialogResult.OK)
            {
                BinaryReader fmodFile = new BinaryReader(new FileStream(fmod.FileName, FileMode.Open));
                fmodBin = fmodFile.ReadBytes((int)fmodFile.BaseStream.Length);
            }
            OpenFileDialog fskl = new OpenFileDialog();
            fskl.Filter = "Monster Hunter PS2 Skeleton (.fskl)|*.fskl";
            fskl.Title = "Select your fmod file:";
            if (fskl.ShowDialog() == DialogResult.OK)
            {
                BinaryReader fsklFile = new BinaryReader(new FileStream(fskl.FileName, FileMode.Open));
                fsklBin = fsklFile.ReadBytes((int)fsklFile.BaseStream.Length);
            }
            if (fmodBin != null && fsklBin != null)
            {
                SaveFileDialog amh = new SaveFileDialog();
                amh.Filter = "Monster Hunter PS2 Model Package (.amh)|*.amh";
                amh.Title = "Choose save location for AMH file:";
                if(amh.ShowDialog() == DialogResult.OK)
                {
                    BinaryWriter amhFile = new BinaryWriter(new FileStream(amh.FileName, FileMode.OpenOrCreate));
                    amhFile.Write((int)2);
                    amhFile.Write(20);//header length
                    amhFile.Write(fmodBin.Length);
                    amhFile.Write(fmodBin.Length + 20);
                    amhFile.Write(fsklBin.Length);
                    amhFile.Write(fmodBin);
                    amhFile.Write(fsklBin);
                }
            }
        }

        static void fmod2amh(string fmod, string fskl,string amh)
        {
            byte[] fmodBin = null;
            byte[] fsklBin = null;
            BinaryReader fmodFile = new BinaryReader(new FileStream(fmod, FileMode.Open));
            fmodBin = fmodFile.ReadBytes((int)fmodFile.BaseStream.Length);
            BinaryReader fsklFile = new BinaryReader(new FileStream(fskl, FileMode.Open));
            fsklBin = fsklFile.ReadBytes((int)fsklFile.BaseStream.Length);
            if (fmodBin != null && fsklBin != null)
            {
                BinaryWriter amhFile = new BinaryWriter(new FileStream(amh, FileMode.OpenOrCreate));
                amhFile.Write((int)2);
                amhFile.Write(20);//header length acts as offset for first file
                amhFile.Write(fmodBin.Length);
                amhFile.Write(fmodBin.Length + 20);
                amhFile.Write(fsklBin.Length);
                amhFile.Write(fmodBin);
                amhFile.Write(fsklBin);
            }
        }

        static void amh2fmod(string amh, string fmod)
        {
            byte[] fmodBin = null;
            byte[] fsklBin = null;
            BinaryReader amhFile = new BinaryReader(new FileStream(amh, FileMode.Open));
            int fileCount = amhFile.ReadInt32();
            int[] offsets = new int[2];
            int[] lengths = new int[2];
            for (int i = 0; i < fileCount; i++)
            {
                offsets[i] = amhFile.ReadInt32();
                lengths[i] = amhFile.ReadInt32();
            };
            amhFile.BaseStream.Seek(offsets[0],SeekOrigin.Begin);
            fmodBin = amhFile.ReadBytes(lengths[0]);
            amhFile.BaseStream.Seek(offsets[1], SeekOrigin.Begin);
            fsklBin = amhFile.ReadBytes(lengths[1]);
            string exportName = fmod.Remove(fmod.LastIndexOf('.'));
            BinaryWriter fmodFile = new BinaryWriter(new FileStream(exportName + ".fmod", FileMode.OpenOrCreate));
            fmodFile.Write(fmodBin);
            BinaryWriter fsklFile = new BinaryWriter(new FileStream(exportName + ".fskl", FileMode.OpenOrCreate));
            fsklFile.Write(fsklBin);
        }

        static void amh2fmod()
        {
            byte[] fmodBin = null;
            byte[] fsklBin = null;
            OpenFileDialog amh = new OpenFileDialog();
            if (amh.ShowDialog() == DialogResult.OK)
            {
                BinaryReader amhFile = new BinaryReader(new FileStream(amh.FileName, FileMode.Open));
                int fileCount = amhFile.ReadInt32();
                int[] offsets = new int[2];
                int[] lengths = new int[2];
                for (int i = 0; i < fileCount; i++)
                {
                    offsets[i] = amhFile.ReadInt32();
                    lengths[i] = amhFile.ReadInt32();
                };
                amhFile.BaseStream.Seek(offsets[0], SeekOrigin.Begin);
                fmodBin = amhFile.ReadBytes(lengths[0]);
                amhFile.BaseStream.Seek(offsets[1], SeekOrigin.Begin);
                fsklBin = amhFile.ReadBytes(lengths[1]);
                SaveFileDialog fmod = new SaveFileDialog();
                fmod.Filter = "Monster Hunter PS2 Model (.fmod)|*.fmod";
                fmod.Title = "Choose where to save your fmod file:";
                if (fmod.ShowDialog() == DialogResult.OK)
                {
                    BinaryWriter fmodFile = new BinaryWriter(new FileStream(fmod.FileName, FileMode.OpenOrCreate));
                    fmodFile.Write(fmodBin);
                }
                SaveFileDialog fskl = new SaveFileDialog();
                fmod.Filter = "Monster Hunter PS2 Skeleton (.fskl)|*.fskl";
                fmod.Title = "Choose where to save your fskl file:";
                if (fskl.ShowDialog() == DialogResult.OK)
                {
                    BinaryWriter fsklFile = new BinaryWriter(new FileStream(fskl.FileName, FileMode.OpenOrCreate));
                    fsklFile.Write(fsklBin);
                }
            }
        }

        static void SwitchHandler(string[] args)
        {
            string choice;
            try { choice = args[0]; }
            catch (IndexOutOfRangeException)
            {
                choice = null;
            }

            if (choice == "-p")
            {
                if (args[1] != null && args[2] != null && args[3] != null)
                {
                    fmod2amh(args[1], args[2], args[3]);
                }
                else
                {
                    fmod2amh();
                }

            }
            else if (choice == "-u")
            {
                if(args[1] != null && args[2] != null)
                {
                    amh2fmod(args[1], args[2]);
                }
                else
                {
                    amh2fmod();
                }
            }
            else if (choice == "-h")
            {
                Console.WriteLine("FMOD to AMH Converter -- Silvris 2020");
                Console.WriteLine("//////////////////////////////////////////////////////////////////////////////////////////////////////");
                Console.WriteLine("//     Options:                                                                                     //\n" +
                                  "// -p -- Pack .fmod and .fskl into a .amh                                                           //\n" +
                                  "//  Usage: FMOD2AMH.exe -p {optional fmod path} {optional fskl path} {optional amh path}            //\n" +
                                  "// -u -- Unpack a .amh into an .fmod and an .fskl                                                   //\n" +
                                  "//  Usage: FMOD2AMH.exe -u {optional amh path} {optional output fmod/fskl path}                     //");
                Console.WriteLine("//////////////////////////////////////////////////////////////////////////////////////////////////////");
            }
            else
            {
                Console.WriteLine("Invalid Input. Type -h to see all options.");
            }
        }


        [STAThread]
        static void Main(string[] args)
        {
            if(args.Length == 0)
            {
                Console.WriteLine("Options:\n" +
                  "-p -- Pack .fmod and .fskl into a .amh\n" +
                  "-u -- Unpack a .amh into an .fmod and an .fskl\n" +
                  "-h -- See options for program");
                string choice = Console.ReadLine();
                string[] choiceIn = new string[4];
                choiceIn[0] = choice;
                SwitchHandler(choiceIn);
            }
            else
            {
                SwitchHandler(args);
            }
        }
    }
}
