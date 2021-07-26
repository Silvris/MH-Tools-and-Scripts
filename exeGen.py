import PyInstaller.__main__
import PyInstaller.config
import os
import sys

abspath = os.path.abspath(sys.argv[0])

dname = os.path.dirname(abspath)

os.chdir(dname)


files = [
    f"MHStories2ARCExtract.py",
    f"MHStories2ARCRepack.py",
    f"btBinaryRepackUnpack.py"
]

PyInstaller.config.CONF["workpath"] = dname + "/dist"

for f in files:
    PyInstaller.__main__.run([f, "--onefile", "--distpath", dname+"/dist"])