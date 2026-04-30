import pygame
import sys
import json
import os
import random
import array
import math

import db
from game import Snake, Food, PoisonFood, PowerUp, make_obstacles, draw_obstacles
from config import *
pygame.mixer.pre_init(22050, -16, 1, 512)
pygame.init()

TOTAL_H = SCREEN_HEIGHT + UI_HEIGHT
screen  = pygame.display.set_mode((SCREEN_WIDTH, TOTAL_H))
pygame.display.set_caption("Snake — TSIS 4")
clock   = pygame.time.Clock()

font       = pygame.font.SysFont("Arial", 20)
font_large = pygame.font.SysFont("Arial", 46, bold=True)
font_small = pygame.font.SysFont("Arial", 14)

def _make_sound(freq: float, duration: float,
                volume: float = 0.40, wave: str = "sine") -> pygame.mixer.Sound:
    sample_rate = 22050
    n_samples   = int(sample_rate * duration)
    fade_len    = int(sample_rate * 0.015)          # 15 ms fade
    buf         = array.array('h')                   # signed 16-bit

    for i in range(n_samples):
        t       = i / sample_rate
        fade    = min(1.0, min(i + 1, n_samples - i) / max(1, fade_len))
        if wave == "square":
            raw = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
        else:
            raw = math.sin(2 * math.pi * freq * t)
        buf.append(int(volume * 32767 * fade * raw))

    return pygame.mixer.Sound(buffer=buf)
try:
    SND_EAT      = _make_sound(660, 0.07, 0.35)           # short high blip
    SND_POISON   = _make_sound(180, 0.28, 0.45, "square") # low buzz
    SND_POWERUP  = _make_sound(880, 0.15, 0.40)           # bright ping
    SND_LEVELUP  = _make_sound(523, 0.22, 0.45)           # C5 chime
    SND_GAMEOVER = _make_sound(150, 0.55, 0.55, "square") # deep drone
    _SOUNDS_OK   = True
except Exception as _e:
    print(f"[Sound] Could not initialise: {_e}")
    _SOUNDS_OK   = False


def play_sound(snd: pygame.mixer.Sound, settings: dict) -> None:
    if settings.get("sound") and _SOUNDS_OK:
        snd.play()

SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")

DEFAULT_SETTINGS: dict = {
    "snake_color": [0, 220, 0],
    "grid":        True,
    "sound":       False,
    "username":    "",
}


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE) as f:
            data = json.load(f)
        for k, v in DEFAULT_SETTINGS.items():
            data.setdefault(k, v)
        return data
    return dict(DEFAULT_SETTINGS)


def save_settings(s: dict) -> None:
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=2)

def draw_btn(rect: pygame.Rect, text: str, active: bool = False) -> None:
    col = (100, 160, 255) if active else (50, 100, 200)
    if rect.collidepoint(pygame.mouse.get_pos()):
        col = (140, 190, 255)
    pygame.draw.rect(screen, col, rect, border_radius=7)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=7)
    lbl = font.render(text, True, WHITE)
    screen.blit(lbl, lbl.get_rect(center=rect.center))


def clicked(rect: pygame.Rect, event: pygame.event.Event) -> bool:
    return (event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and rect.collidepoint(event.pos))


def center_x(text: str, f: pygame.font.Font = None) -> int:
    f = f or font
    return SCREEN_WIDTH // 2 - f.size(text)[0] // 2


