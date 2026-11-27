import asyncio
import math
import random
import time

import array
import sys

import pygame


RATE = 22050

C = {"ship": (61, 245, 224), "enemy": (255, 77, 141), "boss": (255, 182, 39), "eb": (255, 107, 107),
     "life": (255, 77, 109), "missile": (255, 182, 39), "spread": (125, 211, 252), "shield": (163, 230, 53)}
SKINS = [("Cian clásica", (14, 127, 120), (201, 255, 248), (61, 245, 224)),
         ("Fénix rojo", (130, 20, 30), (255, 200, 170), (255, 90, 60)),
         ("Rayo dorado", (140, 100, 0), (255, 245, 180), (255, 200, 40)),
         ("Sombra violeta", (60, 20, 110), (220, 190, 255), (170, 110, 255)),
         ("Hielo blanco", (90, 110, 140), (255, 255, 255), (190, 230, 255))]
JEFES = [{"body": (255, 210, 63), "dark": (166, 124, 0), "glow": (255, 224, 102), "eye": (58, 42, 0)},
         {"body": (255, 59, 59), "dark": (122, 0, 16), "glow": (255, 92, 92), "eye": (255, 224, 102)},
         {"body": (21, 21, 28), "dark": (0, 0, 0), "glow": (255, 26, 26), "eye": (255, 26, 26)}]
DIFS = [("facil", "BÁSICO", dict(enemy_hp=0.85, boss_hp=0.88, speed=0.85, enemy_fire=0.75, boss_fire=0.85)),
        ("normal", "INTERMEDIO", dict(enemy_hp=1, boss_hp=1, speed=1, enemy_fire=1, boss_fire=1)),
        ("dificil", "DIFÍCIL", dict(enemy_hp=1.25, boss_hp=1.25, speed=1.2, enemy_fire=1.3, boss_fire=1.25))]
MAX_LEVEL, MAX_METEORS = 3, 6
LEVEL_SPEED = {1: 1.6, 2: 2.6, 3: 2.6}
NOMBRE_NIVEL = ["Básico", "Intermedio", "Difícil"]


def onda(freq, dur, vol=0.4, tipo="sq", slide=0.0, ruido=False):
    n = int(RATE * dur); buf = array.array("h"); fase = 0.0
    for i in range(n):
        t = i / n
        fr = freq * (1 + slide * t)
        fase += fr / RATE
        if ruido: v = random.uniform(-1, 1)
        elif tipo == "sq": v = 1.0 if (fase % 1) < 0.5 else -1.0
        elif tipo == "tri": v = 4 * abs((fase % 1) - 0.5) - 1
        else: v = math.sin(fase * 2 * math.pi)
        env = min(1.0, i / 200) * (1 - t) ** 1.5
        buf.append(int(v * env * vol * 32767))
    return buf

def nota_hz(n): return 440 * 2 ** ((n - 69) / 12)



MIN, MAJ = (0, 3, 7), (0, 4, 7)

def _lista(compases):
    """compases[bar] = [(paso, nota MIDI, duración en pasos), ...]"""
    return lambda bar, st: next(((n, d) for s, n, d in compases[bar] if s == st), None)

def _jefe_lead(bar, st):
    if st % 2: return None
    r = [52, 53, 52, 53, 52, 58, 53, 59][bar]
    return (r + 24 + [0, 1, 0, 1, 7, 8, 7, 3][st >> 1], 2)

TEMAS = {
    
    "menu": dict(
        bpm=100, eco=True,
        compases=[(57, MIN), (53, MAJ), (60, MAJ), (55, MAJ), (57, MIN), (53, MAJ), (55, MAJ), (52, MAJ)],
        lead=_lista([
            [(0, 76, 6), (6, 79, 2), (8, 81, 8)],
            [(0, 77, 6), (6, 81, 2), (8, 84, 8)],
            [(0, 79, 6), (6, 76, 2), (8, 72, 8)],
            [(0, 74, 6), (6, 79, 2), (8, 83, 4), (12, 81, 4)],
            [(0, 81, 4), (4, 79, 4), (8, 76, 8)],
            [(0, 77, 4), (4, 81, 4), (8, 84, 4), (12, 81, 4)],
            [(0, 83, 6), (6, 79, 2), (8, 74, 8)],
            [(0, 76, 4), (4, 80, 4), (8, 83, 4), (12, 80, 4)]]),
        bajo=lambda r, st: (r - 24, 6) if st % 8 == 0 else None,
        arp=lambda st: [0, 1, 2, 1][(st >> 1) % 4] if st % 2 == 0 else None,
        v_lead=0.07, v_arp=0.05, v_bajo=0.24, t_bajo="tri",
        bombo=lambda st: st in (0, 8), caja=lambda st: False, hat=lambda st: st % 4 == 2, v_bat=0.5),
    
    "battle": dict(
        bpm=148, eco=True,
        compases=[(57, MIN), (57, MIN), (53, MAJ), (55, MAJ), (57, MIN), (57, MIN), (53, MAJ), (52, MAJ)],
        lead=_lista([
            [(0, 81, 3), (3, 79, 1), (4, 76, 4), (8, 79, 3), (11, 76, 1), (12, 72, 4)],
            [(0, 81, 3), (3, 83, 1), (4, 84, 4), (8, 83, 2), (10, 81, 2), (12, 79, 4)],
            [(0, 77, 3), (3, 81, 1), (4, 84, 4), (8, 81, 3), (11, 77, 1), (12, 81, 4)],
            [(0, 79, 3), (3, 83, 1), (4, 86, 4), (8, 83, 2), (10, 79, 2), (12, 74, 4)],
            [(0, 81, 3), (3, 79, 1), (4, 76, 4), (8, 79, 3), (11, 76, 1), (12, 72, 4)],
            [(0, 84, 2), (2, 83, 2), (4, 81, 2), (6, 79, 2), (8, 76, 4), (12, 79, 4)],
            [(0, 81, 3), (3, 84, 1), (4, 89, 4), (8, 84, 2), (10, 81, 2), (12, 77, 4)],
            [(0, 83, 2), (2, 80, 2), (4, 76, 2), (6, 80, 2), (8, 83, 4), (12, 88, 4)]]),
        bajo=lambda r, st: (r - 24 + (12 if st % 4 == 2 else 0), 2) if st % 2 == 0 else None,
        arp=lambda st: [0, 2, 1, 5][st % 4],
        v_lead=0.07, v_arp=0.04, v_bajo=0.28, t_bajo="tri",
        bombo=lambda st: st % 4 == 0, caja=lambda st: st in (4, 12), hat=lambda st: st % 2 == 0, v_bat=1.0),
   
    "boss": dict(
        bpm=168, eco=False,
        compases=[(52, MIN), (53, MAJ), (52, MIN), (53, MAJ), (52, MIN), (58, MAJ), (53, MAJ), (59, MAJ)],
        lead=_jefe_lead,
        bajo=lambda r, st: (r - 24 + (12 if st % 8 >= 6 else 0), 1),
        arp=lambda st: 2 if st % 4 == 1 else 4 if st % 4 == 3 else None,
        v_lead=0.06, v_arp=0.045, v_bajo=0.1, t_bajo="sq",
        bombo=lambda st: st % 4 == 0 or st == 14, caja=lambda st: st in (4, 12), hat=lambda st: True, v_bat=1.1),
}

