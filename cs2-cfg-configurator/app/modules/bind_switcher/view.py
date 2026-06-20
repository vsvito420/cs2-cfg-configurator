# view.py – Haupt-UI fuer den Bind Manager
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QSplitter, QTextEdit, QScrollArea, QFrame,
    QLineEdit, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .model import BindProfile, SimpleBind, ToggleBind, HoldBind, CfgBind
from .generator import generate_profile
from .widgets import SimpleBindRow, ToggleBindRow, HoldBindRow, CfgBindRow


STYLE_ADD_BTN = """
    QPushButton {
        background: #313244; color: #a6e3a1;
        border: 1px dashed #45475a; border-radius: 6px;
        padding: 6px 14px; font-size: 12px;
    }
    QPushButton:hover { background: #3d3f5c; }
"""
STYLE_ACTION_BTN = """
    QPushButton {
        background: #89b4fa; color: #1e1e2e;
        border: none; border-radius: 6px;
        padding: 8px 18px; font-size: 13px; font-weight: bold;
    }
    QPushButton:hover { background: #74c7ec; }
"""
STYLE_SECONDARY_BTN = """
    QPushButton {
        background: #313244; color: #cdd6f4;
        border: none; border-radius: 6px;
        padding: 8px 18px; font-size: 13px;
    }
    QPushButton:hover { background: #45475a; }
"""


class BindManagerPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.profile = BindProfile()
        self._row_widgets: dict[str, list] = {
            "simple": [], "toggle": [], "hold": [], "cfg": []
        }
        self._build_ui()

    # ─────────────────────────────── UI ───────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(2)
        splitter.setStyleSheet("QSplitter::handle { background: #313244; }")

        # ── linke Seite: Editor ──
        left = QWidget()
        left.setStyleSheet("background: #1e1e2e;")
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(16, 16, 16, 16)
        left_layout.setSpacing(10)

        # Profilname
        name_row = QHBoxLayout()
        name_lbl = QLabel("📋  Profil-Name:")
        name_lbl.setStyleSheet("color:#cdd6f4; font-size:13px;")
        self._profile_name_edit = QLineEdit(self.profile.name)
        self._profile_name_edit.setStyleSheet(
            "background:#313244; color:#cdd6f4; border:1px solid #45475a;"
            "border-radius:4px; padding:4px 8px; font-size:13px;"
        )
        self._profile_name_edit.textChanged.connect(
            lambda t: setattr(self.profile, 'name', t)
        )
        name_row.addWidget(name_lbl)
        name_row.addWidget(self._profile_name_edit, 1)
        left_layout.addLayout(name_row)

        # Tabs fuer Bind-Typen
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #1e1e2e; }
            QTabBar::tab {
                background: #313244; color: #a6adc8;
                padding: 8px 18px; border-radius: 4px 4px 0 0;
                margin-right: 2px; font-size: 12px;
            }
            QTabBar::tab:selected { background: #45475a; color: #cdd6f4; }
            QTabBar::tab:hover    { background: #3d3f5c; }
        """)

        self._simple_container = self._make_scroll_area()
        self._toggle_container = self._make_scroll_area()
        self._hold_container   = self._make_scroll_area()
        self._cfg_container    = self._make_scroll_area()

        self._tabs.addTab(self._wrap_tab(self._simple_container, "simple"), "⌨️  Simple")
        self._tabs.addTab(self._wrap_tab(self._toggle_container, "toggle"), "🔄  Toggle")
        self._tabs.addTab(self._wrap_tab(self._hold_container,   "hold"),   "🔥  Hold")
        self._tabs.addTab(self._wrap_tab(self._cfg_container,    "cfg"),    "📁  CFG Exec")
        left_layout.addWidget(self._tabs, 1)

        # Aktions-Buttons
        btn_row = QHBoxLayout()
        btn_generate = QPushButton("⚡  Generate CFG")
        btn_generate.setStyleSheet(STYLE_ACTION_BTN)
        btn_generate.clicked.connect(self._generate)

        btn_save = QPushButton("💾  Speichern")
        btn_save.setStyleSheet(STYLE_SECONDARY_BTN)
        btn_save.clicked.connect(self._save_file)

        btn_clear = QPushButton("🗑️  Leeren")
        btn_clear.setStyleSheet(STYLE_SECONDARY_BTN)
        btn_clear.clicked.connect(self._clear_all)

        btn_row.addWidget(btn_generate)
        btn_row.addWidget(btn_save)
        btn_row.addStretch()
        btn_row.addWidget(btn_clear)
        left_layout.addLayout(btn_row)

        # ── rechte Seite: Preview ──
        right = QWidget()
        right.setStyleSheet("background: #181825;")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(12, 16, 16, 16)
        right_layout.setSpacing(8)

        preview_header = QLabel("📄  CFG Preview")
        preview_header.setStyleSheet("color:#89b4fa; font-size:14px; font-weight:bold;")
        right_layout.addWidget(preview_header)

        self._preview = QTextEdit()
        self._preview.setReadOnly(True)
        self._preview.setFont(QFont("Consolas", 11))
        self._preview.setStyleSheet("""
            background: #11111b; color: #cdd6f4;
            border: 1px solid #313244; border-radius: 6px;
            padding: 10px;
        """)
        self._preview.setPlaceholderText("// Hier erscheint dein generierter CFG-Code...")
        right_layout.addWidget(self._preview, 1)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([600, 450])
        root.addWidget(splitter)

    def _make_scroll_area(self) -> QWidget:
        inner = QWidget()
        inner.setLayout(QVBoxLayout())
        inner.layout().setContentsMargins(0, 4, 0, 4)
        inner.layout().setSpacing(6)
        inner.layout().addStretch()
        inner.setStyleSheet("background: transparent;")
        return inner

    def _wrap_tab(self, container: QWidget, bind_type: str) -> QWidget:
        wrapper = QWidget()
        wrapper.setStyleSheet("background: #1e1e2e;")
        v = QVBoxLayout(wrapper)
        v.setContentsMargins(0, 8, 0, 8)
        v.setSpacing(6)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border: none; background: transparent; }"
            "QScrollBar:vertical { background:#1e1e2e; width:8px; border-radius:4px; }"
            "QScrollBar::handle:vertical { background:#45475a; border-radius:4px; }"
        )
        scroll.setWidget(container)
        v.addWidget(scroll, 1)

        add_btn = QPushButton(f"＋  {bind_type.capitalize()} Bind hinzufügen")
        add_btn.setStyleSheet(STYLE_ADD_BTN)
        add_btn.clicked.connect(lambda: self._add_row(bind_type))
        v.addWidget(add_btn)
        return wrapper

    # ─────────────────────────────── Logik ───────────────────────────────

    def _add_row(self, bind_type: str):
        container_map = {
            "simple": self._simple_container,
            "toggle": self._toggle_container,
            "hold":   self._hold_container,
            "cfg":    self._cfg_container,
        }
        model_map = {
            "simple": SimpleBind,
            "toggle": ToggleBind,
            "hold":   HoldBind,
            "cfg":    CfgBind,
        }
        widget_map = {
            "simple": SimpleBindRow,
            "toggle": ToggleBindRow,
            "hold":   HoldBindRow,
            "cfg":    CfgBindRow,
        }
        list_map = {
            "simple": self.profile.simple_binds,
            "toggle": self.profile.toggle_binds,
            "hold":   self.profile.hold_binds,
            "cfg":    self.profile.cfg_binds,
        }

        model = model_map[bind_type]()
        list_map[bind_type].append(model)
        row = widget_map[bind_type](model)

        container = container_map[bind_type]
        layout = container.layout()
        # Stretch ist immer am Ende – einfuegen vor Stretch
        layout.insertWidget(layout.count() - 1, row)
        self._row_widgets[bind_type].append(row)

        row.sig_delete.connect(lambda r=row, m=model, bt=bind_type: self._remove_row(r, m, bt))

    def _remove_row(self, row_widget, model, bind_type: str):
        list_map = {
            "simple": self.profile.simple_binds,
            "toggle": self.profile.toggle_binds,
            "hold":   self.profile.hold_binds,
            "cfg":    self.profile.cfg_binds,
        }
        try:
            list_map[bind_type].remove(model)
        except ValueError:
            pass
        self._row_widgets[bind_type].remove(row_widget)
        row_widget.setParent(None)
        row_widget.deleteLater()

    def _generate(self):
        cfg = generate_profile(self.profile)
        self._preview.setPlainText(cfg)

    def _save_file(self):
        self._generate()
        path, _ = QFileDialog.getSaveFileName(
            self, "CFG speichern", f"{self.profile.name}.cfg", "CFG Files (*.cfg)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self._preview.toPlainText())
            QMessageBox.information(self, "Gespeichert", f"Gespeichert unter:\n{path}")

    def _clear_all(self):
        reply = QMessageBox.question(
            self, "Leeren?", "Alle Binds wirklich löschen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            for bt in ["simple", "toggle", "hold", "cfg"]:
                for w in list(self._row_widgets[bt]):
                    w.setParent(None)
                    w.deleteLater()
                self._row_widgets[bt].clear()
            self.profile.simple_binds.clear()
            self.profile.toggle_binds.clear()
            self.profile.hold_binds.clear()
            self.profile.cfg_binds.clear()
            self._preview.clear()
