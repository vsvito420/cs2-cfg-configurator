# Contributing to CS2 CFG Configurator

Danke, dass du zum **CS2 CFG Configurator** beitragen möchtest! 🎮  
Dieses Projekt ist ein visueller Editor für CS2-Konfigurationsdateien – jeder Beitrag hilft, es besser zu machen.

---

## Inhaltsverzeichnis

- [Verhaltenskodex](#verhaltenskodex)
- [Wie kann ich beitragen?](#wie-kann-ich-beitragen)
- [Entwicklungssetup](#entwicklungssetup)
- [Code-Stil & Konventionen](#code-stil--konventionen)
- [Pull Request Prozess](#pull-request-prozess)
- [Bugs melden](#bugs-melden)
- [Feature-Ideen einreichen](#feature-ideen-einreichen)
- [Lizenz](#lizenz)

---

## Verhaltenskodex

Bitte gehe respektvoll mit allen Beteiligten um. Konstruktives Feedback ist willkommen – persönliche Angriffe, Beleidigungen oder toxisches Verhalten werden nicht toleriert.

---

## Wie kann ich beitragen?

Es gibt viele Wege, zum Projekt beizutragen:

- 🐛 **Bugs melden** – Ein Issue erstellen mit klarer Beschreibung & Schritten zur Reproduktion
- 💡 **Feature-Ideen** – Neue Ideen als Issue einreichen (Label: `enhancement`)
- 🔧 **Code** – Einen Fork erstellen, Änderungen vornehmen & einen Pull Request öffnen
- 📝 **Dokumentation** – README, Kommentare oder Wikis verbessern
- 🎨 **UI/UX** – Verbesserungen am Catppuccin-Theme oder allgemeinen Layout

---

## Entwicklungssetup

### Voraussetzungen

- Python **3.10+**
- `pip` (kommt mit Python)
- Empfohlen: `git`, ein Editor wie VS Code

### Lokale Installation

```bash
# 1. Repository forken & klonen
git clone https://github.com/DEIN-USERNAME/cs2-cfg-configurator.git
cd cs2-cfg-configurator

# 2. Abhängigkeiten installieren
pip install -r requirements.txt

# 3. Anwendung starten
python main.py
```

### Projektstruktur (Übersicht)

```
cs2-cfg-configurator/
├── main.py                  # Einstiegspunkt
├── cs2-cfg-configurator/    # Hauptpaket
│   ├── ui/                  # GUI-Komponenten (Slider, Dropdowns, etc.)
│   ├── bind_manager/        # Bind-Logik (Simple, Toggle, Hold, CFG Exec)
│   ├── settings/            # Einstellungen & Theming
│   └── ...
├── requirements.txt
├── README.md
└── CONTRIBUTING.md          # Diese Datei
```

---

## Code-Stil & Konventionen

- **Sprache im Code:** Englisch (Variablen, Funktionen, Kommentare)
- **Sprache in Issues/PRs:** Deutsch oder Englisch – beides ist okay
- **Formatierung:** Halte dich an [PEP 8](https://pep8.org/)
- **Commits:** Nutze kurze, aussagekräftige Commit-Messages, z. B.:
  - `fix: slider value not saving correctly`
  - `feat: add hold-bind support for grenades`
  - `docs: update README installation steps`
- **Keine Secrets:** Committe keine persönlichen CFG-Dateien, API-Keys o. Ä.

---

## Pull Request Prozess

1. **Fork** das Repository und erstelle einen neuen Branch:
   ```bash
   git checkout -b feature/mein-neues-feature
   ```
2. Nimm deine Änderungen vor und committe sie (kleine, logische Commits bevorzugt).
3. Stelle sicher, dass `python main.py` ohne Fehler startet.
4. Öffne einen **Pull Request** gegen den `main`-Branch.
5. Beschreibe im PR:
   - Was wurde geändert / hinzugefügt?
   - Warum ist die Änderung sinnvoll?
   - Screenshots / GIFs bei UI-Änderungen sind sehr willkommen 📸

PRs werden zeitnah reviewt. Feedback wird konstruktiv gegeben – hab keine Scheu, auch als Anfänger einen PR zu öffnen!

---

## Bugs melden

Bitte erstelle ein [GitHub Issue](https://github.com/vsvito420/cs2-cfg-configurator/issues) und füge folgende Infos bei:

- **Betriebssystem** (Windows 10/11, Linux, macOS)
- **Python-Version** (`python --version`)
- **Schritte zur Reproduktion** des Fehlers
- **Fehlermeldung / Traceback** (als Codeblock einfügen)
- **Erwartetes vs. tatsächliches Verhalten**

---

## Feature-Ideen einreichen

Öffne ein Issue mit dem Label `enhancement` und beschreibe:

- Was soll das Feature tun?
- Warum wäre es nützlich?
- Hast du schon eine Idee, wie es umgesetzt werden könnte?

---

## Lizenz

Mit deinem Beitrag stimmst du zu, dass dein Code unter der  
**[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)** Lizenz veröffentlicht wird – freie Nutzung, keine Kommerzialisierung ohne Erlaubnis.
