# main_window.py
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QStackedWidget, QLabel, QVBoxLayout,
)
from PySide6.QtCore import Qt

from sidebar import Sidebar


class ModulePage(QWidget):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(title, self)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; color: #888;")
        layout.addWidget(label)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CS2 CFG Configurator")
        self.resize(1000, 650)

        self.modules = {}

        central = QWidget(self)
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.stack = QStackedWidget(self)
        for label, key in Sidebar.MODULES:
            page = ModulePage(label, self)
            self.modules[key] = page
            self.stack.addWidget(page)

        self.sidebar = Sidebar(self)
        self.sidebar.setCurrentRow(0)

        root.addWidget(self.sidebar)
        root.addWidget(self.stack, 1)

    def load_module(self, key: str):
        page = self.modules.get(key)
        if page is not None:
            self.stack.setCurrentWidget(page)
