# dashboard/view.py – Startseite des CS2 CFG Configurators
import json
import subprocess
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QLineEdit, QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, QUrl, QTimer
from PySide6.QtGui import QPixmap, QFont, QPainter, QPainterPath, QDesktopServices
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply

# Pfad-Konstanten
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
DATA_ROOT    = PROJECT_ROOT / "data"
CONFIGS_DIR  = PROJECT_ROOT / "configs"

CATEGORY_META = {
    "crosshair":   {"label": "🎯 Crosshair",    "folder": "crosshair"},
    "viewmodel":   {"label": "🔫 Viewmodel",    "folder": "viewmodel"},
    "map":         {"label": "🗺️  Map / Radar",  "folder": "map"},
    "networking":  {"label": "🌐 Networking",   "folder": "networking"},
    "performance": {"label": "⚡ Performance",   "folder": "performance"},
    "video":       {"label": "🖥️  Video",        "folder": "video"},
    "buy-binds":   {"label": "🛒 Buy Binds",    "folder": "buy-binds"},
}

GITHUB_AVATAR_URL = "https://avatars.githubusercontent.com/u/vsvito420"
GITHUB_AVATAR_FALLBACK = "https://github.com/vsvito420.png?size=100"

# CS2 Standard-Pfade je OS
def _default_cs2_path() -> str:
    if sys.platform == "win32":
        return r"C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike Global Offensive"
    elif sys.platform == "darwin":
        return "~/Library/Application Support/Steam/steamapps/common/Counter-Strike Global Offensive"
    return "~/.steam/steam/steamapps/common/Counter-Strike Global Offensive"


# ── Style-Konstanten ───────────────────────────────────────────────────────────────

