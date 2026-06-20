# buy_binds/view.py
# UI analog zur Web-Version: Taste + Team-Filter, dann Checkboxen fuer Waffen/Utility
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QLineEdit, QScrollArea, QFrame,
    QGroupBox, QGridLayout, QMessageBox,
)
from PySide6.QtCore import Qt

from app.modules.buy_binds.loader import get_weapons, get_utility, get_keys, get_all_key_strings
from app.modules.buy_binds.completer_input import CompleterLineEdit
from app.modules.buy_binds.generator import generate_cfg

OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "configs" / "buy-binds"

STYLE_CB = "QCheckBox { color: #cdd6f4; font-size: 12px; } QCheckBox:disabled { color: #555; }"
STYLE_GROUP = """
    QGroupBox {
        color: #cdd6f4; border: 1px solid #313244;
        border-radius: 6px; margin-top: 8px; padding: 10px;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
"""


class BuyBindsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._checkboxes: dict[str, QCheckBox] = {}  # id -> QCheckBox
        self._build_ui()
        self._apply_team_filter()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)
        root.setAlignment(Qt.AlignTop)

        # Titel
        title = QLabel("🛒 Buy Bind Generator")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #cdd6f4;")
        root.addWidget(title)

        # --- Taste + Team ---
        top_row = QHBoxLayout()

        key_label = QLabel("Bind-Taste:")
        key_label.setStyleSheet("color: #cdd6f4;")
        key_strings = get_all_key_strings()
        self._key_input = CompleterLineEdit(suggestions=key_strings)
        self._key_input.setPlaceholderText("z.B. f1, kp_1, mouse4  [Tab = Autocomplete]")
        self._key_input.setFixedWidth(280)
        self._key_input.setStyleSheet(
            "background: #313244; color: #cdd6f4; border: 1px solid #444;"
            "border-radius: 4px; padding: 4px 8px;"
        )

        team_label = QLabel("Team:")
        team_label.setStyleSheet("color: #cdd6f4;")
        self._team_combo = QComboBox()
        self._team_combo.addItems(["Both", "T", "CT"])
        self._team_combo.setFixedWidth(90)
        self._team_combo.setStyleSheet(
            "background: #313244; color: #cdd6f4; border: 1px solid #444; border-radius: 4px;"
        )
        self._team_combo.currentTextChanged.connect(self._apply_team_filter)

        top_row.addWidget(key_label)
        top_row.addWidget(self._key_input)
        top_row.addSpacing(20)
        top_row.addWidget(team_label)
        top_row.addWidget(self._team_combo)
        top_row.addStretch()
        root.addLayout(top_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #313244;")
        root.addWidget(sep)

        # Scrollbereich fuer Waffen + Utility
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setSpacing(12)
        inner_layout.setAlignment(Qt.AlignTop)

        # Waffen nach Kategorie gruppiert
        categories = {}
        for w in get_weapons():
            categories.setdefault(w["category"], []).append(w)

        CAT_LABELS = {
            "rifle": "Rifles", "sniper": "Snipers", "smg": "SMGs",
            "shotgun": "Shotguns", "heavy": "Heavy", "pistol": "Pistols",
        }
        for cat, items in categories.items():
            group = QGroupBox(CAT_LABELS.get(cat, cat.title()))
            group.setStyleSheet(STYLE_GROUP)
            grid = QGridLayout(group)
            grid.setSpacing(6)
            for idx, item in enumerate(items):
                cb = QCheckBox(f"{item['label']}  ")  
                cb.setStyleSheet(STYLE_CB)
                cb.setProperty("item_data", item)
                self._checkboxes[item["id"]] = cb
                grid.addWidget(cb, idx // 3, idx % 3)
            inner_layout.addWidget(group)

        # Utility
        util_group = QGroupBox("Utility & Equipment")
        util_group.setStyleSheet(STYLE_GROUP)
        util_grid = QGridLayout(util_group)
        util_grid.setSpacing(6)
        for idx, item in enumerate(get_utility()):
            cb = QCheckBox(f"{item['label']}  ")
            cb.setStyleSheet(STYLE_CB)
            cb.setProperty("item_data", item)
            self._checkboxes[item["id"]] = cb
            util_grid.addWidget(cb, idx // 3, idx % 3)
        inner_layout.addWidget(util_group)

        # Output-Preview
        preview_group = QGroupBox("Output Vorschau")
        preview_group.setStyleSheet(STYLE_GROUP)
        preview_layout = QVBoxLayout(preview_group)
        self._preview_label = QLabel('bind "" ""')
        self._preview_label.setStyleSheet(
            "font-family: monospace; color: #a6e3a1; font-size: 12px;"
            "background: #11111b; padding: 8px; border-radius: 4px;"
        )
        self._preview_label.setWordWrap(True)
        preview_layout.addWidget(self._preview_label)
        inner_layout.addWidget(preview_group)

        scroll.setWidget(inner)
        root.addWidget(scroll, 1)

        # Buttons unten
        btn_row = QHBoxLayout()

        preview_btn = QPushButton("🔍 Vorschau")
        preview_btn.setStyleSheet("background: #313244; color: #cdd6f4; border-radius: 4px; padding: 6px 14px;")
        preview_btn.clicked.connect(self._update_preview)

        self._filename_input = QLineEdit()
        self._filename_input.setPlaceholderText("Dateiname (z.B. pistol_setup)")
        self._filename_input.setStyleSheet(
            "background: #313244; color: #cdd6f4; border: 1px solid #444;"
            "border-radius: 4px; padding: 4px 8px;"
        )

        save_btn = QPushButton("💾 CFG speichern")
        save_btn.setStyleSheet(
            "background: #cba6f7; color: #1e1e2e; font-weight: bold;"
            "border-radius: 4px; padding: 6px 16px;"
        )
        save_btn.clicked.connect(self._save_cfg)

        btn_row.addWidget(preview_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._filename_input)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

    def _apply_team_filter(self):
        """Versteckt/deaktiviert Items die nicht zum gewaehlten Team gehoeren."""
        team = self._team_combo.currentText()
        for item_id, cb in self._checkboxes.items():
            data = cb.property("item_data")
            allowed = data["team"] == "Both" or data["team"] == team
            cb.setEnabled(allowed)
            if not allowed:
                cb.setChecked(False)

    def _collect_commands(self) -> list[str] | None:
        """Sammelt alle gecheckte Items, validiert Limits."""
        team = self._team_combo.currentText()
        group_counts: dict[str, int] = {}
        cmds = []
        for cb in self._checkboxes.values():
            if not cb.isChecked():
                continue
            data = cb.property("item_data")
            group = data.get("group", data["id"])
            max_allowed = data.get("max", 99)
            group_counts[group] = group_counts.get(group, 0) + 1
            if group_counts[group] > max_allowed:
                QMessageBox.warning(
                    self, "Limit ueberschritten",
                    f"Zu viele von: {data['label']}\nMax erlaubt: {max_allowed}"
                )
                return None
            cmds.append(data["cmd"])
        return cmds

    def _update_preview(self):
        key = self._key_input.text().strip() or "?"
        cmds = self._collect_commands()
        if cmds is None:
            return
        cmd_str = "; ".join(cmds) if cmds else ""
        self._preview_label.setText(f'bind "{key}" "{cmd_str}"')

    def _save_cfg(self):
        key = self._key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Fehler", "Bitte eine Taste eingeben.")
            return
        cmds = self._collect_commands()
        if cmds is None:
            return
        if not cmds:
            QMessageBox.information(self, "Leer", "Keine Items ausgewaehlt.")
            return

        filename = self._filename_input.text().strip() or "buy_binds"
        if not filename.endswith(".cfg"):
            filename += ".cfg"

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = OUTPUT_DIR / filename
        generate_cfg([{"key": key, "commands": cmds}], out_path)
        QMessageBox.information(self, "Gespeichert", f"CFG gespeichert:\n{out_path}")
        self._update_preview()
