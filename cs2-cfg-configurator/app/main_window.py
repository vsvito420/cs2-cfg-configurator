# main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout,
)
from PySide6.QtCore import Qt

from app.sidebar import Sidebar
from app.modules.settings_page.view import SettingsPage
from app.modules.buy_binds.view import BuyBindsPage
from app.modules.buy_binds.viewer import BuyBindsViewer
from app.modules.cfg_editor.view import CfgEditorPage
from app import settings_manager


class ModulePage(QWidget):
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

        self._pages = {
            "cfg_editor":        CfgEditorPage(),
            "bind_switcher":     ModulePage("\U0001f500  Bind Switcher \u2013 kommt bald"),
            "buy_binds_viewer":  BuyBindsViewer(),
            "buy_binds_editor":  BuyBindsPage(),
            "buy_binds_header":  ModulePage("\U0001f6d2  Buy Binds"),
            "CFG_MAN_settings":  SettingsPage(self),
        }
        for page in self._pages.values():
            self.stack.addWidget(page)

        self.sidebar = Sidebar(self)
        self._apply_settings_to_ui()
        self.sidebar.set_active_key("buy_binds_viewer")

        self._root_layout.addWidget(self.sidebar)
        self._root_layout.addWidget(self.stack, 1)

    def load_module(self, key: str):
        page = self._pages.get(key)
        if page:
            self.stack.setCurrentWidget(page)

    def apply_settings(self, settings: dict):
        self.settings = settings
        self._apply_settings_to_ui()

    def _apply_settings_to_ui(self):
        s = self.settings
        bg = s.get("app_bg", "#181825")
        self.centralWidget().setStyleSheet(f"background-color: {bg};")
        self.stack.setStyleSheet(f"background-color: {bg};")
        self.sidebar.apply_style(s)
