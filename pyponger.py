# PyPonger (Version 0.12) (Date: 2025-09-03)

# Dieses Programm steht unter der MIT-Lizenz und darf frei genutzt, kopiert, verändert und weitergegeben werden, 
# solange in allen Kopien oder abgeleiteten Arbeiten der ursprüngliche Copyright-Hinweis und die Lizenz enthalten sind.  
# Das Programm wird ohne jegliche Gewährleistung bereitgestellt – ohne Garantie der Funktionsfähigkeit, 
# Marktreife oder Eignung für einen bestimmten Zweck.  

# Wenn Sie das Programm weiterentwickeln und einen Fork erstellen, wählen Sie bitte einen neuen Namen für Ihr Projekt 
# und verweisen Sie auf das Originalprojekt.

import pygame
import sys
import random
import math

# Pygame initialisieren
pygame.init()
pygame.mixer.init()  # Audio-System initialisieren

# Konstanten
BREITE = 1200
HOEHE = 800
SPIELER_BREITE = 20
SPIELER_HOEHE = 100
BALL_GROESSE = 25  # Größerer Ball
SPIELER_GESCHWINDIGKEIT = 5
BALL_GESCHWINDIGKEIT = 7
NETZ_BREITE = 4
NETZ_HOEHE = 300  # Höhere Tore
TOR_BREITE = 30   # Breite der Torpfosten

# Farben
WEISS = (255, 255, 255)
SCHWARZ = (0, 0, 0)
GRUEN = (34, 139, 34)
ROT = (255, 0, 0)
BLAU = (0, 0, 255)
GELB = (255, 255, 0)
GRAU = (128, 128, 128)

# Bildschirm erstellen
bildschirm = pygame.display.set_mode((BREITE, HOEHE))
pygame.display.set_caption("PyPonger - Fußball Pong")
uhr = pygame.time.Clock()

