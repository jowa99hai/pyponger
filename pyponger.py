# PyPonger (Version 0.12) (Date: 2025-09-04)

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
import itertools

# Pygame initialisieren
pygame.init()
pygame.mixer.init()  # Audio-System initialisieren
pygame.joystick.init()  # Gamepad-Unterstützung initialisieren

# Konstanten
BREITE = 1200
HOEHE = 800
SPIELER_BREITE = 20
SPIELER_HOEHE = 100
BALL_GROESSE = 25  # Größerer Ball
SPIELER_GESCHWINDIGKEIT = 5
BALL_GESCHWINDIGKEIT = 7
BALL_MIN_GESCHWINDIGKEIT = 5  # Mindestgeschwindigkeit
BALL_MAX_GESCHWINDIGKEIT = 15  # Maximale Geschwindigkeit
BALL_BESCHLEUNIGUNG = 1.02  # Weniger aggressive Beschleunigung
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

# Gamepad-Zuweisungen
GAMEPADS = {'links': None, 'rechts': None}

def spiel_beenden():
    """Sauberes Beenden des Spiels"""
    print("Spiel wird beendet...")
    try:
        pygame.mixer.music.stop()
        print("Musik gestoppt")
    except:
        pass
    try:
        pygame.mixer.quit()
        print("Mixer beendet")
    except:
        pass
    try:
        pygame.quit()
        print("Pygame beendet")
    except:
        pass
    print("Programm wird beendet")
    sys.exit()

class Spieler:
    def __init__(self, x, y, farbe, steuerung, spieler_typ, controls=None, joystick=None):
        self.x = x
        self.y = y
        self.farbe = farbe
        self.steuerung = steuerung  # 'links' oder 'rechts' - bestimmt Spielfeldseite
        self.controls = controls if controls else steuerung  # legt Tastenbelegung fest
        self.spieler_typ = spieler_typ  # 'torwart' oder 'stürmer'
        self.punkte = 0
        self.geschwindigkeit = SPIELER_GESCHWINDIGKEIT
        self.joystick = joystick

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
        # Tastatursteuerung
        if self.controls == 'links':
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

        # Gamepad-Steuerung
        if self.joystick:
            achse_x = self.joystick.get_axis(0)
            achse_y = self.joystick.get_axis(1)
            if achse_y < -0.3 and self.y > 0:
                self.y -= self.geschwindigkeit
            if achse_y > 0.3 and self.y < HOEHE - SPIELER_HOEHE:
                self.y += self.geschwindigkeit
            if achse_x < -0.3 and self.x > self.min_x:
                self.x -= self.geschwindigkeit
            if achse_x > 0.3 and self.x < self.max_x:
                self.x += self.geschwindigkeit
                
    def zeichnen(self):
        pygame.draw.rect(bildschirm, self.farbe, (self.x, self.y, SPIELER_BREITE, SPIELER_HOEHE))