_cache = {}
def _tono(f, dur, tipo, vol):
    k = (round(f, 2), round(dur, 4), tipo, vol)
    if k not in _cache: _cache[k] = onda(f, dur, vol, tipo)
    return _cache[k]

def _bombo(vol):
    k = ("bombo", vol)
    if k not in _cache:
        n = int(RATE * 0.14); buf = array.array("h"); fase = 0.0
        for i in range(n):
            t = i / n; fase += 150 * (40 / 150) ** t / RATE
            buf.append(int(math.sin(fase * 2 * math.pi) * (1 - t) ** 2 * 0.32 * vol * 32767))
        _cache[k] = buf
    return _cache[k]

def _ruido_agudo(dur, vol):
    
    k = ("ruido", dur, vol)
    if k not in _cache:
        n = int(RATE * dur); buf = array.array("h"); prev = 0.0
        for i in range(n):
            v = random.uniform(-1, 1); h = (v - prev) * 0.5; prev = v
            buf.append(int(h * (1 - i / n) ** 2 * vol * 32767))
        _cache[k] = buf
    return _cache[k]

def componer(tr):
    
    paso = 60 / tr["bpm"] / 4; n = int(RATE * paso); nb = len(tr["compases"])
    total = [0] * (n * 16 * nb)

    def mezclar(seg, base, g=1.0):
        fin = min(len(seg), len(total) - base)
        if g == 1.0:
            for i in range(fin): total[base + i] += seg[i]
        else:
            for i in range(fin): total[base + i] += int(seg[i] * g)

    vb = tr["v_bat"]
    for bar in range(nb):
        raiz, q = tr["compases"][bar]
        for st in range(16):
            base = (bar * 16 + st) * n
            l = tr["lead"](bar, st)
            if l:
                seg = _tono(nota_hz(l[0]), l[1] * paso * 0.95, "sq", tr["v_lead"])
                mezclar(seg, base)
                if tr["eco"]:                       # eco espacial: copias retrasadas y más suaves
                    mezclar(seg, base + 3 * n, 0.45); mezclar(seg, base + 6 * n, 0.2)
            b = tr["bajo"](raiz, st)
            if b: mezclar(_tono(nota_hz(b[0]), b[1] * paso * 0.95, tr["t_bajo"], tr["v_bajo"]), base)
            a = tr["arp"](st)
            if a is not None:
                nt = raiz + q[a % 3] + 12 + (12 if a >= 3 else 0)
                mezclar(_tono(nota_hz(nt), paso * 0.8, "sq", tr["v_arp"]), base)
            if tr["bombo"](st): mezclar(_bombo(vb), base)
            if tr["caja"](st): mezclar(_ruido_agudo(0.11, 0.11 * vb), base)
            if tr["hat"](st): mezclar(_ruido_agudo(0.035, 0.045 * vb), base)
    return array.array("h", [max(-32767, min(32767, s)) for s in total])

class Audio:
    def __init__(self):
        self.ok = True; self.on = True; self.actual = None
        try:
            pygame.mixer.pre_init(RATE, -16, 1, 512); pygame.mixer.init(RATE, -16, 1, 512)
        except Exception:
            self.ok = False; return
        S = lambda b: pygame.mixer.Sound(buffer=b.tobytes())
        self.sfx = {
            "shot": S(onda(880, 0.07, 0.18, "sq", -0.5)),
            "missile": S(onda(220, 0.35, 0.25, "sq", 1.5)),
            "hit": S(onda(300, 0.05, 0.2, "sq", -0.6)),
            "boom": S(onda(0, 0.35, 0.35, ruido=True)),
            "bigboom": S(onda(0, 1.0, 0.5, ruido=True)),
            "power": S(onda(523, 0.25, 0.25, "sin", 1.0)),
            "hurt": S(onda(160, 0.4, 0.35, "sq", -0.7)),
            "alert": S(onda(440, 0.6, 0.25, "sq", 0.5)),
            "select": S(onda(660, 0.06, 0.2, "sq")),
            "start": S(onda(392, 0.4, 0.25, "sq", 1.0)),
        }
        
        self.musica = {nombre: S(componer(tr)) for nombre, tr in TEMAS.items()}
        self.canal = pygame.mixer.Channel(0)
        pygame.mixer.set_reserved(1)

    def play(self, nombre):
        if self.ok and self.on: self.sfx[nombre].play()

    def tema(self, nombre):
        if not self.ok or nombre == self.actual: return
        self.actual = nombre
        self.canal.stop()
        if self.on and nombre: self.canal.play(self.musica[nombre], loops=-1)

    def alternar(self):
        if not self.ok: return
        self.on = not self.on
        t = self.actual; self.actual = None
        if self.on: self.tema(t)
        else: self.canal.stop(); self.actual = t



