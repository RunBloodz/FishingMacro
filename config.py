import json
from pathlib import Path

CONFIG = Path("config.json")


def save(data):
    CONFIG.write_text(json.dumps(data, indent=2))


def load():
    if not CONFIG.exists():
        return {}
    return json.loads(CONFIG.read_text())
