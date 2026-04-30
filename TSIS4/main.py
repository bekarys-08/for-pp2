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
    "username": "",
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
    return (event.type == pygame.MOUSEBUTTONDOWN and 
            event.button == 1 and 
            rect.collidepoint(event.pos))

def center_text_x(text, font_obj=None):
    font_obj = font_obj or font
    return SCREEN_WIDTH // 2 - font_obj.size(text)[0] // 2

def ask_username():
    """Screen for entering username"""
    username = ""
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 140, TOTAL_H // 2 - 50, 280, 44)
    
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
        title = font_large.render("Enter Username", True, YELLOW)
        screen.blit(title, (center_text_x("Enter Username", font_large), TOTAL_H // 2 - 120))
        pygame.draw.rect(screen, WHITE, input_box, 2, border_radius=6)
        text_surface = font.render(username + "|", True, YELLOW)
        screen.blit(text_surface, (input_box.x + 8, input_box.y + 10))
        
        hint = font_small.render("Press Enter to confirm", True, GRAY)
        screen.blit(hint, (center_text_x("Press Enter to confirm", font_small), input_box.bottom + 12))
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
        title = font_large.render("SNAKE", True, GREEN)
        screen.blit(title, (center_text_x("SNAKE", font_large), 110))
        
        draw_button(play_btn, "Play")
        draw_button(leaderboard_btn, "Leaderboard")
        draw_button(settings_btn, "Settings")
        draw_button(quit_btn, "Quit")
        pygame.display.flip()
        clock.tick(FPS)

def leaderboard_screen():
    """Leaderboard screen showing top 10 players"""
    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 60, TOTAL_H - 70, 120, 40)
    
    # Load data from database
    rows = db.get_top10()
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if button_clicked(back_btn, event):
                return
        
        screen.fill((20, 20, 50))
        
        # Title
        title = font_large.render("TOP 10 PLAYERS", True, YELLOW)
        screen.blit(title, (center_text_x("TOP 10 PLAYERS", font_large), 30))
        
        if not rows:
            no_data = font.render("No scores yet! Play a game first.", True, GRAY)
            screen.blit(no_data, (center_text_x("No scores yet! Play a game first."), 200))
        else:
            # Table headers
            headers = ["#", "Player", "Score", "Level", "Date"]
            col_x = [50, 120, 280, 380, 460]
            
            for i, header in enumerate(headers):
                header_text = font_small.render(header, True, YELLOW)
                screen.blit(header_text, (col_x[i], 100))
            
            # Line under headers
            pygame.draw.line(screen, GRAY, (30, 120), (SCREEN_WIDTH - 30, 120), 2)
            
            # Display rows
            for rank, row in enumerate(rows, 1):
                y = 140 + (rank - 1) * 35
                if y > TOTAL_H - 80:
                    break
                
                color = YELLOW if rank == 1 else WHITE
                
                if len(row) == 4:
                    username, score, level_reached, date_str = row
                else:
                    continue
                
                # Truncate long usernames
                if len(username) > 12:
                    username = username[:10] + ".."
                
                values = [str(rank), username, str(score), str(level_reached), date_str]
                for i, val in enumerate(values):
                    val_text = font_small.render(val, True, color)
                    screen.blit(val_text, (col_x[i], y))
        
        draw_button(back_btn, "Back")
        pygame.display.flip()
        clock.tick(FPS)

def settings_screen(settings):
    """Settings screen for game preferences"""
    grid_btn = pygame.Rect(250, 88, 130, 36)
    sound_btn = pygame.Rect(250, 138, 130, 36)
    color_btn = pygame.Rect(250, 188, 130, 36)
    user_btn = pygame.Rect(250, 238, 130, 36)
    save_btn = pygame.Rect(SCREEN_WIDTH // 2 - 70, 298, 140, 40)
    back_btn = pygame.Rect(SCREEN_WIDTH // 2 - 70, 352, 140, 40)
    
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
            if button_clicked(user_btn, event):
                new_name = ask_username()
                if new_name:
                    settings["username"] = new_name
            if button_clicked(save_btn, event):
                save_settings(settings)
                saved_msg = "Settings Saved!"
                saved_at = pygame.time.get_ticks()
            if button_clicked(back_btn, event):
                save_settings(settings)
                return settings
        
        screen.fill((20, 20, 50))
        title = font_large.render("Settings", True, YELLOW)
        screen.blit(title, (center_text_x("Settings", font_large), 28))
        
        labels = [
            ("Grid overlay:", 98),
            ("Sound:", 148),
            ("Snake color:", 198),
            ("Username:", 248),
        ]
        for label, y in labels:
            screen.blit(font.render(label, True, WHITE), (30, y))
        
        draw_button(grid_btn, "ON" if settings["grid"] else "OFF")
        draw_button(sound_btn, "ON" if settings["sound"] else "OFF")
        draw_button(color_btn, color_options[color_idx][0])
        
        username_display = (settings.get("username") or "(none)")[:10]
        draw_button(user_btn, username_display)
        
        if saved_msg and pygame.time.get_ticks() - saved_at < 1500:
            screen.blit(font.render(saved_msg, True, GREEN),
                        (center_text_x(saved_msg), 280))
        
        draw_button(save_btn, "Save")
        draw_button(back_btn, "Back")
        pygame.display.flip()
        clock.tick(FPS)

def game_over_screen(score, level, personal_best):
    """Game over screen with options"""
    retry_btn = pygame.Rect(SCREEN_WIDTH // 2 - 110, 340, 100, 42)
    menu_btn = pygame.Rect(SCREEN_WIDTH // 2 + 10, 340, 100, 42)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if button_clicked(retry_btn, event):
                return "retry"
            if button_clicked(menu_btn, event):
                return "menu"
        
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, TOTAL_H))
        overlay.fill(BLACK)
        overlay.set_alpha(185)
        screen.blit(overlay, (0, 0))
        
        title = font_large.render("GAME OVER", True, RED)
        screen.blit(title, (center_text_x("GAME OVER", font_large), 150))
        
        stats = [
            (f"Score: {score}", WHITE),
            (f"Level: {level}", YELLOW),
            (f"Personal Best: {personal_best}", GRAY),
        ]
        for i, (text, color) in enumerate(stats):
            rendered = font.render(text, True, color)
            screen.blit(rendered, (center_text_x(text), 240 + i * 30))
        
        draw_button(retry_btn, "Retry")
        draw_button(menu_btn, "Menu")
        pygame.display.flip()
        clock.tick(FPS)

def run_game(settings):
    """Main game loop"""
    username = settings["username"]
    show_grid = settings["grid"]
    
    # Get personal best from database
    personal_best = db.get_personal_best(username)
    
    # Initialize game objects
    snake = Snake(color=tuple(settings["snake_color"]))
    food = Food()
    poison = PoisonFood()
    powerup = PowerUp()
    obstacles = set()
    
    def get_occupied_positions():
        occupied = set(snake.body) | obstacles
        if food.pos:
            occupied.add(food.pos)
        if poison.pos:
            occupied.add(poison.pos)
        if powerup.pos:
            occupied.add(powerup.pos)
        return occupied
    
    # Spawn initial items
    food.spawn(get_occupied_positions())
    poison.spawn(get_occupied_positions())
    powerup.spawn(get_occupied_positions())
    
    # Game variables
    score = 0
    level = 1
    foods_eaten = 0
    game_over = False
    
    # Movement timing
    move_delay = 150
    last_move = pygame.time.get_ticks()
    
    # Power-up effects
    effect_end = 0
    effect_type = None
    shield_active = False
    
    # Poison spawn timer
    next_poison = pygame.time.get_ticks() + 5000
    
    while True:
        # Handle events
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
            # Handle speed effects
            if effect_type in ("speed", "slow") and current_time > effect_end:
                move_delay = max(50, 150 - (level - 1) * 15)
                effect_type = None
            
            # Update food items
            if food.expired():
                food.spawn(get_occupied_positions())
            if poison.pos and poison.expired():
                poison.pos = None
            if powerup.pos and powerup.field_expired():
                powerup.spawn(get_occupied_positions())
            
            # Spawn poison
            if poison.pos is None and current_time >= next_poison:
                poison.spawn(get_occupied_positions())
                next_poison = current_time + random.randint(8000, 15000)
            
            # Move snake
            if current_time - last_move > move_delay:
                snake.move()
                last_move = current_time
                
                # Check collisions
                collision = (snake.check_wall() or 
                            snake.check_self() or 
                            snake.check_obstacle(obstacles))
                
                if collision:
                    if shield_active:
                        shield_active = False
                        effect_type = None
                        # Rollback position
                        if len(snake.body) > 1:
                            snake.body[0] = snake.body[1]
                    else:
                        game_over = True
                
                # Eat normal food
                if not game_over and snake.body[0] == food.pos:
                    snake.grow()
                    score += food.kind["weight"]
                    foods_eaten += 1
                    food.spawn(get_occupied_positions())
                    
                    # Level up
                    if foods_eaten % LEVEL_UP_FOODS == 0:
                        level += 1
                        if effect_type not in ("speed", "slow"):
                            move_delay = max(50, move_delay - SPEED_INCREASE)
                        obstacles = make_obstacles(level, snake.body)
                        food.spawn(get_occupied_positions())
                        poison.pos = None
                        powerup.spawn(get_occupied_positions())
                
                # Eat poison
                if not game_over and poison.pos and snake.body[0] == poison.pos:
                    poison.pos = None
                    if not snake.shrink(2):
                        game_over = True
                    next_poison = current_time + random.randint(8000, 15000)
                
                # Eat power-up
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
                    powerup.spawn(get_occupied_positions())
            
            # Update personal best
            personal_best = max(personal_best, score)
        
        # Drawing
        screen.fill(BLACK)
        pygame.draw.rect(screen, DARK_GRAY, (0, UI_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Draw grid
        if show_grid:
            for gx in range(0, SCREEN_WIDTH, GRID_SIZE):
                pygame.draw.line(screen, (60, 60, 60), (gx, UI_HEIGHT), (gx, TOTAL_H))
            for gy in range(UI_HEIGHT, TOTAL_H, GRID_SIZE):
                pygame.draw.line(screen, (60, 60, 60), (0, gy), (SCREEN_WIDTH, gy))
        
        # Draw game objects
        draw_obstacles(screen, obstacles)
        food.draw(screen)
        if poison.pos:
            poison.draw(screen)
        if powerup.pos:
            powerup.draw(screen)
        snake.draw(screen, show_grid)
        
        # Draw UI
        pygame.draw.rect(screen, (30, 30, 60), (0, 0, SCREEN_WIDTH, UI_HEIGHT))
        pygame.draw.line(screen, GRAY, (0, UI_HEIGHT), (SCREEN_WIDTH, UI_HEIGHT), 2)
        
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 8))
        screen.blit(font.render(f"Level: {level}", True, YELLOW), (10, 33))
        screen.blit(font_small.render(f"Best: {personal_best}", True, GRAY), (160, 8))
        
        # Draw active effects
        if effect_type == "speed":
            seconds = max(0, (effect_end - current_time) )