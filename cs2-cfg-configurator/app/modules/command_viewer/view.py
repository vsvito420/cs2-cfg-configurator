# command_viewer/view.py – Durchsuche alle CS2-Commands aus data/
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QLineEdit, QSplitter, QTreeWidget,
    QTreeWidgetItem, QTextEdit, QSizePolicy, QComboBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor

DATA_ROOT = Path(__file__).parent.parent.parent.parent / "data"

CATEGORY_META = {
    "crosshair":   {"label": "🎯 Crosshair",    "folder": "crosshair"},
    "viewmodel":   {"label": "🔫 Viewmodel",    "folder": "viewmodel"},
    "map":         {"label": "🗺️  Map / Radar",  "folder": "map"},
    "networking":  {"label": "🌐 Networking",   "folder": "networking"},
    "performance": {"label": "⚡ Performance",   "folder": "performance"},
    "video":       {"label": "🖥️  Video",        "folder": "video"},
    "buy-binds":   {"label": "🛒 Buy Binds",    "folder": "buy-binds"},
}

STYLE_TREE = """
    QTreeWidget {
        background: #1e1e2e; color: #cdd6f4;
        border: none; font-size: 12px;
        outline: none;
    }
    QTreeWidget::item { padding: 5px 8px; border-radius: 4px; }
    QTreeWidget::item:hover { background: #313244; }
    QTreeWidget::item:selected { background: #45475a; color: #cdd6f4; }
    QTreeWidget::branch { background: #1e1e2e; }
    QHeaderView::section {
        background: #181825; color: #6c7086;
        border: none; padding: 6px 8px; font-size: 11px;
        border-bottom: 1px solid #313244;
    }
"""
STYLE_DETAIL = """
    QTextEdit {
        background: #11111b; color: #cdd6f4;
        border: none; padding: 16px;
        font-size: 12px;
        font-family: 'Consolas', monospace;
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
        padding: 6px 12px; font-size: 12px; min-width: 140px;
    }
    QComboBox::drop-down { border: none; }
    QComboBox QAbstractItemView {
        background: #313244; color: #cdd6f4;
        border: 1px solid #45475a;
        selection-background-color: #45475a;
    }
"""


class CommandViewerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._all_commands: list[dict] = []   # {category, command, default, range, description}
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._apply_filter)
        self._build()
        self._load_all()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Toolbar ──
        toolbar = QFrame()
        toolbar.setFixedHeight(52)
        toolbar.setStyleSheet("background:#181825; border-bottom:1px solid #313244;")
        tb = QHBoxLayout(toolbar)
        tb.setContentsMargins(16, 8, 16, 8)
        tb.setSpacing(10)

        title = QLabel("🔍  Command Viewer")
        title.setStyleSheet("color:#cdd6f4; font-size:14px; font-weight:bold;")
        tb.addWidget(title)
        tb.addStretch()

        self._cat_combo = QComboBox()
        self._cat_combo.setStyleSheet(COMBO_STYLE)
        self._cat_combo.addItem("Alle Kategorien", "all")
        for key, meta in CATEGORY_META.items():
            self._cat_combo.addItem(meta["label"], key)
        self._cat_combo.currentIndexChanged.connect(lambda _: self._apply_filter())
        tb.addWidget(self._cat_combo)

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Command suchen...")
        self._search.setStyleSheet(INPUT_STYLE)
        self._search.setFixedWidth(260)
        self._search.textChanged.connect(lambda: self._search_timer.start(200))
        tb.addWidget(self._search)

        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet("color:#6c7086; font-size:11px;")
        tb.addWidget(self._count_lbl)

        root.addWidget(toolbar)

        # ── Splitter: Tree links, Detail rechts ──
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background:#313244; }")

        # Tree
        self._tree = QTreeWidget()
        self._tree.setStyleSheet(STYLE_TREE)
        self._tree.setHeaderLabels(["Command", "Default", "Range"])
        self._tree.setColumnWidth(0, 240)
        self._tree.setColumnWidth(1, 90)
        self._tree.setColumnWidth(2, 120)
        self._tree.setRootIsDecorated(True)
        self._tree.setAnimated(True)
        self._tree.setAlternatingRowColors(False)
        self._tree.itemSelectionChanged.connect(self._on_select)
        splitter.addWidget(self._tree)

        # Detail
        detail_widget = QWidget()
        detail_widget.setStyleSheet("background:#11111b;")
        dv = QVBoxLayout(detail_widget)
        dv.setContentsMargins(0, 0, 0, 0)
        dv.setSpacing(0)

        detail_hdr = QFrame()
        detail_hdr.setFixedHeight(40)
        detail_hdr.setStyleSheet("background:#181825; border-bottom:1px solid #313244;")
        dhdr_l = QHBoxLayout(detail_hdr)
        dhdr_l.setContentsMargins(16, 0, 16, 0)
        self._detail_title = QLabel("📌  Command Details")
        self._detail_title.setStyleSheet("color:#89b4fa; font-size:12px; font-weight:bold;")
        dhdr_l.addWidget(self._detail_title)
        dv.addWidget(detail_hdr)

        self._detail = QTextEdit()
        self._detail.setReadOnly(True)
        self._detail.setStyleSheet(STYLE_DETAIL)
        self._detail.setFont(QFont("Consolas", 11))
        self._detail.setPlaceholderText("Command in der Liste auswählen...")
        dv.addWidget(self._detail, 1)

        splitter.addWidget(detail_widget)
        splitter.setSizes([520, 380])
        root.addWidget(splitter, 1)

    def _load_all(self):
        self._all_commands.clear()
        for key, meta in CATEGORY_META.items():
            p = DATA_ROOT / meta["folder"] / "commands.json"
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    for item in data:
                        self._all_commands.append({
                            "category": key,
                            "cat_label": meta["label"],
                            "command":     item.get("command", ""),
                            "default":     str(item.get("default", "")),
                            "range":       str(item.get("range", "")),
                            "description": item.get("description", ""),
                        })
                except Exception:
                    pass
        self._apply_filter()

    def _apply_filter(self):
        query = self._search.text().strip().lower()
        cat_filter = self._cat_combo.currentData()

        self._tree.clear()
        # Gruppiere nach Kategorie
        groups: dict[str, list] = {}
        for cmd in self._all_commands:
            if cat_filter != "all" and cmd["category"] != cat_filter:
                continue
            if query and query not in cmd["command"].lower() and query not in cmd["description"].lower():
                continue
            groups.setdefault(cmd["category"], []).append(cmd)

        total = 0
        for cat_key, items in groups.items():
            meta = CATEGORY_META.get(cat_key, {})
            group_item = QTreeWidgetItem(self._tree)
            group_item.setText(0, f"{meta.get('label', cat_key)}  ({len(items)})")
            group_item.setForeground(0, QColor("#89b4fa"))
            group_item.setExpanded(True)
            for cmd in items:
                child = QTreeWidgetItem(group_item)
                child.setText(0, cmd["command"])
                child.setText(1, cmd["default"])
                child.setText(2, cmd["range"])
                child.setData(0, Qt.UserRole, cmd)
                child.setForeground(0, QColor("#cdd6f4"))
                child.setForeground(1, QColor("#a6e3a1"))
                child.setForeground(2, QColor("#fab387"))
            total += len(items)

        self._count_lbl.setText(f"{total} Commands")

    def _on_select(self):
        items = self._tree.selectedItems()
        if not items:
            return
        item = items[0]
        cmd = item.data(0, Qt.UserRole)
        if not cmd:
            return
        self._detail_title.setText(f"📌  {cmd['command']}")
        lines = [
            f"<span style='color:#89b4fa;font-size:16px;font-weight:bold;'>{cmd['command']}</span>",
            "",
            f"<span style='color:#6c7086;font-size:11px;'>KATEGORIE</span>",
            f"<span style='color:#cba6f7;'>{cmd['cat_label']}</span>",
            "",
            f"<span style='color:#6c7086;font-size:11px;'>BESCHREIBUNG</span>",
            f"<span style='color:#cdd6f4;'>{cmd['description'] or '<i style=color:#585b70>keine Beschreibung</i>'}</span>",
            "",
            f"<span style='color:#6c7086;font-size:11px;'>DEFAULT-WERT</span>",
            f"<span style='color:#a6e3a1;font-family:Consolas;'>{cmd['default'] or '–'}</span>",
            "",
            f"<span style='color:#6c7086;font-size:11px;'>WERTEBEREICH</span>",
            f"<span style='color:#fab387;font-family:Consolas;'>{cmd['range'] or '–'}</span>",
            "",
            "<hr style='border-color:#313244;'>",
            f"<span style='color:#6c7086;font-size:11px;'>BEISPIEL-USAGE</span>",
            f"<span style='color:#f5c2e7;font-family:Consolas;'>{cmd['command']} {cmd['default']}</span>",
        ]
        self._detail.setHtml("<br>".join(lines))
