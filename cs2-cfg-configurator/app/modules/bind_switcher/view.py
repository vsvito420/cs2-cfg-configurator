# view.py – Bind Manager Haupt-UI
import subprocess
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QSplitter, QTextEdit, QScrollArea, QLineEdit,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .model import BindProfile, SimpleBind, ToggleBind, HoldBind, CfgBind
from .generator import generate_profile
from .widgets import SimpleBindRow, ToggleBindRow, HoldBindRow, CfgBindRow

# Vordefinierter Output-Ordner (relativ zu diesem File: ../../../../configs/bind-manager/)
OUTPUT_DIR = Path(__file__).parent.parent.parent.parent / "configs" / "bind-manager"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


STYLE_ADD = """
    QPushButton {
        background: #1e1e2e; color: #6c7086;
        border: 1px dashed #45475a; border-radius: 8px;
        padding: 8px; font-size: 12px;
    }
    QPushButton:hover {
        background: #24273a; color: #cdd6f4; border-color: #89b4fa;
    }
"""
STYLE_PRIMARY = """
    QPushButton {
        background: #89b4fa; color: #1e1e2e;
        border: none; border-radius: 6px;
        padding: 8px 20px; font-size: 13px; font-weight: bold;
    }
    QPushButton:hover { background: #b4d0ff; }
"""
STYLE_SEC = """
    QPushButton {
        background: #313244; color: #cdd6f4;
        border: none; border-radius: 6px;
        padding: 8px 18px; font-size: 13px;
    }
    QPushButton:hover { background: #45475a; }
"""
STYLE_FOLDER = """
    QPushButton {
        background: #313244; color: #f9e2af;
        border: none; border-radius: 6px;
        padding: 8px 14px; font-size: 13px;
    }
    QPushButton:hover { background: #45475a; }
"""
STYLE_DANGER = """
    QPushButton {
        background: transparent; color: #f38ba8;
        border: 1px solid #f38ba8; border-radius: 6px;
        padding: 8px 18px; font-size: 13px;
    }
    QPushButton:hover { background: #f38ba820; }
"""

TAB_ICONS = {
    "simple": "⌨️  Simple",
    "toggle": "🔄  Toggle",
    "hold":   "🔥  Hold",
    "cfg":    "📁  CFG Exec",
}
TAB_HINTS = {
    "simple": "Taste → Befehl  (einmalig beim Drücken)",
    "toggle": "Taste wechselt bei jedem Druck zwischen State A ↔ B",
    "hold":   "Taste gedrückt halten = aktiv,  loslassen = zurück zum Default",
    "cfg":    "Taste lädt eine .cfg-Datei  (simple / hold / toggle)",
}


class BindManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile = BindProfile()
        self._rows: dict[str, list] = {"simple": [], "toggle": [], "hold": [], "cfg": []}
        self._containers: dict[str, QWidget] = {}
        self._build()

    # ─── Build ──────────────────────────────────────────────────────────────

    def _build(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #313244; }")

        # ── Linke Seite ──
        left = QWidget()
        left.setStyleSheet("background: #1e1e2e;")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(0)

        # Header
        header_bar = QFrame()
        header_bar.setFixedHeight(48)
        header_bar.setStyleSheet("background:#181825; border-bottom:1px solid #313244;")
        hb = QHBoxLayout(header_bar)
        hb.setContentsMargins(16, 8, 16, 8)
        lbl = QLabel("🔗  Bind Manager")
        lbl.setStyleSheet("color:#cdd6f4; font-size:15px; font-weight:bold;")
        hb.addWidget(lbl)
        hb.addStretch()
        name_lbl = QLabel("Profil:")
        name_lbl.setStyleSheet("color:#6c7086; font-size:12px;")
        self._profile_name = QLineEdit(self.profile.name)
        self._profile_name.setFixedWidth(160)
        self._profile_name.setStyleSheet(
            "background:#313244; color:#cdd6f4; border:1px solid #45475a;"
            "border-radius:4px; padding:4px 8px; font-size:12px;"
        )
        self._profile_name.textChanged.connect(lambda t: setattr(self.profile, 'name', t))
        hb.addWidget(name_lbl)
        hb.addWidget(self._profile_name)
        lv.addWidget(header_bar)

        # Tabs
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #1e1e2e; }
            QTabBar::tab {
                background: #181825; color: #6c7086;
                padding: 9px 20px; border: none;
                border-bottom: 2px solid transparent;
                margin-right: 1px; font-size: 12px;
            }
            QTabBar::tab:selected { color: #cdd6f4; border-bottom: 2px solid #89b4fa; background: #1e1e2e; }
            QTabBar::tab:hover { color: #a6adc8; background: #1e1e2e; }
        """)
        for bt in ["simple", "toggle", "hold", "cfg"]:
            self._tabs.addTab(self._build_tab(bt), TAB_ICONS[bt])
        lv.addWidget(self._tabs, 1)

        # Aktions-Leiste
        action_bar = QFrame()
        action_bar.setFixedHeight(54)
        action_bar.setStyleSheet("background:#181825; border-top:1px solid #313244;")
        ab = QHBoxLayout(action_bar)
        ab.setContentsMargins(16, 8, 16, 8)
        ab.setSpacing(10)

        btn_gen  = QPushButton("⚡  Generate & Save")
        btn_gen.setStyleSheet(STYLE_PRIMARY)
        btn_gen.setToolTip(f"Speichert direkt nach: {OUTPUT_DIR}")
        btn_gen.clicked.connect(self._save)

        btn_folder = QPushButton("📂  Ordner öffnen")
        btn_folder.setStyleSheet(STYLE_FOLDER)
        btn_folder.setToolTip(str(OUTPUT_DIR))
        btn_folder.clicked.connect(self._open_folder)

        btn_clr = QPushButton("🗑  Leeren")
        btn_clr.setStyleSheet(STYLE_DANGER)
        btn_clr.clicked.connect(self._clear)

        ab.addWidget(btn_gen)
        ab.addWidget(btn_folder)
        ab.addStretch()
        ab.addWidget(btn_clr)
        lv.addWidget(action_bar)

        # ── Rechte Seite: Preview ──
        right = QWidget()
        right.setStyleSheet("background:#181825;")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(12, 12, 16, 12)
        rv.setSpacing(8)

        ph = QHBoxLayout()
        plbl = QLabel("📄  CFG Preview")
        plbl.setStyleSheet("color:#89b4fa; font-size:13px; font-weight:bold;")
        ph.addWidget(plbl)
        ph.addStretch()

        self._path_lbl = QLabel("")
        self._path_lbl.setStyleSheet("color:#585b70; font-size:10px; font-style:italic;")
        ph.addWidget(self._path_lbl)

        copy_btn = QPushButton("📋 Copy")
        copy_btn.setStyleSheet(STYLE_SEC)
        copy_btn.setFixedHeight(30)
        copy_btn.clicked.connect(self._copy)
        ph.addWidget(copy_btn)
        rv.addLayout(ph)

        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(QFont("Consolas", 11))
        self._preview.setStyleSheet("""
            background:#11111b; color:#cdd6f4;
            border:1px solid #313244; border-radius:6px; padding:10px;
        """)
        self._preview.setPlaceholderText("// Klick auf ⚡ Generate & Save um den Output zu sehen...")
        rv.addWidget(self._preview, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([620, 430])
        root.addWidget(splitter)

    def _build_tab(self, bt: str) -> QWidget:
        wrapper = QWidget()
        wrapper.setStyleSheet("background:#1e1e2e;")
        wv = QVBoxLayout(wrapper)
        wv.setContentsMargins(12, 8, 12, 0)
        wv.setSpacing(6)

        hint = QLabel(TAB_HINTS[bt])
        hint.setStyleSheet("color:#585b70; font-size:11px; font-style:italic; padding:2px 0;")
        wv.addWidget(hint)

        container = QWidget()
        container.setStyleSheet("background:transparent;")
        cl = QVBoxLayout(container)
        cl.setContentsMargins(0, 0, 0, 0)
        cl.setSpacing(8)
        cl.addStretch()
        self._containers[bt] = container

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border:none; background:transparent; }"
            "QScrollBar:vertical { background:#1e1e2e; width:7px; border-radius:3px; }"
            "QScrollBar::handle:vertical { background:#45475a; border-radius:3px; }"
        )
        scroll.setWidget(container)
        wv.addWidget(scroll, 1)

        add_btn = QPushButton(f"＋  {bt.capitalize()} Bind hinzufügen")
        add_btn.setStyleSheet(STYLE_ADD)
        add_btn.setFixedHeight(38)
        add_btn.clicked.connect(lambda _=False, b=bt: self._add(b))
        wv.addWidget(add_btn)
        return wrapper

    # ─── Logik ─────────────────────────────────────────────────────────────

    def _add(self, bt: str):
        model_cls  = {"simple": SimpleBind, "toggle": ToggleBind, "hold": HoldBind, "cfg": CfgBind}[bt]
        widget_cls = {"simple": SimpleBindRow, "toggle": ToggleBindRow, "hold": HoldBindRow, "cfg": CfgBindRow}[bt]
        list_ref   = {"simple": self.profile.simple_binds, "toggle": self.profile.toggle_binds,
                      "hold": self.profile.hold_binds, "cfg": self.profile.cfg_binds}[bt]

        m   = model_cls()
        row = widget_cls(m)
        list_ref.append(m)

        layout = self._containers[bt].layout()
        layout.insertWidget(layout.count() - 1, row)
        self._rows[bt].append(row)
        row.sig_delete.connect(lambda r=row, mod=m, b=bt: self._remove(r, mod, b))

    def _remove(self, row, model, bt: str):
        list_ref = {"simple": self.profile.simple_binds, "toggle": self.profile.toggle_binds,
                    "hold": self.profile.hold_binds, "cfg": self.profile.cfg_binds}[bt]
        try:
            list_ref.remove(model)
        except ValueError:
            pass
        self._rows[bt].remove(row)
        row.setParent(None)
        row.deleteLater()

    def _save(self):
        """Generiert CFG und speichert direkt in configs/bind-manager/<profilname>.cfg"""
        content = generate_profile(self.profile)
        self._preview.setPlainText(content)

        safe_name = "".join(c for c in self.profile.name if c.isalnum() or c in ' _-').strip()
        if not safe_name:
            safe_name = "my_binds"
        filename = safe_name.replace(' ', '_') + ".cfg"
        out_path = OUTPUT_DIR / filename

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)

        self._path_lbl.setText(f"✓ {out_path.name}")
        self._path_lbl.setStyleSheet("color:#a6e3a1; font-size:10px;")

    def _open_folder(self):
        """Oeffnet den Output-Ordner im Dateimanager (Windows/macOS/Linux)."""
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(OUTPUT_DIR)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(OUTPUT_DIR)])
        else:
            subprocess.Popen(["xdg-open", str(OUTPUT_DIR)])

    def _copy(self):
        from PySide6.QtWidgets import QApplication
        QApplication.clipboard().setText(self._preview.toPlainText())

    def _clear(self):
        if QMessageBox.question(self, "Leeren?", "Alle Binds wirklich löschen?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            for bt in ["simple", "toggle", "hold", "cfg"]:
                for w in list(self._rows[bt]):
                    w.setParent(None)
                    w.deleteLater()
                self._rows[bt].clear()
            self.profile.simple_binds.clear()
            self.profile.toggle_binds.clear()
            self.profile.hold_binds.clear()
            self.profile.cfg_binds.clear()
            self._preview.clear()
            self._path_lbl.setText("")
