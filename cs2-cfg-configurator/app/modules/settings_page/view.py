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
    """Button der eine Farbe anzeigt und per Klick einen ColorPicker öffnet."""
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
        color = QColorDialog.getColor(QColor(self._color), self, "Farbe wählen")
        if color.isValid():
            self.set_color(color.name())


class SettingsPage(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self.settings = settings_manager.load()
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(20)
        root.setAlignment(Qt.AlignTop)

        title = QLabel("⚙️ Einstellungen")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #cdd6f4;")
        root.addWidget(title)

        # Trennlinie
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #313244;")
        root.addWidget(line)

        # --- Sidebar Farben ---
        sidebar_group = QGroupBox("Seitenleiste")
        sidebar_group.setStyleSheet("""
            QGroupBox {
                color: #cdd6f4;
                border: 1px solid #313244;
                border-radius: 6px;
                margin-top: 8px;
                padding: 12px;
                font-size: 13px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }
        """)
        form = QFormLayout(sidebar_group)
        form.setSpacing(10)

        self._color_fields = {}
        color_settings = [
            ("sidebar_bg",            "Hintergrund"),
            ("sidebar_text",          "Text"),
            ("sidebar_selected_bg",   "Ausgewählt (Hintergrund)"),
            ("sidebar_selected_text", "Ausgewählt (Text)"),
            ("sidebar_hover_bg",      "Hover"),
        ]
        for key, label in color_settings:
            btn = ColorButton(self.settings.get(key, "#ffffff"))
            self._color_fields[key] = btn
            form.addRow(QLabel(label), btn)

        root.addWidget(sidebar_group)

        # --- Sidebar Breite ---
        width_group = QGroupBox("Sidebar-Breite")
        width_group.setStyleSheet(sidebar_group.styleSheet())
        width_layout = QHBoxLayout(width_group)

        self._width_spin = QSpinBox()
        self._width_spin.setRange(48, 400)
        self._width_spin.setValue(self.settings.get("sidebar_width", 210))
        self._width_spin.setSuffix(" px")
        self._width_spin.setStyleSheet("color: #cdd6f4; background: #313244; border: 1px solid #444; padding: 2px 6px;")

        width_layout.addWidget(QLabel("Breite:"))
        width_layout.addWidget(self._width_spin)
        width_layout.addStretch()
        root.addWidget(width_group)

        # --- Speichern Button ---
        save_btn = QPushButton("💾  Speichern & Anwenden")
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #cba6f7;
                color: #1e1e2e;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover { background-color: #b48ead; }
        """)
        save_btn.clicked.connect(self._save_and_apply)
        root.addWidget(save_btn)
        root.addStretch()

    def _save_and_apply(self):
        for key, btn in self._color_fields.items():
            self.settings[key] = btn.get_color()
        self.settings["sidebar_width"] = self._width_spin.value()
        settings_manager.save(self.settings)
        self.main_window.apply_settings(self.settings)
