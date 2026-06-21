# dashboard/view.py
import json
import shutil
import subprocess
import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QLineEdit, QSizePolicy, QGridLayout,
    QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QPixmap, QPainter, QPainterPath, QDesktopServices, QColor, QPen

PROJECT_ROOT  = Path(__file__).parent.parent.parent.parent
DATA_ROOT     = PROJECT_ROOT / "data"
CONFIGS_DIR   = PROJECT_ROOT / "configs"
SETTINGS_FILE = PROJECT_ROOT / "configs" / "app_settings.json"
ICON_PATH     = PROJECT_ROOT / "app" / "assets" / "icon.png"

CATEGORY_META = {
    "crosshair":   {"label": "Crosshair",    "icon": "🎯", "folder": "crosshair"},
    "viewmodel":   {"label": "Viewmodel",    "icon": "🔫", "folder": "viewmodel"},
    "map":         {"label": "Map / Radar",  "icon": "🗺️",  "folder": "map"},
    "networking":  {"label": "Networking",   "icon": "🌐", "folder": "networking"},
    "performance": {"label": "Performance",  "icon": "⚡", "folder": "performance"},
    "video":       {"label": "Video",        "icon": "🖥️",  "folder": "video"},
    "buy-binds":   {"label": "Buy Binds",    "icon": "🛒", "folder": "buy-binds"},
}

COLORS = ["#89b4fa","#a6e3a1","#fab387","#f38ba8","#cba6f7","#94e2d5","#f9e2af"]


def _find_cs2_path() -> tuple[str, bool]:
    cs2_sub = Path("steamapps") / "common" / "Counter-Strike Global Offensive"
    if sys.platform == "win32":
        candidates = [
            Path(r"C:\Program Files (x86)\Steam") / cs2_sub,
            Path(r"C:\Program Files\Steam") / cs2_sub,
        ]
        import string
        for drive in string.ascii_uppercase:
            for sub in ("SteamLibrary", "Steam", "Games\\Steam"):
                candidates.append(Path(f"{drive}:\\") / sub / cs2_sub)
        for c in candidates:
            if c.exists():
                return str(c), True
        return str(Path(r"C:\Program Files (x86)\Steam") / cs2_sub), False
    elif sys.platform == "darwin":
        p = Path("~/Library/Application Support/Steam").expanduser() / cs2_sub
        return str(p), p.exists()
    else:
        for base in [Path("~/.steam/steam"), Path("~/.local/share/Steam")]:
            p = base.expanduser() / cs2_sub
            if p.exists():
                return str(p), True
        return str(Path("~/.steam/steam").expanduser() / cs2_sub), False


def _load_saved_cs2_path() -> str | None:
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            return data.get("cs2_path")
        except Exception:
            pass
    return None


def _save_cs2_path(path: str):
    data = {}
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    data["cs2_path"] = path
    SETTINGS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ── Styles ─────────────────────────────────────────────────────────────────
CARD_STYLE = "QFrame { background:#24273a; border:1px solid #313244; border-radius:12px; }"
STYLE_LAUNCH = """
    QPushButton {
        background: qlineargradient(x1:0,y1:0,x2:1,y2:0,stop:0 #89b4fa,stop:1 #74c7ec);
        color:#1e1e2e; border:none; border-radius:8px;
        padding:10px 28px; font-size:14px; font-weight:bold;
    }
    QPushButton:hover { background:#b4d0ff; }
"""
STYLE_SEC = """
    QPushButton {
        background:#313244; color:#cdd6f4; border:none;
        border-radius:6px; padding:7px 14px; font-size:12px;
    }
    QPushButton:hover { background:#45475a; }
"""
STYLE_DEPLOY = """
    QPushButton {
        background:#a6e3a1; color:#1e1e2e; border:none;
        border-radius:6px; padding:7px 16px; font-size:12px; font-weight:bold;
    }
    QPushButton:hover { background:#c0f0bb; }
"""
INPUT_STYLE = """
    QLineEdit {
        background:#1e1e2e; color:#cdd6f4;
        border:1px solid #45475a; border-radius:6px;
        padding:6px 10px; font-size:12px;
        font-family:'Consolas',monospace;
    }
    QLineEdit:focus { border:1px solid #89b4fa; }
"""


