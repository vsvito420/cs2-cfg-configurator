# cfg_editor/view.py
# Haupt-UI fuer den CFG Editor: Kategorie-Tabs, Checkbox + Wert-Editor, CFG-Export
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QScrollArea, QFrame, QGroupBox, QGridLayout,
    QMessageBox, QTabWidget, QCheckBox, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from app.modules.cfg_editor.data_loader import load_category, available_categories, CATEGORY_META
from app.modules.cfg_editor.generator import generate_cfg

CONFIGS_ROOT = Path(__file__).parent.parent.parent.parent / "configs"

STYLE_BG = "#1e1e2e"
STYLE_SURFACE = "#313244"
STYLE_TEXT = "#cdd6f4"
STYLE_ACCENT = "#cba6f7"
STYLE_GREEN = "#a6e3a1"
STYLE_SUBTEXT = "#6c7086"

STYLE_CB = f"QCheckBox {{ color: {STYLE_TEXT}; font-size: 12px; }}"
STYLE_GROUP = f"""
    QGroupBox {{
        color: {STYLE_TEXT}; border: 1px solid #313244;
        border-radius: 6px; margin-top: 8px; padding: 10px;
    }}
    QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}
"""
STYLE_INPUT = (
    f"background: {STYLE_SURFACE}; color: {STYLE_TEXT}; border: 1px solid #444;"
    "border-radius: 4px; padding: 3px 6px; font-family: monospace; font-size: 12px;"
)
STYLE_BTN_SECONDARY = (
    f"background: {STYLE_SURFACE}; color: {STYLE_TEXT}; border-radius: 4px; padding: 5px 12px;"
)
STYLE_BTN_PRIMARY = (
    f"background: {STYLE_ACCENT}; color: #1e1e2e; font-weight: bold; border-radius: 4px; padding: 6px 16px;"
)


class CommandRow(QWidget):
    """Eine Zeile: [Checkbox] command_name   [value input]   description"""

    def __init__(self, entry: dict, parent=None):
        super().__init__(parent)
        self.entry = entry
        self._build()

    def _build(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(8)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(True)
        self.checkbox.setStyleSheet(STYLE_CB)
        layout.addWidget(self.checkbox)

        cmd_label = QLabel(self.entry["command"])
        cmd_label.setStyleSheet(
            f"color: {STYLE_ACCENT}; font-family: monospace; font-size: 12px; min-width: 260px;"
        )
        cmd_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(cmd_label)

        self.value_input = QLineEdit(str(self.entry["default"]))
        self.value_input.setFixedWidth(90)
        self.value_input.setStyleSheet(STYLE_INPUT)
        self.value_input.setPlaceholderText(self.entry.get("range", ""))
        layout.addWidget(self.value_input)

        range_label = QLabel(f"[{self.entry.get('range', '')}]")
        range_label.setStyleSheet(f"color: {STYLE_SUBTEXT}; font-size: 11px; min-width: 80px;")
        layout.addWidget(range_label)

        desc_label = QLabel(self.entry.get("description", ""))
        desc_label.setStyleSheet(f"color: {STYLE_SUBTEXT}; font-size: 11px;")
        desc_label.setWordWrap(True)
        desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        layout.addWidget(desc_label, 1)

    def is_selected(self) -> bool:
        return self.checkbox.isChecked()

    def get_value(self) -> str:
        return self.value_input.text().strip()

    def reset_to_default(self):
        self.value_input.setText(str(self.entry["default"]))
        self.checkbox.setChecked(True)


class CategoryTab(QWidget):
    """Tab-Inhalt fuer eine Kategorie: Liste von CommandRows + Aktions-Buttons."""

    def __init__(self, category_key: str, parent=None):
        super().__init__(parent)
        self.category_key = category_key
        self.rows: list[CommandRow] = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 8, 0, 0)
        root.setSpacing(6)

        # --- Toolbar: Alle an/ab, Reset ---
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        select_all_btn = QPushButton("✅ Alle auswaehlen")
        select_all_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        select_all_btn.clicked.connect(self._select_all)
        toolbar.addWidget(select_all_btn)

        deselect_btn = QPushButton("⬜ Alle abwaehlen")
        deselect_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        deselect_btn.clicked.connect(self._deselect_all)
        toolbar.addWidget(deselect_btn)

        reset_btn = QPushButton("🔄 Defaults laden")
        reset_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        reset_btn.clicked.connect(self._reset_defaults)
        toolbar.addWidget(reset_btn)

        toolbar.addStretch()
        root.addLayout(toolbar)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: #313244;")
        root.addWidget(sep)

        # --- Header-Zeile ---
        header = QHBoxLayout()
        header.setContentsMargins(4, 0, 4, 0)
        header.setSpacing(8)
        for text, width, align in [
            ("", 20, Qt.AlignLeft),
            ("Command", 260, Qt.AlignLeft),
            ("Wert", 90, Qt.AlignLeft),
            ("Range", 80, Qt.AlignLeft),
            ("Beschreibung", -1, Qt.AlignLeft),
        ]:
            lbl = QLabel(text)
            lbl.setStyleSheet(f"color: {STYLE_SUBTEXT}; font-size: 11px; font-weight: bold;")
            if width > 0:
                lbl.setFixedWidth(width)
            header.addWidget(lbl, 0 if width > 0 else 1)
        root.addLayout(header)

        # --- Scroll-Bereich mit Command-Rows ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        inner = QWidget()
        inner_layout = QVBoxLayout(inner)
        inner_layout.setSpacing(2)
        inner_layout.setAlignment(Qt.AlignTop)

        commands = load_category(self.category_key)
        for entry in commands:
            row = CommandRow(entry)
            self.rows.append(row)
            inner_layout.addWidget(row)

        if not commands:
            inner_layout.addWidget(
                QLabel("Keine Daten gefunden – commands.json fehlt?")
            )

        scroll.setWidget(inner)
        root.addWidget(scroll, 1)

    def _select_all(self):
        for row in self.rows:
            row.checkbox.setChecked(True)

    def _deselect_all(self):
        for row in self.rows:
            row.checkbox.setChecked(False)

    def _reset_defaults(self):
        for row in self.rows:
            row.reset_to_default()

    def collect_selected(self) -> list[dict]:
        result = []
        for row in self.rows:
            if row.is_selected():
                result.append({"command": row.entry["command"], "value": row.get_value()})
        return result


