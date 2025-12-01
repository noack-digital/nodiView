"""
Simple configuration helper for nodiView.
"""

from __future__ import annotations

import json
from pathlib import Path

from gi.repository import GLib

DEFAULT_CONFIG = {"language": "en"}

CONFIG_DIR = Path(GLib.get_user_config_dir()) / "nodiview"
CONFIG_FILE = CONFIG_DIR / "config.json"


def load_config() -> dict:
    """Load configuration from disk."""
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return {**DEFAULT_CONFIG, **data}
        except (json.JSONDecodeError, OSError):
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()


def save_config(config: dict) -> None:
    """Persist configuration to disk."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")

