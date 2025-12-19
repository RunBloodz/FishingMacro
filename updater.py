import requests, os, sys, shutil, subprocess

REPO = "YOURNAME/FishingMacro"
EXE_NAME = "FishingMacro.exe"
VERSION_URL = f"https://raw.githubusercontent.com/{REPO}/main/version.txt"
EXE_URL = f"https://github.com/{REPO}/releases/latest/download/{EXE_NAME}"

def update():
    local = open("version.txt").read().strip()
    remote = requests.get(VERSION_URL).text.strip()

    if local == remote:
        return

    print("Updating...")
    r = requests.get(EXE_URL, stream=True)
    with open("new.exe", "wb") as f:
        for c in r.iter_content(1024):
            f.write(c)

    os.replace("new.exe", EXE_NAME)
    open("version.txt", "w").write(remote)
    subprocess.Popen([EXE_NAME])
    sys.exit()

update()
