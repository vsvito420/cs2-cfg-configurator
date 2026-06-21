# settings_reader/view.py
from pathlib import Path
import copy
import subprocess
import sys

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTreeWidget, QTreeWidgetItem,
    QComboBox, QLineEdit, QSizePolicy, QMessageBox, QInputDialog, QMenu
)
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QColor, QFont

from .reader import find_steam_userdata, find_cs2_steam_ids, read_all_for_id

# ── Styles ────────────────────────────────────────────────────────────────
STYLE_TREE = """
    QTreeWidget {
        background:#1e1e2e; color:#cdd6f4; border:none;
        font-size:12px; outline:none;
        font-family:'Consolas',monospace;
    }
    QTreeWidget::item { padding:4px 8px; }
    QTreeWidget::item:hover { background:#313244; border-radius:4px; }
    QTreeWidget::item:selected { background:#45475a; color:#cdd6f4; }
    QTreeWidget::branch { background:#1e1e2e; }
    QHeaderView::section {
        background:#181825; color:#6c7086; border:none;
        padding:6px 8px; font-size:11px;
        border-bottom:1px solid #313244;
    }
"""
INPUT_STYLE = """
    QLineEdit {
        background:#313244; color:#cdd6f4;
        border:1px solid #45475a; border-radius:6px;
        padding:7px 12px; font-size:12px;
    }
    QLineEdit:focus { border:1px solid #89b4fa; }
"""
COMBO_STYLE = """
    QComboBox {
        background:#313244; color:#cdd6f4;
        border:1px solid #45475a; border-radius:6px;
        padding:6px 12px; font-size:12px; min-width:200px;
    }
    QComboBox::drop-down { border:none; }
    QComboBox QAbstractItemView {
        background:#313244; color:#cdd6f4;
        selection-background-color:#45475a;
        border:1px solid #45475a;
    }
"""
STYLE_BTN = """
    QPushButton {
        background:#313244; color:#cdd6f4; border:none;
        border-radius:6px; padding:7px 14px; font-size:12px;
    }
    QPushButton:hover { background:#45475a; }
"""
STYLE_RELOAD = """
    QPushButton {
        background:#89b4fa; color:#1e1e2e; border:none;
        border-radius:6px; padding:7px 14px; font-size:12px; font-weight:bold;
    }
    QPushButton:hover { background:#b4d0ff; }
"""
STYLE_SAVE = """
    QPushButton {
        background:#f38ba8; color:#1e1e2e; border:none;
        border-radius:6px; padding:7px 14px; font-size:12px; font-weight:bold;
    }
    QPushButton:hover { background:#ffb3c6; }
"""
STYLE_BACKUP = """
    QPushButton {
        background:#a6e3a1; color:#1e1e2e; border:none;
        border-radius:6px; padding:7px 14px; font-size:12px; font-weight:bold;
    }
    QPushButton:hover { background:#c0f0bb; }
"""
STYLE_FOLDER = """
    QPushButton {
        background:#313244; color:#cdd6f4; border:none;
        border-radius:6px; padding:7px 14px; font-size:12px;
    }
    QPushButton:hover { background:#45475a; }
"""

SECTION_COLORS = {"convars": "#89b4fa", "keys": "#a6e3a1", "video": "#fab387"}
SECTION_LABELS = {
    "convars": ("⚙️", "Aktive Convars",       "cs2_user_convars_0_slot0.vcfg"),
    "keys":    ("⌨️", "Tastenbelegungen",     "cs2_user_keys_0_slot0.vcfg"),
    "video":   ("🖥️", "Video-Einstellungen",  "cs2_video.txt"),
}
BACKUP_DIR = Path(__file__).parent.parent.parent.parent / "configs" / "backups"


class SettingsReaderPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._userdata: Path | None = None
        self._steam_ids: list[str] = []
        self._data: dict = {}
        self._pending: dict = {}
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._apply_filter)
        self._build()
        self._scan()

    # ── UI Build ─────────────────────────────────────────────────────────────

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Toolbar
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

        acc_lbl = QLabel("Account:")
        acc_lbl.setStyleSheet("color:#6c7086; font-size:12px;")
        self._id_combo = QComboBox()
        self._id_combo.setStyleSheet(COMBO_STYLE)
        self._id_combo.currentIndexChanged.connect(self._on_id_changed)
        tb.addWidget(acc_lbl)
        tb.addWidget(self._id_combo)

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

        self._search = QLineEdit()
        self._search.setPlaceholderText("🔍  Suchen...")
        self._search.setStyleSheet(INPUT_STYLE)
        self._search.setFixedWidth(200)
        self._search.textChanged.connect(lambda: self._search_timer.start(200))
        tb.addWidget(self._search)

        self._status = QLabel("")
        self._status.setStyleSheet("color:#6c7086; font-size:11px;")
        tb.addWidget(self._status)

        btn_reload = QPushButton("🔄  Neu lesen")
        btn_reload.setStyleSheet(STYLE_RELOAD)
        btn_reload.clicked.connect(self._scan)
        tb.addWidget(btn_reload)

        self._btn_save = QPushButton("💾  In Datei schreiben")
        self._btn_save.setStyleSheet(STYLE_SAVE)
        self._btn_save.setVisible(False)
        self._btn_save.clicked.connect(self._write_changes)
        tb.addWidget(self._btn_save)

        root.addWidget(toolbar)

        # Info-Bar
        info_bar = QFrame()
        info_bar.setFixedHeight(30)
        info_bar.setStyleSheet("background:#11111b; border-bottom:1px solid #313244;")
        ib = QHBoxLayout(info_bar)
        ib.setContentsMargins(16, 0, 16, 0)
        self._info_lbl = QLabel("")
        self._info_lbl.setStyleSheet("color:#585b70; font-size:10px; font-family:Consolas;")
        ib.addWidget(self._info_lbl)
        ib.addStretch()
        self._pending_lbl = QLabel("")
        self._pending_lbl.setStyleSheet("color:#f38ba8; font-size:10px; font-weight:bold;")
        ib.addWidget(self._pending_lbl)
        self._count_lbl = QLabel("")
        self._count_lbl.setStyleSheet("color:#6c7086; font-size:10px;")
        ib.addWidget(self._count_lbl)
        root.addWidget(info_bar)

        # Backup-Bar
        backup_bar = QFrame()
        backup_bar.setFixedHeight(40)
        backup_bar.setStyleSheet("background:#1e1e2e; border-bottom:1px solid #313244;")
        bb = QHBoxLayout(backup_bar)
        bb.setContentsMargins(16, 5, 16, 5)
        bb.setSpacing(8)
        backup_lbl = QLabel("🗂️  Backup:")
        backup_lbl.setStyleSheet("color:#6c7086; font-size:11px;")
        bb.addWidget(backup_lbl)
        for label, section in [("⚙️ Convars", "convars"), ("⌨️ Keys", "keys"), ("🖥️ Video", "video")]:
            b = QPushButton(label)
            b.setStyleSheet(STYLE_BACKUP)
            b.setFixedHeight(28)
            b.clicked.connect(lambda _=False, s=section: self._backup(s))
            bb.addWidget(b)

        # ── NEU: Backup-Ordner öffnen ──
        btn_open_backup = QPushButton("📂  Backup-Ordner")
        btn_open_backup.setStyleSheet(STYLE_FOLDER)
        btn_open_backup.setFixedHeight(28)
        btn_open_backup.clicked.connect(self._open_backup_dir)
        bb.addWidget(btn_open_backup)

        bb.addStretch()
        hint = QLabel("⚠️ Doppelklick = Wert bearbeiten  |  Rechtsklick = Kontextmenü")
        hint.setStyleSheet("color:#585b70; font-size:10px; font-style:italic;")
        bb.addWidget(hint)
        root.addWidget(backup_bar)

        # Tree: Setting | Aktueller Wert | Änderung | Revert
        self._tree = QTreeWidget()
        self._tree.setStyleSheet(STYLE_TREE)
        self._tree.setHeaderLabels(["Setting", "Aktueller Wert", "➤ Neue Änderung", ""])
        self._tree.setColumnWidth(0, 320)
        self._tree.setColumnWidth(1, 160)
        self._tree.setColumnWidth(2, 160)
        self._tree.setColumnWidth(3, 70)
        self._tree.setRootIsDecorated(True)
        self._tree.setAnimated(True)
        self._tree.setFont(QFont("Consolas", 11))
        self._tree.itemDoubleClicked.connect(self._on_double_click)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        root.addWidget(self._tree, 1)

    # ── Backup-Ordner öffnen ──────────────────────────────────────────────

    def _open_backup_dir(self):
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(BACKUP_DIR)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(BACKUP_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(BACKUP_DIR)])

    # ── Scan & Load ────────────────────────────────────────────────────────────

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
        self._data.clear()
        self._pending.clear()
        for sid in self._steam_ids:
            self._data[sid] = read_all_for_id(self._userdata, sid)
            self._pending[sid] = {"convars": {}, "keys": {}, "video": {}}

        self._id_combo.blockSignals(True)
        self._id_combo.clear()
        for sid in self._steam_ids:
            d = self._data[sid]
            total = len(d["convars"]) + len(d["keys"]) + len(d["video"])
            name = d.get("name", "")
            label = f"👤 {name}  —  ID: {sid}  ({total} Settings)" if name else f"ID: {sid}  ({total} Settings)"
            self._id_combo.addItem(label, sid)
        self._id_combo.blockSignals(False)

        self._status.setText(f"✅  {len(self._steam_ids)} Account(s)")
        self._status.setStyleSheet("color:#a6e3a1; font-size:11px;")
        self._on_id_changed()

    def _on_id_changed(self):
        sid = self._id_combo.currentData()
        if not sid or sid not in self._data:
            return
        self._info_lbl.setText(self._data[sid].get("base_path", ""))
        self._apply_filter()

    # ── Filter & Tree-Render ──────────────────────────────────────────────────

    def _apply_filter(self):
        sid = self._id_combo.currentData()
        if not sid or sid not in self._data:
            return
        d = self._data[sid]
        pending = self._pending.get(sid, {})
        query = self._search.text().strip().lower()
        cat_filter = self._cat_combo.currentData()

        self._tree.clear()
        total_shown = 0

        for section_key in ("convars", "keys", "video"):
            if cat_filter != "all" and section_key != cat_filter:
                continue
            items = d[section_key]
            pend  = pending.get(section_key, {})
            icon, label, filename = SECTION_LABELS[section_key]
            color = SECTION_COLORS[section_key]

            filtered = {
                k: v for k, v in items.items()
                if not query or query in k.lower() or query in v.lower()
                    or (k in pend and query in pend[k].lower())
            }

            group = QTreeWidgetItem(self._tree)
            group.setText(0, f"{icon}  {label}  —  {len(filtered)} Einträge  ({filename})")
            group.setForeground(0, QColor(color))
            group.setExpanded(True)
            group.setData(0, Qt.UserRole, {"section": section_key, "is_group": True})

            for key, orig_val in sorted(filtered.items()):
                item = QTreeWidgetItem(group)
                item.setText(0, f"  {key}")
                item.setText(1, orig_val)
                pending_val = pend.get(key, "")
                item.setText(2, pending_val)
                item.setData(0, Qt.UserRole, {"section": section_key, "key": key, "orig": orig_val})
                item.setForeground(0, QColor("#cdd6f4"))
                item.setForeground(1, QColor(color))
                if pending_val:
                    item.setForeground(2, QColor("#f9e2af"))
                    item.setBackground(0, QColor("#2a2a1a"))
                    item.setText(3, "↺")
                    item.setForeground(3, QColor("#f38ba8"))
                else:
                    item.setForeground(2, QColor("#585b70"))

            total_shown += len(filtered)

        self._count_lbl.setText(f"  {total_shown} Einträge")
        pending_total = sum(len(v) for v in self._pending.get(sid, {}).values())
        if pending_total:
            self._pending_lbl.setText(f"⚠️ {pending_total} ungespeicherte Änderungen  ")
            self._btn_save.setVisible(True)
        else:
            self._pending_lbl.setText("")
            self._btn_save.setVisible(False)

    # ── Edit ───────────────────────────────────────────────────────────────────

    def _on_double_click(self, item: QTreeWidgetItem, col: int):
        meta = item.data(0, Qt.UserRole)
        if not meta or meta.get("is_group"):
            return
        if col == 3:
            self._revert_item(item)
            return
        self._edit_item(item)

    def _on_context_menu(self, pos: QPoint):
        item = self._tree.itemAt(pos)
        if not item:
            return
        meta = item.data(0, Qt.UserRole)
        if not meta or meta.get("is_group"):
            return
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background:#313244; color:#cdd6f4; border:1px solid #45475a; }
            QMenu::item:selected { background:#45475a; }
        """)
        act_edit   = menu.addAction("✏️  Wert bearbeiten")
        act_revert = menu.addAction("↺  Änderung verwerfen")
        act_revert.setEnabled(bool(item.text(2)))
        menu.addSeparator()
        act_copy   = menu.addAction("📋  Command kopieren")
        action = menu.exec(self._tree.viewport().mapToGlobal(pos))
        if action == act_edit:
            self._edit_item(item)
        elif action == act_revert:
            self._revert_item(item)
        elif action == act_copy:
            from PySide6.QtWidgets import QApplication
            meta2 = item.data(0, Qt.UserRole)
            QApplication.clipboard().setText(f"{meta2['key']} {meta2['orig']}")

    def _edit_item(self, item: QTreeWidgetItem):
        meta = item.data(0, Qt.UserRole)
        key  = meta["key"]
        sid  = self._id_combo.currentData()
        section = meta["section"]
        current_pending = self._pending[sid][section].get(key, meta["orig"])
        new_val, ok = QInputDialog.getText(
            self, f"Wert ändern: {key}",
            f"Neuer Wert für  {key}\n(Original: {meta['orig']})",
            text=current_pending
        )
        if ok:
            if new_val == meta["orig"]:
                self._pending[sid][section].pop(key, None)
            else:
                self._pending[sid][section][key] = new_val
            self._apply_filter()

    def _revert_item(self, item: QTreeWidgetItem):
        meta = item.data(0, Qt.UserRole)
        sid  = self._id_combo.currentData()
        self._pending[sid][meta["section"]].pop(meta["key"], None)
        self._apply_filter()

    # ── In Datei schreiben ──────────────────────────────────────────────────

    def _write_changes(self):
        sid = self._id_combo.currentData()
        d   = self._data[sid]
        pending = self._pending[sid]
        confirm = QMessageBox.warning(
            self, "⚠️  Direkt in Datei schreiben?",
            "Diese Änderungen werden direkt in die Steam-Konfigurationsdateien geschrieben.\n"
            "CS2 liest diese nur beim Start — also CS2 neu starten damit sie aktiv werden.\n\nFortfahren?",
            QMessageBox.Yes | QMessageBox.Cancel
        )
        if confirm != QMessageBox.Yes:
            return
        section_files = {"convars": d["convars_file"], "keys": d["keys_file"], "video": d["video_file"]}
        for section_key, changes in pending.items():
            if not changes:
                continue
            filepath = Path(section_files[section_key])
            if not filepath.exists():
                continue
            import re
            content = filepath.read_text(encoding="utf-8", errors="ignore")
            for key, new_val in changes.items():
                pattern = rf'("{re.escape(key)}"\s*)"[^"]*"'
                replacement = rf'\1"{new_val}"'
                new_content = re.sub(pattern, replacement, content)
                if new_content == content:
                    pattern2 = rf'(setcommand\s+"{re.escape(key)}"\s*)"[^"]*"'
                    new_content = re.sub(pattern2, replacement, content)
                content = new_content
            filepath.write_text(content, encoding="utf-8")
        self._pending[sid] = {"convars": {}, "keys": {}, "video": {}}
        self._scan()
        QMessageBox.information(self, "✅  Gespeichert", "Dateien wurden aktualisiert.\nCS2 neu starten um die Änderungen zu übernehmen.")

    # ── Backup ─────────────────────────────────────────────────────────────────

    def _backup(self, section: str):
        sid = self._id_combo.currentData()
        if not sid or sid not in self._data:
            return
        d = self._data[sid]
        name = d.get("name", sid)
        preset_name, ok = QInputDialog.getText(
            self, f"Backup: {section}",
            f"Name für das Backup (z.B. crosshairA, pistol_keys):",
            text=f"{section}_{name}"
        )
        if not ok or not preset_name.strip():
            return
        items = d[section]
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        safe = "".join(c for c in preset_name if c.isalnum() or c in " _-").strip().replace(" ", "_")
        out = BACKUP_DIR / f"{safe}.cfg"
        if section == "convars":
            lines = [f'setcommand "{k}" "{v}"' for k, v in sorted(items.items())]
        elif section == "keys":
            lines = [f'bind "{k}" "{v}"' for k, v in sorted(items.items())]
        else:
            lines = [f'"{k}"\t"{v}"' for k, v in sorted(items.items())]
        header = [
            "// vsvito's CounterStrike2 CFG Configurator – Backup",
            f"// Section: {section}  |  Account: {name}  (ID: {sid})",
            "// Erstellt mit vsvito's CounterStrike2 CFG Configurator", "",
        ]
        out.write_text("\n".join(header + lines), encoding="utf-8")
        QMessageBox.information(self, "✅  Backup erstellt", f"Gespeichert nach:\n{out}")
