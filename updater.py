import os
import sys
import json
import hashlib
import requests
import threading
import tempfile
import shutil
import subprocess

BASE_URL = "https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/updates"
VERSION_URL = "https://raw.githubusercontent.com/YOUR_USER/YOUR_REPO/main/version.txt"

class Updater(threading.Thread):
    def __init__(self, progress_callback=None, silent=True):
        super().__init__(daemon=True)
        self.progress_callback = progress_callback
        self.silent = silent

    def run(self):
        try:
            if not self.update_available():
                return
            self.apply_delta_update()
            self.restart()
        except Exception as e:
            print("Updater error:", e)

    # ---------- VERSION ----------
    def local_version(self):
        try:
            with open(self.resource("version.txt")) as f:
                return f.read().strip()
        except:
            return "0.0.0"

    def remote_version(self):
        return requests.get(VERSION_URL, timeout=5).text.strip()

    def update_available(self):
        return self.remote_version() != self.local_version()

    # ---------- DELTA UPDATE ----------
    def apply_delta_update(self):
        manifest = requests.get(f"{BASE_URL}/manifest.json").json()
        app_dir = self.app_dir()

        files_to_update = []
        for file, remote_hash in manifest.items():
            local_path = os.path.join(app_dir, file)
            if not os.path.exists(local_path) or self.md5(local_path) != remote_hash:
                files_to_update.append(file)

        total = len(files_to_update)
        for i, file in enumerate(files_to_update, 1):
            self.download_file(file, i, total)

        with open(os.path.join(app_dir, "version.txt"), "w") as f:
            f.write(self.remote_version())

    def download_file(self, file, idx, total):
        url = f"{BASE_URL}/{file}"
        dst = os.path.join(self.app_dir(), file)
        os.makedirs(os.path.dirname(dst), exist_ok=True)

        r = requests.get(url, stream=True)
        with open(dst, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)

        if self.progress_callback:
            self.progress_callback(int(idx / total * 100))

    # ---------- HELPERS ----------
    def md5(self, path):
        h = hashlib.md5()
        with open(path, "rb") as f:
            h.update(f.read())
        return h.hexdigest()

    def app_dir(self):
        return os.path.dirname(sys.executable if getattr(sys, "frozen", False) else __file__)

    def resource(self, name):
        return os.path.join(self.app_dir(), name)

    def restart(self):
        subprocess.Popen([sys.executable])
        sys.exit()
