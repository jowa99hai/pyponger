# PyPonger Changelog

## Version 0.12 (2025-09-04)

### Neue Features
- **Gamepad-Unterstützung** mit konfigurierbarem Einstellungsmenü
- **Multiplayer-Liga-Modus** mit bis zu 16 Spielern, Namenseingabe, 2-minütigen Matches und Bereitschaftsbestätigung
- **Einzelspieler steuert nun das blaue Team über die Pfeiltasten**
- **KI-Torwart bewegt sich intelligenter** und verhakt sich nicht mehr mit dem Ball
- **Einzelspieler-Modus** mit KI-gesteuertem Gegner
- **Ultra-robuste Ballphysik** mit zuverlässiger Kollisionserkennung
- **Pause-Funktion** mit P-Taste während des Spiels
- **Sicherheitsabfrage** beim Beenden mit ESC-Taste
- **Vollständiges Sound-System hinzugefügt**
  - Ball-Wand-Kollision Sounds (`sounds/wall.wav`, `sounds/bounce.wav`)
  - Ball-Spieler-Kollision Sounds (`sounds/player.wav`, `sounds/hit.wav`)
  - Tor-Sounds (`sounds/goal.wav`, `sounds/score.wav`)
  - Alle Sounds werden automatisch bei entsprechenden Spielereignissen abgespielt

### Technische Details
- **Sound-Format:** WAV (PCM), 44.1 kHz, 16-bit, Mono
- **Automatische Sound-Erkennung:** Das Spiel lädt die erste verfügbare Sound-Datei
- **Optimierte Lautstärke:** 50% für Spiel-Sounds, 30% für Menü-Musik
- **Hintergrundmusik-Unterstützung:** MP3, WAV, OGG-Formate
- **Kollisionserkennung:** 7 verschiedene Prüfungen für maximale Zuverlässigkeit
- **Ballphysik:** Mindestgeschwindigkeit 5, Maximalgeschwindigkeit 15, Beschleunigung 1.02

### Dateien
- `sounds/` - Neuer Unterordner für alle Sound-Dateien
- `pyponger.py` - Angepasst für neue Verzeichnisstruktur und verbesserte Physik

## Version 0.11 (2025-09-02)
- Grundversion des Spiels mit 4 Spielern (2 Torwarte, 2 Stürmer)
- Fußball-Pong-Mechanik
- Grundlegende Grafik und Steuerung
