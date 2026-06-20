# widgets.py – Einzelne Bind-Zeilen-Widgets
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFrame
)
from PySide6.QtCore import Signal, Qt

ROW_STYLE = """
    QFrame {
        background: #24273a;
        border: 1px solid #313244;
        border-radius: 8px;
    }
"""
INPUT_STYLE = """
    QLineEdit, QTextEdit {
        background: #1e1e2e;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
    }
    QLineEdit:focus, QTextEdit:focus {
        border: 1px solid #89b4fa;
    }
"""
LABEL_STYLE = "color: #a6adc8; font-size: 11px; margin-bottom: 2px;"
DEL_BTN_STYLE = """
    QPushButton {
        background: transparent; color: #f38ba8;
        border: none; font-size: 16px;
        padding: 2px 6px;
    }
    QPushButton:hover { color: #ff6c7c; }
"""
KEY_STYLE = """
    QLineEdit {
        background: #313244;
        color: #f5c2e7;
        border: 1px solid #45475a;
        border-radius: 4px;
        padding: 4px 8px;
        font-size: 12px;
        font-weight: bold;
        max-width: 80px;
        min-width: 60px;
    }
"""


def _lbl(text: str) -> QLabel:
    l = QLabel(text)
    l.setStyleSheet(LABEL_STYLE)
    return l


def _input(placeholder: str = "", multiline: bool = False) -> QLineEdit | QTextEdit:
    if multiline:
        w = QTextEdit()
        w.setPlaceholderText(placeholder)
        w.setFixedHeight(60)
        w.setStyleSheet(INPUT_STYLE)
        return w
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setStyleSheet(INPUT_STYLE)
    return w


def _key_input() -> QLineEdit:
    w = QLineEdit()
    w.setPlaceholderText("Key")
    w.setStyleSheet(KEY_STYLE)
    return w


class _BaseRow(QFrame):
    sig_delete = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(ROW_STYLE)
        self._outer = QVBoxLayout(self)
        self._outer.setContentsMargins(10, 8, 10, 8)
        self._outer.setSpacing(6)

    def _del_btn(self) -> QPushButton:
        btn = QPushButton("✕")
        btn.setStyleSheet(DEL_BTN_STYLE)
        btn.setFixedSize(28, 28)
        btn.clicked.connect(self.sig_delete)
        return btn


# ──────────────────────── Simple Bind ────────────────────────