CARD_STYLE = """
    QFrame {
        background: #24273a;
        border: 1px solid #313244;
        border-radius: 12px;
    }
"""
STYLE_LAUNCH = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #89b4fa, stop:1 #74c7ec);
        color: #1e1e2e;
        border: none; border-radius: 8px;
        padding: 10px 28px;
        font-size: 14px; font-weight: bold;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #b4d0ff, stop:1 #a0e0f5);
    }
    QPushButton:pressed { background: #585b70; }
"""
STYLE_SEC = """
    QPushButton {
        background: #313244; color: #cdd6f4;
        border: none; border-radius: 6px;
        padding: 8px 16px; font-size: 12px;
    }
    QPushButton:hover { background: #45475a; }
"""
INPUT_STYLE = """
    QLineEdit {
        background: #1e1e2e; color: #cdd6f4;
        border: 1px solid #45475a; border-radius: 6px;
        padding: 6px 10px; font-size: 12px;
        font-family: 'Consolas', monospace;
    }
    QLineEdit:focus { border: 1px solid #89b4fa; }
"""


class RoundAvatar(QLabel):
    """Zeigt ein rundes Avatar-Bild."""
    def __init__(self, size=72, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self._pixmap = None
        self._load_avatar()

    def _load_avatar(self):
        self._mgr = QNetworkAccessManager(self)
        req = QNetworkRequest(QUrl(GITHUB_AVATAR_FALLBACK))
        reply = self._mgr.get(req)
        reply.finished.connect(lambda: self._on_loaded(reply))

    def _on_loaded(self, reply: QNetworkReply):
        if reply.error() == QNetworkReply.NoError:
            data = reply.readAll()
            px = QPixmap()
            px.loadFromData(data)
            if not px.isNull():
                self._pixmap = px.scaled(
                    self._size, self._size,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
                self.update()
        reply.deleteLater()

    def paintEvent(self, event):
        if not self._pixmap:
            super().paintEvent(event)
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, self._size, self._size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, self._pixmap)
        # Rand
        painter.setPen(Qt.NoPen)
        from PySide6.QtGui import QColor, QPen
        pen = QPen(QColor("#89b4fa"), 2)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(1, 1, self._size - 2, self._size - 2)


class StatCard(QFrame):
    """Kleine Info-Kachel: Icon + Zahl + Label."""
    def __init__(self, icon: str, count: int, label: str, color: str = "#89b4fa", parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self.setFixedHeight(90)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 12)
        v.setSpacing(2)

        top = QHBoxLayout()
        ico = QLabel(icon)
        ico.setStyleSheet("font-size: 20px; background: transparent; border: none;")
        num = QLabel(str(count))
        num.setStyleSheet(f"color:{color}; font-size:26px; font-weight:bold; background:transparent; border:none;")
        top.addWidget(ico)
        top.addStretch()
        top.addWidget(num)
        v.addLayout(top)

        lbl = QLabel(label)
        lbl.setStyleSheet("color:#6c7086; font-size:11px; background:transparent; border:none;")
        v.addWidget(lbl)


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()

    def _build(self):
        # Outer scroll
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea { border:none; background:#181825; }"
            "QScrollBar:vertical { background:#181825; width:7px; border-radius:3px; }"
            "QScrollBar::handle:vertical { background:#45475a; border-radius:3px; }"
        )
        inner = QWidget()
        inner.setStyleSheet("background:#181825;")
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        root = QVBoxLayout(inner)
        root.setContentsMargins(32, 28, 32, 32)
        root.setSpacing(24)

        # ── Hero-Bereich ──
        hero = QFrame()
        hero.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #1e1e2e, stop:1 #24273a);
                border: 1px solid #313244;
                border-radius: 14px;
            }
        """)
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(28, 24, 28, 24)
        hero_layout.setSpacing(20)

        # Avatar
        avatar = RoundAvatar(80)
        hero_layout.addWidget(avatar)

        # Text
        text_col = QVBoxLayout()
        text_col.setSpacing(4)
        greeting = QLabel("👋  Hey vsvito420!")
        greeting.setStyleSheet("color:#cdd6f4; font-size:22px; font-weight:bold; background:transparent; border:none;")
        subtitle = QLabel("CS2 CFG Configurator  –  dein modulares Config-Tool")
        subtitle.setStyleSheet("color:#6c7086; font-size:13px; background:transparent; border:none;")
        text_col.addWidget(greeting)
        text_col.addWidget(subtitle)
        hero_layout.addLayout(text_col, 1)

        # CS2 starten
        btn_launch = QPushButton("▶️  CS2 starten")
        btn_launch.setStyleSheet(STYLE_LAUNCH)
        btn_launch.setFixedHeight(44)
        btn_launch.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl("steam://rungameid/730"))
        )
        hero_layout.addWidget(btn_launch)

        root.addWidget(hero)

        # ── Statistiken ──
        sec_lbl = QLabel("📊  Command-Kategorien")
        sec_lbl.setStyleSheet("color:#a6adc8; font-size:13px; font-weight:bold;")
        root.addWidget(sec_lbl)

        grid = QGridLayout()
        grid.setSpacing(12)

        COLORS = ["#89b4fa", "#a6e3a1", "#fab387", "#f38ba8", "#cba6f7", "#94e2d5", "#f9e2af"]
        col_idx = 0
        row_idx = 0
        for i, (key, meta) in enumerate(CATEGORY_META.items()):
            folder = DATA_ROOT / meta["folder"] / "commands.json"
            count = 0
            if folder.exists():
                try:
                    data = json.loads(folder.read_text(encoding="utf-8"))
                    count = len(data)
                except Exception:
                    count = 0
            card = StatCard(meta["label"].split()[0], count, meta["label"], COLORS[i % len(COLORS)])
            grid.addWidget(card, row_idx, col_idx)
            col_idx += 1
            if col_idx >= 4:
                col_idx = 0
                row_idx += 1

        # Gespeicherte CFGs in configs/
        total_cfgs = sum(1 for f in CONFIGS_DIR.rglob("*.cfg")) if CONFIGS_DIR.exists() else 0
        bind_cfgs  = sum(1 for f in (CONFIGS_DIR / "bind-manager").rglob("*.cfg")) if (CONFIGS_DIR / "bind-manager").exists() else 0
        cfg_card   = StatCard("📁", total_cfgs, "Gespeicherte .cfg Dateien", "#cba6f7")
        bind_card  = StatCard("🔗", bind_cfgs,  "Bind Manager CFGs", "#f5c2e7")
        grid.addWidget(cfg_card,  row_idx, col_idx)
        col_idx += 1
        if col_idx >= 4:
            col_idx = 0
            row_idx += 1
        grid.addWidget(bind_card, row_idx, col_idx)

        root.addLayout(grid)

        # ── CS2 Pfad ──
        path_card = QFrame()
        path_card.setStyleSheet(CARD_STYLE)
        pv = QVBoxLayout(path_card)
        pv.setContentsMargins(20, 16, 20, 16)
        pv.setSpacing(10)

        path_hdr = QHBoxLayout()
        path_title = QLabel("📂  CS2 Installations-Pfad")
        path_title.setStyleSheet("color:#cdd6f4; font-size:13px; font-weight:bold; background:transparent; border:none;")
        path_hdr.addWidget(path_title)
        path_hdr.addStretch()

        # Erkannte Pfad-Status
        default_path = _default_cs2_path()
        detected = Path(default_path).expanduser().exists()
        status_lbl = QLabel("✅  Gefunden" if detected else "⚠️  Nicht gefunden")
        status_lbl.setStyleSheet(
            ("color:#a6e3a1;" if detected else "color:#fab387;") +
            " font-size:11px; background:transparent; border:none;"
        )
        path_hdr.addWidget(status_lbl)
        pv.addLayout(path_hdr)

        path_row = QHBoxLayout()
        self._path_edit = QLineEdit(default_path)
        self._path_edit.setStyleSheet(INPUT_STYLE)
        self._path_edit.setReadOnly(True)

        btn_open_cs2 = QPushButton("📂  Ordner")
        btn_open_cs2.setStyleSheet(STYLE_SEC)
        btn_open_cs2.clicked.connect(self._open_cs2_folder)

        btn_open_cfg = QPushButton("📂  CFG-Ordner")
        btn_open_cfg.setStyleSheet(STYLE_SEC)
        btn_open_cfg.clicked.connect(self._open_cfg_folder)

        path_row.addWidget(self._path_edit, 1)
        path_row.addWidget(btn_open_cs2)
        path_row.addWidget(btn_open_cfg)
        pv.addLayout(path_row)

        hint = QLabel("💡 CS2 cfg-Ordner:  <installpfad>/game/csgo/cfg/")
        hint.setStyleSheet("color:#585b70; font-size:10px; font-style:italic; background:transparent; border:none;")
        pv.addWidget(hint)

        root.addWidget(path_card)
        root.addStretch()

    def _open_cs2_folder(self):
        path = Path(self._path_edit.text()).expanduser()
        self._open_dir(path)

    def _open_cfg_folder(self):
        path = Path(self._path_edit.text()).expanduser() / "game" / "csgo" / "cfg"
        self._open_dir(path)

    def _open_dir(self, path: Path):
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
