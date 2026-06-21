<div align="center">

# 🎮 [CS2 CFG Configurator](https://vsvito420.github.io/cs2-cfg-configurator/demo/demo.html)

**Ein modulares Desktop-Tool (Python / PySide6) zum Erstellen, Bearbeiten und Verwalten von CS2-Konfigurationsdateien.**

[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/UI-PySide6%20%28Qt6%29-green?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightblue)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Stars](https://img.shields.io/github/stars/vsvito420/cs2-cfg-configurator?style=social)](https://github.com/vsvito420/cs2-cfg-configurator/stargazers)
[![Latest Release](https://img.shields.io/github/v/release/vsvito420/cs2-cfg-configurator?include_prereleases&label=Release)](https://github.com/vsvito420/cs2-cfg-configurator/releases/latest)

---

## ⬇️ Download

[![Download EXE](https://img.shields.io/badge/Download-Windows%20EXE-blue?style=for-the-badge&logo=windows)](https://github.com/vsvito420/cs2-cfg-configurator/releases/latest/download/CS2-CFG-Configurator.exe)
[![Download ZIP](https://img.shields.io/badge/Download-Projekt%20ZIP-grey?style=for-the-badge&logo=github)](https://github.com/vsvito420/cs2-cfg-configurator/releases/latest)

| | Für wen? |
|---|---|
| **EXE** | Normale Nutzer – einfach starten, kein Python nötig 🟢 |
| **ZIP** | Entwickler – Quellcode + selbst starten via Python |
| **🌐 [Web Demo](https://vsvito420.github.io/cs2-cfg-configurator/demo.html)** | Quick-Port im Browser – nur eingeschränkt nutzbar (siehe unten) 🟡 |

_Beide Dateien werden automatisch bei jedem Release gebaut und hochgeladen._

</div>

---

---

## 🌐 Web Edition (Demo) — eingeschränkt!

Es gibt eine **Browser-Demo** unter [vsvito420.github.io/cs2-cfg-configurator/demo.html](https://vsvito420.github.io/cs2-cfg-configurator/demo.html) — das ist allerdings nur ein **Quick-Port** vom Python-Tool.

**Was funktioniert:**
- ✅ Buy Binds / Bind Switcher / Settings Editor erstellen
- ✅ Generiertes `autoexec.cfg` in den CS2-`cfg`-Ordner speichern (File System Access API, Chrome/Edge 86+)

**Was NICHT funktioniert:**
- ❌ **Userdata-Ordner** (Demos, Replays, GPU-Config, gespeicherte ConVars, Autoexec-Backups aus `Steam/userdata/...`) — der Browser hat **keinen Zugriff** darauf
- ❌ Auto-Erkennung des Steam-/CS2-Installationspfads
- ❌ Multi-Profil-Management auf der Festplatte

👉 **Für den vollen Funktionsumfang → EXE aus den [Releases](https://github.com/vsvito420/cs2-cfg-configurator/releases/latest) nutzen.**

---

## 🚀 Schnellstart (aus ZIP / Quellcode)

```bash
git clone https://github.com/vsvito420/cs2-cfg-configurator.git
cd cs2-cfg-configurator/cs2-cfg-configurator
pip install -r requirements.txt
python main.py
```

---

## 🤝 Mitmachen (Contributing)

Beiträge sind herzlich willkommen! Bitte beachte:

- **Fork** das Repo, erstelle einen Branch und öffne einen **Pull Request**
- Neue Module bitte modular halten (eigener Ordner unter `app/modules/`)
- Kein kommerzieller Einsatz ohne schriftliche Erlaubnis (→ [Lizenz](#lizenz))
- Für größere Änderungen erst ein **Issue** öffnen und besprechen

Details findest du in [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## 📁 Projektstruktur

```
cs2-cfg-configurator/
├── main.py                      # Einstiegspunkt – startet die App
├── requirements.txt
├── configs/                     # ⚙️ Alle generierten & gespeicherten CFG-Dateien
│   ├── app_settings.json
│   ├── bind-manager/
│   └── onBind-switcher/
├── data/                        # 📊 CS2-Command-Definitionen (JSON)
│   ├── crosshair/commands.json
│   ├── viewmodel/commands.json
│   ├── map/commands.json
│   ├── networking/commands.json
│   ├── performance/commands.json
│   ├── video/commands.json
│   └── buy-binds/commands.json
└── app/
    ├── main_window.py
    ├── sidebar.py
    ├── settings_manager.py
    └── modules/                 # 🧩 Jedes Modul = eigener Unterordner
        ├── cfg_editor/
        ├── bind_switcher/
        ├── buy_binds/
        └── settings_page/
```

---

## 🧩 Modularer Aufbau

### Neues Modul hinzufügen

**1.** `app/modules/<name>/view.py` mit einer `QWidget`-Klasse anlegen:
```python
class MeinModulPage(QWidget):
    def __init__(self, parent=None): ...
```

**2.** In `main_window.py` importieren & eintragen:
```python
from app.modules.mein_modul.view import MeinModulPage
self._pages = { "mein_modul": MeinModulPage() }
```

**3.** In `sidebar.py` zur NAV-Liste hinzufügen:
```python
NAV = [ SidebarItem("📦  Mein Modul", "mein_modul") ]
```

`main_window.load_module(key)` switcht automatisch zur richtigen Seite.

---

## 🔧 Module Überblick

### ⚙️ CFG Editor (`cfg_editor`)
Visueller Editor für CS2-Einstellungen. Commands kommen aus `data/<kategorie>/commands.json`.

### 🔗 Bind Manager (`bind_switcher`)

| Typ | Was es macht | CS2-Output |
|---|---|---|
| **Simple** | Taste → Befehl | `bind "k" "slot1"` |
| **Toggle** | Taste wechselt A ↔ B | `alias` Doppel-Pattern |
| **Hold** | Halten = aktiv, loslassen = zurück | `alias +name / -name` |
| **CFG Exec** | Taste lädt `.cfg`-Datei | `bind "k" "exec file.cfg"` |

### 🛒 Buy Binds (`buy_binds`)
Viewer und Editor für Waffen-Kauf-Binds.

### 🎮 Settings (`settings_page`)
Farben und Sidebar-Breite. Änderungen werden sofort via `apply_settings()` übernommen.

---

## 🛠️ Tech Stack

| | |
|---|---|
| **UI** | PySide6 (Qt6) |
| **Sprache** | Python 3.11+ |
| **Daten** | JSON (Commands & Settings) |
| **Theme** | Catppuccin Mocha |

---

## 📄 Lizenz

Dieses Projekt steht unter der **[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)** Lizenz.

- ✅ Freie Nutzung, Weitergabe und Anpassung
- ✅ Beiträge & Forks willkommen
- ❌ Keine kommerzielle Nutzung ohne ausdrückliche Genehmigung

© 2026 [vsvito420](https://github.com/vsvito420)