pygame.init()
AUDIO = Audio()
WIDTH, HEIGHT = 600, 800
FPS = 60
FRAME_BUDGET_MS = 1000 / FPS          
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DEFENSOR GALACTICO - PROGRAMACION DINAMICA")
clock = pygame.time.Clock()

# COLORES
BLACK = (3, 3, 12)
WHITE = (245, 250, 255)
CYAN = (0, 240, 255)
BLUE = (35, 100, 255)
PURPLE = (175, 40, 255)
PINK = (255, 45, 160)
GREEN = (30, 255, 115)
YELLOW = (255, 225, 35)
ORANGE = (255, 125, 20)
RED = (255, 45, 60)
GRAY = (105, 115, 140)
GOLD = (255, 195, 35)

font_large = pygame.font.SysFont(None, 52)
font_medium = pygame.font.SysFont(None, 34)
font_small = pygame.font.SysFont(None, 25)
font_tiny = pygame.font.SysFont(None, 19)


MAX_LEVEL = 3
MAX_LIVES = 3
MAX_ENEMIES = 9
MAX_METEORS = 6
MAX_ENEMY_BULLETS = 70

difficulties = {
    1: {"name": "BASICO", "color": GREEN,
        "enemy_speed": (3, 4), "spawn": 0.014, "shoot": 0.004,
        "meteor": 0.0, "kills": 12,
        "boss_hp": 45, "boss_shot": 850, "boss_laser": 5200},
    2: {"name": "INTERMEDIO", "color": CYAN,
        "enemy_speed": (5, 7), "spawn": 0.020, "shoot": 0.008,
        "meteor": 0.0, "kills": 15,
        "boss_hp": 65, "boss_shot": 750, "boss_laser": 4200},
    3: {"name": "DIFICIL", "color": RED,
        "enemy_speed": (5, 7), "spawn": 0.024, "shoot": 0.012,
        "meteor": 0.016, "kills": 18,
        "boss_hp": 90, "boss_shot": 650, "boss_laser": 3400},
}

difficulty = 1   
level = 1           


all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
meteorites = pygame.sprite.Group()
boss_group = pygame.sprite.GroupSingle()
powerups = pygame.sprite.Group()
effects = pygame.sprite.Group()
lasers = pygame.sprite.Group()


_text_cache = {}


def render_text(font, text, color):
    key = (id(font), text, color)
    surf = _text_cache.get(key)
    if surf is None:
        if len(_text_cache) > 300:
            _text_cache.clear()
        surf = font.render(text, True, color)
        _text_cache[key] = surf
    return surf


_bullet_cache = {}


def bullet_image(color):
    img = _bullet_cache.get(color)
    if img is None:
        img = pygame.Surface((6, 17))
        img.fill(color)
        img = img.convert()
        _bullet_cache[color] = img
    return img


def make_player_image():
    image = pygame.Surface((58, 76), pygame.SRCALPHA)
    pygame.draw.polygon(image, CYAN, [(29, 0), (17, 43), (29, 54), (41, 43)])
    pygame.draw.polygon(image, WHITE, [(29, 5), (26, 40), (29, 47), (32, 40)])
    pygame.draw.polygon(image, GOLD, [(5, 47), (53, 47), (44, 57), (14, 57)])
    pygame.draw.rect(image, PURPLE, (25, 55, 8, 15))
    pygame.draw.rect(image, WHITE, (20, 69, 18, 5))
    return image.convert_alpha()


def make_enemy_image():
    image = pygame.Surface((44, 44), pygame.SRCALPHA)
    pygame.draw.polygon(image, RED, [(22, 0), (2, 32), (22, 25), (42, 32)])
    pygame.draw.circle(image, PINK, (22, 18), 7)
    return image.convert_alpha()


def make_meteor_image():
    image = pygame.Surface((50, 50), pygame.SRCALPHA)
    pygame.draw.circle(image, GRAY, (25, 25), 23)
    pygame.draw.circle(image, (55, 60, 80), (15, 15), 7)
    pygame.draw.circle(image, (55, 60, 80), (34, 32), 6)
    return image.convert_alpha()


def make_boss_image():
    image = pygame.Surface((190, 150), pygame.SRCALPHA)
    body_color = PURPLE
    pygame.draw.ellipse(image, (75, 20, 130), (35, 20, 120, 95))
    pygame.draw.ellipse(image, body_color, (43, 15, 104, 88))
    pygame.draw.ellipse(image, PINK, (65, 43, 60, 38))
    pygame.draw.circle(image, WHITE, (83, 61), 9)
    pygame.draw.circle(image, RED, (107, 61), 9)
    pygame.draw.circle(image, BLACK, (83, 61), 4)
    pygame.draw.circle(image, BLACK, (107, 61), 4)

    tentacle_points = [
        ((48, 83), (20, 105), (12, 135)),
        ((60, 96), (45, 120), (48, 145)),
        ((75, 101), (70, 125), (82, 146)),
        ((88, 102), (95, 125), (112, 145)),
        ((105, 100), (130, 120), (145, 145)),
        ((120, 94), (155, 110), (175, 133)),
        ((137, 82), (166, 94), (185, 112)),
        ((43, 72), (18, 83), (5, 105)),
    ]
    for start, middle, end in tentacle_points:
        pygame.draw.lines(image, body_color, False, [start, middle, end], 9)
        pygame.draw.circle(image, CYAN, end, 4)
    return image.convert_alpha()


