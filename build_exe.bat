@echo off
echo Building FishingMacro EXE...

py -3.11 -m pip install -r requirements.txt
py -3.11 -m PyInstaller ^
 --onefile ^
 --noconsole ^
 --name FishingMacro ^
 main.py

pause
