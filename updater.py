import requests
import os
import sys

REPO = "RunBloodz/FishingMacro"
RAW = f"https://raw.githubusercontent.com/{REPO}/main"

def app_path(file):
    base = getattr(sys, '_MEIPASS', os.getcwd())
    return os.path.join(base, file)

def check_for_update():
    try:
        remote = requests.get(f"{RAW}/version.txt", timeout=3).text.strip()
        local = open(app_path("version.txt")).read().strip()

        if remote != local:
            print("Update available:", remote)
        else:
            print("Up to date")
    except Exception as e:
        print("Updater error:", e)
