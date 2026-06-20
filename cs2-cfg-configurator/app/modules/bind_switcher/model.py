# model.py – Datenmodelle fuer alle Bind-Typen
from dataclasses import dataclass, field
from enum import Enum


class BindType(str, Enum):
    SIMPLE = "simple"       # bind "key" "command"
    TOGGLE = "toggle"       # alias toggle zwischen 2 States
    HOLD   = "hold"         # +alias / -alias
    CFG    = "cfg"          # exec <cfg-datei>


@dataclass
class SimpleBind:
    key: str = ""
    command: str = ""
    description: str = ""


@dataclass
class ToggleBind:
    key: str = ""
    alias_name: str = ""        # z.B. "toggle_crosshair"
    state_a_cmds: str = ""      # Befehle fuer State A
    state_b_cmds: str = ""      # Befehle fuer State B
    description: str = ""


@dataclass
class HoldBind:
    key: str = ""
    alias_name: str = ""        # z.B. "radar_zoom"
    press_cmds: str = ""        # Befehle beim Druecken (+)
    release_cmds: str = ""      # Befehle beim Loslassen (-)
    description: str = ""


@dataclass
class CfgBind:
    key: str = ""
    cfg_file: str = ""          # z.B. "crosshairA.cfg"
    description: str = ""


@dataclass
class BindProfile:
    name: str = "My Binds"
    simple_binds: list = field(default_factory=list)
    toggle_binds: list = field(default_factory=list)
    hold_binds:   list = field(default_factory=list)
    cfg_binds:    list = field(default_factory=list)
