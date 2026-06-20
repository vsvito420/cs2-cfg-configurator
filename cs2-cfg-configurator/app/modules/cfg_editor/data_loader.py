# cfg_editor/data_loader.py
# Laedt commands.json fuer jede Kategorie aus data/<kategorie>/commands.json
import json
from pathlib import Path

DATA_ROOT = Path(__file__).parent.parent.parent.parent / "data"

CATEGORY_META = {
    "crosshair":   {"label": "🎯 Crosshair",           "folder": "crosshair"},
    "viewmodel":   {"label": "🔫 Viewmodel",           "folder": "viewmodel"},
    "map":         {"label": "🗺️  Map / Radar",         "folder": "map"},
    "networking":  {"label": "🌐 Networking",           "folder": "networking"},
    "performance": {"label": "⚡ Performance",          "folder": "performance"},
    "video":       {"label": "🖥️  Video",               "folder": "video"},
    "buy-binds":   {"label": "🛒 Buy Binds",            "folder": "buy-binds"},
}


def load_category(category_key: str) -> list[dict]:
    """Gibt Liste von {command, default, range, description} zurueck."""
    folder = CATEGORY_META[category_key]["folder"]
    path = DATA_ROOT / folder / "commands.json"
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def available_categories() -> list[str]:
    """Nur Kategorien zurueckgeben die eine commands.json haben."""
    result = []
    for key, meta in CATEGORY_META.items():
        p = DATA_ROOT / meta["folder"] / "commands.json"
        if p.exists():
            result.append(key)
    return result
