# settings_manager.py
# Verwaltet App-Einstellungen (Farben, Sidebar-Breite etc.) via JSON
import json
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent.parent / "configs" / "app_settings.json"

DEFAULTS = {
    "sidebar_bg": "#1e1e2e",
    "sidebar_text": "#cdd6f4",
    "sidebar_selected_bg": "#313244",
    "sidebar_selected_text": "#cba6f7",
    "sidebar_hover_bg": "#2a2a3d",
    "sidebar_width": 210,
}


def load() -> dict:
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
            return {**DEFAULTS, **data}
        except Exception:
            pass
    return dict(DEFAULTS)


def save(settings: dict):
    SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
