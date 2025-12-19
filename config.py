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
