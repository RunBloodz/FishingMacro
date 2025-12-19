import requests
import pathlib

VERSION_FILE = "version.txt"
GITHUB_VERSION_URL = "https://raw.githubusercontent.com/RunBloodz/FishingMacro/main/version.txt"


def get_local_version():
    if not pathlib.Path(VERSION_FILE).exists():
        return "0.0.0"
    return pathlib.Path(VERSION_FILE).read_text().strip()


def check_update():
    try:
        online = requests.get(GITHUB_VERSION_URL, timeout=5).text.strip()
        local = get_local_version()

        if online != local:
            print(f"Update available: {local} → {online}")
        else:
            print("You are up to date")

    except Exception as e:
        print("Update check failed:", e)
