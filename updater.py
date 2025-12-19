import requests
import os
import sys

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
