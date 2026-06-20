# model.py – Datenmodelle fuer alle Bind-Typen
from dataclasses import dataclass, field


@dataclass
class SimpleBind:
    key: str = ""
    command: str = ""
    description: str = ""


@dataclass
class ToggleBind:
    key: str = ""
    alias_name: str = ""
    state_a_cmds: str = ""
    state_b_cmds: str = ""
    description: str = ""


@dataclass
class HoldBind:
    key: str = ""
    alias_name: str = ""
    before_cmds: str = ""   # Default-State (wird beim Start gesetzt)
    press_cmds: str = ""    # +alias (while pressing)
    release_cmds: str = ""  # -alias (after released)
    description: str = ""


@dataclass
class CfgBind:
    key: str = ""
    exec_type: str = "simple"   # simple | hold | toggle
    cfg_file: str = ""          # simple
    cfg_press: str = ""         # hold: beim Druecken
    cfg_release: str = ""       # hold: beim Loslassen
    cfg_file_a: str = ""        # toggle: State A
    cfg_file_b: str = ""        # toggle: State B
    description: str = ""


@dataclass
class BindProfile:
    name: str = "My Binds"
    simple_binds: list = field(default_factory=list)
    toggle_binds: list = field(default_factory=list)
    hold_binds:   list = field(default_factory=list)
    cfg_binds:    list = field(default_factory=list)
