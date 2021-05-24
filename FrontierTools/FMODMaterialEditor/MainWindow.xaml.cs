using FMODMaterialEditor.Classes;
using Microsoft.Win32;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace FMODMaterialEditor
{
    /// <summary>
    /// Interaction logic for MainWindow.xaml
    /// </summary>
    public partial class MainWindow : Window
    {
        FMODFile fmod = null;
        public MainWindow()
        {
            InitializeComponent();
            ContentController.Content = null;
        }


        private void PopulateTreeView()
        {
            for(int i = 0; i < fmod.materials.Count; i++)
            {
                TreeViewItem matItem = new TreeViewItem();
                matItem.Header = "Material " + (i+1);
                matItem.Foreground = HelperFunctions.GetBrushFromHex("#AAAAAA");
                List<int> tag = new List<int>();
                tag.Add(0);
                tag.Add(i);
                matItem.Tag = tag;
                treeView1.Items.Add(matItem);
            }
            for(int i = 0; i < fmod.texLinks.Count; i++)
            {
                TreeViewItem texItem = new TreeViewItem();
                texItem.Header = "Texture " + (i+1);
                texItem.Foreground = HelperFunctions.GetBrushFromHex("#AAAAAA");
                List<int> tag = new List<int>();
                tag.Add(1);
                tag.Add(i);
                texItem.Tag = tag;
                treeView1.Items.Add(texItem);
            }
        }
        private void ImportFile(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFile = new OpenFileDialog();
            openFile.Filter = "Monster Hunter Frontier Model (*.fmod) | *.fmod";
            openFile.Title = "Select your FMOD file:";
            if (openFile.ShowDialog() == true)
            {
                BinaryReader br = new BinaryReader(new FileStream(openFile.FileName, FileMode.Open));
                fmod = new FMODFile(br);
                br.Close();
                PopulateTreeView();
            }
        }

        private void treeView1_SelectedItemChanged(object sender, RoutedPropertyChangedEventArgs<object> e)
        {
            TreeViewItem ti = (TreeViewItem)treeView1.SelectedItem;
            List<int> tag = (List<int>)ti.Tag;
            if (tag[0] == 0)
            {
                ContentController.Content = fmod.materials[tag[1]];
            }
            else if (tag[0] == 1)
            {
                ContentController.Content = fmod.texLinks[tag[1]];
            }
            else
            {
                ContentController.Content = null;
            }
        }

        private void ExportFile(object sender, RoutedEventArgs e)
        {
            SaveFileDialog saveFile = new SaveFileDialog();
            saveFile.Filter = "Monster Hunter Frontier Model (*.fmod) | *.fmod";
            saveFile.Title = "Export your file:";
            if(saveFile.ShowDialog() == true)
            {
                BinaryWriter bw = new BinaryWriter(new FileStream(saveFile.FileName, FileMode.OpenOrCreate));
                fmod.Write(bw);
                bw.Close();
            }
        }
    }

    public class MatTexSelector : DataTemplateSelector
    {
        public DataTemplate TexEditor { get; set; }
        public DataTemplate MatEditor { get; set; }
        public override DataTemplate SelectTemplate(object item, DependencyObject container)
        {
            if (item != null) 
            {
                if (item is TexLink)
                {
                    return TexEditor;
                }
                else
                {
                    return MatEditor;
                }
            }
            else
            {
                return null;
            }
        }
    }
}
