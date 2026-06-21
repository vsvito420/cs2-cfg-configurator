# 📦 CS2 CFG Configurator – EXE Build Anleitung

Diese Anleitung beschreibt wie du das Projekt als einzelne `.exe` baust mit **PyInstaller**.

---

## 1. Voraussetzungen

```bash
pip install pyinstaller
```

> Python 3.11+ und PySide6 müssen bereits installiert sein.

---

## 2. Einmaliges Setup: Icon konvertieren (optional, für schöneres EXE-Icon)

Windows-Icons müssen im `.ico` Format sein:

```bash
# Mit Pillow (pip install pillow)
python -c "
from PIL import Image
Image.open('app/assets/icon.png').save('app/assets/icon.ico')
"
```

---

## 3. Build-Befehl (aus dem `cs2-cfg-configurator/` Ordner ausführen)

```bash
pyinstaller \
  --onefile \
  --windowed \
  --name "CS2-CFG-Configurator" \
  --icon "app/assets/icon.ico" \
  --add-data "app/assets;app/assets" \
  --add-data "data;data" \
  --add-data "configs;configs" \
  main.py
```

### Windows (PowerShell / CMD) – Semikolon als Trennzeichen:
```powershell
pyinstaller `
  --onefile `
  --windowed `
  --name "CS2-CFG-Configurator" `
  --icon "app\assets\icon.ico" `
  --add-data "app\assets;app\assets" `
  --add-data "data;data" `
  --add-data "configs;configs" `
  main.py
```

---

## 4. Ergebnis

Nach dem Build findest du die `.exe` in:
```
dist/CS2-CFG-Configurator.exe
```

Diese Datei ist standalone — kein Python nötig auf dem Ziel-PC.

---

## 5. Pfade im EXE-Modus (wichtig!)

Wenn das Programm als `.exe` läuft, ändert sich `__file__`. Assets müssen so geladen werden:

```python
import sys
from pathlib import Path

def get_base_path() -> Path:
    """Gibt den Basis-Pfad zurueck – egal ob .py oder .exe"""
    if getattr(sys, 'frozen', False):
        # PyInstaller EXE: temporärer Entpack-Ordner
        return Path(sys._MEIPASS)
    return Path(__file__).parent
```

Diese Funktion ist bereits für zukünftige EXE-Kompatibilität vorbereitet.

---

## 6. Alternative: `--onedir` (schneller Start, Ordner statt Datei)

Statt `--onefile` kannst du `--onedir` nehmen:
- `.exe` startet schneller (kein Entpacken)
- Ergebnis: ein Ordner `dist/CS2-CFG-Configurator/` mit `.exe` + DLLs
- Zum Verteilen: Ordner zippen

---

## 7. Taskleisten-Icon Fix

Unter Windows zeigt die Taskleiste manchmal noch das Python-Icon wenn das Programm
**über VSCode** gestartet wird (nicht per Doppelklick auf `.py`/`.exe`).

Fix für den VSCode-Start – füge diese Zeilen **ganz oben** in `main.py` ein:

```python
import ctypes
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("cs2.cfg.configurator.1")
```

Das setzt eine eindeutige App-ID – Windows zeigt dann das richtige Icon.