class AppIconLabel(QLabel):
    """Zeigt das Programm-Icon rund zugeschnitten — kein Netzwerkzugriff."""
    def __init__(self, size=72, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)
        self._pixmap = None
        if ICON_PATH.exists():
            px = QPixmap(str(ICON_PATH)).scaled(
                size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            self._pixmap = px

    def paintEvent(self, event):
        if not self._pixmap:
            super().paintEvent(event)
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, self._size, self._size)
        p.setClipPath(path)
        p.drawPixmap(0, 0, self._pixmap)
        p.setPen(QPen(QColor("#89b4fa"), 2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(1, 1, self._size - 2, self._size - 2)


class StatCard(QFrame):
    def __init__(self, icon, count, label, sublabel, color="#89b4fa", parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self.setFixedHeight(96)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        v = QVBoxLayout(self)
        v.setContentsMargins(16, 12, 16, 10)
        v.setSpacing(2)
        top = QHBoxLayout()
        ico = QLabel(icon)
        ico.setStyleSheet("font-size:18px; background:transparent; border:none;")
        num = QLabel(str(count))
        num.setStyleSheet(f"color:{color}; font-size:24px; font-weight:bold; background:transparent; border:none;")
        top.addWidget(ico)
        top.addStretch()
        top.addWidget(num)
        v.addLayout(top)
        lbl = QLabel(label)
        lbl.setStyleSheet("color:#cdd6f4; font-size:12px; font-weight:bold; background:transparent; border:none;")
        sub = QLabel(sublabel)
        sub.setStyleSheet("color:#6c7086; font-size:10px; background:transparent; border:none;")
        v.addWidget(lbl)
        v.addWidget(sub)


class DashboardPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cs2_path: str = ""
        self._status_lbl: QLabel = None
        self._path_edit: QLineEdit = None
        self._build()
        self._init_cs2_path()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(
            "QScrollArea{border:none;background:#181825;}"
            "QScrollBar:vertical{background:#181825;width:7px;border-radius:3px;}"
            "QScrollBar::handle:vertical{background:#45475a;border-radius:3px;}"
        )
        inner = QWidget()
        inner.setStyleSheet("background:#181825;")
        scroll.setWidget(inner)
        outer.addWidget(scroll)

        root = QVBoxLayout(inner)
        root.setContentsMargins(32, 28, 32, 32)
        root.setSpacing(22)

        # Hero
        hero = QFrame()
        hero.setStyleSheet("""
            QFrame { background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                stop:0 #1e1e2e,stop:1 #24273a);
                border:1px solid #313244; border-radius:14px; }
        """)
        hl = QHBoxLayout(hero)
        hl.setContentsMargins(28, 22, 28, 22)
        hl.setSpacing(18)
        hl.addWidget(AppIconLabel(76))  # <-- Programm-Icon statt GitHub Avatar
        tc = QVBoxLayout()
        tc.setSpacing(4)
        g = QLabel("🎮  CS2 CFG Configurator")
        g.setStyleSheet("color:#cdd6f4;font-size:20px;font-weight:bold;background:transparent;border:none;")
        s = QLabel("Servus! Hier verwaltest du deine CS2 Configs, Binds und Einstellungen.")
        s.setStyleSheet("color:#6c7086;font-size:12px;background:transparent;border:none;")
        tc.addWidget(g)
        tc.addWidget(s)
        hl.addLayout(tc, 1)
        btn_launch = QPushButton("▶️  CS2 starten")
        btn_launch.setStyleSheet(STYLE_LAUNCH)
        btn_launch.setFixedHeight(42)
        btn_launch.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("steam://rungameid/730")))
        hl.addWidget(btn_launch)
        root.addWidget(hero)

        # Stats
        lbl1 = QLabel("📊  Verfügbare Commands pro Kategorie")
        lbl1.setStyleSheet("color:#a6adc8;font-size:12px;font-weight:bold;")
        root.addWidget(lbl1)

        grid = QGridLayout()
        grid.setSpacing(10)
        col, row = 0, 0
        for i, (key, meta) in enumerate(CATEGORY_META.items()):
            path = DATA_ROOT / meta["folder"] / "commands.json"
            count = 0
            if path.exists():
                try:
                    count = len(json.loads(path.read_text(encoding="utf-8")))
                except Exception:
                    pass
            card = StatCard(meta["icon"], count, meta["label"], f"{count} Commands verfügbar", COLORS[i % len(COLORS)])
            grid.addWidget(card, row, col)
            col += 1
            if col >= 4:
                col = 0
                row += 1
        total_cfgs = sum(1 for _ in CONFIGS_DIR.rglob("*.cfg")) if CONFIGS_DIR.exists() else 0
        bind_cfgs  = sum(1 for _ in (CONFIGS_DIR/"bind-manager").rglob("*.cfg")) if (CONFIGS_DIR/"bind-manager").exists() else 0
        grid.addWidget(StatCard("📁", total_cfgs, "Gespeicherte CFGs", "Alle .cfg im configs/ Ordner", "#cba6f7"), row, col)
        col += 1
        if col >= 4: col = 0; row += 1
        grid.addWidget(StatCard("🔗", bind_cfgs, "Bind Manager CFGs", "In configs/bind-manager/", "#f5c2e7"), row, col)
        root.addLayout(grid)

        # CS2 Pfad + Deploy
        path_card = QFrame()
        path_card.setStyleSheet(CARD_STYLE)
        pv = QVBoxLayout(path_card)
        pv.setContentsMargins(20, 16, 20, 16)
        pv.setSpacing(10)

        phdr = QHBoxLayout()
        pt = QLabel("📂  CS2 Pfad & CFG-Deploy")
        pt.setStyleSheet("color:#cdd6f4;font-size:13px;font-weight:bold;background:transparent;border:none;")
        phdr.addWidget(pt)
        phdr.addStretch()
        self._status_lbl = QLabel("⌛  wird gesucht...")
        self._status_lbl.setStyleSheet("color:#6c7086;font-size:11px;background:transparent;border:none;")
        phdr.addWidget(self._status_lbl)
        pv.addLayout(phdr)

        prow = QHBoxLayout()
        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("CS2 Installationspfad (z.B. G:\\SteamLibrary\\...)")
        self._path_edit.setStyleSheet(INPUT_STYLE)
        self._path_edit.textChanged.connect(self._on_path_changed)

        btn_browse = QPushButton("📂  Durchsuchen")
        btn_browse.setStyleSheet(STYLE_SEC)
        btn_browse.clicked.connect(self._browse_cs2)

        btn_open_cs2 = QPushButton("📁  CS2-Ordner")
        btn_open_cs2.setStyleSheet(STYLE_SEC)
        btn_open_cs2.clicked.connect(lambda: self._open_dir(Path(self._path_edit.text())))

        btn_open_cfg = QPushButton("📁  CFG-Ordner")
        btn_open_cfg.setStyleSheet(STYLE_SEC)
        btn_open_cfg.clicked.connect(self._open_cfg_folder)

        prow.addWidget(self._path_edit, 1)
        prow.addWidget(btn_browse)
        prow.addWidget(btn_open_cs2)
        prow.addWidget(btn_open_cfg)
        pv.addLayout(prow)

        deploy_frame = QFrame()
        deploy_frame.setStyleSheet("QFrame{background:#1e1e2e;border:1px dashed #45475a;border-radius:8px;}")
        dv = QHBoxLayout(deploy_frame)
        dv.setContentsMargins(14, 10, 14, 10)
        dv.setSpacing(12)
        deploy_lbl = QLabel("🚀  CFGs ins Spielverzeichnis kopieren")
        deploy_lbl.setStyleSheet("color:#a6adc8;font-size:12px;background:transparent;border:none;")
        deploy_sub = QLabel("Kopiert alle CFGs aus configs/ nach <cs2>/game/csgo/cfg/")
        deploy_sub.setStyleSheet("color:#585b70;font-size:10px;background:transparent;border:none;")
        text_col2 = QVBoxLayout()
        text_col2.setSpacing(2)
        text_col2.addWidget(deploy_lbl)
        text_col2.addWidget(deploy_sub)
        dv.addLayout(text_col2, 1)
        self._btn_deploy = QPushButton("🚀  Deploy CFGs")
        self._btn_deploy.setStyleSheet(STYLE_DEPLOY)
        self._btn_deploy.setFixedHeight(36)
        self._btn_deploy.clicked.connect(self._deploy_cfgs)
        dv.addWidget(self._btn_deploy)
        pv.addWidget(deploy_frame)

        hint = QLabel("💡 CFG-Zielpfad: <CS2-Pfad>/game/csgo/cfg/")
        hint.setStyleSheet("color:#585b70;font-size:10px;font-style:italic;background:transparent;border:none;")
        pv.addWidget(hint)
        root.addWidget(path_card)
        root.addStretch()

    def _init_cs2_path(self):
        saved = _load_saved_cs2_path()
        if saved and Path(saved).exists():
            self._set_path(saved, found=True)
            return
        found_path, found = _find_cs2_path()
        if found:
            self._set_path(found_path, found=True)
            _save_cs2_path(found_path)
        else:
            self._set_path(found_path, found=False)
            self._ask_for_path()

    def _ask_for_path(self):
        QMessageBox.information(
            self, "CS2-Pfad nicht gefunden",
            "CS2 konnte nicht automatisch gefunden werden.\n"
            "Bitte wähle den Installationsordner manuell.\n\n"
            "Beispiel: G:\\SteamLibrary\\steamapps\\common\\Counter-Strike Global Offensive"
        )
        self._browse_cs2()

    def _browse_cs2(self):
        path = QFileDialog.getExistingDirectory(
            self, "CS2 Installationsordner auswählen",
            self._path_edit.text() or "C:\\"
        )
        if path:
            self._set_path(path, found=True)
            _save_cs2_path(path)

    def _set_path(self, path: str, found: bool):
        self._cs2_path = path
        self._path_edit.setText(path)
        if self._status_lbl:
            if found:
                self._status_lbl.setText("✅  Gefunden")
                self._status_lbl.setStyleSheet("color:#a6e3a1;font-size:11px;background:transparent;border:none;")
            else:
                self._status_lbl.setText("⚠️  Nicht gefunden")
                self._status_lbl.setStyleSheet("color:#fab387;font-size:11px;background:transparent;border:none;")

    def _on_path_changed(self, text: str):
        self._cs2_path = text
        p = Path(text)
        if p.exists():
            _save_cs2_path(text)
            self._status_lbl.setText("✅  Gefunden")
            self._status_lbl.setStyleSheet("color:#a6e3a1;font-size:11px;background:transparent;border:none;")
        else:
            self._status_lbl.setText("⚠️  Nicht gefunden")
            self._status_lbl.setStyleSheet("color:#fab387;font-size:11px;background:transparent;border:none;")

    def _deploy_cfgs(self):
        cs2 = Path(self._path_edit.text())
        target = cs2 / "game" / "csgo" / "cfg"
        if not cs2.exists():
            QMessageBox.warning(self, "Pfad fehlt", "CS2-Pfad ist nicht gesetzt oder existiert nicht.")
            return
        target.mkdir(parents=True, exist_ok=True)
        cfg_files = list(CONFIGS_DIR.rglob("*.cfg"))
        if not cfg_files:
            QMessageBox.information(self, "Keine CFGs", "Keine .cfg-Dateien in configs/ gefunden.")
            return
        copied = []
        for src in cfg_files:
            if src.name == ".gitkeep":
                continue
            shutil.copy2(src, target / src.name)
            copied.append(src.name)
        QMessageBox.information(
            self, "✅  Deploy erfolgreich",
            f"{len(copied)} CFG(s) kopiert nach:\n{target}\n\n" + "\n".join(copied)
        )

    def _open_cfg_folder(self):
        cs2 = Path(self._path_edit.text())
        target = cs2 / "game" / "csgo" / "cfg"
        target.mkdir(parents=True, exist_ok=True)
        self._open_dir(target)

    def _open_dir(self, path: Path):
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
