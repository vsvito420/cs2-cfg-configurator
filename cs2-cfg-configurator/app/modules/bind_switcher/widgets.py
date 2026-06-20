# widgets.py – Bind-Karten mit 2-Zeilen-Layout und Autocomplete
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFrame, QComboBox, QCheckBox,
    QCompleter, QSizePolicy
)
from PySide6.QtCore import Signal, Qt, QStringListModel
from PySide6.QtGui import QFont

from .autocomplete import attach_completer, ALL_COMMANDS

# ── Styles ────────────────────────────────────────────────────────────────────

CARD_STYLE = """
    QFrame {
        background: #24273a;
        border: 1px solid #313244;
        border-radius: 10px;
    }
    QFrame:hover {
        border: 1px solid #45475a;
    }
"""
INPUT_STYLE = """
    QLineEdit {
        background: #1e1e2e;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 5px;
        padding: 5px 9px;
        font-size: 12px;
        font-family: 'Consolas', monospace;
    }
    QLineEdit:focus { border: 1px solid #89b4fa; }
"""
TEXT_STYLE = """
    QTextEdit {
        background: #1e1e2e;
        color: #cdd6f4;
        border: 1px solid #45475a;
        border-radius: 5px;
        padding: 5px 9px;
        font-size: 12px;
        font-family: 'Consolas', monospace;
    }
    QTextEdit:focus { border: 1px solid #89b4fa; }
"""
KEY_STYLE = """
    QLineEdit {
        background: #313244;
        color: #f5c2e7;
        border: 2px solid #585b70;
        border-radius: 6px;
        padding: 5px 10px;
        font-size: 13px;
        font-weight: bold;
        font-family: 'Consolas', monospace;
        max-width: 90px;
        min-width: 70px;
    }
    QLineEdit:focus { border: 2px solid #cba6f7; }
"""
LBL_SMALL = "color: #6c7086; font-size: 10px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;"
LBL_TYPE = "color: #a6adc8; font-size: 11px; font-style: italic;"
DEL_BTN = """
    QPushButton {
        background: transparent; color: #585b70;
        border: none; font-size: 15px; padding: 2px 5px;
    }
    QPushButton:hover { color: #f38ba8; }
"""
BADGE_SIMPLE = "background:#a6e3a1; color:#1e1e2e; border-radius:4px; padding:1px 7px; font-size:10px; font-weight:bold;"
BADGE_TOGGLE = "background:#89b4fa; color:#1e1e2e; border-radius:4px; padding:1px 7px; font-size:10px; font-weight:bold;"
BADGE_HOLD   = "background:#fab387; color:#1e1e2e; border-radius:4px; padding:1px 7px; font-size:10px; font-weight:bold;"
BADGE_CFG    = "background:#cba6f7; color:#1e1e2e; border-radius:4px; padding:1px 7px; font-size:10px; font-weight:bold;"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _lbl(text: str, style: str = LBL_SMALL) -> QLabel:
    l = QLabel(text)
    l.setStyleSheet(style)
    return l


def _key_field(placeholder="z.B.  1  /  w  /  ctrl  /  mouse3") -> QLineEdit:
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setStyleSheet(KEY_STYLE)
    w.setToolTip("CS2 Taste: Buchstabe, Zahl, mouse1–5, ctrl, alt, shift, space, ...")
    return w


def _cmd_field(placeholder="") -> QLineEdit:
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setStyleSheet(INPUT_STYLE)
    attach_completer(w)
    return w


def _text_area(placeholder="", h=58) -> QTextEdit:
    w = QTextEdit()
    w.setPlaceholderText(placeholder)
    w.setFixedHeight(h)
    w.setStyleSheet(TEXT_STYLE)
    return w


def _info_field() -> QLineEdit:
    w = QLineEdit()
    w.setPlaceholderText("Beschreibung (optional)")
    w.setStyleSheet(INPUT_STYLE)
    return w


# ── Basis-Karte ───────────────────────────────────────────────────────────────

