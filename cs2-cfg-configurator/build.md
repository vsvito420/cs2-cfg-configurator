# 📦 CS2 CFG Configurator – EXE Build Anleitung

Diese Anleitung beschreibt wie du das Projekt als einzelne `.exe` baust mit **PyInstaller**.

> **Empfehlung:** Nutze das mitgelieferte Build-Skript `build.ps1` –
> es erledigt alle Schritte (Icon-Konvertierung, PyInstaller-Aufruf,
> Cleanup, EXE-Report) automatisch. Die manuelle Anleitung unten bleibt
> als Referenz erhalten.

---

## Schnellstart mit `build.ps1` (empfohlen)

Aus dem Projektordner (`cs2-cfg-configurator/`):

```powershell
# Standard --onefile Build
.\build.ps1

# Onedir-Modus (schnellerer Start, Ordner statt einzelner EXE)
.\build.ps1 -OneDir

# Vorherige Artefakte (build/, dist/, *.spec) loeschen + neu bauen
.\build.ps1 -Clean

# Icon-Schritt ueberspringen
.\build.ps1 -SkipIcon
```

Das Skript installiert fehlendes PyInstaller automatisch via `pip`,
konvertiert `app/assets/icon.png` zu `icon.ico` (falls noetig), startet
PyInstaller und gibt am Ende Pfad + Groesse der `.exe` aus.

> Falls die Ausfuehrung blockiert wird:
> `powershell -ExecutionPolicy Bypass -File .\build.ps1`

---

## 1. Voraussetzungen

```bash
pip install pyinstaller
```

> Python 3.11+ und PySide6 muessen bereits installiert sein.

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
python -m PyInstaller `
  --onefile `
  --windowed `
  --name "CS2-CFG-Configurator" `
  --icon "app\assets\icon.ico" `
  --add-data "app\assets;app\assets" `
  --add-data "data;data" `
  --add-data "configs;configs" `
  main.py
```

> **Hinweis:** Falls `pyinstaller` nicht direkt aufrufbar ist (häufig bei
> User-Installationen von Python), verwende stattdessen `python -m PyInstaller`.
> Das funktioniert immer, solange PyInstaller via `pip install pyinstaller`
> installiert wurde.

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
