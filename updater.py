import requests
import os
import sys

<<<<<<< HEAD
REPO_RAW = "https://raw.githubusercontent.com/RunBloodz/FishingMacro/main/"

def check_update(local_version_path):
    try:
        r = requests.get(REPO_RAW + "version.txt", timeout=3)
        if not os.path.exists(local_version_path):
            return
        if r.text.strip() != open(local_version_path).read().strip():
            os.startfile("https://github.com/RunBloodz/FishingMacro/releases")
            sys.exit()
    except:
        pass
=======
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
>>>>>>> 421cea7cdfa2bb317814615a282dcb5f05bed511
