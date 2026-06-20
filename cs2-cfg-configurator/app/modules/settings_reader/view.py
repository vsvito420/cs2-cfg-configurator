# settings_reader/view.py – CS2 Aktive Einstellungen Viewer
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QSplitter, QTreeWidget, QTreeWidgetItem,
    QComboBox, QLineEdit, QSizePolicy, QScrollArea
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QColor, QFont

from .reader import find_steam_userdata, find_cs2_steam_ids, read_all_for_id

# ── Styles ─────────────────────────────────────────────────────────────────
STYLE_TREE = """
    QTreeWidget {
        background: #1e1e2e; color: #cdd6f4;
        border: none; font-size: 12px; outline: none;
        font-family: 'Consolas', monospace;
    }
    QTreeWidget::item { padding: 4px 8px; }
    QTreeWidget::item:hover { background: #313244; border-radius: 4px; }
    QTreeWidget::item:selected { background: #45475a; color: #cdd6f4; }
    QTreeWidget::branch { background: #1e1e2e; }
    QHeaderView::section {
        background: #181825; color: #6c7086; border: none;
        padding: 6px 8px; font-size: 11px;
        border-bottom: 1px solid #313244;
    }
"""
INPUT_STYLE = """
    QLineEdit {
        background: #313244; color: #cdd6f4;
        border: 1px solid #45475a; border-radius: 6px;
        padding: 7px 12px; font-size: 12px;
    }
    QLineEdit:focus { border: 1px solid #89b4fa; }
"""
COMBO_STYLE = """
    QComboBox {
        background: #313244; color: #cdd6f4;
        border: 1px solid #45475a; border-radius: 6px;
        padding: 6px 12px; font-size: 12px; min-width: 160px;
    }
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView {
        background: #313244; color: #cdd6f4;
        selection-background-color: #45475a;
        border: 1px solid #45475a;
    }
"""
STYLE_BTN = """
    QPushButton {
        background: #313244; color: #cdd6f4; border: none;
        border-radius: 6px; padding: 7px 16px; font-size: 12px;
    }
    QPushButton:hover { background: #45475a; }
"""
STYLE_RELOAD = """
    QPushButton {
        background: #89b4fa; color: #1e1e2e; border: none;
        border-radius: 6px; padding: 7px 16px; font-size: 12px; font-weight: bold;
    }
    QPushButton:hover { background: #b4d0ff; }
"""

SECTION_COLORS = {
    "convars": "#89b4fa",
    "keys":    "#a6e3a1",
    "video":   "#fab387",
}
SECTION_LABELS = {
    "convars": ("⚙️", "Aktive Convars",      "cs2_user_convars_0_slot0.vcfg"),
    "keys":    ("⌨️", "Tastenbelegungen",    "cs2_user_keys_0_slot0.vcfg"),
    "video":   ("🖥️", "Video-Einstellungen", "cs2_video.txt"),
}


class SettingsReaderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._userdata: Path | None = None
        self._steam_ids: list[str] = []
        self._data: dict = {}           # {steam_id: {convars, keys, video}}
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._apply_filter)
        self._build()
        self._scan()

    # ── Build UI ─────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Toolbar ──
        toolbar = QFrame()
        toolbar.setFixedHeight(54)
        toolbar.setStyleSheet("background:#181825; border-bottom:1px solid #313244;")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(16, 8, 16, 8)
        tb.setSpacing(10)

        title = QLabel("📶  Aktive CS2-Einstellungen")
        title.setStyleSheet("color:#cdd6f4; font-size:14px; font-weight:bold;")
        tb.addWidget(title)
        tb.addStretch()

        # Account-Auswahl
        acc_lbl = QLabel("Account:")
        acc_lbl.setStyleSheet("color:#6c7086; font-size:12px;")
        self._id_combo = QComboBox()
        self._id_combo.setStyleSheet(COMBO_STYLE)
        self._id_combo.currentIndexChanged.connect(self._on_id_changed)
        tb.addWidget(acc_lbl)
        tb.addWidget(self._id_combo)

        # Kategorie-Filter
        cat_lbl = QLabel("Zeige:")
        cat_lbl.setStyleSheet("color:#6c7086; font-size:12px;")
        self._cat_combo = QComboBox()
        self._cat_combo.setStyleSheet(COMBO_STYLE)
        self._cat_combo.addItem("📋  Alles", "all")
        self._cat_combo.addItem("⚙️  Convars", "convars")
        self._cat_combo.addItem("⌨️  Tastenbelegungen", "keys")
        self._cat_combo.addItem("🖥️  Video", "video")
        self._cat_combo.currentIndexChanged.connect(lambda _: self._apply_filter())
        tb.addWidget(cat_lbl)
        tb.addWidget(self._cat_combo)

        # Suche
        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Suchen...")
        self._search.setStyleSheet(INPUT_STYLE)
        self._search.setFixedWidth(220)
        self._search.textChanged.connect(lambda: self._search_timer.start(200))
        tb.addWidget(self._search)

        # Status + Reload
        self._status = QLabel("")
        self._status.setStyleSheet("color:#6c7086; font-size:11px;")
        tb.addWidget(self._status)

        btn_reload = QPushButton("🔄  Neu lesen")
        btn_reload.setStyleSheet(STYLE_RELOAD)
        btn_reload.clicked.connect(self._scan)
        tb.addWidget(btn_reload)

        root.addWidget(toolbar)

        # ── Info-Banner (zeigt Pfad + Anzahl) ──
        self._info_bar = QFrame()
        self._info_bar.setFixedHeight(32)
        self._info_bar.setStyleSheet("background:#11111b; border-bottom:1px solid #313244;")
        ib = QHBoxLayout(self._info_bar)
        ib.setContentsMargins(16, 0, 16, 0)
        self._info_lbl = QLabel("")
        self._info_lbl.setStyleSheet("color:#585b70; font-size:10px; font-family:Consolas;")
        ib.addWidget(self._info_lbl)
        ib.addStretch()
        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet("color:#6c7086; font-size:10px;")
        ib.addWidget(self._count_lbl)
        root.addWidget(self._info_bar)

        # ── Tree ──
        self._tree = QTreeWidget()
        self._tree.setStyleSheet(STYLE_TREE)
        self._tree.setHeaderLabels(["Setting", "Wert"])
        self._tree.setColumnWidth(0, 380)
        self._tree.setRootIsDecorated(True)
        self._tree.setAnimated(True)
        self._tree.setFont(QFont("Consolas", 11))
        root.addWidget(self._tree, 1)

    # ── Logik ─────────────────────────────────────────────────────────────────

    def _scan(self):
        self._status.setText("⌛  lese...")
        self._status.setStyleSheet("color:#fab387; font-size:11px;")

        self._userdata = find_steam_userdata()
        if not self._userdata:
            self._status.setText("❌  Steam userdata nicht gefunden")
            self._status.setStyleSheet("color:#f38ba8; font-size:11px;")
            return

        self._steam_ids = find_cs2_steam_ids(self._userdata)
        if not self._steam_ids:
            self._status.setText("❌  Keine CS2 Accounts gefunden")
            self._status.setStyleSheet("color:#f38ba8; font-size:11px;")
            return

        # Daten laden
        self._data.clear()
        for sid in self._steam_ids:
            self._data[sid] = read_all_for_id(self._userdata, sid)

        # Combo befuellen
        self._id_combo.blockSignals(True)
        self._id_combo.clear()
        for sid in self._steam_ids:
            d = self._data[sid]
            total = len(d["convars"]) + len(d["keys"]) + len(d["video"])
            self._id_combo.addItem(f"ID: {sid}  ({total} Settings)", sid)
        self._id_combo.blockSignals(False)

        self._status.setText(f"✅  {len(self._steam_ids)} Account(s)")
        self._status.setStyleSheet("color:#a6e3a1; font-size:11px;")
        self._on_id_changed()

    def _on_id_changed(self):
        sid = self._id_combo.currentData()
        if not sid or sid not in self._data:
            return
        d = self._data[sid]
        self._info_lbl.setText(d.get("base_path", ""))
        self._apply_filter()

    def _apply_filter(self):
        sid = self._id_combo.currentData()
        if not sid or sid not in self._data:
            return
        d = self._data[sid]
        query = self._search.text().strip().lower()
        cat_filter = self._cat_combo.currentData()

        self._tree.clear()
        total_shown = 0

        sections = {
            "convars": d["convars"],
            "keys":    d["keys"],
            "video":   d["video"],
        }

        for section_key, items in sections.items():
            if cat_filter != "all" and section_key != cat_filter:
                continue

            icon, label, filename = SECTION_LABELS[section_key]
            color = SECTION_COLORS[section_key]

            # Filtern
            filtered = {
                k: v for k, v in items.items()
                if not query or query in k.lower() or query in v.lower()
            }

            group = QTreeWidgetItem(self._tree)
            group.setText(0, f"{icon}  {label}  —  {len(filtered)} Einträge  ({filename})")
            group.setForeground(0, QColor(color))
            group.setExpanded(True)

            if not filtered:
                empty = QTreeWidgetItem(group)
                empty.setText(0, "  (keine Einträge gefunden)")
                empty.setForeground(0, QColor("#585b70"))
            else:
                for key, val in sorted(filtered.items()):
                    item = QTreeWidgetItem(group)
                    item.setText(0, f"  {key}")
                    item.setText(1, val)
                    item.setForeground(0, QColor("#cdd6f4"))
                    item.setForeground(1, QColor(color))

            total_shown += len(filtered)

        self._count_lbl.setText(f"{total_shown} Einträge")
