# buy_binds/view.py
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QScrollArea, QFrame, QGridLayout, QMessageBox,
)
from PySide6.QtCore import Qt
from app.modules.buy_binds.data import KEYS, PRIMARY, SECONDARY, GRENADES
from app.modules.buy_binds.generator import generate_cfg

OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "configs" / "buy-binds"


class BuyBindRow(QWidget):
    """Eine Zeile: Taste -> Waffe/Utility Auswahl"""
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        self.key_combo = QComboBox()
        self.key_combo.addItems(KEYS)
        self.key_combo.setFixedWidth(80)

        arrow = QLabel("→")
        arrow.setFixedWidth(20)
        arrow.setAlignment(Qt.AlignCenter)

        self.primary_combo = QComboBox()
        self.primary_combo.addItem("– keine Primärwaffe –", None)
        for name, cmd in PRIMARY:
            self.primary_combo.addItem(name, cmd)

        self.secondary_combo = QComboBox()
        self.secondary_combo.addItem("– keine Sekundärwaffe –", None)
        for name, cmd in SECONDARY:
            self.secondary_combo.addItem(name, cmd)

        self.grenade_combos = []
        for _ in range(4):
            cb = QComboBox()
            cb.addItem("–", None)
            for name, cmd in GRENADES:
                cb.addItem(name, cmd)
            self.grenade_combos.append(cb)

        remove_btn = QPushButton("✕")
        remove_btn.setFixedWidth(28)
        remove_btn.setStyleSheet("color: #f38ba8; border: none; font-size: 14px;")
        remove_btn.clicked.connect(self._remove)

        layout.addWidget(self.key_combo)
        layout.addWidget(arrow)
        layout.addWidget(self.primary_combo)
        layout.addWidget(self.secondary_combo)
        for cb in self.grenade_combos:
            layout.addWidget(cb)
        layout.addWidget(remove_btn)

    def _remove(self):
        self.setParent(None)
        self.deleteLater()

    def get_bind(self) -> dict | None:
        """Gibt das Bind als dict zurück, None wenn nichts ausgewählt."""
        key = self.key_combo.currentText()
        primary = self.primary_combo.currentData()
        secondary = self.secondary_combo.currentData()
        grenades = [cb.currentData() for cb in self.grenade_combos if cb.currentData()]

        # Grenade Limit: max 2 Flash, max 1 Smoke, max 1 Molotov/Incendiary
        flash_count = grenades.count("buy flashbang")
        smoke_count = grenades.count("buy smokegrenade")
        molotov_count = sum(1 for g in grenades if g in ("buy molotov", "buy incgrenade"))
        if flash_count > 2 or smoke_count > 1 or molotov_count > 1:
            return "invalid"

        buys = [c for c in [primary, secondary] + grenades if c]
        if not buys:
            return None
        return {"key": key, "commands": buys}


class BuyBindsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(12)

        title = QLabel("🛒 Buy Binds")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #cdd6f4;")
        root.addWidget(title)

        # Header-Leiste
        header = QWidget()
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(0, 0, 0, 0)
        for text in ["Taste", "", "Primär", "Sekundär", "Flash 1", "Flash 2", "Smoke", "Molotov", ""]:
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #888; font-size: 11px;")
            if text in ("",):
                lbl.setFixedWidth(20 if text == "" else 28)
            h_layout.addWidget(lbl)
        root.addWidget(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #313244;")
        root.addWidget(line)

        # Scrollbereich für Bind-Zeilen
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        self._rows_container = QWidget()
        self._rows_layout = QVBoxLayout(self._rows_container)
        self._rows_layout.setAlignment(Qt.AlignTop)
        self._rows_layout.setSpacing(4)
        scroll.setWidget(self._rows_container)
        root.addWidget(scroll, 1)

        # Buttons unten
        btn_row = QHBoxLayout()
        add_btn = QPushButton("+ Bind hinzufügen")
        add_btn.setStyleSheet("background: #313244; color: #cdd6f4; border-radius: 4px; padding: 6px 12px;")
        add_btn.clicked.connect(self._add_row)

        self._filename_input = QLineEdit()
        self._filename_input.setPlaceholderText("Dateiname (z.B. pistol_setup)")
        self._filename_input.setStyleSheet("background: #313244; color: #cdd6f4; border: 1px solid #444; border-radius: 4px; padding: 4px 8px;")

        save_btn = QPushButton("💾 CFG generieren")
        save_btn.setStyleSheet("background: #cba6f7; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 6px 16px;")
        save_btn.clicked.connect(self._generate)

        btn_row.addWidget(add_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._filename_input)
        btn_row.addWidget(save_btn)
        root.addLayout(btn_row)

    def _add_row(self):
        row = BuyBindRow()
        self._rows_layout.addWidget(row)

    def _generate(self):
        filename = self._filename_input.text().strip() or "buy_binds"
        if not filename.endswith(".cfg"):
            filename += ".cfg"

        binds = []
        for i in range(self._rows_layout.count()):
            widget = self._rows_layout.itemAt(i).widget()
            if isinstance(widget, BuyBindRow):
                result = widget.get_bind()
                if result == "invalid":
                    QMessageBox.warning(self, "Ungültiges Bind",
                        "Grenade-Limit überschritten!\nMax: 2x Flash, 1x Smoke, 1x Molotov")
                    return
                if result:
                    binds.append(result)

        if not binds:
            QMessageBox.information(self, "Keine Binds", "Füge zuerst Binds hinzu.")
            return

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        out_path = OUTPUT_DIR / filename
        generate_cfg(binds, out_path)
        QMessageBox.information(self, "Gespeichert", f"CFG gespeichert:\n{out_path}")
