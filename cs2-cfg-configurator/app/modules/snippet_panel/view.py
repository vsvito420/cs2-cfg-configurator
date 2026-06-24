# snippet_panel/view.py
# UI-Panel: Rohe CFG-Schnipsel (alias, bind, Kommentare) in .cfg-Dateien einfuegen
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QTextEdit, QComboBox, QFileDialog, QMessageBox,
    QFrame, QSizePolicy, QGroupBox,
)
from PySide6.QtCore import Qt

from app.modules.cfg_editor.snippet_injector import inject_snippet

CONFIGS_ROOT = Path(__file__).parent.parent.parent.parent / "configs"

STYLE_BG      = "#1e1e2e"
STYLE_SURFACE = "#313244"
STYLE_TEXT    = "#cdd6f4"
STYLE_ACCENT  = "#cba6f7"
STYLE_GREEN   = "#a6e3a1"
STYLE_SUBTEXT = "#6c7086"
STYLE_RED     = "#f38ba8"

STYLE_INPUT = (
    f"background: {STYLE_SURFACE}; color: {STYLE_TEXT}; border: 1px solid #444;"
    "border-radius: 4px; padding: 3px 6px; font-family: monospace; font-size: 12px;"
)
STYLE_BTN_SECONDARY = (
    f"background: {STYLE_SURFACE}; color: {STYLE_TEXT}; border-radius: 4px; padding: 5px 12px;"
)
STYLE_BTN_PRIMARY = (
    f"background: {STYLE_ACCENT}; color: #1e1e2e; font-weight: bold;"
    "border-radius: 4px; padding: 6px 16px;"
)

PRESET_SNIPPETS: list[tuple[str, str, str]] = [
    (
        "Crosshair: Schwarz beim Schiessen",
        "Faerbung beim Druecken von Maus1 (schwarz/50%) und Loslassen (weiss/90%)",
        "// Aktiviert benutzerdefinierte Crosshair-Farben und Alpha-Werte\n"
        "cl_crosshaircolor 5\n"
        "cl_crosshairusealpha 1\n"
        "\n"
        "// Alias fuer das Halten der Maustaste (Schwarz & 50% Opacity)\n"
        'alias "+shoot_custom" "+attack; cl_crosshaircolor_r 0; cl_crosshaircolor_g 0; cl_crosshaircolor_b 0; cl_crosshairalpha 128"\n'
        "\n"
        "// Alias fuer das Loslassen der Maustaste (Weiss & 90% Opacity)\n"
        'alias "-shoot_custom" "-attack; cl_crosshaircolor_r 255; cl_crosshaircolor_g 255; cl_crosshaircolor_b 255; cl_crosshairalpha 230"\n'
        "\n"
        "// Bind auf die linke Maustaste\n"
        'bind "mouse1" "+shoot_custom"',
    ),
    (
        "Jumpthrow Bind",
        "Wirft Granate gleichzeitig mit dem Sprung (Standard: ALT)",
        'alias "+jumpthrow" "+jump; -attack"\n'
        'alias "-jumpthrow" "-jump"\n'
        'bind "alt" "+jumpthrow"',
    ),
    (
        "Quick Switch Bind",
        "Schnell zur Pistole und zurueck wechseln",
        'alias "quickswitch" "slot2; wait 5; lastinv"\n'
        'bind "q" "quickswitch"',
    ),
    (
        "Noclip Toggle (Practice)",
        "Noclip an/aus fuer Uebungsserver",
        'bind "n" "noclip"',
    ),
    (
        "Net Graph Toggle",
        "Netzwerkstatistiken ein-/ausblenden",
        'bind "F3" "toggle net_graph 0 1"',
    ),
    (
        "Voice Enable Toggle",
        "Teamspeak stumm schalten und wieder aktivieren",
        'alias "muteteam" "voice_enable 0; alias voicetoggle unmuteteam"\n'
        'alias "unmuteteam" "voice_enable 1; alias voicetoggle muteteam"\n'
        'alias "voicetoggle" "muteteam"\n'
        'bind "F4" "voicetoggle"',
    ),
]