def make_powerup_image(kind):
    image = pygame.Surface((38, 38), pygame.SRCALPHA)
    if kind == "vida":
        pygame.draw.circle(image, GREEN, (19, 19), 16)
        pygame.draw.line(image, WHITE, (19, 9), (19, 29), 4)
        pygame.draw.line(image, WHITE, (9, 19), (29, 19), 4)
    elif kind == "escudo":
        pygame.draw.polygon(
            image, CYAN,
            [(19, 2), (35, 10), (30, 29), (19, 36), (8, 29), (3, 10)])
    else:
        pygame.draw.circle(image, GOLD, (19, 19), 16)
        pygame.draw.line(image, WHITE, (19, 6), (19, 32), 4)
        pygame.draw.line(image, WHITE, (6, 19), (32, 19), 4)
    return image.convert_alpha()


PLAYER_IMG = make_player_image()
ENEMY_IMG = make_enemy_image()
METEOR_IMG = make_meteor_image()
BOSS_IMG = make_boss_image()
POWERUP_IMGS = {k: make_powerup_image(k) for k in ("vida", "escudo", "multibala")}


def make_background():
    """Fondo estatico: se dibuja una sola vez y luego solo se copia."""
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill(BLACK)
    for i in range(4):
        pygame.draw.circle(surf, (12, 8, 35), (WIDTH // 2, HEIGHT // 2),
                           100 + i * 65, 1)
    pygame.draw.polygon(surf, (12, 28, 60),
                        [(300, 180), (280, 390), (300, 430), (320, 390)])
    pygame.draw.line(surf, (18, 35, 75), (245, 415), (355, 415), 10)
    return surf.convert()


BACKGROUND = make_background()



class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.speed = random.uniform(0.5, 2.5)
        self.size = random.randint(1, 3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        pygame.draw.circle(surface, (70, 95, 150),
                           (int(self.x), int(self.y)), self.size)



class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, color=ORANGE, amount=35):
        super().__init__()
        self.particles = []
        for _ in range(amount):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.5, 6)
            self.particles.append([
                float(x), float(y),
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                random.randint(3, 6)
            ])
        self.life = 35

    def update(self):
        for particle in self.particles:
            particle[0] += particle[2]
            particle[1] += particle[3]
            particle[4] = max(1, particle[4] - 0.12)
        self.life -= 1
        if self.life <= 0:
            self.kill()

    def draw(self, surface):
        for x, y, vx, vy, radius in self.particles:
            pygame.draw.circle(surface, ORANGE, (int(x), int(y)),
                               max(1, int(radius)))
            pygame.draw.circle(surface, YELLOW, (int(x), int(y)),
                               max(1, int(radius / 2)))



class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 90))
        self.hitbox = self.rect.inflate(-30, -36)   # zona real de impacto

        self.speed = 7
        self.lives = 3
        self.shoot_delay = 250
        self.last_shot = 0

        self.invulnerable_until = 0
        self.shield_until = 0
        self.multibullet_until = 0

        
        self.auto = False
        self.target_x = self.rect.centerx

        
        self.mouse_active = False

    def update(self):
        if self.auto:
            dx = self.target_x - self.rect.centerx
            self.rect.x += max(-self.speed, min(self.speed, dx))
            dy = (HEIGHT - 90) - self.rect.centery
            self.rect.y += max(-3, min(3, dy))
            self.shoot()
        else:
            keys = pygame.key.get_pressed()
            if (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT]
                    or keys[pygame.K_d] or keys[pygame.K_UP] or keys[pygame.K_w]
                    or keys[pygame.K_DOWN] or keys[pygame.K_s]):
                self.mouse_active = False

            if self.mouse_active:
                mx, my = pygame.mouse.get_pos()
                self.rect.x += max(-14, min(14, mx - self.rect.centerx))
                self.rect.y += max(-14, min(14, my - self.rect.centery))
            else:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.rect.x -= self.speed
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.rect.x += self.speed
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.rect.y -= self.speed
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.rect.y += self.speed

            if keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
                self.shoot()

        self.rect.clamp_ip(screen.get_rect())
        self.hitbox.center = self.rect.center

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            offsets = [-18, 0, 18] if now < self.multibullet_until else [0]
            for offset in offsets:
                bullet = Bullet(self.rect.centerx + offset, self.rect.top,
                                -14, YELLOW)
                bullet.add(all_sprites, player_bullets)

    def draw_effects(self, surface):
        now = pygame.time.get_ticks()
        if now < self.shield_until:
            pygame.draw.circle(surface, CYAN, self.rect.center, 43, 3)
        if now < self.multibullet_until:
            pygame.draw.circle(surface, GOLD, self.rect.center, 48, 2)



class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = ENEMY_IMG
        self.rect = self.image.get_rect(
            center=(random.randint(25, WIDTH - 25), -40))

        config = difficulties[level]
        self.speed = random.randint(*config["enemy_speed"])
        self.direction = random.choice([-1, 0, 1])
        self.shoot_chance = config["shoot"]

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.direction

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1

        if self.rect.top > HEIGHT:
            self.kill()
            return

        if (random.random() < self.shoot_chance
                and len(enemy_bullets) < MAX_ENEMY_BULLETS):
            bullet = Bullet(self.rect.centerx, self.rect.bottom,
                            random.randint(5, 9), RED)
            bullet.add(all_sprites, enemy_bullets)



