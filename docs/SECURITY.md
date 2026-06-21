# 🔒 Ist das sicher? — Sicherheitsanalyse der `.exe`

> **Kurze Antwort: Ja.** Die Warnungen stammen von PyInstaller, nicht von bösartigem Code.

---

## Warum zeigt capa / mein Antivirus Warnungen?

Das Projekt wird mit **[PyInstaller](https://pyinstaller.org/)** zu einer einzelnen `.exe` gebündelt.  
PyInstaller packt den Python-Interpreter, alle Abhängigkeiten und den eigentlichen Code in ein selbstextrahierendes Archiv.  
Genau dieser Mechanismus löst bei statischen Analysewerkzeugen wie [capa](https://github.com/mandiant/capa) oder Antivirenprogrammen Alarm aus — **nicht der Code selbst**.

ok cool aber was ist capa.exe?:

---

## capa-Befunde erklärt

### Was ist capa.exe?

**[capa](https://github.com/mandiant/capa)** ist ein Open-Source-Tool von **Mandiant / Google Cloud** zur statischen Analyse von ausführbaren Dateien (PE, ELF, .NET). Es erkennt automatisiert Fähigkeiten (Capabilities) einer Binary — z. B. Verschlüsselung, Netzwerkzugriffe, Persistence-Mechanismen oder Code-Injection — und ordnet sie MITRE ATT&CK-Taktiken zu. capa ist besonders nützlich, um Malware-Verdachtsmomente einzuordnen, wird aber auch für legitime Software wie PyInstaller-Bundles eingesetzt.

👉 GitHub: [github.com/mandiant/capa](https://github.com/mandiant/capa)

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

## Eigenen capa-Log einfügen

Du hast capa lokal ausgeführt? Hier kannst du deinen Output reinkopieren — entweder als Vorlage oder um ihn mit den oben erklärten Befunden abzugleichen:

```
Windows PowerShell
Copyright (C) Microsoft Corporation. Alle Rechte vorbehalten.

Installieren Sie die neueste PowerShell für neue Funktionen und Verbesserungen! https://aka.ms/PSWindows

PS C:\Users\vitos\Downloads> .\capa.exe .\CS2-CFG-Configurator.exe
┌─────────────┬────────────────────────────────────────────────────────────────────────────────────┐
│ md5         │ 30df0a1d911dcb79e4f198440dbdd8fa                                                   │
│ sha1        │ 1a2a6717882d0f77187645ebb3b436ea55485713                                           │
│ sha256      │ 40709856626afb9fc09a8995094d3eb38af55a577570a702f41175c691d170df                   │
│ analysis    │ static                                                                             │
│ os          │ windows                                                                            │
│ format      │ pe                                                                                 │
│ arch        │ amd64                                                                              │
│ path        │ C:/Users/vitos/Downloads/CS2-CFG-Configurator.exe                                  │
└─────────────┴────────────────────────────────────────────────────────────────────────────────────┘
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ATT&CK Tactic             ┃ ATT&CK Technique                                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ DEFENSE EVASION           │ Obfuscated Files or Information [T1027]                              │
│                           │ Virtualization/Sandbox Evasion::System Checks [T1497.001]            │
│ DISCOVERY                 │ File and Directory Discovery [T1083]                                 │
│                           │ Process Discovery [T1057]                                            │
│                           │ System Information Discovery [T1082]                                 │
│ EXECUTION                 │ Command and Scripting Interpreter [T1059]                            │
│                           │ Shared Modules [T1129]                                               │
└───────────────────────────┴──────────────────────────────────────────────────────────────────────┘
┏━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ MBC Objective            ┃ MBC Behavior                                                               ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ ANTI-BEHAVIORAL ANALYSIS │ Debugger Detection::Timing/Delay Check QueryPerformanceCounter [B0001.033] │
│                          │ Virtual Machine Detection [B0009]                                          │
│ CRYPTOGRAPHY             │ Encrypt Data::RC4 [C0027.009]                                              │
│                          │ Generate Pseudo-random Sequence::RC4 PRGA [C0021.004]                      │
│ DATA                     │ Checksum::Adler [C0032.005]                                                │
│                          │ Compression Library [C0060]                                                │
│                          │ Encode Data::XOR [C0026.002]                                               │
│ DEFENSE EVASION          │ Obfuscated Files or Information::Encoding-Standard Algorithm [E1027.m02]   │
│ DISCOVERY                │ Analysis Tool Discovery::Process detection [B0013.001]                     │
│                          │ Code Discovery::Enumerate PE Sections [B0046.001]                          │
│                          │ File and Directory Discovery [E1083]                                       │
│                          │ System Information Discovery [E1082]                                       │
│ EXECUTION                │ Command and Scripting Interpreter [E1059]                                  │
│ FILE SYSTEM              │ Create Directory [C0046]                                                   │
│                          │ Delete Directory [C0048]                                                   │
│                          │ Delete File [C0047]                                                        │
│                          │ Read File [C0051]                                                          │
│                          │ Writes File [C0052]                                                        │
│ OPERATING SYSTEM         │ Environment Variable::Set Variable [C0034.001]                             │
│ PROCESS                  │ Create Process [C0017]                                                     │
│                          │ Create Process::Create Suspended Process [C0017.003]                       │
│                          │ Terminate Process [C0018]                                                  │
└──────────────────────────┴────────────────────────────────────────────────────────────────────────────┘
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Capability                                       ┃ Namespace                                       ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ reference analysis tools strings                 │ anti-analysis                                   │
│ check for time delay via QueryPerformanceCounter │ anti-analysis/anti-debugging/debugger-detection │
│ reference anti-VM strings targeting Xen          │ anti-analysis/anti-vm/vm-detection              │
│ compute adler32 checksum (2 matches)             │ data-manipulation/checksum/adler32              │
│ encode data using XOR (6 matches)                │ data-manipulation/encoding/xor                  │
│ encrypt data using RC4 PRGA                      │ data-manipulation/encryption/rc4                │
│ accept command line arguments                    │ host-interaction/cli                            │
│ query environment variable (4 matches)           │ host-interaction/environment-variable           │
│ set environment variable (3 matches)             │ host-interaction/environment-variable           │
│ get common file path                             │ host-interaction/file-system                    │
│ create directory (3 matches)                     │ host-interaction/file-system/create             │
│ delete directory                                 │ host-interaction/file-system/delete             │
│ delete file                                      │ host-interaction/file-system/delete             │
│ enumerate files recursively                      │ host-interaction/file-system/files/list         │
│ get file size                                    │ host-interaction/file-system/meta               │
│ read file on Windows (10 matches)                │ host-interaction/file-system/read               │
│ clear file content                               │ host-interaction/file-system/write              │
│ write file on Windows (2 matches)                │ host-interaction/file-system/write              │
│ get disk information (3 matches)                 │ host-interaction/hardware/storage               │
│ create process on Windows                        │ host-interaction/process/create                 │
│ create process suspended                         │ host-interaction/process/create                 │
│ enumerate process modules                        │ host-interaction/process/modules/list           │
│ terminate process (3 matches)                    │ host-interaction/process/terminate              │
│ link function at runtime on Windows (96 matches) │ linking/runtime-linking                         │
│ link many functions at runtime (2 matches)       │ linking/runtime-linking                         │
│ linked against ZLIB                              │ linking/static/zlib                             │
│ enumerate PE sections (2 matches)                │ load-code/pe                                    │
│ parse PE header (5 matches)                      │ load-code/pe                                    │
│ resolve function by parsing PE exports           │ load-code/pe                                    │
└──────────────────────────────────────────────────┴─────────────────────────────────────────────────┘

```

> Tipp: Führe capa mit `capa.exe -v <datei>` für ausführlichere Ausgabe aus und ersetze den obigen Block durch deinen eigenen Output.

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
