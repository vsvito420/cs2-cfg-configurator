from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class Sidebar(QListWidget):
    MODULES = [
        ("⚙️  CFG Editor", "cfg_editor"),
        ("🔀  Bind Switcher", "bind_switcher"),
        ("🛒  Buy Binds", "buy_binds"),
    ]

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFixedWidth(210)
        self.setStyleSheet("""
            QListWidget {
                background-color: #1e1e2e;
                border: none;
                padding-top: 8px;
            }
            QListWidget::item {
                color: #cdd6f4;
                padding: 10px 16px;
                font-size: 13px;
                border-radius: 4px;
                margin: 2px 6px;
            }
            QListWidget::item:selected {
                background-color: #313244;
                color: #cba6f7;
            }
            QListWidget::item:hover {
                background-color: #2a2a3d;
            }
        """)

        font = QFont()
        font.setPointSize(11)
        self.setFont(font)

        for label, key in self.MODULES:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, key)
            self.addItem(item)

        self.currentItemChanged.connect(self.on_select)

    def on_select(self, current, previous):
        if current:
            module_key = current.data(Qt.UserRole)
            self.main_window.load_module(module_key)