class _BaseCard(QFrame):
    sig_delete = Signal()

    def __init__(self, badge_text: str, badge_style: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet(CARD_STYLE)
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(14, 10, 14, 12)
        self._root.setSpacing(8)

        # Header-Zeile
        hdr = QHBoxLayout()
        hdr.setSpacing(8)
        badge = QLabel(badge_text)
        badge.setStyleSheet(badge_style)
        hdr.addWidget(badge)
        hdr.addStretch()
        del_btn = QPushButton("✕")
        del_btn.setStyleSheet(DEL_BTN)
        del_btn.setFixedSize(24, 24)
        del_btn.clicked.connect(self.sig_delete)
        hdr.addWidget(del_btn)
        self._root.addLayout(hdr)


# ── Simple Bind ───────────────────────────────────────────────────────────────

class SimpleBindRow(_BaseCard):
    """Zeile 1: [Taste] [Info]
       Zeile 2: [Befehl (mit Autocomplete)         ]
    """
    def __init__(self, model, parent=None):
        super().__init__("SIMPLE", BADGE_SIMPLE, parent)
        m = model

        # Zeile 1
        r1 = QHBoxLayout(); r1.setSpacing(10)
        self._key  = _key_field()
        self._key.setText(m.key)
        self._info = _info_field()
        self._info.setText(m.description)

        r1.addWidget(_lbl("TASTE")); r1.addWidget(self._key)
        r1.addWidget(_lbl("INFO"));  r1.addWidget(self._info, 1)
        self._root.addLayout(r1)

        # Zeile 2
        r2 = QHBoxLayout(); r2.setSpacing(6)
        r2.addWidget(_lbl("BEFEHL"))
        self._cmd = _cmd_field("z.B.  slot1   oder   noclip   oder  cl_righthand 0")
        self._cmd.setText(m.command)
        r2.addWidget(self._cmd, 1)
        self._root.addLayout(r2)

        self._key.textChanged.connect(lambda t: setattr(m, 'key', t))
        self._cmd.textChanged.connect(lambda t: setattr(m, 'command', t))
        self._info.textChanged.connect(lambda t: setattr(m, 'description', t))


# ── Toggle Bind ───────────────────────────────────────────────────────────────

class ToggleBindRow(_BaseCard):
    """Taste + Alias-Name in Zeile 1.
       State A / State B als zwei nebeneinanderliegende Textareas.
    """
    def __init__(self, model, parent=None):
        super().__init__("TOGGLE  A ↔ B", BADGE_TOGGLE, parent)
        m = model

        # Zeile 1
        r1 = QHBoxLayout(); r1.setSpacing(10)
        self._key   = _key_field()
        self._key.setText(m.key)
        self._alias = _cmd_field("Alias-Name  z.B.  toggle_crosshair")
        self._alias.setPlaceholderText("Alias-Name  z.B.  toggle_crosshair")
        self._info  = _info_field()
        self._info.setText(m.description)

        r1.addWidget(_lbl("TASTE"));   r1.addWidget(self._key)
        r1.addWidget(_lbl("ALIAS"));   r1.addWidget(self._alias, 1)
        r1.addWidget(_lbl("INFO"));    r1.addWidget(self._info, 1)
        self._root.addLayout(r1)

        # Zeile 2: A | B
        r2 = QHBoxLayout(); r2.setSpacing(12)

        col_a = QVBoxLayout(); col_a.setSpacing(3)
        col_a.addWidget(_lbl("STATE A  →  (beim 1. Druck)"))
        self._a = _text_area("cl_crosshairsize 2.1; cl_crosshaircolor 1")
        self._a.setPlainText(m.state_a_cmds)
        col_a.addWidget(self._a)

        col_b = QVBoxLayout(); col_b.setSpacing(3)
        col_b.addWidget(_lbl("STATE B  →  (beim 2. Druck)"))
        self._b = _text_area("cl_crosshairsize 4.42; cl_crosshaircolor 5")
        self._b.setPlainText(m.state_b_cmds)
        col_b.addWidget(self._b)

        r2.addLayout(col_a, 1)
        r2.addLayout(col_b, 1)
        self._root.addLayout(r2)

        self._key.textChanged.connect(lambda t: setattr(m, 'key', t))
        self._alias.textChanged.connect(lambda t: setattr(m, 'alias_name', t))
        self._info.textChanged.connect(lambda t: setattr(m, 'description', t))
        self._a.textChanged.connect(lambda: setattr(m, 'state_a_cmds', self._a.toPlainText()))
        self._b.textChanged.connect(lambda: setattr(m, 'state_b_cmds', self._b.toPlainText()))


# ── Hold Bind ─────────────────────────────────────────────────────────────────

class HoldBindRow(_BaseCard):
    """3 Phasen: Before (default-State), While Pressing (+), After Released (-)"""
    def __init__(self, model, parent=None):
        super().__init__("HOLD  ⬇ gedrückt halten", BADGE_HOLD, parent)
        m = model

        # Zeile 1
        r1 = QHBoxLayout(); r1.setSpacing(10)
        self._key   = _key_field()
        self._key.setText(m.key)
        self._alias = _cmd_field("Alias-Name  z.B.  radar_zoom  oder  big_crosshair")
        self._alias.setPlaceholderText("Alias-Name")
        self._info  = _info_field()
        self._info.setText(m.description)

        r1.addWidget(_lbl("TASTE")); r1.addWidget(self._key)
        r1.addWidget(_lbl("ALIAS")); r1.addWidget(self._alias, 1)
        r1.addWidget(_lbl("INFO"));  r1.addWidget(self._info, 1)
        self._root.addLayout(r1)

        # Zeile 2: 3 Phasen
        r2 = QHBoxLayout(); r2.setSpacing(8)

        col_before = QVBoxLayout(); col_before.setSpacing(3)
        col_before.addWidget(_lbl("BEFORE  (Default-State)", "color:#6c7086; font-size:10px;"))
        self._before = _text_area("cl_crosshairsize 1.8\ncl_crosshair_t 0", h=52)
        self._before.setPlainText(getattr(m, 'before_cmds', ''))
        col_before.addWidget(self._before)

        col_press = QVBoxLayout(); col_press.setSpacing(3)
        col_press.addWidget(_lbl("WHILE PRESSING  (+)", "color:#fab387; font-size:10px; font-weight:bold;"))
        self._press = _text_area("cl_crosshairsize 1000\ncl_crosshair_t 1", h=52)
        self._press.setPlainText(m.press_cmds)
        col_press.addWidget(self._press)

        col_rel = QVBoxLayout(); col_rel.setSpacing(3)
        col_rel.addWidget(_lbl("AFTER RELEASED  (-)", "color:#a6e3a1; font-size:10px; font-weight:bold;"))
        self._release = _text_area("cl_crosshairsize 1.8\ncl_crosshair_t 0", h=52)
        self._release.setPlainText(m.release_cmds)
        col_rel.addWidget(self._release)

        r2.addLayout(col_before, 1)
        r2.addLayout(col_press, 1)
        r2.addLayout(col_rel, 1)
        self._root.addLayout(r2)

        self._key.textChanged.connect(lambda t: setattr(m, 'key', t))
        self._alias.textChanged.connect(lambda t: setattr(m, 'alias_name', t))
        self._info.textChanged.connect(lambda t: setattr(m, 'description', t))
        self._before.textChanged.connect(lambda: setattr(m, 'before_cmds', self._before.toPlainText()))
        self._press.textChanged.connect(lambda: setattr(m, 'press_cmds', self._press.toPlainText()))
        self._release.textChanged.connect(lambda: setattr(m, 'release_cmds', self._release.toPlainText()))


# ── CFG Exec Bind ─────────────────────────────────────────────────────────────

class CfgBindRow(_BaseCard):
    """Taste → exec <cfg>.  Zeigt Typ: simple / toggle / hold."""
    def __init__(self, model, parent=None):
        super().__init__("CFG EXEC", BADGE_CFG, parent)
        m = model

        # Zeile 1
        r1 = QHBoxLayout(); r1.setSpacing(10)
        self._key  = _key_field()
        self._key.setText(m.key)

        self._exec_type = QComboBox()
        self._exec_type.addItems(["Simple (einmalig)", "Hold (gedrückt halten)", "Toggle (umschalten)"])
        self._exec_type.setStyleSheet("""
            QComboBox {
                background:#313244; color:#cba6f7;
                border:1px solid #45475a; border-radius:5px;
                padding:4px 8px; font-size:12px;
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background:#313244; color:#cdd6f4;
                border:1px solid #45475a; selection-background-color:#45475a;
            }
        """)
        idx = {"simple": 0, "hold": 1, "toggle": 2}.get(getattr(m, 'exec_type', 'simple'), 0)
        self._exec_type.setCurrentIndex(idx)

        self._info = _info_field()
        self._info.setText(m.description)

        r1.addWidget(_lbl("TASTE")); r1.addWidget(self._key)
        r1.addWidget(_lbl("TYP"));   r1.addWidget(self._exec_type)
        r1.addWidget(_lbl("INFO"));  r1.addWidget(self._info, 1)
        self._root.addLayout(r1)

        # Zeile 2: CFG-Felder je nach Typ
        self._cfg_widget = QWidget()
        self._cfg_layout = QVBoxLayout(self._cfg_widget)
        self._cfg_layout.setContentsMargins(0, 0, 0, 0)
        self._cfg_layout.setSpacing(6)
        self._root.addWidget(self._cfg_widget)

        self._rebuild_cfg_fields(m)
        self._exec_type.currentIndexChanged.connect(lambda _: self._rebuild_cfg_fields(m))

        self._key.textChanged.connect(lambda t: setattr(m, 'key', t))
        self._info.textChanged.connect(lambda t: setattr(m, 'description', t))
        self._exec_type.currentIndexChanged.connect(
            lambda i: setattr(m, 'exec_type', ["simple", "hold", "toggle"][i])
        )

    def _clear_cfg_layout(self):
        while self._cfg_layout.count():
            item = self._cfg_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _rebuild_cfg_fields(self, m):
        self._clear_cfg_layout()
        t = self._exec_type.currentIndex()  # 0=simple, 1=hold, 2=toggle

        if t == 0:  # Simple
            row = QHBoxLayout(); row.setSpacing(8)
            row.addWidget(_lbl("CFG-DATEI"))
            self._cfg_a = _cmd_field("crosshairA.cfg   oder   pistol_setup.cfg")
            self._cfg_a.setText(getattr(m, 'cfg_file', ''))
            self._cfg_a.textChanged.connect(lambda v: setattr(m, 'cfg_file', v))
            row.addWidget(self._cfg_a, 1)
            hint = _lbl("→  bind \"key\" \"exec file.cfg\"", "color:#6c7086; font-size:10px; font-style:italic;")
            row.addWidget(hint)
            w = QWidget(); w.setLayout(row)
            self._cfg_layout.addWidget(w)

        elif t == 1:  # Hold
            row = QHBoxLayout(); row.setSpacing(12)

            col_p = QVBoxLayout(); col_p.setSpacing(3)
            col_p.addWidget(_lbl("WHILE PRESSING  →  exec", "color:#fab387; font-size:10px;"))
            self._cfg_press = _cmd_field("configPressing.cfg")
            self._cfg_press.setText(getattr(m, 'cfg_press', ''))
            self._cfg_press.textChanged.connect(lambda v: setattr(m, 'cfg_press', v))
            col_p.addWidget(self._cfg_press)

            col_r = QVBoxLayout(); col_r.setSpacing(3)
            col_r.addWidget(_lbl("AFTER RELEASED  →  exec", "color:#a6e3a1; font-size:10px;"))
            self._cfg_rel = _cmd_field("configDefault.cfg")
            self._cfg_rel.setText(getattr(m, 'cfg_release', ''))
            self._cfg_rel.textChanged.connect(lambda v: setattr(m, 'cfg_release', v))
            col_r.addWidget(self._cfg_rel)

            row.addLayout(col_p, 1)
            row.addLayout(col_r, 1)
            w = QWidget(); w.setLayout(row)
            self._cfg_layout.addWidget(w)

        elif t == 2:  # Toggle
            row = QHBoxLayout(); row.setSpacing(12)

            col_a = QVBoxLayout(); col_a.setSpacing(3)
            col_a.addWidget(_lbl("STATE A  →  exec", "color:#89b4fa; font-size:10px;"))
            self._cfg_a = _cmd_field("crosshairA.cfg")
            self._cfg_a.setText(getattr(m, 'cfg_file_a', ''))
            self._cfg_a.textChanged.connect(lambda v: setattr(m, 'cfg_file_a', v))
            col_a.addWidget(self._cfg_a)

            col_b = QVBoxLayout(); col_b.setSpacing(3)
            col_b.addWidget(_lbl("STATE B  →  exec", "color:#89b4fa; font-size:10px;"))
            self._cfg_b = _cmd_field("crosshairB.cfg")
            self._cfg_b.setText(getattr(m, 'cfg_file_b', ''))
            self._cfg_b.textChanged.connect(lambda v: setattr(m, 'cfg_file_b', v))
            col_b.addWidget(self._cfg_b)

            row.addLayout(col_a, 1)
            row.addLayout(col_b, 1)
            w = QWidget(); w.setLayout(row)
            self._cfg_layout.addWidget(w)
