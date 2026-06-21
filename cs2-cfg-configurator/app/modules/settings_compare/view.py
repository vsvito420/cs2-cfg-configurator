# view.py – Modul: Aktive Settings vergleichen
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView,
    QMessageBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush, QFont

from app.modules.settings_reader.reader import (
    find_steam_userdata, find_cs2_steam_ids, read_all_for_id
)


# ── Farben ────────────────────────────────────────────────────────────────────
COL_EQUAL   = QColor("#FFFFFF")   # weiß   – identisch
COL_LESS    = QColor("#FFF176")   # gelb   – Spieler 2 kleiner
COL_GREATER = QColor("#EF9A9A")   # rot    – Spieler 2 größer
COL_DIFF    = QColor("#B0BEC5")   # grau   – text-unterschied
COL_FG      = QColor("#212121")   # dark foreground für farbige Zeilen
COL_FG_NORM = QColor("#E0E0E0")   # heller foreground für normale Zeilen


def _compare(v1: str, v2: str) -> tuple[str, QColor]:
    """Gibt (label, farbe) zurück."""
    if v1 == v2:
        return "✔  Gleich", COL_EQUAL
    try:
        n1, n2 = float(v1), float(v2)
        if n2 < n1:
            return f"↓  Weniger  ({v2} < {v1})", COL_LESS
        return f"↑  Mehr  ({v2} > {v1})", COL_GREATER
    except ValueError:
        return "≠  Verschieden", COL_DIFF


class SettingsComparePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._userdata = find_steam_userdata()
        self._ids: list[str] = find_cs2_steam_ids(self._userdata) if self._userdata else []
        self._id_labels: dict[str, str] = {}   # steam_id → "Name (id)"
        self._cache: dict[str, dict] = {}       # steam_id → read_all_for_id result
        self._build_ui()
        self._refresh_ids()

    # ── UI ───────────────────────────────────────────────────────────────────

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        # ── Titel
        title = QLabel("🔄  Aktive Settings vergleichen")
        title.setStyleSheet("font-size:18px; font-weight:bold; color:#E0E0E0;")
        root.addWidget(title)

        # ── Auswahlzeile
        sel = QHBoxLayout()
        sel.setSpacing(12)

        sel.addWidget(QLabel("Spieler 1:", styleSheet="color:#90CAF9; font-size:13px;"))
        self.cb_p1 = QComboBox()
        self.cb_p1.setMinimumWidth(220)
        self.cb_p1.setStyleSheet(self._combo_style())
        sel.addWidget(self.cb_p1)

        sel.addSpacing(20)

        sel.addWidget(QLabel("Spieler 2:", styleSheet="color:#90CAF9; font-size:13px;"))
        self.cb_p2 = QComboBox()
        self.cb_p2.setMinimumWidth(220)
        self.cb_p2.setStyleSheet(self._combo_style())
        sel.addWidget(self.cb_p2)

        sel.addStretch()

        self.btn_compare = QPushButton("▶  Vergleichen")
        self.btn_compare.setStyleSheet(self._btn_style("#3949AB"))
        self.btn_compare.clicked.connect(self._run_compare)
        sel.addWidget(self.btn_compare)

        self.btn_transfer = QPushButton("⇒  Settings übertragen  (1 → 2)")
        self.btn_transfer.setStyleSheet(self._btn_style("#2E7D32"))
        self.btn_transfer.clicked.connect(self._transfer_settings)
        sel.addWidget(self.btn_transfer)

        root.addLayout(sel)

        # ── Legende
        legend = QHBoxLayout()
        legend.setSpacing(6)
        for color, text in [
            (COL_EQUAL,   "Gleich"),
            (COL_LESS,    "Spieler 2 kleiner"),
            (COL_GREATER, "Spieler 2 größer"),
            (COL_DIFF,    "Text-Unterschied"),
        ]:
            dot = QFrame()
            dot.setFixedSize(14, 14)
            dot.setStyleSheet(f"background:{color.name()}; border-radius:3px;")
            legend.addWidget(dot)
            legend.addWidget(QLabel(text, styleSheet="color:#9E9E9E; font-size:11px;"))
            legend.addSpacing(14)
        legend.addStretch()
        root.addLayout(legend)

        # ── Tabelle
        self.tree = QTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Command", "Spieler 1", "Spieler 2", "Vergleich"])
        self.tree.setAlternatingRowColors(False)
        self.tree.setRootIsDecorated(False)
        self.tree.setSortingEnabled(True)
        self.tree.setStyleSheet("""
            QTreeWidget {
                background: #2A2A3E;
                color: #E0E0E0;
                border: 1px solid #3a3a5c;
                font-size: 12px;
                font-family: Consolas, monospace;
            }
            QHeaderView::section {
                background: #3949AB;
                color: white;
                padding: 6px;
                font-size: 12px;
                font-weight: bold;
                border: none;
            }
            QTreeWidget::item:selected { background: #4A4A6A; }
            QTreeWidget::item:hover    { background: #32324e; }
        """)
        hdr = self.tree.header()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        root.addWidget(self.tree, 1)

        # ── Status
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet("color:#78909C; font-size:11px;")
        root.addWidget(self.lbl_status)

    # ── IDs laden ─────────────────────────────────────────────────────────────

    def _refresh_ids(self):
        self.cb_p1.clear()
        self.cb_p2.clear()
        if not self._ids:
            self.lbl_status.setText("⚠  Keine Steam-IDs mit CS2-Daten gefunden.")
            return
        for sid in self._ids:
            data = self._get_cached(sid)
            name = data.get("name", "") or sid
            label = f"{name}  ({sid})"
            self._id_labels[sid] = label
            self.cb_p1.addItem(label, userData=sid)
            self.cb_p2.addItem(label, userData=sid)
        if len(self._ids) > 1:
            self.cb_p2.setCurrentIndex(1)

    def _get_cached(self, sid: str) -> dict:
        if sid not in self._cache:
            self._cache[sid] = read_all_for_id(self._userdata, sid) if self._userdata else {}
        return self._cache[sid]

    # ── Vergleich ─────────────────────────────────────────────────────────────

    def _run_compare(self):
        p1 = self.cb_p1.currentData()
        p2 = self.cb_p2.currentData()
        if not p1 or not p2:
            QMessageBox.warning(self, "Auswahl fehlt", "Bitte beide Spieler auswählen.")
            return
        if p1 == p2:
            QMessageBox.warning(self, "Gleiche ID", "Bitte zwei verschiedene Spieler auswählen.")
            return

        d1 = self._get_cached(p1)
        d2 = self._get_cached(p2)

        self.tree.clear()

        sections = [
            ("convars", "⚙  Convars"),
            ("keys",    "🔗  Keybinds"),
            ("video",   "🎥  Video"),
        ]

        total = 0
        diff_count = 0

        for sec_key, sec_label in sections:
            cfg1: dict = d1.get(sec_key, {})
            cfg2: dict = d2.get(sec_key, {})
            all_keys = sorted(set(cfg1) | set(cfg2))
            if not all_keys:
                continue

            # Kategorie-Header
            header_item = QTreeWidgetItem([sec_label, "", "", ""])
            header_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            hfont = QFont()
            hfont.setBold(True)
            hfont.setPointSize(11)
            for col in range(4):
                header_item.setFont(col, hfont)
                header_item.setForeground(col, QBrush(QColor("#CBA6F7")))
                header_item.setBackground(col, QBrush(QColor("#1a1a2e")))
            self.tree.addTopLevelItem(header_item)

            for cmd in all_keys:
                v1 = cfg1.get(cmd, "—")
                v2 = cfg2.get(cmd, "—")
                label, color = _compare(str(v1), str(v2))
                total += 1
                if v1 != v2:
                    diff_count += 1

                item = QTreeWidgetItem([cmd, str(v1), str(v2), label])
                item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
                item.setTextAlignment(2, Qt.AlignmentFlag.AlignCenter)
                item.setTextAlignment(3, Qt.AlignmentFlag.AlignCenter)

                # Nur die Vergleichsspalte (3) einfärben
                item.setBackground(3, QBrush(color))
                item.setForeground(3, QBrush(COL_FG))

                self.tree.addTopLevelItem(item)

        self.tree.expandAll()
        name1 = d1.get("name", p1) or p1
        name2 = d2.get("name", p2) or p2
        self.lbl_status.setText(
            f"Verglichen: {name1} vs {name2}  |  {total} Commands gesamt  |  {diff_count} Unterschiede"
        )

    # ── Transfer ─────────────────────────────────────────────────────────────

    def _transfer_settings(self):
        import shutil
        from pathlib import Path

        p1 = self.cb_p1.currentData()
        p2 = self.cb_p2.currentData()
        if not p1 or not p2:
            QMessageBox.warning(self, "Auswahl fehlt", "Bitte beide Spieler auswählen.")
            return
        if p1 == p2:
            QMessageBox.warning(self, "Gleiche ID", "Quelle und Ziel sind identisch.")
            return

        d1 = self._get_cached(p1)
        d2 = self._get_cached(p2)
        name1 = d1.get("name", p1) or p1
        name2 = d2.get("name", p2) or p2

        ans = QMessageBox.question(
            self,
            "Settings übertragen",
            f"Alle CS2-Config-Dateien von\n\n  {name1}  ({p1})\n\nauf\n\n  {name2}  ({p2})\n\n"
            f"kopieren?\n\nAchtung: bestehende Dateien von Spieler 2 werden überschrieben!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if ans != QMessageBox.StandardButton.Yes:
            return

        src_base = Path(d1.get("base_path", ""))
        dst_base = Path(d2.get("base_path", ""))

        if not src_base.exists():
            QMessageBox.critical(self, "Fehler", f"Quellpfad nicht gefunden:\n{src_base}")
            return
        if not dst_base.exists():
            dst_base.mkdir(parents=True, exist_ok=True)

        files_to_copy = [
            "cs2_user_convars_0_slot0.vcfg",
            "cs2_user_keys_0_slot0.vcfg",
            "cs2_video.txt",
        ]
        copied = []
        errors = []
        for fname in files_to_copy:
            src = src_base / fname
            dst = dst_base / fname
            if src.exists():
                try:
                    shutil.copy2(src, dst)
                    copied.append(fname)
                except Exception as e:
                    errors.append(f"{fname}: {e}")

        # Cache für p2 invalidieren
        self._cache.pop(p2, None)

        msg = f"{len(copied)} Datei(en) erfolgreich kopiert:\n" + "\n".join(f"  ✔ {f}" for f in copied)
        if errors:
            msg += "\n\nFehler:\n" + "\n".join(f"  ✖ {e}" for e in errors)
            QMessageBox.warning(self, "Transfer mit Fehlern", msg)
        else:
            QMessageBox.information(self, "Fertig", msg)

        self._run_compare()

    # ── Styles ────────────────────────────────────────────────────────────────

    @staticmethod
    def _btn_style(bg: str) -> str:
        return f"""
            QPushButton {{
                background: {bg}; color: white;
                border: none; border-radius: 5px;
                padding: 6px 14px; font-size: 12px; font-weight: bold;
            }}
            QPushButton:hover  {{ background: {bg}cc; }}
            QPushButton:pressed {{ background: {bg}99; }}
        """

    @staticmethod
    def _combo_style() -> str:
        return """
            QComboBox {
                background: #313244; color: #E0E0E0;
                border: 1px solid #4a4a6a; border-radius: 4px;
                padding: 4px 8px; font-size: 12px;
            }
            QComboBox QAbstractItemView {
                background: #313244; color: #E0E0E0;
                selection-background-color: #4A4A6A;
            }
        """
