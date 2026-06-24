import json
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QPlainTextEdit, QLineEdit, QFrame,
    QComboBox, QMessageBox
)
from PySide6.QtCore import Qt

SETTINGS_FILE = Path(__file__).parent.parent.parent.parent / "configs" / "app_settings.json"


def _get_cfg_dir() -> Path | None:
    """Liest cs2_path aus app_settings.json und gibt den cfg-Ordner zurück."""
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
            p = data.get("cs2_path")
            if p:
                cfg = Path(p) / "game" / "csgo" / "cfg"
                if cfg.exists():
                    return cfg
        except Exception:
            pass
    return None


# ── Styles ─────────────────────────────────────────────────────────────────
CARD = "QFrame{background:#24273a;border:1px solid #313244;border-radius:12px;}"
EDITOR_STYLE = """
    QPlainTextEdit {
        background:#1e1e2e;
        color:#a6e3a1;
        border:1px solid #45475a;
        border-radius:8px;
        padding:10px;
        font-family:'Consolas','Courier New',monospace;
        font-size:13px;
    }
    QPlainTextEdit:focus { border:1px solid #89b4fa; }
"""
INPUT_STYLE = """
    QLineEdit {
        background:#1e1e2e;
        color:#cdd6f4;
        border:1px solid #45475a;
        border-radius:6px;
        padding:6px 10px;
        font-size:12px;
        font-family:'Consolas',monospace;
    }
    QLineEdit:focus { border:1px solid #89b4fa; }
"""
COMBO_STYLE = """
    QComboBox {
        background:#1e1e2e;
        color:#cdd6f4;
        border:1px solid #45475a;
        border-radius:6px;
        padding:5px 10px;
        font-size:12px;
        min-width:180px;
    }
    QComboBox::drop-down { border:none; }
    QComboBox QAbstractItemView {
        background:#24273a;
        color:#cdd6f4;
        border:1px solid #45475a;
        selection-background-color:#313244;
    }
"""
BTN_PRIMARY = """
    QPushButton {
        background:#89b4fa;
        color:#1e1e2e;
        border:none;
        border-radius:8px;
        padding:10px 24px;
        font-size:13px;
        font-weight:bold;
    }
    QPushButton:hover { background:#b4d0ff; }
    QPushButton:disabled { background:#45475a; color:#6c7086; }
"""
BTN_SEC = """
    QPushButton {
        background:#313244;
        color:#cdd6f4;
        border:none;
        border-radius:6px;
        padding:7px 14px;
        font-size:12px;
    }
    QPushButton:hover { background:#45475a; }
"""


class SnippetPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build()
        self._refresh_cfg_path()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(18)
        self.setStyleSheet("background:#181825;")

        # ── Header ──────────────────────────────────────────────────────
        title = QLabel("✏️  CFG Snippet Injector")
        title.setStyleSheet("color:#cdd6f4;font-size:18px;font-weight:bold;")
        root.addWidget(title)

        sub = QLabel("Schreibe oder füge beliebigen CFG-Code ein und speichere ihn direkt in deinen CS2 cfg-Ordner.")
        sub.setStyleSheet("color:#6c7086;font-size:12px;")
        sub.setWordWrap(True)
        root.addWidget(sub)

        # ── Zieldatei ───────────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet(CARD)
        cv = QVBoxLayout(card)
        cv.setContentsMargins(20, 16, 20, 16)
        cv.setSpacing(10)

        file_hdr = QLabel("🎯  Zieldatei")
        file_hdr.setStyleSheet("color:#cdd6f4;font-size:13px;font-weight:bold;background:transparent;border:none;")
        cv.addWidget(file_hdr)

        file_row = QHBoxLayout()
        file_lbl = QLabel("Dateiname:")
        file_lbl.setStyleSheet("color:#a6adc8;font-size:12px;background:transparent;border:none;")
        file_lbl.setFixedWidth(80)

        self._filename_combo = QComboBox()
        self._filename_combo.setStyleSheet(COMBO_STYLE)
        self._filename_combo.setEditable(True)
        self._filename_combo.addItems(["autoexec.cfg", "config.cfg"])
        self._filename_combo.setCurrentText("autoexec.cfg")

        file_row.addWidget(file_lbl)
        file_row.addWidget(self._filename_combo)
        file_row.addStretch()
        cv.addLayout(file_row)

        # Pfad-Anzeige
        self._path_lbl = QLabel("")
        self._path_lbl.setStyleSheet(
            "color:#585b70;font-size:10px;font-family:'Consolas',monospace;"
            "background:transparent;border:none;"
        )
        cv.addWidget(self._path_lbl)

        root.addWidget(card)

        # ── Editor ──────────────────────────────────────────────────────
        editor_lbl = QLabel("📝  CFG-Code")
        editor_lbl.setStyleSheet("color:#cdd6f4;font-size:13px;font-weight:bold;")
        root.addWidget(editor_lbl)

        self._editor = QPlainTextEdit()
        self._editor.setStyleSheet(EDITOR_STYLE)
        self._editor.setPlaceholderText(
            "// Hier CFG-Code eingeben, z.B.:\n"
            "bind \"mouse1\" \"+shoot_custom\"\n"
            "alias \"+shoot_custom\" \"+attack; cl_crosshaircolor_r 0; ...\""
        )
        self._editor.setMinimumHeight(300)
        root.addWidget(self._editor, 1)

        # ── Modus ───────────────────────────────────────────────────────
        mode_row = QHBoxLayout()
        mode_lbl = QLabel("Einfügemodus:")
        mode_lbl.setStyleSheet("color:#a6adc8;font-size:12px;")
        self._mode_combo = QComboBox()
        self._mode_combo.setStyleSheet(COMBO_STYLE)
        self._mode_combo.addItems(["Anhängen (append)", "Voranstellen (prepend)", "Überschreiben (overwrite)"])
        mode_row.addWidget(mode_lbl)
        mode_row.addWidget(self._mode_combo)
        mode_row.addStretch()
        root.addLayout(mode_row)

        # ── Buttons ─────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_save = QPushButton("💾  In CS2 speichern")
        btn_save.setStyleSheet(BTN_PRIMARY)
        btn_save.setFixedHeight(42)
        btn_save.clicked.connect(self._save)

        btn_clear = QPushButton("🗑  Editor leeren")
        btn_clear.setStyleSheet(BTN_SEC)
        btn_clear.setFixedHeight(42)
        btn_clear.clicked.connect(self._editor.clear)

        btn_row.addWidget(btn_save)
        btn_row.addWidget(btn_clear)
        btn_row.addStretch()
        root.addLayout(btn_row)

        # ── Status ──────────────────────────────────────────────────────
        self._status = QLabel("")
        self._status.setStyleSheet("font-size:12px;")
        root.addWidget(self._status)

        # Dateiname → Pfad aktualisieren
        self._filename_combo.currentTextChanged.connect(self._refresh_cfg_path)

    # ── Helpers ─────────────────────────────────────────────────────────────
    def _refresh_cfg_path(self):
        cfg_dir = _get_cfg_dir()
        fname = self._filename_combo.currentText().strip() or "autoexec.cfg"
        if cfg_dir:
            full = cfg_dir / fname
            self._path_lbl.setText(f"→  {full}")
        else:
            self._path_lbl.setText("⚠️  CS2-Pfad nicht gefunden — bitte im Dashboard setzen.")
            self._path_lbl.setStyleSheet(
                "color:#fab387;font-size:10px;font-family:'Consolas',monospace;"
                "background:transparent;border:none;"
            )

    def _save(self):
        code = self._editor.toPlainText().strip()
        if not code:
            self._set_status("⚠️  Editor ist leer.", ok=False)
            return

        cfg_dir = _get_cfg_dir()
        if cfg_dir is None:
            self._set_status(
                "❌  CS2-Pfad nicht gefunden. Bitte im Dashboard setzen.", ok=False
            )
            return

        fname = self._filename_combo.currentText().strip()
        if not fname:
            fname = "autoexec.cfg"
        if not fname.endswith(".cfg"):
            fname += ".cfg"

        target = cfg_dir / fname
        mode_idx = self._mode_combo.currentIndex()  # 0=append 1=prepend 2=overwrite

        existing = target.read_text(encoding="utf-8") if target.exists() else ""
        block = code + "\n"

        if mode_idx == 2:  # overwrite
            target.write_text(block, encoding="utf-8")
        elif mode_idx == 1:  # prepend
            target.write_text(block + "\n" + existing, encoding="utf-8")
        else:  # append (default)
            sep = "\n" if existing.endswith("\n") else "\n\n"
            target.write_text(existing + sep + block, encoding="utf-8")

        self._set_status(f"✅  Gespeichert: {target}", ok=True)
        self._refresh_cfg_path()

    def _set_status(self, msg: str, ok: bool):
        color = "#a6e3a1" if ok else "#f38ba8"
        self._status.setText(msg)
        self._status.setStyleSheet(f"font-size:12px; color:{color};")
