<<<<<<< HEAD
import json

def save(cfg):
    with open("config.json", "w") as f:
        json.dump(cfg, f)

def load():
    try:
        with open("config.json") as f:
            return json.load(f)
    except:
        return {}
=======
import json
import os
import sys

def path(file):
    base = getattr(sys, '_MEIPASS', os.getcwd())
    return os.path.join(base, file)

def save(cfg):
    with open(path("config.json"), "w") as f:
        json.dump(cfg, f, indent=2)

def load():
    try:
        with open(path("config.json")) as f:
            return json.load(f)
    except:
        return {}
>>>>>>> 421cea7cdfa2bb317814615a282dcb5f05bed511
