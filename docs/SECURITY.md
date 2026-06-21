# 🔒 Ist das sicher? — Sicherheitsanalyse der `.exe`

> **Kurze Antwort: Ja.** Die Warnungen stammen von PyInstaller, nicht von bösartigem Code.

---

## Warum zeigt capa / mein Antivirus Warnungen?

Das Projekt wird mit **[PyInstaller](https://pyinstaller.org/)** zu einer einzelnen `.exe` gebündelt.  
PyInstaller packt den Python-Interpreter, alle Abhängigkeiten und den eigentlichen Code in ein selbstextrahierendes Archiv.  
Genau dieser Mechanismus löst bei statischen Analysewerkzeugen wie [capa](https://github.com/mandiant/capa) oder Antivirenprogrammen Alarm aus — **nicht der Code selbst**.

---

## capa-Befunde erklärt

| capa-Befund | Ursache |
|---|---|
| `Obfuscated Files / RC4 + XOR Encryption` | PyInstaller verschlüsselt intern die `.pyc`-Dateien im Bundle |
| `Link functions at runtime (96×)` | Python-Interpreter lädt Windows-DLLs dynamisch |
| `Create / Terminate Process` | PyInstaller-Bootloader entpackt sich und startet Python |
| `Create Process Suspended` | Bootloader-Technik beim Selbststart, kein Code Injection |
| `VM / Debugger Detection` | PyInstaller-Bootloader prüft die Laufzeitumgebung |
| `ZLIB / Adler32 Checksum` | Komprimierung des eingebetteten Python-Archivs |
| `Enumerate PE Sections` | Bootloader liest sich selbst, um das Python-Archiv zu finden |
| `File & Directory Discovery` | Der Config-Editor sucht CS2-Konfigurationsdateien |

### Was **nicht** auftaucht (gutes Zeichen ✅)

- Kein **Network**-Tactic (keine Sockets, kein DNS, kein HTTP)
- Kein **Credential Access** (keine Passwörter, keine Keylogger-Funktionen)
- Keine **Persistence** (keine Registry-Keys, kein Autorun)
- Kein **Lateral Movement** oder **Exfiltration**

---

## Selbst verifizieren

Du möchtest es selbst prüfen? Hier sind drei Wege:

### 1. VirusTotal
Lade die `.exe` auf [virustotal.com](https://www.virustotal.com) hoch oder prüfe den SHA256-Hash:
```
SHA256: 40709856626afb9fc09a8995094d3eb38af55a577570a702f41175c691d170df
```

### 2. Quellcode lesen
Der gesamte Quellcode ist offen einsehbar:  
👉 [github.com/vsvito420/cs2-cfg-configurator](https://github.com/vsvito420/cs2-cfg-configurator)

### 3. Selbst bauen
Statt der vorgefertigten `.exe` kannst du das Projekt direkt aus dem Quellcode starten:

```bash
git clone https://github.com/vsvito420/cs2-cfg-configurator.git
cd cs2-cfg-configurator
pip install -r requirements.txt
python main.py
```

Oder selbst zu einer `.exe` bauen:
```bash
pip install pyinstaller
pyinstaller --onefile main.py
```

---

## Was macht das Programm tatsächlich?

Der CS2 CFG Configurator liest und schreibt ausschließlich **Counter-Strike 2 Konfigurationsdateien** (`.cfg`) in deinem lokalen Steam-Verzeichnis.  
Es werden **keine Daten ins Internet übertragen**, keine Systemeinstellungen verändert und keine Dateien außerhalb des CS2-Verzeichnisses angefasst.

---

*Bei weiteren Fragen oder Sicherheitsbedenken bitte ein [Issue öffnen](https://github.com/vsvito420/cs2-cfg-configurator/issues).*
