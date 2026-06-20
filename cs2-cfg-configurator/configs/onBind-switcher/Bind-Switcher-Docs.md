---

## 1. Waffe Selektion

### Ziel
Automatische Erkennung und Anpassung der Settings basierend auf der aktuellen Waffe (Pistol vs Rifle vs Messer vs Granaten).

### CS2 Slots
```text
slot1 = Primaerewaffe (AK-47, M4, AWP...)
slot2 = Sekundaewaffe (Deagle, Glock...)
slot3 = Messer / Zeus
slot4 = Granaten-Cycle (HE → Flash → Smoke → Decoy → Molotov)
slot5 = C4 / Bomb
slot6 = HE Grenade
slot7 = Flashbang
slot8 = Smoke Grenade
slot9 = Decoy
slot10 = Molotov / Incendiary
```

### Beispiel-Bind
```text
bind "1" "slot1"
bind "2" "slot2"
bind "3" "slot3"
bind "4" "slot4"
bind "5" "slot5"
bind "6" "slot6"
bind "7" "slot7"
bind "8" "slot8"
bind "0" "slot10"
```

### Programm-Feature
- Automatische Loadout-Anpassung beim Waffe-Wechsel
- Erkennung via Slot-aenderung
- Separate Settings fuer Pistol/Rifle/Granaten

---
