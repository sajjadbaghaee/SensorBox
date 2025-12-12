import os
import json
from copy import deepcopy
from config import DEFAULTS

# Always save config.json inside /home/evolvedcity/SensorBox
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "..", "config.json")  # one level up from utils/


def _deep_merge(dst, src):
    """
    Recursively merge src -> dst (in place).
    - Keeps anything already in dst (user overrides win).
    - Fills in only keys that are missing in dst.
    This way, new defaults like sensorIds show up even if
    the old config.json didn't have them yet.
    """
    for key, src_val in src.items():
        if key not in dst:
            dst[key] = deepcopy(src_val)
        else:
            dst_val = dst[key]
            if isinstance(dst_val, dict) and isinstance(src_val, dict):
                _deep_merge(dst_val, src_val)
            # if it's not a dict, we keep dst_val as-is


def load_config():
    """Load runtime config, merged with DEFAULTS so new keys (like sensorIds) appear."""
    path = os.path.abspath(CONFIG_FILE)
    cfg = {}

    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                cfg = json.load(f)
        except Exception:
            print("Error reading runtime config, using only defaults.")
            cfg = {}

    # Merge defaults into loaded cfg so any missing keys (sensorIds, new intervals, etc.) get populated.
    _deep_merge(cfg, DEFAULTS)

    return cfg


def save_config(cfg, reboot=False):
    """Save runtime config to file. Optionally reboot the Pi."""
    path = os.path.abspath(CONFIG_FILE)
    try:
        with open(path, "w") as f:
            json.dump(cfg, f, indent=4)
        print("Configuration saved to", path)

        if reboot:
            print("Rebooting Raspberry Pi...")
            os.system("sudo reboot")
    except Exception as e:
        print(f"Could not save config: {e}")