def ask_username() -> str:
    buf = ""
    box = pygame.Rect(SCREEN_WIDTH // 2 - 140, TOTAL_H // 2, 280, 44)
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN and buf.strip():
                    return buf.strip()
                elif ev.key == pygame.K_BACKSPACE:
                    buf = buf[:-1]
                elif len(buf) < 20 and ev.unicode.isprintable():
                    buf += ev.unicode

        screen.fill((20, 20, 50))
        lbl = font_large.render("Enter Username", True, YELLOW)
        screen.blit(lbl, (center_x("Enter Username", font_large), 160))
        pygame.draw.rect(screen, WHITE, box, 2, border_radius=6)
        screen.blit(font.render(buf + "|", True, YELLOW), (box.x + 8, box.y + 10))
        hint = font_small.render("Press Enter to confirm", True, GRAY)
        screen.blit(hint, (center_x("Press Enter to confirm", font_small), box.bottom + 12))
        pygame.display.flip()
        clock.tick(FPS)

def main_menu() -> str:
    btn_play  = pygame.Rect(SCREEN_WIDTH // 2 - 90, 220, 180, 48)
    btn_board = pygame.Rect(SCREEN_WIDTH // 2 - 90, 285, 180, 48)
    btn_sett  = pygame.Rect(SCREEN_WIDTH // 2 - 90, 350, 180, 48)
    btn_quit  = pygame.Rect(SCREEN_WIDTH // 2 - 90, 415, 180, 48)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if clicked(btn_play,  ev): return "play"
            if clicked(btn_board, ev): return "leaderboard"
            if clicked(btn_sett,  ev): return "settings"
            if clicked(btn_quit,  ev): pygame.quit(); sys.exit()

        screen.fill((20, 20, 50))
        lbl = font_large.render("SNAKE", True, GREEN)
        screen.blit(lbl, (center_x("SNAKE", font_large), 110))
        sub = font_small.render("TSIS 4", True, GRAY)
        screen.blit(sub, (center_x("TSIS 4", font_small), 170))

        draw_btn(btn_play,  "Play")
        draw_btn(btn_board, "Leaderboard")
        draw_btn(btn_sett,  "Settings")
        draw_btn(btn_quit,  "Quit")
        pygame.display.flip()
        clock.tick(FPS)

def run_game(settings: dict) -> tuple:
    username  = settings["username"]
    col       = tuple(settings["snake_color"])
    show_grid = settings["grid"]

    try:
        best = db.get_personal_best(username)
    except Exception:
        best = 0

    snake     = Snake(color=col)
    food      = Food()
    poison    = PoisonFood()
    powerup   = PowerUp()
    obstacles: set = set()

    def occupied() -> set:
        o = set(snake.body) | obstacles
        if food.pos:    o.add(food.pos)
        if poison.pos:  o.add(poison.pos)
        if powerup.pos: o.add(powerup.pos)
        return o

    food.spawn(occupied())
    poison.spawn(occupied())
    powerup.spawn(occupied())

    score       = 0
    level       = 1
    foods_eaten = 0
    game_over   = False

    move_delay = 150
    last_move  = pygame.time.get_ticks()

    effect_end  = 0        # ms when current timed effect expires
    effect_kind = None     # "speed" | "slow" | "shield" | None
    shield_on   = False

    poison_next = pygame.time.get_ticks() + 5000

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return "menu", score, level
                if not game_over:
                    if ev.key in (pygame.K_UP,    pygame.K_w): snake.change_direction(UP)
                    if ev.key in (pygame.K_DOWN,  pygame.K_s): snake.change_direction(DOWN)
                    if ev.key in (pygame.K_LEFT,  pygame.K_a): snake.change_direction(LEFT)
                    if ev.key in (pygame.K_RIGHT, pygame.K_d): snake.change_direction(RIGHT)

        now = pygame.time.get_ticks()

        if not game_over:
            if effect_kind in ("speed", "slow") and now > effect_end:
                move_delay  = max(50, 150 - (level - 1) * 15)
                effect_kind = None
            if food.expired():
                food.spawn(occupied())
            if poison.pos and poison.expired():
                poison.pos = None
            if powerup.pos and powerup.field_expired():
                powerup.spawn(occupied())

            if poison.pos is None and now >= poison_next:
                poison.spawn(occupied())
                poison_next = now + random.randint(8000, 15000)

            if now - last_move > move_delay:
                snake.move()
                last_move = now

                hit = (snake.check_wall() or
                       snake.check_self() or
                       snake.check_obstacle(obstacles))

                if hit:
                    if shield_on:
                        shield_on   = False
                        effect_kind = None
                        snake.body[0] = snake.body[1]   # push head back
                    else:
                        game_over = True
                        play_sound(SND_GAMEOVER, settings)

                if not game_over and snake.body[0] == food.pos:
                    snake.grow()
                    score       += food.kind["weight"]
                    foods_eaten += 1
                    play_sound(SND_EAT, settings)
                    food.spawn(occupied())

                    if foods_eaten % 4 == 0:
                        level += 1
                        play_sound(SND_LEVELUP, settings)
                        if effect_kind not in ("speed", "slow"):
                            move_delay = max(50, move_delay - 15)
                        obstacles = make_obstacles(level, snake.body)
                        food.spawn(occupied())
                        poison.pos = None
                        powerup.spawn(occupied())
                if not game_over and poison.pos and snake.body[0] == poison.pos:
                    poison.pos = None
                    play_sound(SND_POISON, settings)
                    still_alive = snake.shrink(2)
                    if not still_alive:
                        game_over = True
                        play_sound(SND_GAMEOVER, settings)
                    poison_next = now + random.randint(8000, 15000)

                if not game_over and powerup.pos and snake.body[0] == powerup.pos:
                    k = powerup.kind
                    powerup.pos = None
                    play_sound(SND_POWERUP, settings)
                    if k == "speed":
                        move_delay  = max(30, move_delay - 40)
                        effect_kind = "speed"
                        effect_end  = now + 5000
                    elif k == "slow":
                        move_delay  = move_delay + 60
                        effect_kind = "slow"
                        effect_end  = now + 5000
                    elif k == "shield":
                        shield_on   = True
                        effect_kind = "shield"
                    score += 20
                    powerup.spawn(occupied())

            best = max(best, score)

        screen.fill(BLACK)
        pygame.draw.rect(screen, DARK_GRAY, (0, UI_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT))

        if show_grid:
            for gx in range(0, SCREEN_WIDTH, GRID_SIZE):
                pygame.draw.line(screen, (60, 60, 60), (gx, UI_HEIGHT), (gx, TOTAL_H))
            for gy in range(UI_HEIGHT, TOTAL_H, GRID_SIZE):
                pygame.draw.line(screen, (60, 60, 60), (0, gy), (SCREEN_WIDTH, gy))

        draw_obstacles(screen, obstacles)
        food.draw(screen)
        if poison.pos:  poison.draw(screen)
        if powerup.pos: powerup.draw(screen)
        snake.draw(screen, show_grid)

        pygame.draw.rect(screen, (30, 30, 60), (0, 0, SCREEN_WIDTH, UI_HEIGHT))
        pygame.draw.line(screen, GRAY, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)

        screen.blit(font.render(f"Score: {score}", True, WHITE),  (10, 8))
        screen.blit(font.render(f"Level: {level}", True, YELLOW), (10, 33))
        screen.blit(font_small.render(f"Best: {best}", True, GRAY), (160, 8))

        if effect_kind == "speed":
            secs = max(0, (effect_end - now) // 1000)
            screen.blit(font_small.render(f"SPEED {secs}s", True, ORANGE), (160, 30))
        elif effect_kind == "slow":
            secs = max(0, (effect_end - now) // 1000)
            screen.blit(font_small.render(f"SLOW {secs}s", True, CYAN), (160, 30))
        elif effect_kind == "shield":
            screen.blit(font_small.render("SHIELD", True, PURPLE), (160, 30))

        if food.pos:
            fi = font_small.render(
                f"{food.kind['name']} {food.kind['weight']}pt  "
                f"{int(food.time_frac() * food.kind['life'] // 1000)}s",
                True, food.kind["color"])
            screen.blit(fi, (320, 8))
        if poison.pos:
            screen.blit(font_small.render("POISON on field!", True, DARK_RED), (320, 30))

        if game_over:
            action = _game_over_screen(score, level, best)
            return action, score, level

        pygame.display.flip()
        clock.tick(FPS)


def _game_over_screen(score: int, level: int, best: int) -> str:
    btn_retry = pygame.Rect(SCREEN_WIDTH // 2 - 110, 340, 100, 42)
    btn_menu  = pygame.Rect(SCREEN_WIDTH // 2 + 10,  340, 100, 42)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if clicked(btn_retry, ev): return "retry"
            if clicked(btn_menu,  ev): return "menu"

        overlay = pygame.Surface((SCREEN_WIDTH, TOTAL_H))
        overlay.fill(BLACK)
        overlay.set_alpha(185)
        screen.blit(overlay, (0, 0))

        lbl = font_large.render("GAME OVER", True, RED)
        screen.blit(lbl, (center_x("GAME OVER", font_large), 150))

        for i, (text, col) in enumerate([
            (f"Score: {score}",        WHITE),
            (f"Level: {level}",        YELLOW),
            (f"Personal Best: {best}", GRAY),
        ]):
            rendered = font.render(text, True, col)
            screen.blit(rendered, (center_x(text), 240 + i * 30))

        draw_btn(btn_retry, "Retry")
        draw_btn(btn_menu,  "Menu")
        pygame.display.flip()
        clock.tick(FPS)

def leaderboard_screen() -> None:
    btn_back = pygame.Rect(SCREEN_WIDTH // 2 - 70, TOTAL_H - 55, 140, 38)

    try:
        rows = db.get_top10()
        err  = ""
    except Exception as e:
        rows = []
        err  = str(e)

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if clicked(btn_back, ev): return

        screen.fill((20, 20, 50))
        lbl = font_large.render("TOP 10", True, YELLOW)
        screen.blit(lbl, (center_x("TOP 10", font_large), 25))

        if err:
            screen.blit(font_small.render("DB error: " + err[:50], True, RED), (10, 90))
        else:
            headers = ["#", "Player", "Score", "Level", "Date"]
            col_x   = [10, 45, 210, 305, 360]
            for i, h in enumerate(headers):
                screen.blit(font_small.render(h, True, YELLOW), (col_x[i], 90))
            pygame.draw.line(screen, GRAY, (8, 108), (SCREEN_WIDTH - 8, 108), 1)

            for rank, (uname, sc, lv, dt) in enumerate(rows, 1):
                y   = 115 + (rank - 1) * 36
                col = YELLOW if rank == 1 else WHITE
                for i, val in enumerate([str(rank), uname[:14], str(sc), str(lv), dt]):
                    screen.blit(font_small.render(val, True, col), (col_x[i], y))

        if not rows and not err:
            screen.blit(font.render("No scores yet!", True, GRAY),
                        (center_x("No scores yet!"), 200))

        draw_btn(btn_back, "Back")
        pygame.display.flip()
        clock.tick(FPS)


def settings_screen(settings: dict) -> dict:
    # Compact layout — all rows must fit within TOTAL_H (460 px)
    btn_grid  = pygame.Rect(250,  88, 130, 36)
    btn_sound = pygame.Rect(250, 138, 130, 36)
    btn_color = pygame.Rect(250, 188, 130, 36)
    btn_user  = pygame.Rect(250, 238, 130, 36)
    btn_save  = pygame.Rect(SCREEN_WIDTH // 2 - 70, 298, 140, 40)
    btn_back  = pygame.Rect(SCREEN_WIDTH // 2 - 70, 352, 140, 40)

    color_opts = [
        ("Green",  [0, 220, 0]),
        ("Blue",   [50, 120, 255]),
        ("Yellow", [255, 220, 0]),
        ("Orange", [255, 140, 0]),
    ]
    color_idx = 0
    for i, (_, c) in enumerate(color_opts):
        if c == settings["snake_color"]:
            color_idx = i
            break

    saved_msg = ""
    saved_at  = 0

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if clicked(btn_grid,  ev):
                settings["grid"]  = not settings["grid"]
            if clicked(btn_sound, ev):
                settings["sound"] = not settings["sound"]
            if clicked(btn_color, ev):
                color_idx = (color_idx + 1) % len(color_opts)
                settings["snake_color"] = color_opts[color_idx][1]
            if clicked(btn_user, ev):
                new_name = ask_username()
                if new_name:
                    settings["username"] = new_name

            if clicked(btn_save, ev):
                save_settings(settings)
                saved_msg = "Saved!"
                saved_at  = pygame.time.get_ticks()

            if clicked(btn_back, ev):
                save_settings(settings)
                return settings

        screen.fill((20, 20, 50))
        lbl = font_large.render("Settings", True, YELLOW)
        screen.blit(lbl, (center_x("Settings", font_large), 28))

        labels = [
            ("Grid overlay:", 98),
            ("Sound:",        148),
            ("Snake color:",  198),
            ("Username:",     248),
        ]
        for label, y in labels:
            screen.blit(font.render(label, True, WHITE), (30, y))

        draw_btn(btn_grid,  "ON" if settings["grid"]  else "OFF", settings["grid"])
        draw_btn(btn_sound, "ON" if settings["sound"] else "OFF", settings["sound"])
        draw_btn(btn_color, color_opts[color_idx][0])

        uname_display = (settings.get("username") or "(none)")[:10]
        draw_btn(btn_user, uname_display)

        if saved_msg and pygame.time.get_ticks() - saved_at < 1200:
            screen.blit(font.render(saved_msg, True, GREEN),
                        (center_x(saved_msg), 272))

        draw_btn(btn_save, "Save")
        draw_btn(btn_back, "Back")
        pygame.display.flip()
        clock.tick(FPS)

def main() -> None:
    settings = load_settings()

    try:
        db.setup_schema()
    except Exception as e:
        print(f"[DB] Could not connect: {e}")

    while True:
        action = main_menu()

        if action == "leaderboard":
            leaderboard_screen()

        elif action == "settings":
            settings = settings_screen(settings)

        elif action == "play":
            if not settings.get("username"):
                settings["username"] = ask_username()
                save_settings(settings)

            while True:
                result, score, level = run_game(settings)
                try:
                    db.save_session(settings["username"], score, level)
                except Exception as e:
                    print(f"[DB] Save failed: {e}")
                if result == "menu":
                    break

if __name__ == "__main__":
    main()