# app/modules/about/view.py
import webbrowser
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTextEdit, QLineEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QFont

GITHUB_USER       = "vsvito420"
GITHUB_REPO       = "cs2-cfg-configurator"
BASE_URL          = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}"
ISSUES_URL        = f"{BASE_URL}/issues"
NEW_BUG_URL       = f"{BASE_URL}/issues/new?template=bug_report.md"
NEW_FEATURE_URL   = f"{BASE_URL}/issues/new?template=feature_request.md"
RELEASES_URL      = f"{BASE_URL}/releases/latest"
PROFILE_URL       = f"https://github.com/{GITHUB_USER}"


def _open(url: str):
    QDesktopServices.openUrl(QUrl(url))


def _link_button(label: str, url: str, color: str = "#89b4fa") -> QPushButton:
    btn = QPushButton(label)
    btn.setCursor(Qt.PointingHandCursor)
    btn.setFlat(True)
    btn.setStyleSheet(f"""
        QPushButton {{
            color: {color};
            font-size: 13px;
            text-align: left;
            border: none;
            padding: 4px 0px;
            background: transparent;
        }}
        QPushButton:hover {{ color: #cba6f7; text-decoration: underline; }}
    """)
    btn.clicked.connect(lambda: _open(url))
    return btn


def _section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("color: #cba6f7; font-size: 12px; font-weight: bold; margin-top: 12px;")
    return lbl


def _divider() -> QFrame:
    line = QFrame()
    line.setFrameShape(QFrame.HLine)
    line.setStyleSheet("color: #313244;")
    return line


class AboutPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(40, 32, 40, 32)
        root.setSpacing(6)
        root.setAlignment(Qt.AlignTop)

        # ── Header ──────────────────────────────────────────────────────────
        title = QLabel("🎮  CS2 CFG Configurator")
        title.setStyleSheet("color: #cdd6f4; font-size: 22px; font-weight: bold;")
        root.addWidget(title)

        subtitle = QLabel(f"von <a href='{PROFILE_URL}' style='color:#89b4fa;'>@{GITHUB_USER}</a> · CC BY-NC 4.0")
        subtitle.setOpenExternalLinks(True)
        subtitle.setStyleSheet("color: #a6adc8; font-size: 13px;")
        root.addWidget(subtitle)

        root.addWidget(_divider())

        # ── Quick Links ──────────────────────────────────────────────────────
        root.addWidget(_section_label("🔗  Links"))
        for label, url in [
            ("💻  GitHub Repository",          BASE_URL),
            ("📦  Neuestes Release / Download", RELEASES_URL),
            ("🐛  Alle Issues ansehen",          ISSUES_URL),
            ("👤  Profil: @vsvito420",           PROFILE_URL),
        ]:
            root.addWidget(_link_button(label, url))

        root.addWidget(_divider())

        # ── Feedback Form ────────────────────────────────────────────────────
        root.addWidget(_section_label("📨  Feedback / Issue einreichen"))

        hint = QLabel(
            "Fülle das Formular aus – ein Klick öffnet GitHub Issues mit den Infos vor-ausgefüllt."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #6c7086; font-size: 12px; margin-bottom: 4px;")
        root.addWidget(hint)

        # Type picker
        type_row = QHBoxLayout()
        type_lbl = QLabel("Typ:")
        type_lbl.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        type_lbl.setFixedWidth(60)
        self._type_box = QComboBox()
        self._type_box.addItems(["🐛  Bug Report", "💡  Feature Request", "ℹ️  Frage / Sonstiges"])
        self._type_box.setStyleSheet("""
            QComboBox {
                background: #1e1e2e; color: #cdd6f4;
                border: 1px solid #313244; border-radius: 4px;
                padding: 4px 8px; font-size: 13px;
            }
            QComboBox QAbstractItemView {
                background: #1e1e2e; color: #cdd6f4;
                selection-background-color: #313244;
            }
        """)
        type_row.addWidget(type_lbl)
        type_row.addWidget(self._type_box, 1)
        root.addLayout(type_row)

        # Title field
        title_row = QHBoxLayout()
        title_lbl = QLabel("Titel:")
        title_lbl.setStyleSheet("color: #cdd6f4; font-size: 13px;")
        title_lbl.setFixedWidth(60)
        self._title_input = QLineEdit()
        self._title_input.setPlaceholderText("Kurze Zusammenfassung...")
        self._title_input.setStyleSheet("""
            QLineEdit {
                background: #1e1e2e; color: #cdd6f4;
                border: 1px solid #313244; border-radius: 4px;
                padding: 4px 8px; font-size: 13px;
            }
        """)
        title_row.addWidget(title_lbl)
        title_row.addWidget(self._title_input, 1)
        root.addLayout(title_row)

        # Body
        body_lbl = QLabel("Details:")
        body_lbl.setStyleSheet("color: #cdd6f4; font-size: 13px; margin-top: 4px;")
        root.addWidget(body_lbl)
        self._body_input = QTextEdit()
        self._body_input.setPlaceholderText(
            "Beschreibe das Problem / den Wunsch möglichst genau...\n\n"
            "Bei Bugs: Was hast du gemacht? Was ist passiert? Was hättest du erwartet?"
        )
        self._body_input.setFixedHeight(120)
        self._body_input.setStyleSheet("""
            QTextEdit {
                background: #1e1e2e; color: #cdd6f4;
                border: 1px solid #313244; border-radius: 4px;
                padding: 6px; font-size: 13px;
            }
        """)
        root.addWidget(self._body_input)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self._submit_btn = QPushButton("🚀  Auf GitHub einreichen")
        self._submit_btn.setCursor(Qt.PointingHandCursor)
        self._submit_btn.setFixedHeight(36)
        self._submit_btn.setStyleSheet("""
            QPushButton {
                background: #cba6f7; color: #1e1e2e;
                border: none; border-radius: 6px;
                font-size: 13px; font-weight: bold; padding: 0 16px;
            }
            QPushButton:hover { background: #b4befe; }
        """)
        self._submit_btn.clicked.connect(self._submit)

        clear_btn = QPushButton("🗑️  Leeren")
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.setFixedHeight(36)
        clear_btn.setStyleSheet("""
            QPushButton {
                background: #313244; color: #cdd6f4;
                border: none; border-radius: 6px;
                font-size: 13px; padding: 0 16px;
            }
            QPushButton:hover { background: #45475a; }
        """)
        clear_btn.clicked.connect(self._clear)

        btn_row.addWidget(self._submit_btn)
        btn_row.addWidget(clear_btn)
        btn_row.addStretch()
        root.addLayout(btn_row)

        root.addStretch()

    # ── Actions ─────────────────────────────────────────────────────────────

    def _submit(self):
        title = self._title_input.text().strip()
        body  = self._body_input.toPlainText().strip()
        idx   = self._type_box.currentIndex()

        if not title:
            QMessageBox.warning(self, "Titel fehlt", "Bitte gib einen Titel ein.")
            return

        import urllib.parse
        base = NEW_BUG_URL if idx == 0 else NEW_FEATURE_URL if idx == 1 else f"{ISSUES_URL}/new"
        params = urllib.parse.urlencode({"title": title, "body": body})
        _open(f"{base}&{params}" if "?" in base else f"{base}?{params}")

    def _clear(self):
        self._title_input.clear()
        self._body_input.clear()
