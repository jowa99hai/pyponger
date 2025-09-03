# PyPonger Changelog

## Version 0.12 (2025-09-03)

### Neue Features
- **Vollständiges Sound-System hinzugefügt**
  - Ball-Wand-Kollision Sounds (`sounds/wall.wav`, `sounds/bounce.wav`)
  - Ball-Spieler-Kollision Sounds (`sounds/player.wav`, `sounds/hit.wav`)
  - Tor-Sounds (`sounds/goal.wav`, `sounds/score.wav`)
  - Alle Sounds werden automatisch bei entsprechenden Spielereignissen abgespielt

### Verbesserungen
- **Bessere Projektstruktur**
  - Alle Sound-Dateien sind jetzt im `sounds/` Unterordner organisiert
  - Saubere Trennung zwischen Spielcode und Audiodateien
  - Einfachere Wartung und Organisation

### Technische Details
- **Sound-Format:** WAV (PCM), 44.1 kHz, 16-bit, Mono
- **Automatische Sound-Erkennung:** Das Spiel lädt die erste verfügbare Sound-Datei
- **Optimierte Lautstärke:** 50% für Spiel-Sounds, 30% für Menü-Musik
- **Hintergrundmusik-Unterstützung:** MP3, WAV, OGG-Formate

### Dateien
- `sounds/` - Neuer Unterordner für alle Sound-Dateien
- `SOUNDS_README.md` - Detaillierte Dokumentation des Sound-Systems
- `pyponger.py` - Angepasst für neue Verzeichnisstruktur

## Version 0.11 (2025-09-02)
- Grundversion des Spiels mit 4 Spielern (2 Torwarte, 2 Stürmer)
- Fußball-Pong-Mechanik
- Grundlegende Grafik und Steuerung
