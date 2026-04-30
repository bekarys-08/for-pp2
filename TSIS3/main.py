"""
TSIS 3: Racer Game — Advanced Driving, Leaderboard & Power-Ups
Author: TSIS 3 implementation
"""

import pygame, sys, random, time, json, os
from pygame.locals import *
from datetime import datetime

# ─── Init ────────────────────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

FPS         = 60
clock       = pygame.time.Clock()
SW, SH      = 400, 600
screen      = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Racer — TSIS 3")

ASSET_DIR   = os.path.join(os.path.dirname(__file__), "assets")
LB_FILE     = os.path.join(os.path.dirname(__file__), "leaderboard.json")
SET_FILE    = os.path.join(os.path.dirname(__file__), "settings.json")

# ─── Colors ───────────────────────────────────────────────────────────────────
WHITE   = (255, 255, 255)
BLACK   = (0,   0,   0)
RED     = (220, 30,  30)
GREEN   = (30,  200, 50)
BLUE    = (30,  80,  220)
YELLOW  = (255, 220, 0)
ORANGE  = (255, 140, 0)
GRAY    = (180, 180, 180)
DGRAY   = (80,  80,  80)
LBLUE   = (160, 200, 255)
LGREEN  = (160, 255, 180)
NITRO_C = (0,   200, 255)
SHIELD_C= (255, 215, 0)
REPAIR_C= (0,   220, 100)
OIL_C   = (40,  40,  80)
ROAD_C  = (50,  50,  55)
LANE_C  = (200, 200, 60)

CAR_COLORS = {
    "Blue":   BLUE,
    "Red":    RED,
    "Green":  GREEN,
    "Yellow": YELLOW,
    "Orange": ORANGE,
}

# ─── Fonts ────────────────────────────────────────────────────────────────────
f_big   = pygame.font.SysFont("Verdana", 52, bold=True)
f_med   = pygame.font.SysFont("Verdana", 26, bold=True)
f_sm    = pygame.font.SysFont("Verdana", 17)
f_xs    = pygame.font.SysFont("Verdana", 13)

# ─── Asset loaders ────────────────────────────────────────────────────────────
def load_img(name, size=None):
    path = os.path.join(ASSET_DIR, name)
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception:
        surf = pygame.Surface(size or (40, 60), pygame.SRCALPHA)
        surf.fill((150, 0, 200, 200))
        return surf

def load_sound(name):
    path = os.path.join(ASSET_DIR, name)
    try:
        return pygame.mixer.Sound(path)
    except Exception:
        return None

# Pre-load assets
img_bg      = load_img("AnimatedStreet.png", (SW, SH))
img_player  = load_img("Player.png",  (40, 70))
img_enemy   = load_img("Enemy.png",   (40, 60))
img_coin_raw= load_img("coin.png",    (30, 30))
snd_crash   = load_sound("crash.wav")
snd_bg_path = os.path.join(ASSET_DIR, "background.wav")

# ─── Persistence ─────────────────────────────────────────────────────────────
def load_json(path, default):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_settings():
    d = load_json(SET_FILE, {})
    return {
        "sound":      d.get("sound", True),
        "car_color":  d.get("car_color", "Blue"),
        "difficulty": d.get("difficulty", "Normal"),
    }

def save_settings(s):
    save_json(SET_FILE, s)

def load_lb():
    data = load_json(LB_FILE, [])
    if not isinstance(data, list):
        return []
    return data

def save_lb(entries):
    save_json(LB_FILE, entries[:10])

def add_lb_entry(name, score, distance, coins):
    entries = load_lb()
    entries.append({
        "name":     name,
        "score":    score,
        "distance": distance,
        "coins":    coins,
        "date":     datetime.now().strftime("%Y-%m-%d"),
    })
    entries.sort(key=lambda e: e["score"], reverse=True)
    save_lb(entries)

