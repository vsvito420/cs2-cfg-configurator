# buy_binds/loader.py
# Laedt Waffen, Utility und Keys aus JSON-Dateien.
# Neue Eintraege einfach in data/buy_binds/*.json hinzufuegen.
import json
from pathlib import Path
from functools import lru_cache

_DATA_DIR = Path(__file__).parent.parent.parent.parent / "data" / "buy_binds"


@lru_cache(maxsize=None)
def get_weapons() -> list[dict]:
    return json.loads((_DATA_DIR / "weapons.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def get_utility() -> list[dict]:
    return json.loads((_DATA_DIR / "utility.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def get_keys() -> list[dict]:
    return json.loads((_DATA_DIR / "keys.json").read_text(encoding="utf-8"))


def get_all_labels() -> list[str]:
    """Alle Anzeigenamen fuer spaeteres Tab-Autocomplete."""
    weapons = [w["label"] for w in get_weapons()]
    utility = [u["label"] for u in get_utility()]
    return sorted(set(weapons + utility))


def get_all_key_strings() -> list[str]:
    """Alle Tastennamen fuer spaeteres Tab-Autocomplete."""
    return [k["key"] for k in get_keys()]
