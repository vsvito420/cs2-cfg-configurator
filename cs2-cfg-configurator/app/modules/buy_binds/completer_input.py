# buy_binds/completer_input.py
# QLineEdit mit Tab-Autocomplete. Bereit fuer spaetere Nutzung.
from PySide6.QtWidgets import QLineEdit, QCompleter
from PySide6.QtCore import Qt


class CompleterLineEdit(QLineEdit):
    """
    QLineEdit mit Tab-Autocomplete.
    Verwendung:
        widget = CompleterLineEdit(suggestions=["ak47", "awp", ...])
    Tab-Taste vervollstaendigt den ersten Vorschlag.
    """
    def __init__(self, suggestions: list[str] = None, parent=None):
        super().__init__(parent)
        self._completer = None
        if suggestions:
            self.set_suggestions(suggestions)

    def set_suggestions(self, suggestions: list[str]):
        self._completer = QCompleter(suggestions, self)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.setCompletionMode(QCompleter.InlineCompletion)
        self.setCompleter(self._completer)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab and self._completer:
            suggestion = self._completer.currentCompletion()
            if suggestion:
                self.setText(suggestion)
                return
        super().keyPressEvent(event)
