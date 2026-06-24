# sidebar.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PySide6.QtCore import Signal


class SidebarItem:
    def __init__(self, label: str, key: str, indent: bool = False):
        self.label = label
        self.key = key
        self.indent = indent


class SidebarCategory:
    def __init__(self, label: str, key: str, children: list = None):
        self.label = label
        self.key = key
        self.children = children or []


NAV = [
    SidebarItem("\U0001f3e0  Dashboard",             "dashboard"),
    SidebarItem("\u2699\ufe0f  CFG Editor",           "cfg_editor"),
    SidebarItem("\u270f\ufe0f  Snippet Injector",     "snippet_panel"),
    SidebarItem("\U0001f50d  Commands",              "command_viewer"),
    SidebarItem("\U0001f517  Bind Manager",          "bind_switcher"),
    SidebarItem("\U0001f4f6  Aktive Settings",       "settings_reader"),
    SidebarItem("\U0001f504  Settings vergleichen",  "settings_compare"),
    SidebarCategory(
        "\U0001f6d2  Buy Binds", "buy_binds_header",
        children=[
            SidebarItem("\U0001f4cb  View Binds", "buy_binds_viewer", indent=True),
            SidebarItem("\u270f\ufe0f   Edit Binds",  "buy_binds_editor", indent=True),
        ]
    ),
    SidebarItem("\U0001f3ae  Settings",             "CFG_MAN_settings"),
    SidebarItem("\U0001f4ac  Feedback & About",     "about"),
]


class SidebarButton(QPushButton):
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
                text-align: left; padding-left: {indent_pad};
                font-size: {font_size}; color: {color};
                background: {bg}; border: none;
                border-radius: 4px; margin: 1px 6px;
            }}
            QPushButton:hover {{ background: #2a2a3d; }}
        """)

    def set_active(self, active: bool):
        self._apply_style(active)


class Sidebar(QWidget):
    MODULES = [
        ("\U0001f3e0  Dashboard",             "dashboard"),
        ("\u2699\ufe0f  CFG Editor",           "cfg_editor"),
        ("\u270f\ufe0f  Snippet Injector",     "snippet_panel"),
        ("\U0001f50d  Commands",              "command_viewer"),
        ("\U0001f517  Bind Manager",          "bind_switcher"),
        ("\U0001f4f6  Aktive Settings",       "settings_reader"),
        ("\U0001f504  Settings vergleichen",  "settings_compare"),
        ("\U0001f4cb  View Binds",            "buy_binds_viewer"),
        ("\u270f\ufe0f   Edit Binds",           "buy_binds_editor"),
        ("\U0001f3ae  Settings",             "CFG_MAN_settings"),
        ("\U0001f4ac  Feedback & About",     "about"),
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
                h = SidebarButton(SidebarItem(entry.label, entry.key))
                h.clicked_key.connect(self._on_click)
                self._buttons.append(h)
                layout.addWidget(h)
                for child in entry.children:
                    b = SidebarButton(child)
                    b.clicked_key.connect(self._on_click)
                    self._buttons.append(b)
                    layout.addWidget(b)
            else:
                b = SidebarButton(entry)
                b.clicked_key.connect(self._on_click)
                self._buttons.append(b)
                layout.addWidget(b)
        layout.addStretch()

    def _on_click(self, key: str):
        self._active_key = key
        for btn in self._buttons:
            btn.set_active(btn.key == key)
        self.main_window.load_module(key)

    def set_active_key(self, key: str):
        self._on_click(key)

    def apply_style(self, settings: dict):
        self.setFixedWidth(settings.get("sidebar_width", 210))
        bg = settings.get("sidebar_bg", "#1e1e2e")
        self.setStyleSheet(f"QWidget{{background-color:{bg};}}")
        for btn in self._buttons:
            btn._apply_style(btn.key == self._active_key)