class SimpleBindRow(_BaseRow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self._model = model

        header = QHBoxLayout()
        header.addWidget(_lbl("⌨️  Simple Bind"))
        header.addStretch()
        header.addWidget(self._del_btn())
        self._outer.addLayout(header)

        row = QHBoxLayout()
        self._key = _key_input()
        self._key.setText(model.key)
        self._key.setToolTip("Taste, z.B.  h  /  ctrl  /  mouse3")

        self._cmd = _input("Befehl, z.B. slot1   oder   noclip")
        self._cmd.setText(model.command)

        self._desc = _input("Beschreibung (optional)")
        self._desc.setText(model.description)

        self._key.textChanged.connect(lambda t: setattr(model, 'key', t))
        self._cmd.textChanged.connect(lambda t: setattr(model, 'command', t))
        self._desc.textChanged.connect(lambda t: setattr(model, 'description', t))

        row.addWidget(_lbl("Taste")); row.addWidget(self._key)
        row.addWidget(_lbl("Befehl")); row.addWidget(self._cmd, 1)
        row.addWidget(_lbl("Info")); row.addWidget(self._desc, 1)
        self._outer.addLayout(row)


# ──────────────────────── Toggle Bind ────────────────────────

class ToggleBindRow(_BaseRow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self._model = model

        header = QHBoxLayout()
        header.addWidget(_lbl("🔄  Toggle Bind  (wechselt bei jedem Druck zwischen A ↔ B)"))
        header.addStretch()
        header.addWidget(self._del_btn())
        self._outer.addLayout(header)

        row1 = QHBoxLayout()
        self._key   = _key_input()
        self._key.setText(model.key)
        self._alias = _input("Alias-Name, z.B. toggle_crosshair")
        self._alias.setText(model.alias_name)
        self._desc  = _input("Beschreibung (optional)")
        self._desc.setText(model.description)

        row1.addWidget(_lbl("Taste")); row1.addWidget(self._key)
        row1.addWidget(_lbl("Alias")); row1.addWidget(self._alias, 1)
        row1.addWidget(_lbl("Info"));  row1.addWidget(self._desc, 1)
        self._outer.addLayout(row1)

        row2 = QHBoxLayout()
        self._a = _input("State A – Befehle (Semikolon-getrennt)\nz.B. cl_crosshairsize 2.1; cl_crosshaircolor 1", multiline=True)
        self._a.setPlainText(model.state_a_cmds)
        self._b = _input("State B – Befehle (Semikolon-getrennt)\nz.B. cl_crosshairsize 4.42; cl_crosshaircolor 5", multiline=True)
        self._b.setPlainText(model.state_b_cmds)

        col_a = QVBoxLayout(); col_a.addWidget(_lbl("State A  →")); col_a.addWidget(self._a)
        col_b = QVBoxLayout(); col_b.addWidget(_lbl("State B  →")); col_b.addWidget(self._b)
        row2.addLayout(col_a, 1)
        row2.addLayout(col_b, 1)
        self._outer.addLayout(row2)

        self._key.textChanged.connect(lambda t: setattr(model, 'key', t))
        self._alias.textChanged.connect(lambda t: setattr(model, 'alias_name', t))
        self._desc.textChanged.connect(lambda t: setattr(model, 'description', t))
        self._a.textChanged.connect(lambda: setattr(model, 'state_a_cmds', self._a.toPlainText()))
        self._b.textChanged.connect(lambda: setattr(model, 'state_b_cmds', self._b.toPlainText()))


# ──────────────────────── Hold Bind ────────────────────────

class HoldBindRow(_BaseRow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self._model = model

        header = QHBoxLayout()
        header.addWidget(_lbl("🔥  Hold Bind  (gedrückt halten = aktiv, loslassen = zurück)"))
        header.addStretch()
        header.addWidget(self._del_btn())
        self._outer.addLayout(header)

        row1 = QHBoxLayout()
        self._key   = _key_input()
        self._key.setText(model.key)
        self._alias = _input("Alias-Name, z.B. radar_zoom")
        self._alias.setText(model.alias_name)
        self._desc  = _input("Beschreibung (optional)")
        self._desc.setText(model.description)

        row1.addWidget(_lbl("Taste")); row1.addWidget(self._key)
        row1.addWidget(_lbl("Alias")); row1.addWidget(self._alias, 1)
        row1.addWidget(_lbl("Info"));  row1.addWidget(self._desc, 1)
        self._outer.addLayout(row1)

        row2 = QHBoxLayout()
        self._press   = _input("Druecken (+) – Befehle\nz.B. cl_radar_scale 0.3", multiline=True)
        self._press.setPlainText(model.press_cmds)
        self._release = _input("Loslassen (-) – Befehle\nz.B. cl_radar_scale 0.5", multiline=True)
        self._release.setPlainText(model.release_cmds)

        col_p = QVBoxLayout(); col_p.addWidget(_lbl("+  Druecken")); col_p.addWidget(self._press)
        col_r = QVBoxLayout(); col_r.addWidget(_lbl("-  Loslassen")); col_r.addWidget(self._release)
        row2.addLayout(col_p, 1)
        row2.addLayout(col_r, 1)
        self._outer.addLayout(row2)

        self._key.textChanged.connect(lambda t: setattr(model, 'key', t))
        self._alias.textChanged.connect(lambda t: setattr(model, 'alias_name', t))
        self._desc.textChanged.connect(lambda t: setattr(model, 'description', t))
        self._press.textChanged.connect(lambda: setattr(model, 'press_cmds', self._press.toPlainText()))
        self._release.textChanged.connect(lambda: setattr(model, 'release_cmds', self._release.toPlainText()))


# ──────────────────────── CFG Exec Bind ────────────────────────

class CfgBindRow(_BaseRow):
    def __init__(self, model, parent=None):
        super().__init__(parent)
        self._model = model

        header = QHBoxLayout()
        header.addWidget(_lbl("📁  CFG Exec Bind  (lädt eine .cfg-Datei mit einer Taste)"))
        header.addStretch()
        header.addWidget(self._del_btn())
        self._outer.addLayout(header)

        row = QHBoxLayout()
        self._key = _key_input()
        self._key.setText(model.key)

        self._cfg = _input("CFG-Datei, z.B. crosshairA.cfg  oder  pistol_setup.cfg")
        self._cfg.setText(model.cfg_file)

        self._desc = _input("Beschreibung (optional)")
        self._desc.setText(model.description)

        self._key.textChanged.connect(lambda t: setattr(model, 'key', t))
        self._cfg.textChanged.connect(lambda t: setattr(model, 'cfg_file', t))
        self._desc.textChanged.connect(lambda t: setattr(model, 'description', t))

        row.addWidget(_lbl("Taste")); row.addWidget(self._key)
        row.addWidget(_lbl("CFG-Datei")); row.addWidget(self._cfg, 1)
        row.addWidget(_lbl("Info")); row.addWidget(self._desc, 1)
        self._outer.addLayout(row)
