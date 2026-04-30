import pygame
import sys
import json
import os
import random

import db
from game import Snake, Food, PoisonFood, PowerUp, make_obstacles, draw_obstacles
from config import *

# Initialize Pygame
pygame.init()
TOTAL_H = SCREEN_HEIGHT + UI_HEIGHT
screen = pygame.display.set_mode((SCREEN_WIDTH, TOTAL_H))
pygame.display.set_caption("Snake — TSIS 4")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont("Arial", 20)
font_large = pygame.font.SysFont("Arial", 46, bold=True)
font_small = pygame.font.SysFont("Arial", 14)

# Settings
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "snake_color": [0, 220, 0],
    "grid": True,
    "sound": False,
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            data = json.load(f)
        for k, v in DEFAULT_SETTINGS.items():
            data.setdefault(k, v)
        return data
    return dict(DEFAULT_SETTINGS)

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def draw_button(rect, text, active=False):
    color = (100, 160, 255) if active else (50, 100, 200)
    if rect.collidepoint(pygame.mouse.get_pos()):
        color = (140, 190, 255)
    pygame.draw.rect(screen, color, rect, border_radius=7)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=7)
    label = font.render(text, True, WHITE)
    screen.blit(label, label.get_rect(center=rect.center))

def button_clicked(rect, event):
    return (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and rect.collidepoint(event.pos))

def center_text(text, font_obj=None):
    font_obj = font_obj or font
    return SCREEN_WIDTH // 2 - font_obj.size(text)[0] // 2