class Ball:
    def __init__(self, sound_wand=None, sound_spieler=None):
        self.sound_wand = sound_wand
        self.sound_spieler = sound_spieler
        self.max_speed = BALL_MAX_GESCHWINDIGKEIT
        self.reset()

    def reset(self):
        self.x = BREITE // 2 - BALL_GROESSE // 2
        self.y = HOEHE // 2 - BALL_GROESSE // 2
        self.speed = BALL_GESCHWINDIGKEIT
        # Zufällige Richtung mit leichtem Winkel
        richtung = random.choice([-1, 1])
        winkel = random.uniform(-math.pi/6, math.pi/6)  # Weniger steiler Winkel
        self.dx = richtung * self.speed * math.cos(winkel)
        self.dy = self.speed * math.sin(winkel)
        
        # Sicherstellen, dass der Ball nicht zu langsam startet
        gesamt_geschwindigkeit = math.sqrt(self.dx**2 + self.dy**2)
        if gesamt_geschwindigkeit < BALL_MIN_GESCHWINDIGKEIT:
            faktor = BALL_MIN_GESCHWINDIGKEIT / gesamt_geschwindigkeit
            self.dx *= faktor
            self.dy *= faktor
        
    def bewegen(self):
        self.x += self.dx
        self.y += self.dy

        # Obere und untere Wand-Kollision mit Toleranz
        if self.y <= 0:
            self.y = 0  # Ball zurück auf Rand setzen
            self.dy = abs(self.dy)  # Nach unten abprallen
            # Kleine Zufälligkeit beim Abprall
            self.dy += random.uniform(-0.5, 0.5)
            if self.sound_wand:
                self.sound_wand.play()
        elif self.y >= HOEHE - BALL_GROESSE:
            self.y = HOEHE - BALL_GROESSE  # Ball zurück auf Rand setzen
            self.dy = -abs(self.dy)  # Nach oben abprallen
            # Kleine Zufälligkeit beim Abprall
            self.dy += random.uniform(-0.5, 0.5)
            if self.sound_wand:
                self.sound_wand.play()
        
        # Mindestgeschwindigkeit sicherstellen
        gesamt_geschwindigkeit = math.sqrt(self.dx**2 + self.dy**2)
        if gesamt_geschwindigkeit < BALL_MIN_GESCHWINDIGKEIT:
            faktor = BALL_MIN_GESCHWINDIGKEIT / gesamt_geschwindigkeit
            self.dx *= faktor
            self.dy *= faktor
        
        # Maximale Geschwindigkeit begrenzen
        if gesamt_geschwindigkeit > BALL_MAX_GESCHWINDIGKEIT:
            faktor = BALL_MAX_GESCHWINDIGKEIT / gesamt_geschwindigkeit
            self.dx *= faktor
            self.dy *= faktor
            
    def kollision_spieler(self, spieler):
        # Ultra-robuste Kollisionserkennung für alle Richtungen
        ball_center_x = self.x + BALL_GROESSE // 2
        ball_center_y = self.y + BALL_GROESSE // 2
        
        # Vorherige Position berechnen
        prev_x = self.x - self.dx
        prev_y = self.y - self.dy
        prev_ball_center_x = prev_x + BALL_GROESSE // 2
        prev_ball_center_y = prev_y + BALL_GROESSE // 2
        
        # 1. Direkte Kollision mit aktueller Position
        if (spieler.x <= ball_center_x <= spieler.x + SPIELER_BREITE and 
            spieler.y <= ball_center_y <= spieler.y + SPIELER_HOEHE):
            return self._handle_kollision(spieler)
        
        # 2. Kollision mit vorheriger Position
        if (spieler.x <= prev_ball_center_x <= spieler.x + SPIELER_BREITE and 
            spieler.y <= prev_ball_center_y <= spieler.y + SPIELER_HOEHE):
            return self._handle_kollision(spieler)
        
        # 3. Linien-Kollision: Prüfe ob Ball-Pfad den Spieler kreuzt
        if self._linie_kreuzt_rechteck(prev_ball_center_x, prev_ball_center_y, 
                                      ball_center_x, ball_center_y,
                                      spieler.x, spieler.y, 
                                      spieler.x + SPIELER_BREITE, spieler.y + SPIELER_HOEHE):
            return self._handle_kollision(spieler)
        
        # 4. Erweiterte Kollision mit Ball-Rand
        ball_rect = pygame.Rect(self.x, self.y, BALL_GROESSE, BALL_GROESSE)
        spieler_rect = pygame.Rect(spieler.x, spieler.y, SPIELER_BREITE, SPIELER_HOEHE)
        if ball_rect.colliderect(spieler_rect):
            return self._handle_kollision(spieler)
        
        # 5. Vorherige Position mit Ball-Rand
        prev_ball_rect = pygame.Rect(prev_x, prev_y, BALL_GROESSE, BALL_GROESSE)
        if prev_ball_rect.colliderect(spieler_rect):
            return self._handle_kollision(spieler)
        
        # 6. Spezielle Rückseiten-Kollision für von hinten kommende Bälle
        if self._rueckseiten_kollision(spieler, prev_x, prev_y):
            return self._handle_kollision(spieler)
        
        # 7. Zusätzliche Sicherheitsprüfung: Ball ist sehr nah am Spieler
        if self._ball_nahe_spieler(spieler):
            return self._handle_kollision(spieler)
        
        return False
    
    def _rueckseiten_kollision(self, spieler, prev_x, prev_y):
        """Spezielle Kollisionserkennung für von hinten kommende Bälle"""
        ball_center_x = self.x + BALL_GROESSE // 2
        ball_center_y = self.y + BALL_GROESSE // 2
        prev_ball_center_x = prev_x + BALL_GROESSE // 2
        prev_ball_center_y = prev_y + BALL_GROESSE // 2
        
        # Prüfe ob Ball von hinten kommt und durch den Spieler fliegt
        if spieler.steuerung == 'rechts':
            # Rechter Spieler - Ball kommt von links (Rückseite)
            if (prev_ball_center_x < spieler.x and ball_center_x > spieler.x + SPIELER_BREITE and
                spieler.y <= ball_center_y <= spieler.y + SPIELER_HOEHE and
                spieler.y <= prev_ball_center_y <= spieler.y + SPIELER_HOEHE):
                return True
        else:
            # Linker Spieler - Ball kommt von rechts (Rückseite)
            if (prev_ball_center_x > spieler.x + SPIELER_BREITE and ball_center_x < spieler.x and
                spieler.y <= ball_center_y <= spieler.y + SPIELER_HOEHE and
                spieler.y <= prev_ball_center_y <= spieler.y + SPIELER_HOEHE):
                return True
        
        return False
    
    def _ball_nahe_spieler(self, spieler):
        """Prüft ob Ball sehr nah am Spieler ist (Sicherheitsprüfung)"""
        ball_center_x = self.x + BALL_GROESSE // 2
        ball_center_y = self.y + BALL_GROESSE // 2
        
        # Erweiterte Kollisionszone um den Spieler
        erweiterte_zone = 5  # Pixel
        
        if (spieler.x - erweiterte_zone <= ball_center_x <= spieler.x + SPIELER_BREITE + erweiterte_zone and
            spieler.y - erweiterte_zone <= ball_center_y <= spieler.y + SPIELER_HOEHE + erweiterte_zone):
            return True
        
        return False
    
    def _linie_kreuzt_rechteck(self, x1, y1, x2, y2, rx1, ry1, rx2, ry2):
        """Prüft ob eine Linie ein Rechteck kreuzt"""
        # Prüfe alle vier Seiten des Rechtecks
        seiten = [
            ((rx1, ry1), (rx2, ry1)),  # Obere Seite
            ((rx2, ry1), (rx2, ry2)),  # Rechte Seite
            ((rx2, ry2), (rx1, ry2)),  # Untere Seite
            ((rx1, ry2), (rx1, ry1))   # Linke Seite
        ]
        
        for (sx1, sy1), (sx2, sy2) in seiten:
            if self._linien_schneiden(x1, y1, x2, y2, sx1, sy1, sx2, sy2):
                return True
        return False
    
    def _linien_schneiden(self, x1, y1, x2, y2, x3, y3, x4, y4):
        """Prüft ob zwei Linien sich schneiden"""
        # Berechne Determinanten
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return False  # Parallele Linien
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        # Schnittpunkt liegt auf beiden Linien
        return 0 <= t <= 1 and 0 <= u <= 1
    
    def _handle_kollision(self, spieler):
        """Behandelt die Kollision mit einem Spieler"""
        # Ball zurückschlagen mit Winkel basierend auf Trefferposition
        offset = ((self.y + BALL_GROESSE / 2) - (spieler.y + SPIELER_HOEHE / 2)) / (SPIELER_HOEHE / 2)
        winkel = offset * math.pi/3  # -60° bis +60°

        ball_center_x = self.x + BALL_GROESSE // 2
        spieler_center_x = spieler.x + SPIELER_BREITE // 2

        # Bestimme Abprallrichtung basierend auf Spieler-Seite und Ball-Richtung
        if spieler.steuerung == 'rechts':
            # Rechter Spieler - Ball prallt nach links ab
            richtung = -1
        else:
            # Linker Spieler - Ball prallt nach rechts ab
            richtung = 1

        # Geschwindigkeit leicht erhöhen bis zum Maximum
        self.speed = min(self.speed * BALL_BESCHLEUNIGUNG, self.max_speed)
        self.dx = richtung * self.speed * math.cos(winkel)
        self.dy = self.speed * math.sin(winkel)
        
        # Kleine Zufälligkeit beim Abprall hinzufügen
        self.dx += random.uniform(-0.2, 0.2)
        self.dy += random.uniform(-0.2, 0.2)
        
        # Mindestgeschwindigkeit sicherstellen
        gesamt_geschwindigkeit = math.sqrt(self.dx**2 + self.dy**2)
        if gesamt_geschwindigkeit < BALL_MIN_GESCHWINDIGKEIT:
            faktor = BALL_MIN_GESCHWINDIGKEIT / gesamt_geschwindigkeit
            self.dx *= faktor
            self.dy *= faktor
        
        # Ball sauber aus dem Spieler herausdrücken
        if spieler.steuerung == 'rechts':
            # Rechter Spieler - Ball nach links drücken
            self.x = spieler.x - BALL_GROESSE - 2
        else:
            # Linker Spieler - Ball nach rechts drücken
            self.x = spieler.x + SPIELER_BREITE + 2
        
        # Zusätzliche Sicherheit: Ball darf nicht im Spieler stecken
        if (spieler.x <= self.x + BALL_GROESSE//2 <= spieler.x + SPIELER_BREITE and
            spieler.y <= self.y + BALL_GROESSE//2 <= spieler.y + SPIELER_HOEHE):
            # Ball ist noch im Spieler - weiter herausdrücken
            if spieler.steuerung == 'rechts':
                self.x = spieler.x - BALL_GROESSE - 10
            else:
                self.x = spieler.x + SPIELER_BREITE + 10
        
        # Finale Sicherheitsprüfung: Ball muss außerhalb des Spielers sein
        if (spieler.x <= self.x + BALL_GROESSE//2 <= spieler.x + SPIELER_BREITE and
            spieler.y <= self.y + BALL_GROESSE//2 <= spieler.y + SPIELER_HOEHE):
            # Notfall: Ball sehr weit herausdrücken
            if spieler.steuerung == 'rechts':
                self.x = spieler.x - BALL_GROESSE - 20
            else:
                self.x = spieler.x + SPIELER_BREITE + 20
        
        if self.sound_spieler:
            self.sound_spieler.play()
        return True
    
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
    def __init__(self, singleplayer=False, gamepads=None, spieler_links="Team Links", spieler_rechts="Team Rechts", zeit_limit=None):
        self.singleplayer = singleplayer
        self.gamepads = gamepads or {}
        self.name_links = spieler_links
        self.name_rechts = spieler_rechts
        self.zeit_limit = zeit_limit
        # Soundeffekte laden
        self.sound_wand, self.sound_spieler, self.sound_tor = self.soundeffekte_laden()

        # 4 Spieler: Torwart und Stürmer für jede Seite
        # Torwarte stehen näher an den Toren
        # Stürmer stehen in der Mitte des gegnerischen Feldes
        controls_links = 'rechts' if singleplayer else 'links'
        controls_rechts = 'links' if singleplayer else 'rechts'
        
        # Torwarte: näher an den Toren
        self.torwart_links = Spieler(50, HOEHE//2 - SPIELER_HOEHE//2, BLAU, 'links', 'torwart', controls_links, self.gamepads.get('links'))
        self.torwart_rechts = Spieler(BREITE - 50 - SPIELER_BREITE, HOEHE//2 - SPIELER_HOEHE//2, ROT, 'rechts', 'torwart', controls_rechts, self.gamepads.get('rechts'))
        
        # Stürmer: im gegnerischen Feld, aber nicht zu nah an der Mittellinie
        self.stürmer_links = Spieler(BREITE//2 + 100, HOEHE//2 - SPIELER_HOEHE//2, BLAU, 'links', 'stürmer', controls_links, self.gamepads.get('links'))
        self.stürmer_rechts = Spieler(BREITE//2 - 100 - SPIELER_BREITE, HOEHE//2 - SPIELER_HOEHE//2, ROT, 'rechts', 'stürmer', controls_rechts, self.gamepads.get('rechts'))
        
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

    def ai_bewegen(self, spieler):
        ziel_y = self.ball.y + BALL_GROESSE/2
        spieler_center = spieler.y + SPIELER_HOEHE/2
        if ziel_y < spieler_center and spieler.y > 0:
            spieler.y -= spieler.geschwindigkeit
        elif ziel_y > spieler_center and spieler.y < HOEHE - SPIELER_HOEHE:
            spieler.y += spieler.geschwindigkeit

        if spieler.spieler_typ == 'torwart':
            if spieler.steuerung == 'rechts':
                if self.ball.x > spieler.x and spieler.x > spieler.min_x:
                    spieler.x -= spieler.geschwindigkeit
                elif self.ball.x < spieler.x and spieler.x < spieler.max_x:
                    spieler.x += spieler.geschwindigkeit
            else:
                if self.ball.x < spieler.x and spieler.x < spieler.max_x:
                    spieler.x += spieler.geschwindigkeit
                elif self.ball.x > spieler.x and spieler.x > spieler.min_x:
                    spieler.x -= spieler.geschwindigkeit
        
    def tor_pruefen(self):
        # Tor-Bereiche definieren
        tor_links_y_start = HOEHE//2 - NETZ_HOEHE//2
        tor_links_y_ende = HOEHE//2 + NETZ_HOEHE//2
        tor_rechts_y_start = HOEHE//2 - NETZ_HOEHE//2
        tor_rechts_y_ende = HOEHE//2 + NETZ_HOEHE//2
        
        # Linkes Tor (Ball muss komplett im Tor sein)
        if self.ball.x <= 0:
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
                
        # Rechtes Tor (Ball muss komplett im Tor sein)
        elif self.ball.x >= BREITE - BALL_GROESSE:
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
    
    def pause_anzeigen(self):
        """Zeigt Pause-Bildschirm an"""
        font_gross = pygame.font.Font(None, 74)
        font_klein = pygame.font.Font(None, 36)
        
        # Halbtransparenter Overlay
        overlay = pygame.Surface((BREITE, HOEHE))
        overlay.set_alpha(128)
        overlay.fill(SCHWARZ)
        bildschirm.blit(overlay, (0, 0))
        
        text_pause = font_gross.render("PAUSE", True, WEISS)
        text_anweisung = font_klein.render("Drücke P zum Fortsetzen oder ESC zum Beenden", True, WEISS)
        
        pause_rect = text_pause.get_rect(center=(BREITE//2, HOEHE//2 - 50))
        anweisung_rect = text_anweisung.get_rect(center=(BREITE//2, HOEHE//2 + 50))
        
        bildschirm.blit(text_pause, pause_rect)
        bildschirm.blit(text_anweisung, anweisung_rect)
    
    def sicherheitsabfrage_anzeigen(self):
        """Zeigt Sicherheitsabfrage für Spielabbruch an"""
        font_gross = pygame.font.Font(None, 48)
        font_klein = pygame.font.Font(None, 36)
        
        # Halbtransparenter Overlay
        overlay = pygame.Surface((BREITE, HOEHE))
        overlay.set_alpha(180)
        overlay.fill(SCHWARZ)
        bildschirm.blit(overlay, (0, 0))
        
        text_frage = font_gross.render("Spiel wirklich beenden?", True, WEISS)
        text_ja = font_klein.render("Drücke ESC für JA", True, ROT)
        text_nein = font_klein.render("Drücke eine andere Taste für NEIN", True, WEISS)
        text_alt = font_klein.render("Oder drücke Q zum direkten Beenden", True, GELB)
        
        frage_rect = text_frage.get_rect(center=(BREITE//2, HOEHE//2 - 100))
        ja_rect = text_ja.get_rect(center=(BREITE//2, HOEHE//2 - 40))
        nein_rect = text_nein.get_rect(center=(BREITE//2, HOEHE//2))
        alt_rect = text_alt.get_rect(center=(BREITE//2, HOEHE//2 + 40))
        
        bildschirm.blit(text_frage, frage_rect)
        bildschirm.blit(text_ja, ja_rect)
        bildschirm.blit(text_nein, nein_rect)
        bildschirm.blit(text_alt, alt_rect)
    
    def spiel_ausfuehren(self):
        # Warten bis beide Spieler bereit sind
        bereit_links = bereit_rechts = False
        font_gross = pygame.font.Font(None, 48)
        font_klein = pygame.font.Font(None, 36)
        
        # Für Singleplayer: Automatisch bereit machen
        if self.singleplayer:
            bereit_links = True
            bereit_rechts = True
        
        while not (bereit_links and bereit_rechts):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    spiel_beenden()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        bereit_links = True
                    if event.key == pygame.K_l:
                        bereit_rechts = True
                    # Alternative: Leertaste für beide
                    if event.key == pygame.K_SPACE:
                        bereit_links = True
                        bereit_rechts = True
            
            # Spielfeld zeichnen
            self.spiel_feld_zeichnen()
            self.torwart_links.zeichnen()
            self.stürmer_links.zeichnen()
            self.torwart_rechts.zeichnen()
            self.stürmer_rechts.zeichnen()
            self.ball.zeichnen()
            
            # Bereitschafts-Text anzeigen
            text_gross = font_gross.render("Bereit zum Spielen?", True, WEISS)
            text_links = font_klein.render(f"{self.name_links}: Drücke A", True, WEISS)
            text_rechts = font_klein.render(f"{self.name_rechts}: Drücke L", True, WEISS)
            text_alt = font_klein.render("Oder drücke LEERTASTE für beide", True, WEISS)
            
            text_gross_rect = text_gross.get_rect(center=(BREITE//2, HOEHE//2 - 80))
            text_links_rect = text_links.get_rect(center=(BREITE//2, HOEHE//2 - 20))
            text_rechts_rect = text_rechts.get_rect(center=(BREITE//2, HOEHE//2 + 20))
            text_alt_rect = text_alt.get_rect(center=(BREITE//2, HOEHE//2 + 60))
            
            bildschirm.blit(text_gross, text_gross_rect)
            bildschirm.blit(text_links, text_links_rect)
            bildschirm.blit(text_rechts, text_rechts_rect)
            bildschirm.blit(text_alt, text_alt_rect)
            
            # Status anzeigen
            status_links = "✓" if bereit_links else "✗"
            status_rechts = "✓" if bereit_rechts else "✗"
            status_text = font_klein.render(f"{self.name_links}: {status_links} | {self.name_rechts}: {status_rechts}", True, WEISS)
            status_rect = status_text.get_rect(center=(BREITE//2, HOEHE//2 + 100))
            bildschirm.blit(status_text, status_rect)
            
            pygame.display.flip()
            uhr.tick(60)

        startzeit = pygame.time.get_ticks()
        gewinner = None
        pause_aktiv = False
        sicherheitsabfrage_aktiv = False
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    spiel_beenden()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r and not self.spiel_aktiv:
                        self.__init__(self.singleplayer, self.gamepads, self.name_links, self.name_rechts, self.zeit_limit)
                    elif event.key == pygame.K_q and not self.spiel_aktiv:
                        spiel_beenden()
                    elif event.key == pygame.K_p and self.spiel_aktiv and not sicherheitsabfrage_aktiv:
                        # Pause umschalten
                        pause_aktiv = not pause_aktiv
                    elif event.key == pygame.K_ESCAPE:
                        print(f"ESC gedrückt - Pause: {pause_aktiv}, Sicherheitsabfrage: {sicherheitsabfrage_aktiv}")
                        if pause_aktiv:
                            # In Pause: Sicherheitsabfrage starten
                            sicherheitsabfrage_aktiv = True
                            print("Sicherheitsabfrage gestartet")
                        elif sicherheitsabfrage_aktiv:
                            # In Sicherheitsabfrage: Spiel beenden
                            print("Spiel wird beendet (ESC in Sicherheitsabfrage)")
                            spiel_beenden()
                        else:
                            # Im Spiel: Pause aktivieren
                            pause_aktiv = True
                            print("Pause aktiviert")
                    elif event.key == pygame.K_q and sicherheitsabfrage_aktiv:
                        # Direktes Beenden mit Q in Sicherheitsabfrage
                        print("Direktes Beenden mit Q")
                        spiel_beenden()
                    elif sicherheitsabfrage_aktiv and event.key != pygame.K_ESCAPE:
                        # In Sicherheitsabfrage: Andere Taste = Abbrechen
                        sicherheitsabfrage_aktiv = False
                        print("Sicherheitsabfrage abgebrochen")

            if self.spiel_aktiv and not pause_aktiv and not sicherheitsabfrage_aktiv:
                # Spieler bewegen
                tasten = pygame.key.get_pressed()
                self.torwart_links.bewegen(tasten)
                self.stürmer_links.bewegen(tasten)
                if self.singleplayer:
                    self.ai_bewegen(self.torwart_rechts)
                    self.ai_bewegen(self.stürmer_rechts)
                else:
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

                # Zeitlimit prüfen
                if self.zeit_limit and pygame.time.get_ticks() - startzeit > self.zeit_limit * 1000:
                    self.spiel_aktiv = False
                    if self.torwart_links.punkte > self.torwart_rechts.punkte:
                        gewinner = "Team Links"
                    elif self.torwart_rechts.punkte > self.torwart_links.punkte:
                        gewinner = "Team Rechts"
                    else:
                        gewinner = None

                # Gewinner prüfen
                if self.spiel_aktiv:
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

            # Pause oder Sicherheitsabfrage anzeigen
            if pause_aktiv and not sicherheitsabfrage_aktiv:
                self.pause_anzeigen()
            elif sicherheitsabfrage_aktiv:
                self.sicherheitsabfrage_anzeigen()

            if not self.spiel_aktiv:
                self.spiel_ende_anzeigen(gewinner)
                pygame.display.flip()
                pygame.time.wait(2000)
                return gewinner

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
    
    anleitung = font_klein.render("1: Singleplayer  2: Multiplayer  3: Liga  4: Einstellungen", True, WEISS)
    steuerung1 = font_klein.render("Links - Torwart & Stürmer: W/S oder Gamepad", True, WEISS)
    steuerung2 = font_klein.render("Rechts - Torwart & Stürmer: Pfeiltasten oder Gamepad", True, WEISS)
    steuerung3 = font_klein.render("P: Pause  ESC: Spiel beenden (mit Sicherheitsabfrage)", True, WEISS)
    credits = font_credits.render("Von Jan Heiko Wohltmann, 2025 - Version 0.1 vom 31.08.2025", True, WEISS)

    anleitung_rect = anleitung.get_rect(center=(BREITE//2, HOEHE//2 + 30))
    steuerung1_rect = steuerung1.get_rect(center=(BREITE//2, HOEHE//2 + 60))
    steuerung2_rect = steuerung2.get_rect(center=(BREITE//2, HOEHE//2 + 90))
    steuerung3_rect = steuerung3.get_rect(center=(BREITE//2, HOEHE//2 + 120))
    credits_rect = credits.get_rect(center=(BREITE//2, HOEHE//2 + 170))

    bildschirm.blit(anleitung, anleitung_rect)
    bildschirm.blit(steuerung1, steuerung1_rect)
    bildschirm.blit(steuerung2, steuerung2_rect)
    bildschirm.blit(steuerung3, steuerung3_rect)
    bildschirm.blit(credits, credits_rect)
    
    pygame.display.flip()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spiel_beenden()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "single"
                elif event.key == pygame.K_2:
                    return "multi"
                elif event.key == pygame.K_3:
                    return "liga"
                elif event.key == pygame.K_4:
                    gamepad_einstellungen()
        
        uhr.tick(60)

def gamepad_einstellungen():
    """Gamepad-Einstellungen mit GUI"""
    pygame.joystick.quit()
    pygame.joystick.init()
    anzahl = pygame.joystick.get_count()
    pads = [pygame.joystick.Joystick(i) for i in range(anzahl)]
    for pad in pads:
        pad.init()
    
    if anzahl == 0:
        gamepad_keine_anzeigen()
        return
    
    links_index = -1
    rechts_index = -1
    aktueller_auswahl = "links"  # "links" oder "rechts"
    
    font_gross = pygame.font.Font(None, 48)
    font_klein = pygame.font.Font(None, 36)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spiel_beenden()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                elif event.key == pygame.K_RETURN:
                    # Auswahl bestätigen
                    if aktueller_auswahl == "links":
                        if links_index >= 0:
                            GAMEPADS['links'] = pads[links_index]
                        aktueller_auswahl = "rechts"
                    else:
                        if rechts_index >= 0:
                            GAMEPADS['rechts'] = pads[rechts_index]
                        return
                elif event.key == pygame.K_UP:
                    if aktueller_auswahl == "links" and links_index > -1:
                        links_index -= 1
                    elif aktueller_auswahl == "rechts" and rechts_index > -1:
                        rechts_index -= 1
                elif event.key == pygame.K_DOWN:
                    if aktueller_auswahl == "links" and links_index < anzahl - 1:
                        links_index += 1
                    elif aktueller_auswahl == "rechts" and rechts_index < anzahl - 1:
                        rechts_index += 1
                elif event.key == pygame.K_TAB:
                    # Zwischen Links und Rechts wechseln
                    aktueller_auswahl = "rechts" if aktueller_auswahl == "links" else "links"
        
        # Zeichnen
        bildschirm.fill(SCHWARZ)
        
        text_titel = font_gross.render("Gamepad-Einstellungen", True, WEISS)
        titel_rect = text_titel.get_rect(center=(BREITE//2, 50))
        bildschirm.blit(text_titel, titel_rect)
        
        # Verfügbare Gamepads anzeigen
        text_pads = font_klein.render("Verfügbare Gamepads:", True, WEISS)
        pads_rect = text_pads.get_rect(center=(BREITE//2, 100))
        bildschirm.blit(text_pads, pads_rect)
        
        y_start = 150
        for i, pad in enumerate(pads):
            farbe = WEISS
            if aktueller_auswahl == "links" and i == links_index:
                farbe = BLAU
            elif aktueller_auswahl == "rechts" and i == rechts_index:
                farbe = ROT
            
            text_pad = font_klein.render(f"{i}: {pad.get_name()}", True, farbe)
            pad_rect = text_pad.get_rect(center=(BREITE//2, y_start + i * 30))
            bildschirm.blit(text_pad, pad_rect)
        
        # Auswahl anzeigen
        links_text = f"Team Links: {links_index if links_index >= 0 else 'Keine'}"
        rechts_text = f"Team Rechts: {rechts_index if rechts_index >= 0 else 'Keine'}"
        
        links_farbe = BLAU if aktueller_auswahl == "links" else WEISS
        rechts_farbe = ROT if aktueller_auswahl == "rechts" else WEISS
        
        text_links = font_klein.render(links_text, True, links_farbe)
        text_rechts = font_klein.render(rechts_text, True, rechts_farbe)
        
        links_rect = text_links.get_rect(center=(BREITE//2, HOEHE - 120))
        rechts_rect = text_rechts.get_rect(center=(BREITE//2, HOEHE - 90))
        
        bildschirm.blit(text_links, links_rect)
        bildschirm.blit(text_rechts, rechts_rect)
        
        # Steuerung anzeigen
        text_steuerung = font_klein.render("Pfeiltasten: Auswählen  ENTER: Bestätigen  TAB: Wechseln  ESC: Abbrechen", True, WEISS)
        steuerung_rect = text_steuerung.get_rect(center=(BREITE//2, HOEHE - 50))
        bildschirm.blit(text_steuerung, steuerung_rect)
        
        pygame.display.flip()
        uhr.tick(60)

def gamepad_keine_anzeigen():
    """Zeigt an, dass keine Gamepads gefunden wurden"""
    font_gross = pygame.font.Font(None, 48)
    font_klein = pygame.font.Font(None, 36)
    
    bildschirm.fill(SCHWARZ)
    
    text_keine = font_gross.render("Keine Gamepads gefunden!", True, WEISS)
    text_anweisung = font_klein.render("Drücke ENTER zum Fortfahren", True, WEISS)
    
    keine_rect = text_keine.get_rect(center=(BREITE//2, HOEHE//2 - 50))
    anweisung_rect = text_anweisung.get_rect(center=(BREITE//2, HOEHE//2 + 50))
    
    bildschirm.blit(text_keine, keine_rect)
    bildschirm.blit(text_anweisung, anweisung_rect)
    
    pygame.display.flip()
    
    # Warten auf ENTER
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spiel_beenden()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
        uhr.tick(60)

def liga_modus():
    """Liga-Modus mit GUI-Eingabe"""
    # Anzahl Spieler eingeben
    anzahl = liga_anzahl_eingeben()
    if anzahl is None:
        return
    
    # Spielernamen eingeben
    namen = liga_namen_eingeben(anzahl)
    if namen is None:
        return
    
    # Liga durchführen
    punkte = {n: 0 for n in namen}
    for p1, p2 in itertools.combinations(namen, 2):
        # Match-Info anzeigen
        match_info_anzeigen(p1, p2)
        
        spiel = Spiel(singleplayer=False, gamepads=GAMEPADS, spieler_links=p1, spieler_rechts=p2, zeit_limit=120)
        gewinner = spiel.spiel_ausfuehren()
        
        if gewinner == "Team Links":
            punkte[p1] += 3
        elif gewinner == "Team Rechts":
            punkte[p2] += 3
        else:
            punkte[p1] += 1
            punkte[p2] += 1
        
        # Tabelle anzeigen
        liga_tabelle_anzeigen(punkte)
    
    # Liga-Ende anzeigen
    liga_ende_anzeigen()

def liga_anzahl_eingeben():
    """GUI für Anzahl Spieler"""
    font_gross = pygame.font.Font(None, 48)
    font_klein = pygame.font.Font(None, 36)
    anzahl = 2
    eingabe_aktiv = True
    
    while eingabe_aktiv:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spiel_beenden()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    eingabe_aktiv = False
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.key == pygame.K_UP and anzahl < 16:
                    anzahl += 1
                elif event.key == pygame.K_DOWN and anzahl > 2:
                    anzahl -= 1
        
        # Zeichnen
        bildschirm.fill(SCHWARZ)
        
        text_titel = font_gross.render("Liga-Modus", True, WEISS)
        text_anweisung = font_klein.render("Anzahl Spieler (2-16):", True, WEISS)
        text_anzahl = font_gross.render(str(anzahl), True, GELB)
        text_steuerung = font_klein.render("Pfeiltasten: Ändern  ENTER: Bestätigen  ESC: Abbrechen", True, WEISS)
        
        titel_rect = text_titel.get_rect(center=(BREITE//2, HOEHE//2 - 100))
        anweisung_rect = text_anweisung.get_rect(center=(BREITE//2, HOEHE//2 - 30))
        anzahl_rect = text_anzahl.get_rect(center=(BREITE//2, HOEHE//2 + 20))
        steuerung_rect = text_steuerung.get_rect(center=(BREITE//2, HOEHE//2 + 80))
        
        bildschirm.blit(text_titel, titel_rect)
        bildschirm.blit(text_anweisung, anweisung_rect)
        bildschirm.blit(text_anzahl, anzahl_rect)
        bildschirm.blit(text_steuerung, steuerung_rect)
        
        pygame.display.flip()
        uhr.tick(60)
    
    return anzahl

def liga_namen_eingeben(anzahl):
    """GUI für Spielernamen"""
    font_gross = pygame.font.Font(None, 48)
    font_klein = pygame.font.Font(None, 36)
    namen = []
    aktueller_spieler = 0
    
    while aktueller_spieler < anzahl:
        name = f"Spieler{aktueller_spieler + 1}"
        eingabe_aktiv = True
        
        while eingabe_aktiv:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    spiel_beenden()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name.strip():
                        namen.append(name)
                        aktueller_spieler += 1
                        eingabe_aktiv = False
                    elif event.key == pygame.K_ESCAPE:
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif event.unicode.isprintable() and len(name) < 20:
                        name += event.unicode
            
            # Zeichnen
            bildschirm.fill(SCHWARZ)
            
            text_titel = font_gross.render(f"Spieler {aktueller_spieler + 1} von {anzahl}", True, WEISS)
            text_anweisung = font_klein.render("Name eingeben:", True, WEISS)
            text_name = font_gross.render(name + "|", True, GELB)
            text_steuerung = font_klein.render("ENTER: Bestätigen  ESC: Abbrechen", True, WEISS)
            
            titel_rect = text_titel.get_rect(center=(BREITE//2, HOEHE//2 - 100))
            anweisung_rect = text_anweisung.get_rect(center=(BREITE//2, HOEHE//2 - 30))
            name_rect = text_name.get_rect(center=(BREITE//2, HOEHE//2 + 20))
            steuerung_rect = text_steuerung.get_rect(center=(BREITE//2, HOEHE//2 + 80))
            
            bildschirm.blit(text_titel, titel_rect)
            bildschirm.blit(text_anweisung, anweisung_rect)
            bildschirm.blit(text_name, name_rect)
            bildschirm.blit(text_steuerung, steuerung_rect)
            
            pygame.display.flip()
            uhr.tick(60)
    
    return namen

def match_info_anzeigen(p1, p2):
    """Zeigt Match-Information an"""
    font_gross = pygame.font.Font(None, 48)
    font_klein = pygame.font.Font(None, 36)
    
    bildschirm.fill(SCHWARZ)
    
    text_match = font_gross.render(f"Match: {p1} vs {p2}", True, WEISS)
    text_anweisung = font_klein.render("Drücke ENTER zum Starten", True, WEISS)
    
    match_rect = text_match.get_rect(center=(BREITE//2, HOEHE//2 - 50))
    anweisung_rect = text_anweisung.get_rect(center=(BREITE//2, HOEHE//2 + 50))
    
    bildschirm.blit(text_match, match_rect)
    bildschirm.blit(text_anweisung, anweisung_rect)
    
    pygame.display.flip()
    
    # Warten auf ENTER
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spiel_beenden()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
                elif event.key == pygame.K_ESCAPE:
                    return
        uhr.tick(60)

def liga_tabelle_anzeigen(punkte):
    """Zeigt Liga-Tabelle an"""
    font_gross = pygame.font.Font(None, 48)
    font_klein = pygame.font.Font(None, 36)
    
    bildschirm.fill(SCHWARZ)
    
    text_titel = font_gross.render("Aktuelle Tabelle", True, WEISS)
    titel_rect = text_titel.get_rect(center=(BREITE//2, 50))
    bildschirm.blit(text_titel, titel_rect)
    
    # Tabelle sortiert nach Punkten
    sortierte_spieler = sorted(punkte.items(), key=lambda x: -x[1])
    
    y_start = 120
    for i, (name, pkt) in enumerate(sortierte_spieler):
        text_zeile = font_klein.render(f"{i+1}. {name}: {pkt} Punkte", True, WEISS)
        zeile_rect = text_zeile.get_rect(center=(BREITE//2, y_start + i * 40))
        bildschirm.blit(text_zeile, zeile_rect)
    
    text_anweisung = font_klein.render("Drücke ENTER zum Fortfahren", True, WEISS)
    anweisung_rect = text_anweisung.get_rect(center=(BREITE//2, HOEHE - 50))
    bildschirm.blit(text_anweisung, anweisung_rect)
    
    pygame.display.flip()
    
    # Warten auf ENTER
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
        uhr.tick(60)

def liga_ende_anzeigen():
    """Zeigt Liga-Ende an"""
    font_gross = pygame.font.Font(None, 48)
    font_klein = pygame.font.Font(None, 36)
    
    bildschirm.fill(SCHWARZ)
    
    text_ende = font_gross.render("Liga beendet!", True, WEISS)
    text_anweisung = font_klein.render("Drücke ENTER zum Hauptmenü", True, WEISS)
    
    ende_rect = text_ende.get_rect(center=(BREITE//2, HOEHE//2 - 50))
    anweisung_rect = text_anweisung.get_rect(center=(BREITE//2, HOEHE//2 + 50))
    
    bildschirm.blit(text_ende, ende_rect)
    bildschirm.blit(text_anweisung, anweisung_rect)
    
    pygame.display.flip()
    
    # Warten auf ENTER
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                spiel_beenden()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return
        uhr.tick(60)

if __name__ == "__main__":
    # Notfall-Beenden mit Ctrl+C
    import signal
    def signal_handler(sig, frame):
        print("\nNotfall-Beenden mit Ctrl+C")
        spiel_beenden()
    signal.signal(signal.SIGINT, signal_handler)
    
    while True:
        modus = hauptmenue()
        if modus == "liga":
            liga_modus()
        elif modus == "single" or modus == "multi":
            spiel = Spiel(singleplayer=(modus == "single"), gamepads=GAMEPADS)
            spiel.spiel_ausfuehren()
        # Bei "einstellungen" (modus == "einstellungen") wird gamepad_einstellungen() bereits im Hauptmenü aufgerufen
