# CS2 Bind Manager - Programm-Dokumentation

Ein Programm zur automatischen Anpassung von CS2 Binds und Settings.

---

## 📋 uebersicht der 11 Funktionen

| # | Funktion | Beschreibung |
|---|----------|--------------|
| 1 | Waffe Selektion | Automatische Settings fuer Pistol/Rifle/Messer/Granaten |
| 2 | Toggle Binds | Zwischen 2 Settings wechseln (z.B. Pistol ↔ Rifle) |
| 3 | Hold-Binds | Beim Drhalten aktiv, beim Loslassen zurueck |
| 4 | Buy Binds | Automatischer Waffenkauf mit einer Taste |
| 5 | Jumpthrow Bind | Granate beim Jump abwerfen |
| 6 | Quick Switch | Messer ↔ Waffe mit einer Taste |
| 7 | HUD Hide/Show | HUD fuer Fragmovies verstecken |
| 8 | Viewmodel Commands | Waffe Position anpassen |
| 9 | Radar Commands | Radar Zoom/Size aendern |
| 10 | Crosshair Commands | Crosshair Groeße/Farbe/Style aendern |
| 11 | Netzwerk & Performance | Netgraph, FPS, Frame Cap |


## 2. Toggle Binds

### Ziel
Zwischen 2 verschiedenen Settings mit einer Taste wechseln (z.B. Pistol-Crosshair ↔ Rifle-Crosshair).

### Syntax
```text
alias "setting1" "cl_crosshairsize 2.1; cl_crosshaircolor 1"
alias "setting2" "cl_crosshairsize 4.42; cl_crosshaircolor 5"
bind "p" "toggle setting1 setting2"
```

### Beispiel: Crosshair Toggle
```text
alias "pistol_crosshair" "cl_crosshairsize 2.1; cl_crosshairgap 1.5; cl_crosshaircolor 1"
alias "rifle_crosshair" "cl_crosshairsize 4.42; cl_crosshairgap 1; cl_crosshaircolor 5"
bind "p" "toggle pistol_crosshair rifle_crosshair"
```

### Beispiel: Hand Toggle (Left/Right)
```text
bind "l" "toggle cl_righthand 0 1"
```

### Programm-Feature
- Toggle zwischen 2 vordefinierten Settings
- Einfache Konfiguration im UI
- Visuelle Anzeige des aktuellen Status

---

## 3. Hold-Binds

### Ziel
Setting ist nur aktiv, wenn Taste gedrueckt gehalten wird (z.B. Radar Zoom beim Drucken von CTRL).

### Syntax
```text
alias "+name" "cl_radar_scale 0.3; cl_radar_always_centered 0"
alias "-name" "cl_radar_scale 0.5; cl_radar_always_centered 1"
bind "ctrl" "+name"
```

### Beispiel: Radar Zoom Hold
```text
alias "+mz" "cl_radar_scale 0.3; cl_radar_always_centered 0; cl_radar_icon_scale_min 0.4"
alias "-mz" "cl_radar_scale 0.5; cl_radar_always_centered 1; cl_radar_icon_scale_min 0.6"
bind "ctrl" "+mz"
```

### Beispiel: Crosshair Groeße Hold
```text
alias "+longch" "cl_crosshairsize 1000"
alias "-longch" "cl_crosshairsize 1.8"
bind "h" "+longch"
```

### Programm-Feature
- Hold-Bind Erstellung mit +/−Alias
- Automatische Syntax-Generierung
- Keine manuelle Alias-Schreibung noetig

---

---

## 5. Jumpthrow Bind

### Ziel
Granate wird automatisch beim Jump abgeworfen (perfekt fuer Smoke-Lineups).

### Syntax (Version 1)
```text
alias "+jt" "+jump"
alias "+ta" "-attack; -attack2"
alias "-jt" "-jump"
bind "alt" "+jt; +ta"
```

### Syntax (Version 2 - Alternative)
```text
alias "+throw" "-attack;-attack2"
bind "space" "+jump;+throw"
```

### Run-Jumpthrow
```text
alias "+wthrow" "+forward; +jump"
alias "-wthrow" "-jump; -forward"
bind "mouse5" "+wthrow; +ta"
```

