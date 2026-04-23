import pygame
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer")

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (220, 50, 50)
GRAY   = (100, 100, 100)
YELLOW = (255, 215, 0)
GREEN  = (50, 200, 50)

clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 32)

player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 100, 50, 80)
player_speed = 5

enemy_width, enemy_height = 50, 80
enemies = []
enemy_speed = 4
SPAWN_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY, 1200)


coins = []
coin_radius = 12
SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 800)

coin_count = 0
score = 0
running = True

def spawn_enemy():
    """Create a new enemy car at a random x position."""
    x = random.randint(0, WIDTH - enemy_width)
    return pygame.Rect(x, -enemy_height, enemy_width, enemy_height)

def spawn_coin():
    """Create a new coin at a random x position."""
    x = random.randint(coin_radius, WIDTH - coin_radius)
    return [x, -coin_radius]  

def draw_car(rect, color):
    """Draw a simple car shape."""
    pygame.draw.rect(screen, color, rect, border_radius=6)
   
    inner = rect.inflate(-10, -20)
    pygame.draw.rect(screen, (180, 220, 255), inner, border_radius=4)

def draw_road():
    """Draw dashed road lines."""
    screen.fill(GRAY)
    for y in range(0, HEIGHT, 60):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 3, y, 6, 30))

while running:
    clock.tick(60)
    score += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == SPAWN_ENEMY:
            enemies.append(spawn_enemy())
        if event.type == SPAWN_COIN:
            coins.append(spawn_coin())

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]  and player.left  > 0:
        player.x -= player_speed
    if keys[pygame.K_RIGHT] and player.right < WIDTH:
        player.x += player_speed
    if keys[pygame.K_UP]    and player.top   > 0:
        player.y -= player_speed
    if keys[pygame.K_DOWN]  and player.bottom < HEIGHT:
        player.y += player_speed

    for e in enemies[:]:
        e.y += enemy_speed
        if e.top > HEIGHT:
            enemies.remove(e)
        elif player.colliderect(e):
            running = False  

    for c in coins[:]:
        c[1] += enemy_speed
        cx, cy = c
        coin_rect = pygame.Rect(cx - coin_radius, cy - coin_radius,
                                coin_radius * 2, coin_radius * 2)
        if cy > HEIGHT:
            coins.remove(c)
        elif player.colliderect(coin_rect):
            coins.remove(c)
            coin_count += 1  

    draw_road()
    draw_car(player, GREEN)
    for e in enemies:
        draw_car(e, RED)
    for c in coins:
        pygame.draw.circle(screen, YELLOW, (c[0], c[1]), coin_radius)
        pygame.draw.circle(screen, (200, 160, 0), (c[0], c[1]), coin_radius, 2)

    
    score_text = font.render(f"Score: {score // 60}", True, WHITE)
    coin_text  = font.render(f"Coins: {coin_count}", True, YELLOW)
    screen.blit(score_text, (10, 10))
    screen.blit(coin_text,  (WIDTH - coin_text.get_width() - 10, 10)) 
    pygame.display.flip()


screen.fill(BLACK)
go_text  = font.render("GAME OVER", True, RED)
sc_text  = font.render(f"Score: {score // 60}  Coins: {coin_count}", True, WHITE)
screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 30))
screen.blit(sc_text, (WIDTH // 2 - sc_text.get_width() // 2, HEIGHT // 2 + 10))
pygame.display.flip()
pygame.time.wait(2500)
pygame.quit()
