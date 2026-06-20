# CounterStrike 2 CFG Configurator (cs2)

Ein modulares Desktop-Tool (Python / PySide6) zum Erstellen, Bearbeiten und Verwalten von CS2-Konfigurationsdateien.

---

## Schnellstart

```bash
cd cs2-cfg-configurator
pip install -r requirements.txt
python main.py
```

---

## Projektstruktur

```
cs2-cfg-configurator/
├── main.py                      # Einstiegspunkt – startet die App
├── requirements.txt
├── configs/                     # ⚙️ Alle generierten & gespeicherten CFG-Dateien
│   ├── app_settings.json        # App-Einstellungen (Farben, Sidebar-Breite ...)
│   ├── bind-manager/            # Output-Ordner des Bind Managers
│   └── onBind-switcher/         # (Legacy)
├── data/                        # 📊 CS2-Command-Definitionen (JSON)
│   ├── crosshair/commands.json
│   ├── viewmodel/commands.json
│   ├── map/commands.json
│   ├── networking/commands.json
│   ├── performance/commands.json
│   ├── video/commands.json
│   └── buy-binds/commands.json
└── app/
    ├── main_window.py           # QMainWindow – registriert alle Module im QStackedWidget
    ├── sidebar.py               # Sidebar-Navigation (NAV-Liste → Buttons)
    ├── settings_manager.py      # load() / save() für app_settings.json
    └── modules/                 # 🧩 Jedes Modul = eigener Unterordner
        ├── cfg_editor/          # Visueller CS2-Settings-Editor (Slider, Dropdowns)
        ├── bind_switcher/       # Bind Manager (Simple / Toggle / Hold / CFG Exec)
        ├── buy_binds/           # Buy-Bind Viewer & Editor
        └── settings_page/       # App-Einstellungen (Farben, Pfade)
```

---

## Modularer Aufbau

### Wie ein Modul registriert wird

**1. Modul anlegen** – `app/modules/<name>/view.py` mit einer `QWidget`-Klasse:
```python
class MeinModulPage(QWidget):
    def __init__(self, parent=None): ...
```

**2. In `main_window.py` importieren & eintragen:**
```python
from app.modules.mein_modul.view import MeinModulPage

self._pages = {
    "mein_modul": MeinModulPage(),
    # ...
}
```

**3. In `sidebar.py` zur NAV-Liste hinzufügen:**
```python
NAV = [
    SidebarItem("📦  Mein Modul", "mein_modul"),
    # ...
]
```

Das war’s. `main_window.load_module(key)` switcht automatisch zur richtigen Seite.

---

## Module überblick

### ⚙️ CFG Editor (`cfg_editor`)
Visueller Editor für CS2-Einstellungen. Commands kommen aus `data/<kategorie>/commands.json`.
Jede Zeile hat Command-Name, Typ (Slider / Dropdown / Text), Default und Range.

**Wichtige Dateien:**
- `data_loader.py` – liest `commands.json` der jeweiligen Kategorie
- `generator.py` – baut daraus `set command value`-Zeilen
- `view.py` – rendert die UI-Widgets dynamisch

### 🔗 Bind Manager (`bind_switcher`)
Erstellt und exportiert CS2-Binds in vier Typen:

| Typ | Was es macht | CS2-Output |
|---|---|---|
| **Simple** | Taste → Befehl | `bind "k" "slot1"` |
| **Toggle** | Taste wechselt A ↔ B | `alias` Doppel-Pattern |
| **Hold** | Halten = aktiv, loslassen = zurück | `alias +name / -name` |
| **CFG Exec** | Taste lädt `.cfg`-Datei (simple/hold/toggle) | `bind "k" "exec file.cfg"` |

**Wichtige Dateien:**
- `model.py` – Datenklassen (SimpleBind, ToggleBind, HoldBind, CfgBind)
- `generator.py` – wandelt Modelle in CFG-Text um
- `widgets.py` – UI-Karten pro Bind-Typ (2-Zeilen-Layout)
- `autocomplete.py` – lädt alle Commands aus `data/` für QCompleter
- `view.py` – Tabs, Splitter, CFG-Preview, Speichern

Output-Ordner: `configs/bind-manager/`

### 🛒 Buy Binds (`buy_binds`)
Viewer und Editor für Waffen-Kauf-Binds.
- `viewer.py` – Listenansicht der aktuellen Binds
- `view.py` (Editor) – Binds ändern & speichern

### 🎮 Settings (`settings_page`)
Farben und Sidebar-Breite ändern. Ruft nach dem Speichern `main_window.apply_settings()` auf, damit die UI sofort aktualisiert wird.

---

## Neue Command-Kategorie hinzufügen

1. Ordner `data/<name>/` anlegen
2. `commands.json` erstellen:
```json
[
  {
    "command": "cl_beispiel",
    "default": "1",
    "range": "0 – 10",
    "description": "Beispiel-Einstellung"
  }
]
```
3. In `cfg_editor/data_loader.py` unter `CATEGORY_META` eintragen:
```python
"name": {"label": "📦 Label", "folder": "name"}
```

---

## Tech Stack

| | |
|---|---|
| **UI** | PySide6 (Qt6) |
| **Sprache** | Python 3.11+ |
| **Daten** | JSON (Commands), JSON (Settings) |
| **Theme** | Catppuccin Mocha |
