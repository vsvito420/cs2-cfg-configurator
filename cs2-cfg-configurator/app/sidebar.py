# sidebar.py
# Objektorientierte Sidebar mit Kategorien und Sub-Eintraegen.
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont


class SidebarItem:
    """Repraesentiert einen einzelnen navigierbaren Eintrag."""
    def __init__(self, label: str, key: str, indent: bool = False):
        self.label = label
        self.key = key
        self.indent = indent


class SidebarCategory:
    """Eine Gruppe mit optionalen Sub-Eintraegen."""
    def __init__(self, label: str, key: str, children: list[SidebarItem] = None):
        self.label = label
        self.key = key
        self.children = children or []


# --- Navigationsdefinition ---
NAV: list[SidebarCategory | SidebarItem] = [
    SidebarItem("\U0001f3e0  Dashboard",        "dashboard"),         # <-- ganz oben
    SidebarItem("\u2699\ufe0f  CFG Editor",        "cfg_editor"),
    SidebarItem("\U0001f517  Bind Manager",      "bind_switcher"),
    SidebarCategory(
        "\U0001f6d2  Buy Binds", "buy_binds_header",
        children=[
            SidebarItem("\U0001f4cb  View Binds",  "buy_binds_viewer", indent=True),
            SidebarItem("\u270f\ufe0f   Edit Binds",  "buy_binds_editor", indent=True),
        ]
    ),
    SidebarItem("\U0001f3ae  Settings",          "CFG_MAN_settings"),
]


class SidebarButton(QPushButton):
    """Ein einzelner Button in der Sidebar."""
    clicked_key = Signal(str)

    def __init__(self, item: SidebarItem, parent=None):
        super().__init__(item.label, parent)
        self.key = item.key
        self.setCheckable(True)
        self.setFlat(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(36)
        self._indent = item.indent
        self._apply_style(False)
        self.clicked.connect(lambda: self.clicked_key.emit(self.key))

    def _apply_style(self, active: bool):
        indent_pad = "28px" if self._indent else "14px"
        font_size = "12px" if self._indent else "13px"
        bg = "#313244" if active else "transparent"
        color = "#cba6f7" if active else ("#a6adc8" if self._indent else "#cdd6f4")
        self.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding-left: {indent_pad};
                font-size: {font_size};
                color: {color};
                background: {bg};
                border: none;
                border-radius: 4px;
                margin: 1px 6px;
            }}
            QPushButton:hover {{ background: #2a2a3d; }}
        """)

    def set_active(self, active: bool):
        self._apply_style(active)


class SidebarCategoryLabel(QLabel):
    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(36)
        self.setContentsMargins(14, 0, 0, 0)
        self.setStyleSheet("""
            QLabel {
                font-size: 13px; color: #cdd6f4;
                font-weight: bold; padding-left: 14px;
            }
        """)


class Sidebar(QWidget):
    MODULES = [
        ("\U0001f3e0  Dashboard",      "dashboard"),
        ("\u2699\ufe0f  CFG Editor",     "cfg_editor"),
        ("\U0001f517  Bind Manager",  "bind_switcher"),
        ("\U0001f4cb  View Binds",    "buy_binds_viewer"),
        ("\u270f\ufe0f   Edit Binds",    "buy_binds_editor"),
        ("\U0001f3ae  Settings",      "CFG_MAN_settings"),
    ]

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        self._buttons: list[SidebarButton] = []
        self._active_key: str | None = None
        self.setFixedWidth(210)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(0)

        for entry in NAV:
            if isinstance(entry, SidebarCategory):
                header_item = SidebarItem(entry.label, entry.key, indent=False)
                header_btn = SidebarButton(header_item)
                header_btn.clicked_key.connect(self._on_click)
                self._buttons.append(header_btn)
                layout.addWidget(header_btn)
                for child in entry.children:
                    btn = SidebarButton(child)
                    btn.clicked_key.connect(self._on_click)
                    self._buttons.append(btn)
                    layout.addWidget(btn)
            else:
                btn = SidebarButton(entry)
                btn.clicked_key.connect(self._on_click)
                self._buttons.append(btn)
                layout.addWidget(btn)

        layout.addStretch()

    def _on_click(self, key: str):
        self._active_key = key
        for btn in self._buttons:
            btn.set_active(btn.key == key)
        self.main_window.load_module(key)

    def set_active_key(self, key: str):
        self._on_click(key)

    def apply_style(self, settings: dict):
        width = settings.get("sidebar_width", 210)
        self.setFixedWidth(width)
        bg = settings.get("sidebar_bg", "#1e1e2e")
        self.setStyleSheet(f"QWidget {{ background-color: {bg}; }}")
        for btn in self._buttons:
            btn._apply_style(btn.key == self._active_key)
