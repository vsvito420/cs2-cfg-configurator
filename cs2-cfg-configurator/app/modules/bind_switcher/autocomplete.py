# autocomplete.py – CS2 Command Autocomplete basierend auf data_loader
import json
from pathlib import Path
from PySide6.QtWidgets import QCompleter, QLineEdit
from PySide6.QtCore import QStringListModel, Qt

DATA_ROOT = Path(__file__).parent.parent.parent.parent / "data"

CATEGORY_FOLDERS = [
    "crosshair", "viewmodel", "map", "networking",
    "performance", "video", "buy-binds",
]


def _load_all_commands() -> list[str]:
    cmds = []
    for folder in CATEGORY_FOLDERS:
        p = DATA_ROOT / folder / "commands.json"
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                for item in data:
                    if isinstance(item, dict) and "command" in item:
                        cmds.append(item["command"])
            except Exception:
                pass
    # slot-Befehle und haeufige Binds
    extras = [
        *[f"slot{i}" for i in range(1, 14)],
        "noclip", "kill", "exec", "say", "buy",
        "cl_righthand", "toggle", "incrementvar",
    ]
    return sorted(set(cmds + extras))


ALL_COMMANDS: list[str] = _load_all_commands()


def attach_completer(line_edit: QLineEdit) -> None:
    """Haengt einen Autocompleter an ein QLineEdit.
    Komplettiert nur das letzte Token (nach Semikolon/Leerzeichen).
    """
    model = QStringListModel(ALL_COMMANDS)
    comp = QCompleter(model, line_edit)
    comp.setCaseSensitivity(Qt.CaseInsensitive)
    comp.setFilterMode(Qt.MatchContains)
    comp.setCompletionMode(QCompleter.PopupCompletion)
    comp.popup().setStyleSheet("""
        background: #313244; color: #cdd6f4;
        border: 1px solid #89b4fa; border-radius: 4px;
        font-size: 12px;
    """)

    def _on_activated(text: str):
        current = line_edit.text()
        # Letztes Token ersetzen
        parts = current.replace(';', ' ;').split()
        # finde letzte nicht-Semikolon-Einheit
        for i in range(len(parts) - 1, -1, -1):
            if parts[i] != ';':
                parts[i] = text
                break
        else:
            parts = [text]
        line_edit.setText(' '.join(parts))

    comp.activated.connect(_on_activated)
    line_edit.setCompleter(comp)