class CfgEditorPage(QWidget):
    """Haupt-Widget das in MainWindow eingebunden wird."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs: dict[str, CategoryTab] = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        # Titel
        title = QLabel("⚙️  CFG Editor")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {STYLE_TEXT};")
        root.addWidget(title)

        subtitle = QLabel(
            "Waehle Kategorien und passe Werte an – danach als .cfg exportieren."
        )
        subtitle.setStyleSheet(f"color: {STYLE_SUBTEXT}; font-size: 12px;")
        root.addWidget(subtitle)

        # Tabs pro Kategorie
        self._tab_widget = QTabWidget()
        self._tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{ border: 1px solid #313244; background: {STYLE_BG}; }}
            QTabBar::tab {{
                background: {STYLE_SURFACE}; color: {STYLE_SUBTEXT};
                padding: 6px 14px; border-radius: 4px 4px 0 0;
            }}
            QTabBar::tab:selected {{ background: #45475a; color: {STYLE_TEXT}; }}
        """)

        for cat_key in available_categories():
            meta = CATEGORY_META.get(cat_key, {})
            label = meta.get("label", cat_key)
            tab = CategoryTab(cat_key)
            self._tabs[cat_key] = tab
            self._tab_widget.addTab(tab, label)

        root.addWidget(self._tab_widget, 1)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: #313244;")
        root.addWidget(sep)

        # --- Export-Bereich ---
        export_row = QHBoxLayout()
        export_row.setSpacing(10)

        fn_label = QLabel("Dateiname:")
        fn_label.setStyleSheet(f"color: {STYLE_TEXT};")
        export_row.addWidget(fn_label)

        self._filename_input = QLineEdit()
        self._filename_input.setPlaceholderText("z.B. crosshair_pro  (ohne .cfg)")
        self._filename_input.setFixedWidth(240)
        self._filename_input.setStyleSheet(STYLE_INPUT)
        export_row.addWidget(self._filename_input)

        export_row.addStretch()

        preview_btn = QPushButton("🔍 Vorschau")
        preview_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        preview_btn.clicked.connect(self._show_preview)
        export_row.addWidget(preview_btn)

        save_btn = QPushButton("💾 CFG speichern")
        save_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        save_btn.clicked.connect(self._save_cfg)
        export_row.addWidget(save_btn)

        root.addLayout(export_row)

        # Vorschau-Box
        self._preview_box = QLabel("")
        self._preview_box.setStyleSheet(
            f"font-family: monospace; font-size: 11px; color: {STYLE_GREEN};"
            f"background: #11111b; padding: 10px; border-radius: 4px; min-height: 60px;"
        )
        self._preview_box.setWordWrap(True)
        self._preview_box.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._preview_box.setVisible(False)
        root.addWidget(self._preview_box)

    def _current_tab(self) -> CategoryTab | None:
        idx = self._tab_widget.currentIndex()
        key = list(self._tabs.keys())[idx] if idx >= 0 else None
        return self._tabs.get(key) if key else None

    def _build_lines(self) -> list[str]:
        tab = self._current_tab()
        if not tab:
            return []
        entries = tab.collect_selected()
        lines = []
        for e in entries:
            val = e["value"]
            lines.append(e["command"] if val == "" else f"{e['command']} {val}")
        return lines

    def _show_preview(self):
        lines = self._build_lines()
        if not lines:
            self._preview_box.setText("(keine Commands ausgewaehlt)")
        else:
            self._preview_box.setText("\n".join(lines))
        self._preview_box.setVisible(True)

    def _save_cfg(self):
        tab = self._current_tab()
        if not tab:
            return
        entries = tab.collect_selected()
        if not entries:
            QMessageBox.information(self, "Leer", "Keine Commands ausgewaehlt.")
            return

        filename = self._filename_input.text().strip()
        if not filename:
            # Fallback: kategorie-name
            filename = tab.category_key
        if not filename.endswith(".cfg"):
            filename += ".cfg"

        cat_folder = CATEGORY_META.get(tab.category_key, {}).get("folder", tab.category_key)
        out_dir = CONFIGS_ROOT / cat_folder
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / filename

        generate_cfg(entries, out_path)
        QMessageBox.information(
            self, "Gespeichert",
            f"CFG gespeichert:\n{out_path}"
        )
        self._show_preview()
