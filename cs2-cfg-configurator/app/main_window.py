# main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout,
)
from PySide6.QtCore import Qt

from app.sidebar import Sidebar
from app.modules.settings_page.view import SettingsPage
from app.modules.buy_binds.view import BuyBindsPage
from app import settings_manager


class ModulePage(QWidget):
    """Einfacher Platzhalter für noch nicht implementierte Module."""
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(title, self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; color: #555;")
        layout.addWidget(label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CS2 CFG Configurator")
        self.resize(1200, 700)

        self.settings = settings_manager.load()

        central = QWidget(self)
        self.setCentralWidget(central)
        self._root_layout = QHBoxLayout(central)
        self._root_layout.setContentsMargins(0, 0, 0, 0)
        self._root_layout.setSpacing(0)

        self.stack = QStackedWidget(self)

        # Module registrieren
        self._pages = {
            "cfg_editor":    ModulePage("⚙️  CFG Editor – kommt bald"),
            "bind_switcher": ModulePage("🔀  Bind Switcher – kommt bald"),
            "buy_binds":     BuyBindsPage(),
            "CFG_MAN_settings": SettingsPage(self),
        }
        for page in self._pages.values():
            self.stack.addWidget(page)

        self.sidebar = Sidebar(self)
        self.sidebar.setCurrentRow(0)
        self._apply_sidebar_style()

        self._root_layout.addWidget(self.sidebar)
        self._root_layout.addWidget(self.stack, 1)

    def load_module(self, key: str):
        page = self._pages.get(key)
        if page is not None:
            self.stack.setCurrentWidget(page)

    def apply_settings(self, settings: dict):
        """Wird von SettingsPage aufgerufen nach dem Speichern."""
        self.settings = settings
        self._apply_sidebar_style()

    def _apply_sidebar_style(self):
        s = self.settings
        width = s.get("sidebar_width", 210)
        self.sidebar.setFixedWidth(width)
        self.sidebar.setStyleSheet(f"""
            QListWidget {{
                background-color: {s.get('sidebar_bg', '#1e1e2e')};
                border: none;
                padding-top: 8px;
            }}
            QListWidget::item {{
                color: {s.get('sidebar_text', '#cdd6f4')};
                padding: 10px 16px;
                font-size: 13px;
                border-radius: 4px;
                margin: 2px 6px;
            }}
            QListWidget::item:selected {{
                background-color: {s.get('sidebar_selected_bg', '#313244')};
                color: {s.get('sidebar_selected_text', '#cba6f7')};
            }}
            QListWidget::item:hover {{
                background-color: {s.get('sidebar_hover_bg', '#2a2a3d')};
            }}
        """)
