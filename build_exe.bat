@echo off
echo Building EXE...

py -3.11 -m PyInstaller ^
--onefile ^
--noconsole ^
--add-data "version.txt;." ^
--name FishingMacro ^
main.py

pause
