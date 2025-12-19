@echo off
echo ===============================
echo Building FishingMacro EXE
echo ===============================

py -3.11 -m PyInstaller ^
 --onefile ^
 --noconsole ^
 --add-data "version.txt;." ^
 --add-data "config.py;." ^
 --add-data "macro.py;." ^
 --add-data "ui.py;." ^
 --add-data "updater.py;." ^
 main.py

pause
