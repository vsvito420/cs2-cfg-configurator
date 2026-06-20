# buy_binds/viewer.py
# Zeigt alle gespeicherten .cfg Dateien im buy-binds Ordner an.
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QTextEdit, QSplitter, QMessageBox, QFrame,
)
from PySide6.QtCore import Qt

CFG_DIR = Path(__file__).parent.parent.parent.parent / "configs" / "buy-binds"


class BuyBindsViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(12)

        # Titel + Refresh
        top = QHBoxLayout()
        title = QLabel("\U0001f4cb Buy Binds Viewer")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #cdd6f4;")
        refresh_btn = QPushButton("\U0001f504 Refresh")
        refresh_btn.setFixedWidth(90)
        refresh_btn.setStyleSheet(
            "background: #313244; color: #cdd6f4; border-radius: 4px; padding: 4px 10px;"
        )
        refresh_btn.clicked.connect(self._refresh_list)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(refresh_btn)
        root.addLayout(top)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #313244;")
        root.addWidget(sep)

        # Splitter: Liste links, Inhalt rechts
        splitter = QSplitter(Qt.Horizontal)

        # Dateiliste
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        list_layout.setSpacing(6)
        list_label = QLabel("Gespeicherte Configs")
        list_label.setStyleSheet("color: #888; font-size: 11px;")
        self._file_list = QListWidget()
        self._file_list.setStyleSheet("""
            QListWidget {
                background: #181825;
                border: 1px solid #313244;
                border-radius: 6px;
                color: #cdd6f4;
                font-size: 13px;
            }
            QListWidget::item:selected { background: #313244; color: #cba6f7; }
            QListWidget::item:hover { background: #2a2a3d; }
        """)
        self._file_list.currentItemChanged.connect(self._on_file_select)
        list_layout.addWidget(list_label)
        list_layout.addWidget(self._file_list)

        # Buttons unter der Liste
        btn_row = QHBoxLayout()
        delete_btn = QPushButton("\U0001f5d1 L\u00f6schen")
        delete_btn.setStyleSheet(
            "background: #45475a; color: #f38ba8; border-radius: 4px; padding: 4px 10px; font-size: 12px;"
        )
        delete_btn.clicked.connect(self._delete_selected)
        btn_row.addWidget(delete_btn)
        btn_row.addStretch()
        list_layout.addLayout(btn_row)

        splitter.addWidget(list_widget)

        # Dateiinhalt rechts
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(6)
        content_label = QLabel("Inhalt")
        content_label.setStyleSheet("color: #888; font-size: 11px;")
        self._content_view = QTextEdit()
        self._content_view.setReadOnly(True)
        self._content_view.setStyleSheet("""
            QTextEdit {
                background: #11111b;
                color: #a6e3a1;
                font-family: monospace;
                font-size: 13px;
                border: 1px solid #313244;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        self._content_view.setPlaceholderText("Datei ausw\u00e4hlen...")
        content_layout.addWidget(content_label)
        content_layout.addWidget(self._content_view)
        splitter.addWidget(content_widget)

        splitter.setSizes([220, 580])
        root.addWidget(splitter, 1)

    def _refresh_list(self):
        self._file_list.clear()
        self._content_view.clear()
        CFG_DIR.mkdir(parents=True, exist_ok=True)
        for f in sorted(CFG_DIR.glob("*.cfg")):
            item = QListWidgetItem(f.name)
            item.setData(Qt.UserRole, f)
            self._file_list.addItem(item)
        if self._file_list.count() == 0:
            self._content_view.setPlaceholderText(
                "Keine .cfg Dateien in configs/buy-binds/\nErstelle zuerst einen Bind im Editor."
            )

    def _on_file_select(self, current, previous):
        if current:
            path: Path = current.data(Qt.UserRole)
            try:
                self._content_view.setText(path.read_text(encoding="utf-8"))
            except Exception as e:
                self._content_view.setText(f"Fehler beim Lesen:\n{e}")

    def _delete_selected(self):
        item = self._file_list.currentItem()
        if not item:
            return
        path: Path = item.data(Qt.UserRole)
        reply = QMessageBox.question(
            self, "L\u00f6schen?", f"{path.name} wirklich l\u00f6schen?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            path.unlink(missing_ok=True)
            self._refresh_list()
