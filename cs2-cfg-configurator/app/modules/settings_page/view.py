# settings_page/view.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QColorDialog, QSpinBox, QFormLayout,
    QGroupBox, QFrame,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt
from app import settings_manager


class ColorButton(QPushButton):
    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 28)
        self.set_color(color)
        self.clicked.connect(self._pick_color)

    def set_color(self, hex_color: str):
        self._color = hex_color
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {hex_color};
                border: 1px solid #444;
                border-radius: 4px;
            }}
        """)

    def get_color(self) -> str:
        return self._color

    def _pick_color(self):
        color = QColorDialog.getColor(QColor(self._color), self, "Farbe w\u00e4hlen")
        if color.isValid():
            self.set_color(color.name())


GROUP_STYLE = """
    QGroupBox {
        color: #cdd6f4; border: 1px solid #313244; border-radius: 6px;
        margin-top: 8px; padding: 12px; font-size: 13px;
    }
    QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }
"""


class SettingsPage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.settings = settings_manager.load()
        self._color_fields = {}
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)
        root.setAlignment(Qt.AlignTop)

        title = QLabel("\u2699\ufe0f Einstellungen")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #cdd6f4;")
        root.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #313244;")
        root.addWidget(line)

        # --- App Farben ---
        app_group = QGroupBox("App")
        app_group.setStyleSheet(GROUP_STYLE)
        app_form = QFormLayout(app_group)
        app_form.setSpacing(10)
        self._add_color_row(app_form, "app_bg", "Hintergrundfarbe (App)")
        root.addWidget(app_group)

        # --- Sidebar Farben ---
        sidebar_group = QGroupBox("Seitenleiste")
        sidebar_group.setStyleSheet(GROUP_STYLE)
        sidebar_form = QFormLayout(sidebar_group)
        sidebar_form.setSpacing(10)
        for key, label in [
            ("sidebar_bg",            "Hintergrund"),
            ("sidebar_text",          "Text"),
            ("sidebar_selected_bg",   "Ausgew\u00e4hlt (Hintergrund)"),
            ("sidebar_selected_text", "Ausgew\u00e4hlt (Text)"),
            ("sidebar_hover_bg",      "Hover"),
        ]:
            self._add_color_row(sidebar_form, key, label)
        root.addWidget(sidebar_group)

        # --- Sidebar Breite ---
        width_group = QGroupBox("Sidebar-Breite")
        width_group.setStyleSheet(GROUP_STYLE)
        width_layout = QHBoxLayout(width_group)
        self._width_spin = QSpinBox()
        self._width_spin.setRange(48, 400)
        self._width_spin.setValue(self.settings.get("sidebar_width", 210))
        self._width_spin.setSuffix(" px")
        self._width_spin.setStyleSheet(
            "color: #cdd6f4; background: #313244; border: 1px solid #444; padding: 2px 6px;"
        )
        width_layout.addWidget(QLabel("Breite:"))
        width_layout.addWidget(self._width_spin)
        width_layout.addStretch()
        root.addWidget(width_group)

        # --- Speichern ---
        save_btn = QPushButton("\U0001f4be  Speichern & Anwenden")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7; color: #1e1e2e;
                border: none; border-radius: 6px;
                font-weight: bold; font-size: 13px;
            }
            QPushButton:hover { background-color: #b48ead; }
        """)
        save_btn.clicked.connect(self._save_and_apply)
        root.addWidget(save_btn)
        root.addStretch()

    def _add_color_row(self, form, key: str, label: str):
        btn = ColorButton(self.settings.get(key, "#ffffff"))
        self._color_fields[key] = btn
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #cdd6f4;")
        form.addRow(lbl, btn)

    def _save_and_apply(self):
        for key, btn in self._color_fields.items():
            self.settings[key] = btn.get_color()
        self.settings["sidebar_width"] = self._width_spin.value()
        settings_manager.save(self.settings)
        self.main_window.apply_settings(self.settings)
