@echo off 
Pushd "%~dp0"
TexConv2.exe -i "%~1" -o "%~1".dds