### Programm-Feature
- Jumpthrow-Varianten (Standard + Run-Jumpthrow)
- Automatische Alias-Generierung
- Mouse/Keyboard-Select option

---

## 6. Quick Switch

### Ziel
Mit einer Taste zwischen Messer und Waffe wechseln (z.B. Q fuer Quick-Check).

### Syntax
```text
alias "+qswitch" "slot3"
alias "-qswitch" "lastinv"
bind "q" "+qswitch"
```

### Programm-Feature
- Quick-Switch Vorlage
- Toggle-Modus (Messer ↔ Waffe)
- Hold-Modus (nur Messer beim Drucken)

---

## 7. HUD Hide/Show

### Ziel
HUD fuer Fragmovies/Screenshots verstecken, nur Killfeed sichtbar.

### Syntax
```text
bind "kp_minus" "toggle cl_draw_only_deathnotices 1 0"
```

### Weitere Commands
```text
cl_drawhud 0                    // HUD komplett verstecken (nur mit sv_cheats 1)
cl_draw_only_deathnotices 1     // Nur Killfeed sichtbar
```

### Programm-Feature
- HUD Toggle Vorlage
- Deathnotices-only Modus
- Full Hide Modus (sv_cheats)

---

## 8. Viewmodel Commands

### Ziel
Waffe Position (X/Y/Z) und FOV anpassen fuer besseren Sichtwinkel.

### Commands & Ranges
```text
viewmodel_offset_x  -2.5 bis 2.5   // Links/Rechts
viewmodel_offset_y  -2 bis 2       // Nah/Fern
viewmodel_offset_z  -2 bis 2       // Hoch/Runter
viewmodel_fov       54 bis 68      // Weapon FOV
```

### Pro-Setup
```text
viewmodel_fov 68
viewmodel_offset_x 2.5
viewmodel_offset_y 2
viewmodel_offset_z -2
```

### Programm-Feature
- Preset-Viewer (Pro-Settings)
- Slider-UI fuer X/Y/Z/FOV
- Auto-Generierung der Bind-Syntax

---

## 9. Radar Commands

### Ziel
Radar Zoom, Size und Rotation anpassen (z.B. Zoomed Out fuer Pistol, Normal fuer Rifle).

### Commands
```text
cl_radar_always_centered  0/1     // Centered auf Spieler
cl_radar_rotate           0/1     // Rotation beim Look
cl_radar_scale            0.25-1.0 // Zoom Level
cl_radar_icon_scale_min   0.4-1.25 // Icon Size
cl_hud_radar_scale        0.8-1.3  // HUD Radar Size
```

### Deine Settings
```text
cl_radar_always_centered 0
cl_radar_rotate 0
cl_radar_icon_scale_min 0.4
cl_radar_scale 0.4
cl_hud_radar_scale 1.3
```

### Programm-Feature
- Radar-Presets (Zoomed Out, Normal, Square)
- Toggle zwischen Pistol/Radar-Radar
- Visual Preview der Settings

---

## 10. Crosshair Commands

### Ziel
Crosshair Groeße, Farbe, Style, Gap, Thickness anpassen.

### Commands
```text
cl_crosshairstyle       0-5          // Style (2=Dynamic, 4=Static)
cl_crosshairsize        2-10         // Linienlaenge
cl_crosshairthickness   decimals     // Linienstaerke
cl_crosshairgap         decimals     // Gap zur Mitte
cl_crosshairalpha       0-255        // Transparency
cl_crosshaircolor       1-5          // Farbe (1=Green, 5=Default)
cl_crosshairdot         0/1          // Center Dot
cl_crosshair_drawoutline 0/1         // Black Outline
cl_crosshair_outlinethickness 0-3    // Outline Staerke
cl_crosshair_recoil     0/1          // Follows Recoil
cl_crosshair_sniper_width 1+         // Sniper Scope Breite
```

### Beispiel: Pistol vs Rifle
```text
pistol: cl_crosshairsize 2.1; cl_crosshairgap 1.5; cl_crosshaircolor 1
rifle:  cl_crosshairsize 4.42; cl_crosshairgap 1; cl_crosshaircolor 5
```