def username_entry_screen():
    """Screen for entering username before game"""
    username = ""
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 140, TOTAL_H // 2 - 30, 280, 50)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif len(username) < 20 and event.unicode.isprintable():
                    username += event.unicode
        
        screen.fill((20, 20, 50))
        
        title = font_large.render("ENTER YOUR NAME", True, YELLOW)
        screen.blit(title, (center_text("ENTER YOUR NAME", font_large), TOTAL_H // 2 - 120))
        
        subtitle = font_small.render("This name will appear on leaderboard", True, GRAY)
        screen.blit(subtitle, (center_text("This name will appear on leaderboard", font_small), TOTAL_H // 2 - 70))
        
        pygame.draw.rect(screen, WHITE, input_box, 2, border_radius=6)
        text_surface = font.render(username + "|", True, YELLOW)
        screen.blit(text_surface, (input_box.x + 10, input_box.y + 12))
        
        hint = font_small.render("Press ENTER to start game", True, GREEN)
        screen.blit(hint, (center_text("Press ENTER to start game", font_small), input_box.bottom + 15))
        
        pygame.display.flip()
        clock.tick(FPS)

def main_menu():
    """Main menu screen"""
    play_btn = pygame.Rect(SCREEN_WIDTH // 2 - 90, 220, 180, 48)
    leaderboard_btn = pygame.Rect(SCREEN_WIDTH // 2 - 90, 285, 180, 48)
    settings_btn = pygame.Rect(SCREEN_WIDTH // 2 - 90, 350, 180, 48)
    quit_btn = pygame.Rect(SCREEN_WIDTH // 2 - 90, 415, 180, 48)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if button_clicked(play_btn, event):
                return "play"
            if button_clicked(leaderboard_btn, event):
                return "leaderboard"
            if button_clicked(settings_btn, event):
                return "settings"
            if button_clicked(quit_btn, event):
                pygame.quit()
                sys.exit()
        
        screen.fill((20, 20, 50))
        title = font_large.render("SNAKE GAME", True, GREEN)
        screen.blit(title, (center_text("SNAKE GAME", font_large), 100))
        
        subtitle = font_small.render("TSIS 4 - Advanced Edition", True, GRAY)
        screen.blit(subtitle, (center_text("TSIS 4 - Advanced Edition", font_small), 170))
        
        draw_button(play_btn, "PLAY")
        draw_button(leaderboard_btn, "LEADERBOARD")
        draw_button(settings_btn, "SETTINGS")
        draw_button(quit_btn, "QUIT")
        pygame.display.flip()
        clock.tick(FPS)

def leaderboard_screen():
    """Leaderboard screen showing top 10 players"""
    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 60, TOTAL_H - 70, 120, 40)
    
    # Force refresh data from database
    print("Loading leaderboard...")
    rows = db.get_top10()
    print(f"Loaded {len(rows)} records")
    
    # If no data, add some test data
    if not rows:
        print("No data found, adding test data...")
        db.save_game_result("TestPlayer1", 1000, 5)
        db.save_game_result("TestPlayer2", 2000, 8)
        db.save_game_result("TestPlayer3", 1500, 6)
        rows = db.get_top10()
        print(f"Now loaded {len(rows)} records after adding test data")
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if button_clicked(back_btn, event):
                return
        
        screen.fill((20, 20, 50))
        
        title = font_large.render("TOP 10 PLAYERS", True, YELLOW)
        screen.blit(title, (center_text("TOP 10 PLAYERS", font_large), 25))
        
        if not rows:
            no_data = font.render("No scores yet! Play a game first.", True, GRAY)
            screen.blit(no_data, (center_text("No scores yet! Play a game first."), 200))
        else:
            headers = ["#", "Player", "Score", "Level", "Date"]
            col_x = [40, 80, 220, 320, 440]
            
            for i, header in enumerate(headers):
                header_text = font_small.render(header, True, YELLOW)
                screen.blit(header_text, (col_x[i], 90))
            
            pygame.draw.line(screen, GRAY, (20, 108), (SCREEN_WIDTH - 20, 108), 2)
            
            for rank, row in enumerate(rows, 1):
                y = 125 + (rank - 1) * 35
                if y > TOTAL_H - 80:
                    break
                
                color = YELLOW if rank == 1 else WHITE
                
                # Handle different row formats
                if len(row) == 4:
                    username, score, level, date_str = row
                elif len(row) == 3:
                    username, score, level = row
                    date_str = "N/A"
                else:
                    print(f"Unexpected row format: {row}")
                    continue
                
                if len(username) > 12:
                    username = username[:10] + ".."
                
                values = [str(rank), username, str(score), str(level), date_str[:12] if date_str else "N/A"]
                for i, val in enumerate(values):
                    val_text = font_small.render(val, True, color)
                    screen.blit(val_text, (col_x[i], y))
        
        draw_button(back_btn, "BACK")
        pygame.display.flip()
        clock.tick(FPS)

def settings_screen(settings):
    """Settings screen"""
    grid_btn = pygame.Rect(250, 100, 130, 40)
    sound_btn = pygame.Rect(250, 155, 130, 40)
    color_btn = pygame.Rect(250, 210, 130, 40)
    save_btn = pygame.Rect(SCREEN_WIDTH // 2 - 70, 290, 140, 45)
    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 70, 350, 140, 45)
    
    color_options = [
        ("Green", [0, 220, 0]),
        ("Blue", [50, 120, 255]),
        ("Yellow", [255, 220, 0]),
        ("Orange", [255, 140, 0]),
        ("Purple", [160, 32, 240]),
    ]
    
    color_idx = 0
    for i, (_, c) in enumerate(color_options):
        if c == settings["snake_color"]:
            color_idx = i
            break
    
    saved_msg = ""
    saved_at = 0
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if button_clicked(grid_btn, event):
                settings["grid"] = not settings["grid"]
            if button_clicked(sound_btn, event):
                settings["sound"] = not settings["sound"]
            if button_clicked(color_btn, event):
                color_idx = (color_idx + 1) % len(color_options)
                settings["snake_color"] = color_options[color_idx][1]
            if button_clicked(save_btn, event):
                save_settings(settings)
                saved_msg = "Settings Saved!"
                saved_at = pygame.time.get_ticks()
            if button_clicked(back_btn, event):
                save_settings(settings)
                return settings
        
        screen.fill((20, 20, 50))
        title = font_large.render("SETTINGS", True, YELLOW)
        screen.blit(title, (center_text("SETTINGS", font_large), 30))
        
        labels = [
            ("Grid Overlay:", 112),
            ("Sound Effects:", 167),
            ("Snake Color:", 222),
        ]
        for label, y in labels:
            screen.blit(font.render(label, True, WHITE), (30, y))
        
        draw_button(grid_btn, "ON" if settings["grid"] else "OFF")
        draw_button(sound_btn, "ON" if settings["sound"] else "OFF")
        draw_button(color_btn, color_options[color_idx][0])
        
        if saved_msg and pygame.time.get_ticks() - saved_at < 1500:
            screen.blit(font.render(saved_msg, True, GREEN), (center_text(saved_msg), 270))
        
        draw_button(save_btn, "SAVE")
        draw_button(back_btn, "BACK")
        pygame.display.flip()
        clock.tick(FPS)

def game_over_screen(score, level, personal_best):
    """Game over screen"""
    retry_btn = pygame.Rect(SCREEN_WIDTH // 2 - 110, 340, 100, 45)
    menu_btn = pygame.Rect(SCREEN_WIDTH // 2 + 10, 340, 100, 45)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if button_clicked(retry_btn, event):
                return "retry"
            if button_clicked(menu_btn, event):
                return "menu"
        
        overlay = pygame.Surface((SCREEN_WIDTH, TOTAL_H))
        overlay.fill(BLACK)
        overlay.set_alpha(185)
        screen.blit(overlay, (0, 0))
        
        title = font_large.render("GAME OVER", True, RED)
        screen.blit(title, (center_text("GAME OVER", font_large), 140))
        
        stats = [
            (f"Score: {score}", WHITE),
            (f"Level: {level}", YELLOW),
            (f"Personal Best: {personal_best}", GRAY),
        ]
        for i, (text, color) in enumerate(stats):
            rendered = font.render(text, True, color)
            screen.blit(rendered, (center_text(text), 220 + i * 30))
        
        draw_button(retry_btn, "RETRY")
        draw_button(menu_btn, "MENU")
        pygame.display.flip()
        clock.tick(FPS)

def run_game(username, settings):
    """Main game loop"""
    snake_color = tuple(settings["snake_color"])
    show_grid = settings["grid"]
    
    personal_best = db.get_personal_best(username)
    print(f"Personal best for {username}: {personal_best}")
    
    snake = Snake(color=snake_color)
    food = Food()
    poison = PoisonFood()
    powerup = PowerUp()
    obstacles = set()
    
    def get_occupied():
        occupied = set(snake.body) | obstacles
        if food.pos:
            occupied.add(food.pos)
        if poison.pos:
            occupied.add(poison.pos)
        if powerup.pos:
            occupied.add(powerup.pos)
        return occupied
    
    food.spawn(get_occupied())
    poison.spawn(get_occupied())
    powerup.spawn(get_occupied())
    
    score = 0
    level = 1
    foods_eaten = 0
    game_over = False
    
    move_delay = 150
    last_move = pygame.time.get_ticks()
    
    effect_end = 0
    effect_type = None
    shield_active = False
    
    next_poison = pygame.time.get_ticks() + 5000
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu", score, level
                if not game_over:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        snake.change_direction(UP)
                    if event.key in (pygame.K_DOWN, pygame.K_s):
                        snake.change_direction(DOWN)
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        snake.change_direction(LEFT)
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        snake.change_direction(RIGHT)
        
        current_time = pygame.time.get_ticks()
        
        if not game_over:
            if effect_type in ("speed", "slow") and current_time > effect_end:
                move_delay = max(50, 150 - (level - 1) * 15)
                effect_type = None
            
            if food.expired():
                food.spawn(get_occupied())
            if poison.pos and poison.expired():
                poison.pos = None
            if powerup.pos and powerup.field_expired():
                powerup.spawn(get_occupied())
            
            if poison.pos is None and current_time >= next_poison:
                poison.spawn(get_occupied())
                next_poison = current_time + random.randint(8000, 15000)
            
            if current_time - last_move > move_delay:
                snake.move()
                last_move = current_time
                
                collision = (snake.check_wall() or snake.check_self() or snake.check_obstacle(obstacles))
                
                if collision:
                    if shield_active:
                        shield_active = False
                        effect_type = None
                        if len(snake.body) > 1:
                            snake.body[0] = snake.body[1]
                    else:
                        game_over = True
                
                if not game_over and snake.body[0] == food.pos:
                    snake.grow()
                    score += food.kind["weight"]
                    foods_eaten += 1
                    food.spawn(get_occupied())
                    
                    if foods_eaten % LEVEL_UP_FOODS == 0:
                        level += 1
                        if effect_type not in ("speed", "slow"):
                            move_delay = max(50, move_delay - SPEED_INCREASE)
                        obstacles = make_obstacles(level, snake.body)
                        food.spawn(get_occupied())
                        poison.pos = None
                        powerup.spawn(get_occupied())
                
                if not game_over and poison.pos and snake.body[0] == poison.pos:
                    poison.pos = None
                    if not snake.shrink(2):
                        game_over = True
                    next_poison = current_time + random.randint(8000, 15000)
                
                if not game_over and powerup.pos and snake.body[0] == powerup.pos:
                    powerup_type = powerup.kind
                    powerup.pos = None
                    
                    if powerup_type == "speed":
                        move_delay = max(30, move_delay - 40)
                        effect_type = "speed"
                        effect_end = current_time + POWERUP_DURATION
                    elif powerup_type == "slow":
                        move_delay = move_delay + 60
                        effect_type = "slow"
                        effect_end = current_time + POWERUP_DURATION
                    elif powerup_type == "shield":
                        shield_active = True
                        effect_type = "shield"
                    
                    score += 20
                    powerup.spawn(get_occupied())
            
            personal_best = max(personal_best, score)
        
        # Drawing
        screen.fill(BLACK)
        pygame.draw.rect(screen, DARK_GRAY, (0, UI_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        if show_grid:
            for gx in range(0, SCREEN_WIDTH, GRID_SIZE):
                pygame.draw.line(screen, (60, 60, 60), (gx, UI_HEIGHT), (gx, TOTAL_H))
            for gy in range(UI_HEIGHT, TOTAL_H, GRID_SIZE):
                pygame.draw.line(screen, (60, 60, 60), (0, gy), (SCREEN_WIDTH, gy))
        
        draw_obstacles(screen, obstacles)
        food.draw(screen)
        if poison.pos:
            poison.draw(screen)
        if powerup.pos:
            powerup.draw(screen)
        snake.draw(screen, show_grid)
        
        pygame.draw.rect(screen, (30, 30, 60), (0, 0, SCREEN_WIDTH, UI_HEIGHT))
        pygame.draw.line(screen, GRAY, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)
        
        screen.blit(font.render(f"Player: {username}", True, WHITE), (10, 8))
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 33))
        screen.blit(font.render(f"Level: {level}", True, YELLOW), (200, 8))
        screen.blit(font_small.render(f"Best: {personal_best}", True, GRAY), (200, 33))
        
        if effect_type == "speed":
            secs = max(0, (effect_end - current_time) // 1000)
            screen.blit(font_small.render(f"SPEED {secs}s", True, ORANGE), (350, 8))
        elif effect_type == "slow":
            secs = max(0, (effect_end - current_time) // 1000)
            screen.blit(font_small.render(f"SLOW {secs}s", True, CYAN), (350, 8))
        elif effect_type == "shield":
            screen.blit(font_small.render("SHIELD ACTIVE", True, PURPLE), (350, 8))
        
        if poison.pos:
            screen.blit(font_small.render("POISON!", True, DARK_RED), (480, 8))
        
        if game_over:
            action = game_over_screen(score, level, personal_best)
            return action, score, level
        
        pygame.display.flip()
        clock.tick(FPS)

def main():
    # Load settings
    settings = load_settings()
    
    # Setup database
    print("Setting up database...")
    if db.setup_schema():
        print("Database ready!")
    else:
        print("Database connection failed! Check your config.py")
    
    # Test database connection
    print("\nTesting database...")
    test_rows = db.get_top10()
    print(f"Current leaderboard has {len(test_rows)} entries")
    
    # Main game loop
    while True:
        action = main_menu()
        
        if action == "leaderboard":
            leaderboard_screen()
        elif action == "settings":
            settings = settings_screen(settings)
        elif action == "play":
            # Always ask for username before game
            username = username_entry_screen()
            print(f"\nStarting game for player: {username}")
            
            while True:
                result, score, level = run_game(username, settings)
                
                # Save result to database
                print(f"\nGame over! Saving result: {username} - Score: {score}, Level: {level}")
                try:
                    saved = db.save_game_result(username, score, level)
                    if saved:
                        print("✓ Result saved successfully!")
                    else:
                        print("✗ Failed to save result!")
                except Exception as e:
                    print(f"✗ Save error: {e}")
                
                if result == "menu":
                    break

if __name__ == "__main__":
    main()