# ─── UI helpers ───────────────────────────────────────────────────────────────
def txt(surface, text, font, color, cx, y):
    s = font.render(text, True, color)
    surface.blit(s, (cx - s.get_width()//2, y))

def button(surface, label, rect, hover=False, font=f_sm):
    col  = (100, 140, 220) if hover else (70, 100, 180)
    bord = WHITE if hover else LBLUE
    pygame.draw.rect(surface, col,  rect, border_radius=10)
    pygame.draw.rect(surface, bord, rect, 2, border_radius=10)
    s = font.render(label, True, WHITE)
    surface.blit(s, (rect.centerx - s.get_width()//2,
                     rect.centery - s.get_height()//2))

def mouse_on(rect):
    return rect.collidepoint(pygame.mouse.get_pos())

# ─── Draw a simple player/enemy car surface ───────────────────────────────────
def colorize_player(base_img, color):
    surf = base_img.copy()
    overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    overlay.fill((*color, 120))
    surf.blit(overlay, (0, 0))
    return surf

# ─── Lanes ───────────────────────────────────────────────────────────────────
ROAD_LEFT  = 30
ROAD_RIGHT = SW - 30
NUM_LANES  = 4
LANE_W     = (ROAD_RIGHT - ROAD_LEFT) // NUM_LANES

def lane_cx(lane):          # lane: 0-3
    return ROAD_LEFT + lane * LANE_W + LANE_W // 2

# ─── Difficulty config ────────────────────────────────────────────────────────
DIFF_CONFIG = {
    "Easy":   {"base_speed": 4,  "enemy_count": 1, "hazard_freq": 0.003, "powerup_freq": 0.007},
    "Normal": {"base_speed": 6,  "enemy_count": 2, "hazard_freq": 0.005, "powerup_freq": 0.005},
    "Hard":   {"base_speed": 9,  "enemy_count": 3, "hazard_freq": 0.008, "powerup_freq": 0.003},
}

# ─── Sprites ──────────────────────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self, color_name):
        super().__init__()
        self.base_image = colorize_player(img_player, CAR_COLORS.get(color_name, BLUE))
        self.image      = self.base_image.copy()
        self.rect       = self.image.get_rect(center=(SW//2, SH - 80))
        self.shield     = False
        self.nitro      = False
        self.shield_flash = 0

    def move(self, speed_mult):
        keys = pygame.key.get_pressed()
        spd  = 6 * speed_mult
        if keys[K_LEFT]  and self.rect.left  > ROAD_LEFT:
            self.rect.x -= int(spd)
        if keys[K_RIGHT] and self.rect.right < ROAD_RIGHT:
            self.rect.x += int(spd)
        if keys[K_UP]    and self.rect.top   > SH // 2:
            self.rect.y -= int(spd * 0.5)
        if keys[K_DOWN]  and self.rect.bottom < SH - 10:
            self.rect.y += int(spd * 0.5)

    def draw(self, surface):
        img = self.base_image.copy()
        if self.shield:
            self.shield_flash = (self.shield_flash + 1) % 30
            if self.shield_flash < 15:
                glow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                pygame.draw.ellipse(glow, (*SHIELD_C, 100), glow.get_rect().inflate(6, 10))
                img.blit(glow, (0, 0))
        self.image = img
        surface.blit(self.image, self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        lane = random.randint(0, NUM_LANES - 1)
        self.image = img_enemy.copy()
        self.rect  = self.image.get_rect(
            center=(lane_cx(lane), random.randint(-200, -60)))
        self.speed = speed + random.uniform(-1, 1)

    def update(self):
        self.rect.y += int(self.speed)
        if self.rect.top > SH + 10:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.weight = random.randint(1, 3)
        size = 18 + self.weight * 8
        self.image = pygame.transform.scale(img_coin_raw, (size, size))
        lane = random.randint(0, NUM_LANES - 1)
        self.rect  = self.image.get_rect(
            center=(lane_cx(lane), random.randint(-300, -40)))
        self.speed = speed

    def update(self):
        self.rect.y += int(self.speed)
        if self.rect.top > SH + 10:
            self.kill()


class Hazard(pygame.sprite.Sprite):
    """Oil spill, pothole, or slow zone."""
    TYPES = ["oil", "pothole", "slowzone", "speedbump"]

    def __init__(self, speed):
        super().__init__()
        self.kind = random.choice(self.TYPES)
        lane = random.randint(0, NUM_LANES - 1)

        w, h = (LANE_W - 10, 20) if self.kind in ("slowzone", "speedbump") else (36, 20)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        if self.kind == "oil":
            pygame.draw.ellipse(self.image, (*OIL_C, 200), self.image.get_rect())
            pygame.draw.ellipse(self.image, (80, 80, 140, 120),
                                self.image.get_rect().inflate(-4, -4))
        elif self.kind == "pothole":
            pygame.draw.ellipse(self.image, (30, 20, 10, 230), self.image.get_rect())
        elif self.kind == "slowzone":
            self.image.fill((255, 80, 0, 160))
            lbl = f_xs.render("SLOW", True, WHITE)
            self.image.blit(lbl, (w//2 - lbl.get_width()//2, 2))
        elif self.kind == "speedbump":
            self.image.fill((80, 80, 80, 200))
            pygame.draw.rect(self.image, (180, 180, 50, 255),
                             pygame.Rect(0, h//2-3, w, 6))

        self.rect  = self.image.get_rect(center=(lane_cx(lane), -30))
        self.speed = speed

    def update(self):
        self.rect.y += int(self.speed)
        if self.rect.top > SH + 10:
            self.kill()

    @property
    def slow(self):
        return self.kind in ("oil", "slowzone")

    @property
    def is_bump(self):
        return self.kind == "speedbump"


class PowerUp(pygame.sprite.Sprite):
    KINDS = ["nitro", "shield", "repair"]
    COLORS = {"nitro": NITRO_C, "shield": SHIELD_C, "repair": REPAIR_C}
    LABELS = {"nitro": "N", "shield": "S", "repair": "R"}

    def __init__(self, speed):
        super().__init__()
        self.kind = random.choice(self.KINDS)
        lane = random.randint(0, NUM_LANES - 1)
        self.image = pygame.Surface((34, 34), pygame.SRCALPHA)
        col = self.COLORS[self.kind]
        pygame.draw.circle(self.image, (*col, 220), (17, 17), 17)
        pygame.draw.circle(self.image, WHITE, (17, 17), 17, 2)
        lbl = f_sm.render(self.LABELS[self.kind], True, BLACK)
        self.image.blit(lbl, (17 - lbl.get_width()//2, 17 - lbl.get_height()//2))
        self.rect  = self.image.get_rect(center=(lane_cx(lane), -40))
        self.speed = speed
        self.born  = time.time()

    def update(self):
        self.rect.y += int(self.speed)
        if self.rect.top > SH + 10 or time.time() - self.born > 8:
            self.kill()


class NitroStrip(pygame.sprite.Sprite):
    """Road event: nitro boost strip."""
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((ROAD_RIGHT - ROAD_LEFT, 14), pygame.SRCALPHA)
        for x in range(0, self.image.get_width(), 20):
            pygame.draw.rect(self.image, (*NITRO_C, 150), (x, 0, 10, 14))
        self.rect  = self.image.get_rect(topleft=(ROAD_LEFT, -20))
        self.speed = speed

    def update(self):
        self.rect.y += int(self.speed)
        if self.rect.top > SH + 10:
            self.kill()


# ─── Background scrolling ─────────────────────────────────────────────────────
bg_y = 0
def draw_bg(speed):
    global bg_y
    bg_y = (bg_y + speed * 0.5) % SH
    screen.blit(img_bg, (0, bg_y - SH))
    screen.blit(img_bg, (0, bg_y))


# ─── HUD ──────────────────────────────────────────────────────────────────────
def draw_hud(score, coins, distance, active_pu, pu_timer, speed, shield, nitro):
    # Semi-transparent top bar
    bar = pygame.Surface((SW, 38), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 140))
    screen.blit(bar, (0, 0))

    screen.blit(f_xs.render(f"Score: {score}", True, WHITE),        (6,  4))
    screen.blit(f_xs.render(f"Coins: {coins}", True, YELLOW),       (6,  20))
    dist_s = f_xs.render(f"Dist: {distance}m", True, LGREEN)
    screen.blit(dist_s, (SW - dist_s.get_width() - 6, 4))
    spd_s  = f_xs.render(f"Spd: {speed:.1f}", True, LBLUE)
    screen.blit(spd_s,  (SW - spd_s.get_width()  - 6, 20))

    # Power-up indicator
    if active_pu:
        remaining = max(0, pu_timer - time.time())
        col = PowerUp.COLORS.get(active_pu, WHITE)
        pu_bar = pygame.Surface((140, 22), pygame.SRCALPHA)
        pu_bar.fill((0, 0, 0, 160))
        screen.blit(pu_bar, (SW//2 - 70, 6))
        lbl = f_xs.render(
            f"{active_pu.upper()}: {remaining:.1f}s" if remaining > 0 else active_pu.upper(),
            True, col)
        screen.blit(lbl, (SW//2 - lbl.get_width()//2, 12))

    # Shield / nitro status dots
    if shield:
        pygame.draw.circle(screen, SHIELD_C, (SW//2 - 10, 50), 7)
    if nitro:
        pygame.draw.circle(screen, NITRO_C,  (SW//2 + 10, 50), 7)


# ─── Screens ──────────────────────────────────────────────────────────────────

# ── Name Entry ────────────────────────────────────────────────────────────────
def screen_name_entry():
    name = ""
    while True:
        screen.fill(DGRAY)
        txt(screen, "RACER — TSIS 3", f_big, YELLOW, SW//2, 60)
        txt(screen, "Enter your name:", f_med, WHITE, SW//2, 180)

        box = pygame.Rect(SW//2 - 100, 225, 200, 42)
        pygame.draw.rect(screen, WHITE, box, border_radius=8)
        pygame.draw.rect(screen, YELLOW, box, 2, border_radius=8)
        n_surf = f_med.render(name + "█", True, BLACK)
        screen.blit(n_surf, (box.x + 8, box.y + 6))

        txt(screen, "Press Enter to start", f_xs, GRAY, SW//2, 290)

        btn_start = pygame.Rect(SW//2 - 70, 330, 140, 42)
        button(screen, "START", btn_start, mouse_on(btn_start), f_sm)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            elif event.type == KEYDOWN:
                if event.key == K_RETURN and name.strip():
                    return name.strip()
                elif event.key == K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode and event.unicode.isprintable() and len(name) < 16:
                    name += event.unicode
            elif event.type == MOUSEBUTTONDOWN and mouse_on(btn_start) and name.strip():
                return name.strip()


# ── Main Menu ─────────────────────────────────────────────────────────────────
def screen_main_menu(settings):
    btns = {
        "Play":        pygame.Rect(SW//2 - 90, 200, 180, 46),
        "Leaderboard": pygame.Rect(SW//2 - 90, 260, 180, 46),
        "Settings":    pygame.Rect(SW//2 - 90, 320, 180, 46),
        "Quit":        pygame.Rect(SW//2 - 90, 380, 180, 46),
    }
    while True:
        screen.fill(ROAD_C)
        screen.blit(img_bg, (0, 0))
        overlay = pygame.Surface((SW, SH), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        txt(screen, "RACER",   f_big, YELLOW, SW//2, 80)
        txt(screen, "TSIS 3",  f_sm,  GRAY,   SW//2, 148)

        for label, rect in btns.items():
            button(screen, label, rect, mouse_on(rect))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                for label, rect in btns.items():
                    if mouse_on(rect):
                        return label.lower()


# ── Settings Screen ───────────────────────────────────────────────────────────
def screen_settings(settings):
    diff_opts   = ["Easy", "Normal", "Hard"]
    color_opts  = list(CAR_COLORS.keys())
    back_btn    = pygame.Rect(SW//2 - 70, SH - 70, 140, 42)

    while True:
        screen.fill(DGRAY)
        txt(screen, "SETTINGS", f_big, YELLOW, SW//2, 30)

        # Sound toggle
        sd_rect = pygame.Rect(SW//2 - 70, 120, 140, 38)
        label   = "Sound: ON" if settings["sound"] else "Sound: OFF"
        button(screen, label, sd_rect, mouse_on(sd_rect))

        # Difficulty selector
        txt(screen, "Difficulty:", f_sm, WHITE, SW//2, 178)
        for i, d in enumerate(diff_opts):
            r = pygame.Rect(SW//2 - 135 + i * 95, 200, 88, 36)
            active = (settings["difficulty"] == d)
            col = (80, 180, 80) if active else (70, 100, 180)
            pygame.draw.rect(screen, col, r, border_radius=8)
            pygame.draw.rect(screen, WHITE if active else LBLUE, r, 2, border_radius=8)
            s = f_xs.render(d, True, WHITE)
            screen.blit(s, (r.centerx - s.get_width()//2, r.centery - s.get_height()//2))

        # Car color selector
        txt(screen, "Car Color:", f_sm, WHITE, SW//2, 258)
        for i, cname in enumerate(color_opts):
            r = pygame.Rect(12 + i * 76, 280, 68, 36)
            active = (settings["car_color"] == cname)
            pygame.draw.rect(screen, CAR_COLORS[cname], r, border_radius=8)
            pygame.draw.rect(screen, WHITE if active else DGRAY, r, 2 if not active else 3, border_radius=8)
            s = f_xs.render(cname, True, WHITE)
            screen.blit(s, (r.centerx - s.get_width()//2, r.centery - s.get_height()//2))

        button(screen, "← Back", back_btn, mouse_on(back_btn))
        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if mouse_on(back_btn):
                    save_settings(settings)
                    return
                if mouse_on(sd_rect):
                    settings["sound"] = not settings["sound"]
                    apply_sound(settings["sound"])
                for i, d in enumerate(diff_opts):
                    r = pygame.Rect(SW//2 - 135 + i * 95, 200, 88, 36)
                    if mouse_on(r):
                        settings["difficulty"] = d
                for i, cname in enumerate(color_opts):
                    r = pygame.Rect(12 + i * 76, 280, 68, 36)
                    if mouse_on(r):
                        settings["car_color"] = cname


# ── Leaderboard Screen ────────────────────────────────────────────────────────
def screen_leaderboard():
    entries  = load_lb()
    back_btn = pygame.Rect(SW//2 - 60, SH - 60, 120, 40)

    while True:
        screen.fill(DGRAY)
        txt(screen, "TOP 10", f_big, YELLOW, SW//2, 18)

        # Headers
        hdrs = [("#", 20), ("Name", 55), ("Score", 195), ("Dist", 285), ("Date", 340)]
        for h, x in hdrs:
            screen.blit(f_xs.render(h, True, GRAY), (x, 72))
        pygame.draw.line(screen, GRAY, (10, 88), (SW - 10, 88), 1)

        for i, e in enumerate(entries[:10]):
            y   = 96 + i * 42
            row = pygame.Surface((SW - 20, 36), pygame.SRCALPHA)
            row.fill((255,255,255,15) if i % 2 == 0 else (0,0,0,0))
            screen.blit(row, (10, y))
            medal = ["🥇","🥈","🥉"][i] if i < 3 else f"{i+1}."
            cols_data = [
                (medal,          20),
                (e.get("name","?")[:10], 55),
                (str(e.get("score", 0)), 195),
                (f"{e.get('distance',0)}m", 285),
                (e.get("date",""), 340),
            ]
            for val, x in cols_data:
                col = [YELLOW, GRAY, (200,200,180)][min(i,2)] if i < 3 else WHITE
                screen.blit(f_xs.render(str(val), True, col), (x, y + 10))

        if not entries:
            txt(screen, "No scores yet!", f_sm, GRAY, SW//2, 200)

        button(screen, "← Back", back_btn, mouse_on(back_btn))
        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            elif event.type == MOUSEBUTTONDOWN and mouse_on(back_btn):
                return
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return


# ── Game Over Screen ──────────────────────────────────────────────────────────
def screen_game_over(score, distance, coins):
    retry_btn = pygame.Rect(SW//2 - 95, 380, 175, 46)
    menu_btn  = pygame.Rect(SW//2 - 95, 440, 175, 46)

    while True:
        screen.fill((30, 0, 0))
        txt(screen, "GAME OVER",  f_big, RED,    SW//2, 60)
        txt(screen, f"Score:    {score}",    f_sm, WHITE,  SW//2, 190)
        txt(screen, f"Distance: {distance}m",f_sm, LGREEN, SW//2, 225)
        txt(screen, f"Coins:    {coins}",    f_sm, YELLOW, SW//2, 260)

        button(screen, "▶ Play Again", retry_btn, mouse_on(retry_btn))
        button(screen, "⬅ Main Menu",  menu_btn,  mouse_on(menu_btn))

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if mouse_on(retry_btn): return "retry"
                if mouse_on(menu_btn):  return "menu"
            elif event.type == KEYDOWN and event.key == K_r:
                return "retry"


# ─── Sound helpers ────────────────────────────────────────────────────────────
def apply_sound(enabled):
    if enabled:
        try:
            pygame.mixer.music.load(snd_bg_path)
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.5)
        except Exception:
            pass
    else:
        pygame.mixer.music.stop()


# ─── Main game session ────────────────────────────────────────────────────────
def run_game(player_name, settings):
    global bg_y
    bg_y = 0

    dc   = DIFF_CONFIG[settings["difficulty"]]
    speed = dc["base_speed"]

    # Player
    player = Player(settings["car_color"])

    # Sprite groups
    enemies    = pygame.sprite.Group()
    coins_g    = pygame.sprite.Group()
    hazards    = pygame.sprite.Group()
    powerups   = pygame.sprite.Group()
    nitro_strips = pygame.sprite.Group()

    def safe_spawn_enemy():
        for _ in range(10):
            e = Enemy(speed)
            if not pygame.sprite.spritecollideany(e, enemies) and \
               abs(e.rect.centerx - player.rect.centerx) > 30:
                enemies.add(e)
                break

    # Spawn initial enemies
    for _ in range(dc["enemy_count"]):
        safe_spawn_enemy()

    # Spawn initial coins
    for _ in range(3):
        coins_g.add(Coin(speed))

    # State
    score       = 0
    coin_score  = 0
    distance    = 0
    active_pu   = None        # "nitro" | "shield" | "repair" | None
    pu_end_time = 0
    slow_mult   = 1.0
    slow_timer  = 0.0
    nitro_mult  = 1.0
    start_time  = time.time()
    last_dist_t = time.time()

    # Enemy spawn timer
    enemy_timer   = time.time()
    enemy_interval= 3.0

    running = True
    while running:
        dt    = clock.tick(FPS) / 1000.0
        now   = time.time()

        # ── Distance & score accumulation
        distance += int(speed * 0.4)
        score     = coin_score * 10 + distance // 8

        # ── Difficulty scaling (every 500 distance)
        level      = distance // 500
        speed      = dc["base_speed"] + level * 0.8
        if active_pu == "nitro":
            speed *= 1.6
        if slow_mult < 1.0:
            if now > slow_timer:
                slow_mult = 1.0
            else:
                speed *= slow_mult

        effective_speed = max(2, speed)

        # ── Spawn enemies on interval
        if now - enemy_timer > max(0.8, enemy_interval - level * 0.2):
            safe_spawn_enemy()
            enemy_timer = now

        # ── Spawn coins
        if len(coins_g) < 4 and random.random() < 0.02:
            coins_g.add(Coin(effective_speed))

        # ── Spawn hazards
        if random.random() < dc["hazard_freq"] * (1 + level * 0.3):
            hazards.add(Hazard(effective_speed))

        # ── Spawn power-ups
        if not active_pu and random.random() < dc["powerup_freq"]:
            powerups.add(PowerUp(effective_speed))

        # ── Spawn nitro strip (road event)
        if random.random() < 0.002:
            nitro_strips.add(NitroStrip(effective_speed))

        # ── Event handling
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit(); sys.exit()
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                return "menu", score, distance, coin_score

        # ── Power-up expiry
        if active_pu and active_pu != "shield" and now > pu_end_time:
            active_pu  = None
            nitro_mult = 1.0

        # ── Move player
        player.move(nitro_mult)
        player.shield = (active_pu == "shield")
        player.nitro  = (active_pu == "nitro")

        # ── Update all sprites
        for grp in (enemies, coins_g, hazards, powerups, nitro_strips):
            grp.update()

        # ── Collision: coins
        hit_coins = pygame.sprite.spritecollide(player, coins_g, True)
        for c in hit_coins:
            old    = coin_score
            coin_score += c.weight
            score   = coin_score * 10 + distance // 8
            if coin_score // 10 > old // 10:
                speed = min(speed + 0.5, dc["base_speed"] + 20)

        # ── Collision: power-ups
        hit_pu = pygame.sprite.spritecollide(player, powerups, True)
        for pu in hit_pu:
            if pu.kind == "nitro":
                active_pu  = "nitro"
                pu_end_time = now + 4
                nitro_mult = 1.6
            elif pu.kind == "shield":
                active_pu  = "shield"
                pu_end_time = now + 999  # until hit
            elif pu.kind == "repair":
                # Repair: clear all hazards near player
                for h in list(hazards):
                    if abs(h.rect.centery - player.rect.centery) < 150:
                        h.kill()
                score += 50

        # ── Collision: hazards
        hit_haz = pygame.sprite.spritecollide(player, hazards, False)
        for h in hit_haz:
            if h.slow:
                slow_mult  = 0.4
                slow_timer = now + 1.5
                h.kill()
            elif h.is_bump:
                slow_mult  = 0.6
                slow_timer = now + 0.6
                h.kill()

        # ── Collision: nitro strips (boost)
        if pygame.sprite.spritecollideany(player, nitro_strips):
            if active_pu != "nitro":
                slow_mult  = 1.5
                slow_timer = now + 0.8

        # ── Collision: enemies → game over
        hit_enemy = pygame.sprite.spritecollideany(player, enemies)
        if hit_enemy:
            if active_pu == "shield":
                hit_enemy.kill()
                active_pu = None   # shield consumed
            else:
                if snd_crash:
                    pygame.mixer.music.stop()
                    snd_crash.play()
                time.sleep(0.4)
                return "gameover", score, distance, coin_score

        # ── Draw
        draw_bg(effective_speed)

        # Lane markers
        for l in range(1, NUM_LANES):
            lx = ROAD_LEFT + l * LANE_W
            pygame.draw.line(screen, (*LANE_C, 80), (lx, 0), (lx, SH), 1)

        # Sprites
        for grp in (nitro_strips, hazards, coins_g, powerups, enemies):
            grp.draw(screen)
        player.draw(screen)

        draw_hud(score, coin_score, distance // 10, active_pu, pu_end_time,
                 effective_speed, player.shield, player.nitro)

        pygame.display.flip()

    return "menu", score, distance, coin_score


# ─── Entry point ──────────────────────────────────────────────────────────────
def main():
    settings    = load_settings()
    apply_sound(settings["sound"])
    player_name = screen_name_entry()

    while True:
        action = screen_main_menu(settings)

        if action == "quit":
            pygame.quit(); sys.exit()
        elif action == "leaderboard":
            screen_leaderboard()
        elif action == "settings":
            screen_settings(settings)
            apply_sound(settings["sound"])
        elif action == "play":
            while True:
                result, score, distance, coins = run_game(player_name, settings)
                if result == "gameover":
                    add_lb_entry(player_name, score, distance // 10, coins)
                    action2 = screen_game_over(score, distance // 10, coins)
                    if action2 == "retry":
                        continue
                    else:
                        break   # → main menu
                else:
                    break       # ESC → main menu

if __name__ == "__main__":
    main()
