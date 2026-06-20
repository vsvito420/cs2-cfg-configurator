# reader.py – Liest CS2-Einstellungen aus Steam userdata
import os
import sys
import string
from pathlib import Path


def find_steam_userdata() -> Path | None:
    """Sucht Steam userdata auf Windows, macOS, Linux – inkl. aller Laufwerke."""
    candidates = []

    if sys.platform == "win32":
        # Standard-Pfade
        for env in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA"):
            base = os.environ.get(env, "")
            if base:
                candidates.append(Path(base) / "Steam" / "userdata")
        # Alle Laufwerke (fuer Steam Libraries auf anderen Festplatten)
        for drive in string.ascii_uppercase:
            for sub in ("SteamLibrary", "Steam", "Games\\Steam"):
                candidates.append(Path(f"{drive}:\\") / sub / "userdata")
    elif sys.platform == "darwin":
        candidates.append(Path.home() / "Library" / "Application Support" / "Steam" / "userdata")
    else:
        for base in (Path.home() / ".steam" / "steam", Path.home() / ".local" / "share" / "Steam"):
            candidates.append(base / "userdata")

    for p in candidates:
        if p.exists():
            return p
    return None


def find_cs2_steam_ids(userdata: Path) -> list[str]:
    """Gibt alle Steam-IDs zurueck die CS2 (AppID 730) installiert haben."""
    ids = []
    if not userdata or not userdata.exists():
        return ids
    for entry in userdata.iterdir():
        if entry.is_dir() and entry.name.isdigit():
            if (entry / "730").exists():
                ids.append(entry.name)
    return ids


def parse_vcfg(filepath: Path) -> dict[str, str]:
    """
    Parst .vcfg Dateien (convars & keys).
    Format: setcommand "key" "value"
    Fallback: erkennt auch einfaches key "value" Format.
    """
    result = {}
    if not filepath or not filepath.exists():
        return result
    with filepath.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            # Format: setcommand "key" "value"
            if line.startswith("setcommand"):
                parts = line.split('"')
                if len(parts) >= 4:
                    result[parts[1]] = parts[3]
            # Fallback: "key" "value"
            elif line.startswith('"'):
                parts = line.split('"')
                if len(parts) >= 4:
                    result[parts[1]] = parts[3]
    return result


def parse_video(filepath: Path) -> dict[str, str]:
    """
    Parst cs2_video.txt.
    Format: "key" "value" (mit Anfuehrungszeichen) oder key value
    """
    result = {}
    if not filepath or not filepath.exists():
        return result
    with filepath.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//") or line in ("{", "}"):
                continue
            # Format mit Anfuehrungszeichen: "key"\t"value"
            if line.startswith('"'):
                parts = line.split('"')
                if len(parts) >= 4:
                    result[parts[1]] = parts[3]
            # Format ohne: key value
            else:
                parts = line.split()
                if len(parts) >= 2:
                    result[parts[0].strip('"')] = parts[1].strip('"')
    return result


def read_all_for_id(userdata: Path, steam_id: str) -> dict:
    """Liest convars, keys und video fuer eine Steam-ID."""
    base = userdata / steam_id / "730" / "local" / "cfg"
    return {
        "convars": parse_vcfg(base / "cs2_user_convars_0_slot0.vcfg"),
        "keys":    parse_vcfg(base / "cs2_user_keys_0_slot0.vcfg"),
        "video":   parse_video(base / "cs2_video.txt"),
        "base_path": str(base),
    }
