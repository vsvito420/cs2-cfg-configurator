# app/sidebar.py
from PySide6.QtWidgets import QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

class Sidebar(QListWidget):
    MODULES = [
        ("⚙️ CFG Editor", "cfg_editor"),
        ("🔀 Bind Switcher", "bind_switcher"),   # noch leer
        ("🛒 Buy Binds", "buy_binds"),           # noch leer
    ]

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setFixedWidth(200)
        for label, key in self.MODULES:
            item = QListWidgetItem(label)
            item.setData(Qt.UserRole, key)
            self.addItem(item)
        self.currentItemChanged.connect(self.on_select)

    def on_select(self, current, previous):
        if current:
            module_key = current.data(Qt.UserRole)
            self.main_window.load_module(module_key)