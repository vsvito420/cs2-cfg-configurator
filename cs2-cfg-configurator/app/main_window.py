from PySide6.QtWidgets import QMainWindow, QSplitter, QLabel, QWidget
from PySide6.QtCore import Qt
from app.sidebar import Sidebar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CS2 CFG Configurator")
        self.resize(1200, 800)

        splitter = QSplitter(Qt.Horizontal)

        self.sidebar = Sidebar(self)

        self.content = QLabel("← Modul aus der Sidebar wählen")
        self.content.setAlignment(Qt.AlignCenter)
        self.content.setStyleSheet("color: #888; font-size: 16px;")

        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.content)
        splitter.setSizes([200, 1000])

        self.setCentralWidget(splitter)

    def load_module(self, module_key: str):
        """Hier werden später echte Module geladen."""
        placeholder = QLabel(f"[{module_key}] – Noch nicht implementiert")
        placeholder.setAlignment(Qt.AlignCenter)
        placeholder.setStyleSheet("color: #aaa; font-size: 14px;")
        # Alten Content ersetzen
        splitter = self.centralWidget()
        splitter.replaceWidget(1, placeholder)
        self.content = placeholder