class Spieler:
    def __init__(self, x, y, farbe, steuerung, spieler_typ):
        self.x = x
        self.y = y
        self.farbe = farbe
        self.steuerung = steuerung  # 'links' oder 'rechts'
        self.spieler_typ = spieler_typ  # 'torwart' oder 'stürmer'
        self.punkte = 0
        self.geschwindigkeit = SPIELER_GESCHWINDIGKEIT

        # Horizontaler Bewegungsbereich abhängig vom Spieler-Typ
        bewegung = 40 if self.spieler_typ == 'torwart' else 80
        self.min_x = max(0, x - bewegung)
        self.max_x = min(BREITE - SPIELER_BREITE, x + bewegung)

        # Stürmer bleiben auf ihrer jeweiligen Spielfeldseite
        if self.spieler_typ == 'stürmer':
            if self.steuerung == 'links':
                self.min_x = max(self.min_x, BREITE // 2 + 10)
            else:
                self.max_x = min(self.max_x, BREITE // 2 - SPIELER_BREITE - 10)

    def bewegen(self, tasten):
        if self.steuerung == 'links':
            hoch, runter, links, rechts = (
                pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d
            )
        else:
            hoch, runter, links, rechts = (
                pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
            )

        if tasten[hoch] and self.y > 0:
            self.y -= self.geschwindigkeit
        if tasten[runter] and self.y < HOEHE - SPIELER_HOEHE:
            self.y += self.geschwindigkeit
        if tasten[links] and self.x > self.min_x:
            self.x -= self.geschwindigkeit
        if tasten[rechts] and self.x < self.max_x:
            self.x += self.geschwindigkeit
                
    def zeichnen(self):
        pygame.draw.rect(bildschirm, self.farbe, (self.x, self.y, SPIELER_BREITE, SPIELER_HOEHE))

class Ball:
    def __init__(self, sound_wand=None, sound_spieler=None):
        self.sound_wand = sound_wand
        self.sound_spieler = sound_spieler
        self.reset()

    def reset(self):
        self.x = BREITE // 2
        self.y = HOEHE // 2
        # Zufällige Richtung mit leichtem Winkel
        richtung = random.choice([-1, 1])
        winkel = random.uniform(-math.pi/4, math.pi/4)
        self.dx = richtung * BALL_GESCHWINDIGKEIT * math.cos(winkel)
        self.dy = BALL_GESCHWINDIGKEIT * math.sin(winkel)
        
    def bewegen(self):
        self.x += self.dx
        self.y += self.dy

        # Obere und untere Wand-Kollision
        if self.y <= 0 or self.y >= HOEHE - BALL_GROESSE:
            self.dy = -self.dy
            if self.sound_wand:
                self.sound_wand.play()
            
    def kollision_spieler(self, spieler):
        ball_rect = pygame.Rect(self.x, self.y, BALL_GROESSE, BALL_GROESSE)
        spieler_rect = pygame.Rect(spieler.x, spieler.y, SPIELER_BREITE, SPIELER_HOEHE)
        
        if ball_rect.colliderect(spieler_rect):
            # Ball zurückschlagen mit Winkel basierend auf Trefferposition
            treffer_position = (self.y - spieler.y) / SPIELER_HOEHE
            winkel = treffer_position * math.pi/3  # -60° bis +60°
            
            # Bestimme die Kollisionsrichtung basierend auf Ball-Position relativ zum Spieler
            ball_center_x = self.x + BALL_GROESSE // 2
            spieler_center_x = spieler.x + SPIELER_BREITE // 2
            
            # Wenn Ball von links kommt (auf linke Spieler-Seite)
            if ball_center_x < spieler_center_x:
                self.dx = -abs(self.dx)  # Ball nach links abprallen
            else:
                self.dx = abs(self.dx)   # Ball nach rechts abprallen

            self.dy = BALL_GESCHWINDIGKEIT * math.sin(winkel)
            if self.sound_spieler:
                self.sound_spieler.play()
            return True
        return False
    
    def zeichnen(self):
        # Ball-Zentrum
        center_x = int(self.x + BALL_GROESSE//2)
        center_y = int(self.y + BALL_GROESSE//2)
        radius = BALL_GROESSE//2
        
        # Hauptball (weiß)
        pygame.draw.circle(bildschirm, WEISS, (center_x, center_y), radius)
        
        # Schwarze Linien für Fußball-Muster
        pygame.draw.circle(bildschirm, SCHWARZ, (center_x, center_y), radius, 2)
        
        # Fußball-Muster: 5- und 6-Ecke (vereinfacht)
        # Horizontale Linien
        pygame.draw.line(bildschirm, SCHWARZ, 
                        (center_x - radius//2, center_y - radius//3), 
                        (center_x + radius//2, center_y - radius//3), 2)
        pygame.draw.line(bildschirm, SCHWARZ, 
                        (center_x - radius//2, center_y + radius//3), 
                        (center_x + radius//2, center_y + radius//3), 2)
        
        # Vertikale Linien
        pygame.draw.line(bildschirm, SCHWARZ, 
                        (center_x - radius//3, center_y - radius//2), 
                        (center_x - radius//3, center_y + radius//2), 2)
        pygame.draw.line(bildschirm, SCHWARZ, 
                        (center_x + radius//3, center_y - radius//2), 
                        (center_x + radius//3, center_y + radius//2), 2)
        
        # Diagonale Linien für mehr Details
        pygame.draw.line(bildschirm, SCHWARZ, 
                        (center_x - radius//3, center_y - radius//3), 
                        (center_x + radius//3, center_y + radius//3), 1)
        pygame.draw.line(bildschirm, SCHWARZ, 
                        (center_x + radius//3, center_y - radius//3), 
                        (center_x - radius//3, center_y + radius//3), 1)
        
        # Zentrumspunkt
        pygame.draw.circle(bildschirm, SCHWARZ, (center_x, center_y), 2)
        
        # Kleine Details an den Ecken
        pygame.draw.circle(bildschirm, SCHWARZ, (center_x - radius//2, center_y - radius//2), 1)
        pygame.draw.circle(bildschirm, SCHWARZ, (center_x + radius//2, center_y - radius//2), 1)
        pygame.draw.circle(bildschirm, SCHWARZ, (center_x - radius//2, center_y + radius//2), 1)
        pygame.draw.circle(bildschirm, SCHWARZ, (center_x + radius//2, center_y + radius//2), 1)

class Spiel:
    def __init__(self):
        # Soundeffekte laden
        self.sound_wand, self.sound_spieler, self.sound_tor = self.soundeffekte_laden()

        # 4 Spieler: Torwart und Stürmer für jede Seite
        # Stürmer stehen direkt hinter der Mittellinie im gegnerischen Feld
        self.torwart_links = Spieler(80, HOEHE//2 - SPIELER_HOEHE//2, BLAU, 'links', 'torwart')
        self.stürmer_links = Spieler(BREITE//2 + 50, HOEHE//2 - SPIELER_HOEHE//2, BLAU, 'links', 'stürmer')
        self.torwart_rechts = Spieler(BREITE - 80 - SPIELER_BREITE, HOEHE//2 - SPIELER_HOEHE//2, ROT, 'rechts', 'torwart')
        self.stürmer_rechts = Spieler(BREITE//2 - 50 - SPIELER_BREITE, HOEHE//2 - SPIELER_HOEHE//2, ROT, 'rechts', 'stürmer')
        self.ball = Ball(self.sound_wand, self.sound_spieler)
        self.spiel_aktiv = True
        self.gewinn_punkte = 5

        # Hintergrundmusik laden und abspielen
        self.musik_laden()
        
    def spiel_feld_zeichnen(self):
        # Hintergrund mit Streifen
        hell = GRUEN
        dunkel = (30, 130, 30)
        for i in range(0, BREITE, 40):
            farbe = hell if (i // 40) % 2 == 0 else dunkel
            pygame.draw.rect(bildschirm, farbe, (i, 0, 40, HOEHE))

        # Mittellinie
        pygame.draw.line(bildschirm, WEISS, (BREITE//2, 0), (BREITE//2, HOEHE), 3)
        
        # Mittlerer Kreis
        pygame.draw.circle(bildschirm, WEISS, (BREITE//2, HOEHE//2), 50, 3)
        
        # Tore mit Torpfosten
        # Linkes Tor
        pygame.draw.rect(bildschirm, WEISS, (0, HOEHE//2 - NETZ_HOEHE//2, TOR_BREITE, NETZ_HOEHE), NETZ_BREITE)
        # Rechtes Tor
        pygame.draw.rect(bildschirm, WEISS, (BREITE - TOR_BREITE, HOEHE//2 - NETZ_HOEHE//2, TOR_BREITE, NETZ_HOEHE), NETZ_BREITE)
        
        # Eckfahnen
        pygame.draw.polygon(bildschirm, ROT, [(0, 0), (30, 0), (15, 20)])
        pygame.draw.polygon(bildschirm, ROT, [(BREITE, 0), (BREITE - 30, 0), (BREITE - 15, 20)])
        pygame.draw.polygon(bildschirm, ROT, [(0, HOEHE), (30, HOEHE), (15, HOEHE - 20)])
        pygame.draw.polygon(bildschirm, ROT, [(BREITE, HOEHE), (BREITE - 30, HOEHE), (BREITE - 15, HOEHE - 20)])
        
    def punkte_anzeigen(self):
        font = pygame.font.Font(None, 74)
        # Punkte der linken Seite (Torwart und Stürmer teilen sich Punkte)
        text_links = font.render(str(self.torwart_links.punkte), True, WEISS)
        text_rechts = font.render(str(self.torwart_rechts.punkte), True, WEISS)
        
        bildschirm.blit(text_links, (BREITE//4, 50))
        bildschirm.blit(text_rechts, (3*BREITE//4, 50))
        
    def tor_pruefen(self):
        # Tor-Bereiche definieren
        tor_links_y_start = HOEHE//2 - NETZ_HOEHE//2
        tor_links_y_ende = HOEHE//2 + NETZ_HOEHE//2
        tor_rechts_y_start = HOEHE//2 - NETZ_HOEHE//2
        tor_rechts_y_ende = HOEHE//2 + NETZ_HOEHE//2
        
        # Linkes Tor
        if self.ball.x <= TOR_BREITE:
            if tor_links_y_start <= self.ball.y <= tor_links_y_ende - BALL_GROESSE:
                # Tor getroffen!
                self.torwart_rechts.punkte += 1
                self.ball.reset()
                if self.sound_tor:
                    self.sound_tor.play()
                return True
            else:
                # Torpfosten getroffen - Ball prallt ab
                self.ball.dx = abs(self.ball.dx)
                if self.sound_wand:
                    self.sound_wand.play()
                return False
        # Rechtes Tor
        elif self.ball.x >= BREITE - TOR_BREITE - BALL_GROESSE:
            if tor_rechts_y_start <= self.ball.y <= tor_rechts_y_ende - BALL_GROESSE:
                # Tor getroffen!
                self.torwart_links.punkte += 1
                self.ball.reset()
                if self.sound_tor:
                    self.sound_tor.play()
                return True
            else:
                # Torpfosten getroffen - Ball prallt ab
                self.ball.dx = -abs(self.ball.dx)
                if self.sound_wand:
                    self.sound_wand.play()
                return False
        return False
    
    def gewinner_pruefen(self):
        if self.torwart_links.punkte >= self.gewinn_punkte:
            return "Team Links"
        elif self.torwart_rechts.punkte >= self.gewinn_punkte:
            return "Team Rechts"
        return None

    def soundeffekte_laden(self):
        """Lädt Soundeffekte für Kollisionen und Tore"""

        def lade(dateien):
            for datei in dateien:
                try:
                    sound = pygame.mixer.Sound(datei)
                    sound.set_volume(0.5)
                    return sound
                except:
                    continue
            print(f"Keine Sounddatei gefunden: {', '.join(dateien)}")
            return None

        sound_wand = lade([
            "sounds/wall.wav",
            "sounds/wall.ogg",
            "sounds/bounce.wav",
        ])
        sound_spieler = lade([
            "sounds/player.wav",
            "sounds/hit.wav",
            "sounds/pong.wav",
        ])
        sound_tor = lade([
            "sounds/goal.wav",
            "sounds/score.wav",
        ])
        return sound_wand, sound_spieler, sound_tor
    
    def musik_laden(self):
        """Lädt und startet die Hintergrundmusik"""
        # Verschiedene Musikdateien versuchen
        musik_dateien = [
            "background_music.mp3",
            "music.mp3", 
            "background.wav",
            "music.wav",
            "background.ogg",
            "music.ogg"
        ]
        
        musik_gefunden = False
        for datei in musik_dateien:
            try:
                pygame.mixer.music.load(datei)
                pygame.mixer.music.set_volume(0.5)  # 50% Lautstärke
                pygame.mixer.music.play(-1)  # -1 = Endlosschleife
                print(f"Hintergrundmusik geladen: {datei}")
                musik_gefunden = True
                break
            except:
                continue
        
        if not musik_gefunden:
            print("Keine Musikdatei gefunden. Unterstützte Formate: .mp3, .wav, .ogg")
            print("Legen Sie eine der folgenden Dateien ins Projektverzeichnis:")
            for datei in musik_dateien:
                print(f"  - {datei}")
    
    def spiel_ende_anzeigen(self, gewinner):
        font_gross = pygame.font.Font(None, 74)
        font_klein = pygame.font.Font(None, 36)
        
        text_gewinner = font_gross.render(f"{gewinner} gewinnt!", True, WEISS)
        text_neustart = font_klein.render("Drücke R für Neustart oder Q zum Beenden", True, WEISS)
        
        text_rect = text_gewinner.get_rect(center=(BREITE//2, HOEHE//2 - 50))
        neustart_rect = text_neustart.get_rect(center=(BREITE//2, HOEHE//2 + 50))
        
        bildschirm.blit(text_gewinner, text_rect)
        bildschirm.blit(text_neustart, neustart_rect)
    
    def spiel_ausfuehren(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and not self.spiel_aktiv:
                        self.__init__()  # Spiel zurücksetzen
                    elif event.key == pygame.K_q and not self.spiel_aktiv:
                        pygame.quit()
                        sys.exit()
            
            if self.spiel_aktiv:
                # Spieler bewegen
                tasten = pygame.key.get_pressed()
                self.torwart_links.bewegen(tasten)
                self.stürmer_links.bewegen(tasten)
                self.torwart_rechts.bewegen(tasten)
                self.stürmer_rechts.bewegen(tasten)
                
                # Ball bewegen
                self.ball.bewegen()
                
                # Kollisionen prüfen
                self.ball.kollision_spieler(self.torwart_links)
                self.ball.kollision_spieler(self.stürmer_links)
                self.ball.kollision_spieler(self.torwart_rechts)
                self.ball.kollision_spieler(self.stürmer_rechts)
                
                # Tor prüfen
                self.tor_pruefen()
                
                # Gewinner prüfen
                gewinner = self.gewinner_pruefen()
                if gewinner:
                    self.spiel_aktiv = False
            
            # Zeichnen
            self.spiel_feld_zeichnen()
            self.torwart_links.zeichnen()
            self.stürmer_links.zeichnen()
            self.torwart_rechts.zeichnen()
            self.stürmer_rechts.zeichnen()
            self.ball.zeichnen()
            self.punkte_anzeigen()
            
            if not self.spiel_aktiv:
                self.spiel_ende_anzeigen(gewinner)
            
            pygame.display.flip()
            uhr.tick(60)

def hauptmenue():
    bildschirm.fill(GRUEN)
    font_klein = pygame.font.Font(None, 36)
    font_credits = pygame.font.Font(None, 24)
    
    # Start-Bild laden und anzeigen
    try:
        start_bild = pygame.image.load("start.jpg")
        # Bild auf Bildschirmgröße skalieren
        start_bild = pygame.transform.scale(start_bild, (BREITE, HOEHE))
        bildschirm.blit(start_bild, (0, 0))
    except:
        # Fallback: Grüner Hintergrund falls Bild nicht gefunden
        bildschirm.fill(GRUEN)
    
    # Hintergrundmusik für Hauptmenü laden
    musik_dateien = [
        "background_music.mp3",
        "music.mp3", 
        "background.wav",
        "music.wav",
        "background.ogg",
        "music.ogg"
    ]
    
    musik_gefunden = False
    for datei in musik_dateien:
        try:
            pygame.mixer.music.load(datei)
            pygame.mixer.music.set_volume(0.3)  # 30% Lautstärke für Menü
            pygame.mixer.music.play(-1)  # Endlosschleife
            musik_gefunden = True
            break
        except:
            continue
    
    if not musik_gefunden:
        print("Keine Musikdatei für Hauptmenü gefunden.")
    
    anleitung = font_klein.render("Drücke SPACE zum Starten", True, WEISS)
    steuerung1 = font_klein.render("Links - Torwart & Stürmer: W/S", True, WEISS)
    steuerung2 = font_klein.render("Rechts - Torwart & Stürmer: Pfeiltasten oben/unten", True, WEISS)
    credits = font_credits.render("Von Jan Heiko Wohltmann, 2025 - Version 0.1 vom 31.08.2025", True, WEISS)
    
    anleitung_rect = anleitung.get_rect(center=(BREITE//2, HOEHE//2 + 50))
    steuerung1_rect = steuerung1.get_rect(center=(BREITE//2, HOEHE//2 + 80))
    steuerung2_rect = steuerung2.get_rect(center=(BREITE//2, HOEHE//2 + 110))
    credits_rect = credits.get_rect(center=(BREITE//2, HOEHE//2 + 160))
    
    bildschirm.blit(anleitung, anleitung_rect)
    bildschirm.blit(steuerung1, steuerung1_rect)
    bildschirm.blit(steuerung2, steuerung2_rect)
    bildschirm.blit(credits, credits_rect)
    
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
        
        uhr.tick(60)

if __name__ == "__main__":
    hauptmenue()
    spiel = Spiel()
    spiel.spiel_ausfuehren()