### Programm-Feature
- Crosshair-Editor mit Live-Preview
- Pro-Crosshair-Datenbank (donk, NiKo, ropz...)
- Toggle zwischen Pistol/Rifle Settings
- Export als CS2 Code oder Commands

---

## 11. Netzwerk & Performance

### Ziel
Netgraph, FPS, Frame Cap anzeigen fuer Performance-Monitoring.

### Commands
```text
cq_netgraph_problem_show_auto  0/1    // Ping/Loss/Choke in HUD
cl_showfps                     0-3    // FPS Counter (1=FPS, 2=FPS+avg)
fps_max                        0-300  // Frame Cap (0=unlimited)
mm_dedicated_search_maxping    value  // Max Ping fuer Matchmaking
```

### Beispiel
```text
cq_netgraph_problem_show_auto 1
cl_showfps 1
fps_max 0
```

### Programm-Feature
- Performance-Presets (Max FPS, Unlimited, Balanced)
- Netgraph Toggle
- FPS-Counter Anzeige

---

## 🎯 Gesamt-Beispiel: autoexec.cfg

```text
// === 1. Waffe Selektion (Default) ===
bind "1" "slot1"
bind "2" "slot2"
bind "3" "slot3"
bind "4" "slot4"
bind "5" "slot5"
bind "6" "slot6"
bind "7" "slot7"
bind "8" "slot8"
bind "0" "slot10"

// === 2. Toggle Binds (Pistol ↔ Rifle) ===
alias "pistol_ch" "cl_crosshairsize 2.1; cl_crosshairgap 1.5; cl_crosshaircolor 1"
alias "rifle_ch" "cl_crosshairsize 4.42; cl_crosshairgap 1; cl_crosshaircolor 5"
bind "p" "toggle pistol_ch rifle_ch"

// === 3. Hold-Binds (Radar Zoom) ===
alias "+mz" "cl_radar_scale 0.3; cl_radar_always_centered 0; cl_radar_icon_scale_min 0.4"
alias "-mz" "cl_radar_scale 0.5; cl_radar_always_centered 1; cl_radar_icon_scale_min 0.6"
bind "ctrl" "+mz"

// === 4. Buy Binds ===
bind "f1" "buy ak47; buy vesthelm; buy molotov"
bind "f2" "buy m4a1; buy vesthelm; buy smokegrenade"
bind "f5" "buy hegrenade; buy flashbang; buy smokegrenade; buy molotov"

// === 5. Jumpthrow Bind ===
alias "+jt" "+jump"
alias "+ta" "-attack; -attack2"
alias "-jt" "-jump"
bind "alt" "+jt; +ta"

// === 6. Quick Switch ===
alias "+qswitch" "slot3"
alias "-qswitch" "lastinv"
bind "q" "+qswitch"

// === 7. HUD Hide/Show ===
bind "kp_minus" "toggle cl_draw_only_deathnotices 1 0"

// === 8. Viewmodel ===
viewmodel_fov 68
viewmodel_offset_x 2.5
viewmodel_offset_y 2
viewmodel_offset_z -2

// === 9. Radar ===
cl_radar_always_centered 0
cl_radar_rotate 0
cl_radar_icon_scale_min 0.4
cl_radar_scale 0.4
cl_hud_radar_scale 1.3

// === 10. Crosshair (Default) ===
cl_crosshairstyle 2
cl_crosshairsize 4.42
cl_crosshairgap 1
cl_crosshaircolor 5
cl_crosshairdot 1

// === 11. Netzwerk & Performance ===
cq_netgraph_problem_show_auto 1
cl_showfps 1
fps_max 0

// === Save ===
host_writeconfig
```

---

## 📁 Dateien & Ordner

```
CS2_Bind_Manager/
├── autoexec.cfg          // Generiertes Haupt-Script
├── pistol.cfg            // Pistol Preset
├── rifle.cfg             // Rifle Preset
├── smoke.cfg             // Smoke Lineup Preset
├── pngmovies.cfg         // HUD Hide Preset
└── config.json           // Programm-Einstellungen
```

**autoexec.cfg speichern in:**
```
Steam/steamapps/common/Counter-Strike Global Offensive/game/csgo/cfg/autoexec.cfg
```

**Launch Option in Steam:**
```text
+exec autoexec.cfg
```