class SnippetPanel(QWidget):
    """UI um rohe CFG-Schnipsel (alias, bind, Kommentare) in .cfg-Dateien einzufuegen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(14)

        title = QLabel("\u270f\ufe0f  CFG Snippet Injector")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {STYLE_TEXT};")
        root.addWidget(title)

        subtitle = QLabel(
            "Fuege beliebige CFG-Bloecke (alias, bind, Kommentare) direkt in .cfg-Dateien ein."
        )
        subtitle.setStyleSheet(f"color: {STYLE_SUBTEXT}; font-size: 12px;")
        root.addWidget(subtitle)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #313244;")
        root.addWidget(sep)

        # --- Preset-Auswahl ---
        preset_group = QGroupBox("\U0001f4cb Vorlagen")
        preset_group.setStyleSheet(
            f"QGroupBox {{ color: {STYLE_TEXT}; border: 1px solid #313244;"
            "border-radius: 6px; margin-top: 8px; padding: 10px; }}"
            "QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }"
        )
        preset_layout = QHBoxLayout(preset_group)

        self._preset_combo = QComboBox()
        self._preset_combo.setStyleSheet(
            f"background: {STYLE_SURFACE}; color: {STYLE_TEXT}; border-radius: 4px; padding: 4px;"
        )
        self._preset_combo.addItem("-- Vorlage waehlen --")
        for name, _, _ in PRESET_SNIPPETS:
            self._preset_combo.addItem(name)
        preset_layout.addWidget(self._preset_combo, 1)

        load_preset_btn = QPushButton("Laden")
        load_preset_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        load_preset_btn.clicked.connect(self._load_preset)
        preset_layout.addWidget(load_preset_btn)

        root.addWidget(preset_group)

        # --- Kommentar-Header ---
        header_row = QHBoxLayout()
        header_lbl = QLabel("Kommentar-Header (optional):")
        header_lbl.setStyleSheet(f"color: {STYLE_TEXT};")
        header_row.addWidget(header_lbl)
        self._header_input = QLineEdit()
        self._header_input.setPlaceholderText("z.B.  Crosshair Farbwechsel beim Schiessen")
        self._header_input.setStyleSheet(STYLE_INPUT)
        header_row.addWidget(self._header_input, 1)
        root.addLayout(header_row)

        # --- Snippet-Editor ---
        editor_lbl = QLabel("CFG-Schnipsel:")
        editor_lbl.setStyleSheet(f"color: {STYLE_TEXT};")
        root.addWidget(editor_lbl)

        self._editor = QTextEdit()
        self._editor.setStyleSheet(
            f"background: #11111b; color: {STYLE_GREEN}; font-family: monospace;"
            "font-size: 12px; border: 1px solid #313244; border-radius: 4px;"
        )
        self._editor.setPlaceholderText(
            '// Trage hier deinen CFG-Block ein, z.B.:\n'
            'alias "+shoot_custom" "+attack; cl_crosshaircolor_r 0"\n'
            'bind "mouse1" "+shoot_custom"'
        )
        self._editor.setMinimumHeight(180)
        root.addWidget(self._editor, 1)

        # --- Ziel-Datei ---
        target_row = QHBoxLayout()
        target_lbl = QLabel("Ziel .cfg-Datei:")
        target_lbl.setStyleSheet(f"color: {STYLE_TEXT}; min-width: 110px;")
        target_row.addWidget(target_lbl)

        self._target_input = QLineEdit()
        self._target_input.setPlaceholderText("configs/crosshair/autoexec.cfg  oder Pfad waehlen")
        self._target_input.setStyleSheet(STYLE_INPUT)
        target_row.addWidget(self._target_input, 1)

        browse_btn = QPushButton("\U0001f4c2 Durchsuchen")
        browse_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        browse_btn.clicked.connect(self._browse_target)
        target_row.addWidget(browse_btn)

        new_file_btn = QPushButton("+ Neue Datei")
        new_file_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        new_file_btn.clicked.connect(self._new_file)
        target_row.addWidget(new_file_btn)

        root.addLayout(target_row)

        # --- Modus-Auswahl + Inject-Button ---
        action_row = QHBoxLayout()

        mode_lbl = QLabel("Einfuegemodus:")
        mode_lbl.setStyleSheet(f"color: {STYLE_TEXT};")
        action_row.addWidget(mode_lbl)

        self._mode_combo = QComboBox()
        self._mode_combo.setStyleSheet(
            f"background: {STYLE_SURFACE}; color: {STYLE_TEXT}; border-radius: 4px; padding: 4px;"
        )
        self._mode_combo.addItems([
            "Anhaengen (append)",
            "Voranstellen (prepend)",
            "Ueberschreiben (overwrite)",
        ])
        action_row.addWidget(self._mode_combo)
        action_row.addStretch()

        clear_btn = QPushButton("\U0001f5d1 Editor leeren")
        clear_btn.setStyleSheet(STYLE_BTN_SECONDARY)
        clear_btn.clicked.connect(self._editor.clear)
        action_row.addWidget(clear_btn)

        inject_btn = QPushButton("\U0001f489 In CFG einfuegen")
        inject_btn.setStyleSheet(STYLE_BTN_PRIMARY)
        inject_btn.clicked.connect(self._inject)
        action_row.addWidget(inject_btn)

        root.addLayout(action_row)

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(f"color: {STYLE_GREEN}; font-size: 11px;")
        self._status_lbl.setWordWrap(True)
        root.addWidget(self._status_lbl)

    def _load_preset(self):
        idx = self._preset_combo.currentIndex() - 1
        if idx < 0:
            return
        name, description, code = PRESET_SNIPPETS[idx]
        self._editor.setPlainText(code)
        self._header_input.setText(description)
        self._status_lbl.setText(f"\u2705 Vorlage geladen: {name}")
        self._status_lbl.setStyleSheet(f"color: {STYLE_GREEN}; font-size: 11px;")

    def _browse_target(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "CFG-Datei oeffnen", str(CONFIGS_ROOT), "CFG Files (*.cfg);;All Files (*)"
        )
        if path:
            self._target_input.setText(path)

    def _new_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Neue CFG-Datei erstellen", str(CONFIGS_ROOT), "CFG Files (*.cfg)"
        )
        if path:
            if not path.endswith(".cfg"):
                path += ".cfg"
            self._target_input.setText(path)

    def _get_mode(self) -> str:
        return ["append", "prepend", "overwrite"][self._mode_combo.currentIndex()]

    def _inject(self):
        snippet = self._editor.toPlainText().strip()
        if not snippet:
            QMessageBox.warning(self, "Leerer Schnipsel", "Bitte zuerst einen CFG-Block eingeben.")
            return

        raw_target = self._target_input.text().strip()
        if not raw_target:
            QMessageBox.warning(self, "Kein Ziel", "Bitte eine Ziel-.cfg-Datei angeben.")
            return

        target_path = Path(raw_target)
        if not target_path.is_absolute():
            target_path = CONFIGS_ROOT / target_path

        header = self._header_input.text().strip()
        mode = self._get_mode()

        try:
            inject_snippet(snippet, target_path, mode=mode, header_comment=header)
            self._status_lbl.setText(
                f"\u2705 Schnipsel eingefuegt ({mode}) \u2192 {target_path}"
            )
            self._status_lbl.setStyleSheet(f"color: {STYLE_GREEN}; font-size: 11px;")
        except Exception as exc:
            self._status_lbl.setText(f"\u274c Fehler: {exc}")
            self._status_lbl.setStyleSheet(f"color: {STYLE_RED}; font-size: 11px;")