class Meteorite(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = METEOR_IMG
        self.rect = self.image.get_rect(
            center=(random.randint(30, WIDTH - 30), -50))
        self.speed_y = random.randint(4, 9)
        self.speed_x = random.choice([-2, -1, 1, 2])

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if (self.rect.top > HEIGHT or self.rect.left > WIDTH
                or self.rect.right < 0):
            self.kill()



class Laser(pygame.sprite.Sprite):
    def __init__(self, x, start_y):
        super().__init__()
        self.x = x
        self.start_y = start_y
        self.image = pygame.Surface((1, 1), pygame.SRCALPHA)

        self.warning_until = pygame.time.get_ticks() + 650
        self.end_until = self.warning_until + 500

        self.rect = pygame.Rect(x - 13, start_y, 26, HEIGHT - start_y)

    def update(self):
        if pygame.time.get_ticks() > self.end_until:
            self.kill()

    def is_damaging(self):
        return pygame.time.get_ticks() >= self.warning_until

    def draw(self, surface):
        if pygame.time.get_ticks() < self.warning_until:
            pygame.draw.line(surface, (255, 100, 100),
                             (self.x, self.start_y), (self.x, HEIGHT), 3)
        else:
            pygame.draw.line(surface, RED,
                             (self.x, self.start_y), (self.x, HEIGHT), 24)
            pygame.draw.line(surface, WHITE,
                             (self.x, self.start_y), (self.x, HEIGHT), 5)



class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = BOSS_IMG
        self.rect = self.image.get_rect(center=(WIDTH // 2, -120))

        config = difficulties[level]
        self.cfg = config
        self.max_hp = config["boss_hp"]
        self.hp = self.max_hp

        self.speed = 3
        self.direction = 1
        self.vx = 0
        self.vy = 2

        now = pygame.time.get_ticks()
        self.last_shot = now
        self.last_laser = now
        self.fury = False

    def update(self):
        now = pygame.time.get_ticks()

        if self.rect.y < 105:
            self.rect.y += 2
            self.vx, self.vy = 0, 2
            return

        self.vy = 0
        self.fury = self.hp <= self.max_hp // 2

        speed = self.speed + (2 if self.fury else 0)
        self.vx = speed * self.direction
        self.rect.x += self.vx
        if self.rect.right >= WIDTH or self.rect.left <= 0:
            self.direction *= -1

        
        shot_delay = self.cfg["boss_shot"] * (0.5 if self.fury else 1)
        if now - self.last_shot > shot_delay:
            self.last_shot = now
            spread = [-60, -30, 0, 30, 60] if self.fury else [-40, 0, 40]
            for offset in spread:
                bullet = Bullet(self.rect.centerx + offset,
                                self.rect.bottom - 15,
                                8 if not self.fury else 10, RED,
                                vx=offset / 30)
                bullet.add(all_sprites, enemy_bullets)

       
        laser_delay = self.cfg["boss_laser"] * (0.66 if self.fury else 1)
        if now - self.last_laser > laser_delay:
            self.last_laser = now
            laser = Laser(self.rect.centerx, self.rect.bottom - 5)
            laser.add(all_sprites, lasers)



class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed, color, vx=0.0):
        super().__init__()
        self.image = bullet_image(color)
        self.rect = self.image.get_rect(center=(x, y))
        self.fx = float(self.rect.x)
        self.fy = float(self.rect.y)
        self.vx = vx
        self.vy = speed

    def update(self):
        self.fx += self.vx
        self.fy += self.vy
        self.rect.x = int(self.fx)
        self.rect.y = int(self.fy)
        if (self.rect.bottom < 0 or self.rect.top > HEIGHT
                or self.rect.right < 0 or self.rect.left > WIDTH):
            self.kill()



class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.kind = kind
        self.image = POWERUP_IMGS[kind]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()




CELL = 15
COLS = WIDTH // CELL               
COL_MIN, COL_MAX = 2, COLS - 3     
STEPS = 8                           
STEP_FRAMES = 5                     
STEP_MS = STEP_FRAMES * 1000 / FPS
MAX_MOVE = 2                        
MOVE_COST = 0.6
GOAL_W = 0.02
HARD = 1000.0
INF = 1e9
HIT_HW = 18                        
PAD = 8                             
LOOK_FRAMES = STEPS * STEP_FRAMES


def collect_obstacles():
    obs = []
    for e in enemies:
        obs.append((e.rect, e.direction, e.speed))
    for m in meteorites:
        obs.append((m.rect, m.speed_x, m.speed_y))
    for b in enemy_bullets:
        obs.append((b.rect, b.vx, b.vy))
    boss = boss_group.sprite
    if boss:
        obs.append((boss.rect, boss.vx, boss.vy))
    return obs


def build_danger(px, py, obstacles, laser_list, now):
   
    top, bot = py - 32, py + 32
    danger = [[0.0] * COLS for _ in range(STEPS + 1)]

    for rect, vx, vy in obstacles:
        # descarta lo que no puede alcanzar la franja de la nave
        if vy >= 0 and rect.top > bot:
            continue
        if rect.bottom + max(vy, 0) * LOOK_FRAMES < top:
            continue
        w, h = rect.width, rect.height
        for t in range(1, STEPS + 1):
            f0 = (t - 1) * STEP_FRAMES
            f1 = t * STEP_FRAMES
            ya, yb = rect.top + vy * f0, rect.top + vy * f1
            if (min(ya, yb) > bot) or (max(ya, yb) + h < top):
                continue
            xa, xb = rect.left + vx * f0, rect.left + vx * f1
            xl = min(xa, xb) - HIT_HW - PAD
            xr = max(xa, xb) + w + HIT_HW + PAD
            c0 = max(COL_MIN, math.ceil((xl - CELL / 2) / CELL))
            c1 = min(COL_MAX, int((xr - CELL / 2) // CELL))
            row = danger[t]
            for c in range(c0, c1 + 1):
                row[c] = HARD

    for lz in laser_list:
        xl = lz.x - 13 - HIT_HW - PAD
        xr = lz.x + 13 + HIT_HW + PAD
        c0 = max(COL_MIN, math.ceil((xl - CELL / 2) / CELL))
        c1 = min(COL_MAX, int((xr - CELL / 2) // CELL))
        for t in range(1, STEPS + 1):
            if now + t * STEP_MS <= lz.end_until:
                row = danger[t]
                for c in range(c0, c1 + 1):
                    row[c] = HARD
    return danger


def plan_route(px, py, obstacles, laser_list, now, goal_x):
    
    danger = build_danger(px, py, obstacles, laser_list, now)
    start = min(COL_MAX, max(COL_MIN, int(px // CELL)))
    prev = [INF] * COLS
    prev[start] = 0.0
    parents = [None] * (STEPS + 1)

    for t in range(1, STEPS + 1):
        cur = [INF] * COLS
        par = [0] * COLS
        drow = danger[t]
        for c in range(COL_MIN, COL_MAX + 1):
            best, bp = INF, c
            lo = c - MAX_MOVE if c - MAX_MOVE > COL_MIN else COL_MIN
            hi = c + MAX_MOVE if c + MAX_MOVE < COL_MAX else COL_MAX
            for p in range(lo, hi + 1):
                v = prev[p] + abs(p - c) * MOVE_COST
                if v < best:
                    best, bp = v, p
            if best < INF:
                cur[c] = best + drow[c]
                par[c] = bp
        parents[t] = par
        prev = cur

    
    best_c, best_v = start, INF
    for c in range(COL_MIN, COL_MAX + 1):
        v = prev[c] + abs(c * CELL + CELL / 2 - goal_x) * GOAL_W
        if v < best_v:
            best_v, best_c = v, c

    path = [0] * (STEPS + 1)
    c = best_c
    for t in range(STEPS, 0, -1):
        path[t] = c
        c = parents[t][c]
    return path[1:]


def choose_goal_x(player):
    
    boss = boss_group.sprite
    if boss:
        return boss.rect.centerx
    best, best_y = WIDTH / 2, -1
    for e in enemies:
        if e.rect.bottom < player.rect.top and e.rect.centery > best_y:
            best, best_y = e.rect.centerx, e.rect.centery
    return best



power_message = ""
power_message_until = 0


def show_power_message(name):
    global power_message, power_message_until
    power_message = name
    power_message_until = pygame.time.get_ticks() + 1500



def drop_reward(x, y, boss=False):
    if boss:
        rewards = ["vida", "escudo", "multibala"]
        count = 2
    else:
        chance = min(0.22 + level * 0.025, 0.55)
        if random.random() > chance:
            return
        rewards = ["escudo", "multibala"]
        if level >= 2:
            rewards.append("vida")
        count = 1

    for _ in range(count):
        kind = random.choice(rewards)
        reward = PowerUp(x + random.randint(-25, 25),
                         y + random.randint(-15, 15), kind)
        reward.add(all_sprites, powerups)



def draw_box(x, y, w, h, color, text, selected=False):
    pygame.draw.rect(screen, (12, 12, 30), (x, y, w, h), border_radius=9)
    pygame.draw.rect(screen, color, (x, y, w, h),
                     3 if selected else 1, border_radius=9)
    label = render_text(font_small, text, color)
    screen.blit(label, label.get_rect(center=(x + w // 2, y + h // 2)))



def draw_background(stars, move=True):
    screen.blit(BACKGROUND, (0, 0))
    for star in stars:
        if move:
            star.update()
        star.draw(screen)



def draw_menu(stars):
    draw_background(stars)

    title = render_text(font_large, "DEFENSOR GALACTICO", CYAN)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 245)))

    subtitle = render_text(font_small, "SELECCIONA TU DIFICULTAD", WHITE)
    screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 310)))

    positions = [355, 415, 475]
    for number in range(1, MAX_LEVEL + 1):
        config = difficulties[number]
        draw_box(100, positions[number - 1], 400, 45, config["color"],
                 f"{number} - {config['name']}", difficulty == number)

    draw_box(150, 610, 300, 48, GREEN, "ENTER - COMENZAR", True)

    controls = render_text(
        font_tiny,
        "Mover: FLECHAS / WASD / MOUSE     Disparar: ESPACIO / CLIC     Pausa: ESC", WHITE)
    screen.blit(controls, controls.get_rect(center=(WIDTH // 2, 700)))

    extra = render_text(
        font_tiny, "T: autopiloto (ruta dinamica)     F: tiempo por fotograma",
        GRAY)
    screen.blit(extra, extra.get_rect(center=(WIDTH // 2, 725)))



def draw_hud(player, score, level, boss_active, boss_group, autopilot):
    config = difficulties[level]
    pygame.draw.rect(screen, (8, 8, 27), (5, 5, 590, 82), border_radius=9)
    pygame.draw.rect(screen, config["color"], (5, 5, 590, 82), 2,
                     border_radius=9)

    screen.blit(render_text(font_small, "VIDAS:", WHITE), (18, 14))

    for i in range(player.lives):
        x = 88 + i * 27
        y = 24
        pygame.draw.circle(screen, RED, (x + 6, y + 5), 6)
        pygame.draw.circle(screen, RED, (x + 16, y + 5), 6)
        pygame.draw.polygon(screen, RED,
                            [(x, y + 7), (x + 22, y + 7), (x + 11, y + 21)])

    labels = [f"PUNTOS: {score}", f"NIVEL: {level}"]
    for i, value in enumerate(labels):
        screen.blit(render_text(font_small, value, WHITE), (208 + i * 190, 14))

    
    for i in range(1, MAX_LEVEL + 1):
        color = GOLD if i <= level else GRAY
        pygame.draw.rect(screen, color, (20 + (i - 1) * 34, 49, 26, 12),
                         border_radius=3)

    now = pygame.time.get_ticks()
    statuses = []
    if autopilot:
        statuses.append("AUTOPILOTO")
    if now < player.shield_until:
        statuses.append("ESCUDO ACTIVO")
    if now < player.multibullet_until:
        statuses.append("MULTIBALA ACTIVA")

    status = " | ".join(statuses) if statuses else "PODERES: ninguno"
    screen.blit(render_text(font_tiny, status, CYAN if statuses else GRAY),
                (220, 48))

    if boss_active and boss_group.sprite:
        boss = boss_group.sprite
        pygame.draw.rect(screen, RED, (WIDTH - 180, 96, 160, 12))
        pygame.draw.rect(screen, GREEN,
                         (WIDTH - 180, 96,
                          max(0, 160 * boss.hp / boss.max_hp), 12))
        if boss.fury:
            screen.blit(render_text(font_tiny, "MODO FURIA", ORANGE),
                        (WIDTH - 180, 112))



def reset_game():
    global player, stars, score, level, kills, boss_active
    global power_message, power_message_until, autopilot, route

    for group in (all_sprites, enemies, player_bullets, enemy_bullets,
                  meteorites, boss_group, powerups, effects, lasers):
        group.empty()

    player = Player()
    all_sprites.add(player)

    stars = [Star() for _ in range(100)]

    score = 0
    level = difficulty
    kills = 0
    boss_active = False
    autopilot = False
    route = []

    power_message = ""
    power_message_until = 0


def draw_text(text, font, color, y):
    label = render_text(font, text, color)
    screen.blit(label, label.get_rect(center=(WIDTH // 2, y)))


def draw_world(draw_player=True):
    
    meteorites.draw(screen)
    enemies.draw(screen)
    boss_group.draw(screen)
    for laser in lasers:
        laser.draw(screen)
    enemy_bullets.draw(screen)
    player_bullets.draw(screen)
    powerups.draw(screen)
    for effect in effects:
        effect.draw(screen)


def hit_player(p, s):
    return p.hitbox.colliderect(s.rect)


async def main():
    global difficulty, score, level, kills, boss_active
    global power_message, power_message_until, autopilot, route

    game_state = "MENU"
    end_state = "GAME_OVER"
    running = True
    show_perf = False
    frame_ms = 0.0
    plan_ms = 0.0
    frame_count = 0

    menu_stars = [Star() for _ in range(100)]

    reset_game()
    game_over_time = 0

    while running:
        clock.tick(FPS)
        t_frame = time.perf_counter()
        now = pygame.time.get_ticks()
        frame_count += 1

        # MUSICA: tema según estado y se detiene en pausa
        if game_state in ("PLAYING", "PAUSED", "EXPLODING"):
            AUDIO.tema("boss" if boss_active else "battle")
        else:
            AUDIO.tema("menu")
        if AUDIO.ok:
            if game_state == "PAUSED": AUDIO.canal.pause()
            else: AUDIO.canal.unpause()

       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if (event.type == pygame.MOUSEMOTION
                    or event.type == pygame.MOUSEBUTTONDOWN):
                player.mouse_active = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    AUDIO.alternar()
                if event.key == pygame.K_f:
                    show_perf = not show_perf

                if game_state == "MENU":
                    if event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                        difficulty = int(event.unicode)
                    elif event.key == pygame.K_RETURN:
                        reset_game()
                        game_state = "PLAYING"
                        show_power_message(
                            f"NIVEL {level} - {difficulties[level]['name']}")

                elif game_state == "PLAYING":
                    if event.key == pygame.K_ESCAPE:
                        game_state = "PAUSED"
                    elif event.key == pygame.K_t:
                        autopilot = not autopilot
                        player.auto = autopilot
                        route = []

                elif game_state == "PAUSED" and event.key == pygame.K_ESCAPE:
                    game_state = "PLAYING"

                elif (game_state in ("GAME_OVER", "VICTORY")
                      and event.key == pygame.K_RETURN):
                    game_state = "MENU"

        
        if game_state == "MENU":
            draw_menu(menu_stars)

        # PARTIDA
        elif game_state == "PLAYING":
            config = difficulties[level]

            # GENERAR JEFE O ENEMIGOS
            if not boss_active:
                if kills >= config["kills"]:
                    boss = Boss()
                    boss.add(all_sprites, boss_group)
                    boss_active = True
                    show_power_message("JEFE FINAL")
                else:
                    if (random.random() < config["spawn"]
                            and len(enemies) < MAX_ENEMIES):
                        Enemy().add(all_sprites, enemies)

                    if (config["meteor"] and random.random() < config["meteor"]
                            and len(meteorites) < MAX_METEORS):
                        Meteorite().add(all_sprites, meteorites)

            
            if autopilot and frame_count % 2 == 0:
                t_plan = time.perf_counter()
                route = plan_route(
                    player.rect.centerx, player.rect.centery,
                    collect_obstacles(), lasers, now,
                    choose_goal_x(player))
                player.target_x = route[0] * CELL + CELL / 2
                plan_ms = (time.perf_counter() - t_plan) * 1000

           
            all_sprites.update()
            effects.update()

          
            hits = pygame.sprite.groupcollide(enemies, player_bullets,
                                              True, True)
            for enemy in hits:
                score += 1
                kills += 1
                drop_reward(enemy.rect.centerx, enemy.rect.centery)

            
            if boss_active and boss_group.sprite:
                boss = boss_group.sprite
                boss_hits = pygame.sprite.spritecollide(
                    boss, player_bullets, True)
                boss.hp -= len(boss_hits)

                if boss.hp <= 0:
                    x, y = boss.rect.center
                    effects.add(Explosion(x, y, PURPLE, 55))
                    boss.kill()
                    boss_active = False
                    score += 10
                    enemy_bullets.empty()
                    for laser in lasers:
                        laser.kill()
                    drop_reward(x, y, True)

                    if level >= MAX_LEVEL:
                        end_state = "VICTORY"
                        game_state = "EXPLODING"
                        game_over_time = now + 1500
                    else:
                        level += 1
                        kills = 0
                        show_power_message(
                            f"NIVEL {level} - {difficulties[level]['name']}")

           
            for reward in pygame.sprite.spritecollide(
                    player, powerups, True, hit_player):
                if reward.kind == "vida":
                    player.lives = min(player.lives + 1, MAX_LIVES)
                    show_power_message("VIDA EXTRA +1")
                elif reward.kind == "escudo":
                    player.shield_until = now + 8000
                    show_power_message("ESCUDO 8 SEGUNDOS")
                elif reward.kind == "multibala":
                    player.multibullet_until = now + 10000
                    show_power_message("MULTIBALA 10 SEGUNDOS")

            
            damaged = (
                bool(pygame.sprite.spritecollide(
                    player, enemies, True, hit_player)) or
                bool(pygame.sprite.spritecollide(
                    player, enemy_bullets, True, hit_player)) or
                bool(pygame.sprite.spritecollide(
                    player, meteorites, True, hit_player))
            )

            if (not damaged and boss_active
                    and boss_group.sprite
                    and player.hitbox.colliderect(boss_group.sprite.rect)):
                damaged = True

            if not damaged:
                for laser in lasers:
                    if (laser.is_damaging()
                            and laser.rect.colliderect(player.hitbox)):
                        damaged = True
                        break

            
            if damaged and now >= player.invulnerable_until:
                if now < player.shield_until:
                    player.shield_until = 0
                    player.invulnerable_until = now + 500
                    show_power_message("ESCUDO ABSORBIO EL GOLPE")
                else:
                    player.lives -= 1
                    player.invulnerable_until = now + 1500
                    show_power_message("VIDA PERDIDA")

                if player.lives <= 0:
                    effects.add(Explosion(player.rect.centerx,
                                          player.rect.centery, CYAN, 65))
                    player.kill()
                    end_state = "GAME_OVER"
                    game_state = "EXPLODING"
                    game_over_time = now + 1100

            
            draw_background(stars)
            draw_world()

            
            if autopilot and route and player.alive():
                pts = [(player.rect.centerx, player.rect.top - 8)]
                for i, col in enumerate(route):
                    pts.append((col * CELL + CELL // 2,
                                player.rect.top - 8 - (i + 1) * 12))
                pygame.draw.lines(screen, (0, 150, 170), False, pts, 2)
                for p in pts[1:]:
                    pygame.draw.circle(screen, CYAN, p, 3)

            
            if player.alive():
                if (now >= player.invulnerable_until
                        or (now // 120) % 2 == 0):
                    screen.blit(player.image, player.rect)
                player.draw_effects(screen)

            draw_hud(player, score, level, boss_active, boss_group, autopilot)

            if now < power_message_until:
                draw_text(power_message, font_small, GOLD, 145)

       
        elif game_state == "EXPLODING":
            effects.update()
            for group in (enemies, enemy_bullets, meteorites):
                group.update()

            draw_background(stars)
            draw_world()
            if player.alive():
                screen.blit(player.image, player.rect)

            if end_state == "VICTORY":
                draw_text("JEFE FINAL DESTRUIDO", font_medium, GREEN, 340)
            else:
                draw_text("NAVE DESTRUIDA", font_medium, ORANGE, 340)

            if now >= game_over_time:
                game_state = end_state

        elif game_state == "PAUSED":
            draw_background(stars, move=False)
            draw_world()
            if player.alive():
                screen.blit(player.image, player.rect)
            draw_text("JUEGO EN PAUSA", font_large, GOLD, 340)
            draw_text("Presiona ESC para continuar", font_small, WHITE, 405)

        
        elif game_state == "GAME_OVER":
            draw_background(menu_stars)
            draw_text("GAME OVER", font_large, RED, 300)
            draw_text(f"PUNTUACION FINAL: {score}", font_medium, WHITE, 370)
            draw_text(f"NIVEL ALCANZADO: {level}", font_small, CYAN, 420)
            draw_box(90, 500, 420, 50, GREEN, "ENTER - VOLVER AL MENU", True)

        
        elif game_state == "VICTORY":
            draw_background(menu_stars)
            draw_text("MISION CUMPLIDA", font_large, GREEN, 300)
            draw_text(f"PUNTUACION FINAL: {score}", font_medium, WHITE, 370)
            draw_text("LOS 3 NIVELES COMPLETADOS", font_small, CYAN, 420)
            draw_box(90, 500, 420, 50, GREEN, "ENTER - VOLVER AL MENU", True)

        
        if show_perf:
            frame_ms = frame_ms * 0.9 + (
                (time.perf_counter() - t_frame) * 1000) * 0.1
            ok = frame_ms < FRAME_BUDGET_MS
            text = (f"FOTOGRAMA {frame_ms:.2f} ms / {FRAME_BUDGET_MS:.1f} ms"
                    f"   RUTA {plan_ms:.2f} ms   FPS {clock.get_fps():.0f}")
            screen.blit(render_text(font_tiny, text, GREEN if ok else RED),
                        (8, HEIGHT - 20))

        pygame.display.flip()

        await asyncio.sleep(0)

    pygame.quit()


asyncio.run(main())
