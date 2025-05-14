import json
from pathlib import Path

CONFIG_FILE = Path("data/config.json")


def load_config():
    """Load configuration from JSON file"""
    if not CONFIG_FILE.exists():
        default_config = {
            "horses": {},
            "closed_channels": [],
            "log_channel": None,
            "trade_counter": 1
        }
        save_config(default_config)
        return default_config

    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def save_config(config):
    """Save configuration to JSON file"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
