# Configuration management
import json
import os

CONFIG_FILE = "config.json"

DEFAULT_CONFIG = {
    "rod_key": "5",
    "reset_key": "1",
    "exclamation_pos": [0, 0],
    "exclamation_color": [255, 0, 0], # Red
    "minigame_bar_y": 0,
    "minigame_bar_x_start": 0,
    "minigame_bar_x_end": 0,
    "fish_color": [0, 0, 255], # Blue
    "catcher_color": [211, 211, 211], # Light Gray
    "chest_color": [255, 215, 0], # Gold/Yellow
    "tolerance": 20
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except:
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
