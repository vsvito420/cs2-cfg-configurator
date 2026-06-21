# reader.py – Liest CS2-Einstellungen aus Steam userdata
import os
import sys
import string
from pathlib import Path


def find_steam_userdata() -> Path | None:
    candidates = []
    if sys.platform == "win32":
        for env in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA"):
            base = os.environ.get(env, "")
            if base:
                candidates.append(Path(base) / "Steam" / "userdata")
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
    ids = []
    if not userdata or not userdata.exists():
        return ids
    for entry in userdata.iterdir():
        if entry.is_dir() and entry.name.isdigit():
            if (entry / "730").exists():
                ids.append(entry.name)
    return ids


def get_account_name(userdata: Path, steam_id: str) -> str:
    """
    Versucht den Steam-Accountnamen aus localconfig.vdf zu lesen.
    Gibt den Namen zurueck oder '' wenn nicht gefunden.
    """
    # localconfig.vdf liegt in userdata/<id>/config/localconfig.vdf
    cfg = userdata / steam_id / "config" / "localconfig.vdf"
    if not cfg.exists():
        return ""
    try:
        with cfg.open(encoding="utf-8", errors="ignore") as f:
            for line in f:
                stripped = line.strip().lower()
                # Suche nach: "PersonaName"	"vsvito420"
                if '"personaname"' in stripped:
                    parts = line.split('"')
                    # parts: ["", "PersonaName", "\t", "vsvito420", ...]
                    if len(parts) >= 4:
                        return parts[3]
    except Exception:
        pass
    # Fallback: name aus convars
    convars_file = userdata / steam_id / "730" / "local" / "cfg" / "cs2_user_convars_0_slot0.vcfg"
    if convars_file.exists():
        try:
            with convars_file.open(encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if '"name"' in line.lower():
                        parts = line.split('"')
                        if len(parts) >= 4:
                            return parts[3]
        except Exception:
            pass
    return ""


def parse_vcfg(filepath: Path) -> dict[str, str]:
    result = {}
    if not filepath or not filepath.exists():
        return result
    with filepath.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            if line.startswith("setcommand"):
                parts = line.split('"')
                if len(parts) >= 4:
                    result[parts[1]] = parts[3]
            elif line.startswith('"'):
                parts = line.split('"')
                if len(parts) >= 4:
                    result[parts[1]] = parts[3]
    return result


def parse_video(filepath: Path) -> dict[str, str]:
    result = {}
    if not filepath or not filepath.exists():
        return result
    with filepath.open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//") or line in ("{", "}"):
                continue
            if line.startswith('"'):
                parts = line.split('"')
                if len(parts) >= 4:
                    result[parts[1]] = parts[3]
            else:
                parts = line.split()
                if len(parts) >= 2:
                    result[parts[0].strip('"')] = parts[1].strip('"')
    return result


def read_all_for_id(userdata: Path, steam_id: str) -> dict:
    base = userdata / steam_id / "730" / "local" / "cfg"
    convars = parse_vcfg(base / "cs2_user_convars_0_slot0.vcfg")
    keys    = parse_vcfg(base / "cs2_user_keys_0_slot0.vcfg")
    video   = parse_video(base / "cs2_video.txt")
    name    = get_account_name(userdata, steam_id)
    return {
        "convars": convars,
        "keys":    keys,
        "video":   video,
        "name":    name,
        "base_path": str(base),
        "convars_file": str(base / "cs2_user_convars_0_slot0.vcfg"),
        "keys_file":    str(base / "cs2_user_keys_0_slot0.vcfg"),
        "video_file":   str(base / "cs2_video.txt"),
    }
