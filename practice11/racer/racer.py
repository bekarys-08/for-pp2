import pygame
import random

pygame.init()

WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer – Practice 11")

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
RED    = (220, 50, 50)
GRAY   = (100, 100, 100)
GREEN  = (50, 200, 50)

clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 30)


player = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 100, 50, 80)
PLAYER_SPEED = 5


enemies      = []
enemy_speed  = 4   
ENEMY_BOOST_EVERY = 5   

SPAWN_ENEMY = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_ENEMY, 1200)



COIN_TYPES = [
    {"color": (255, 215, 0),   "value": 1,  "weight": 60, "radius": 10},  
    {"color": (192, 192, 192), "value": 3,  "weight": 30, "radius": 13},  
    {"color": (205, 127, 50),  "value": 5,  "weight": 10, "radius": 16},  
]

coins       = []     
coin_score  = 0      
SPAWN_COIN = pygame.USEREVENT + 2
pygame.time.set_timer(SPAWN_COIN, 900)

def spawn_enemy():
    x = random.randint(0, WIDTH - 50)
    return pygame.Rect(x, -80, 50, 80)

def spawn_coin():
    """Pick a random coin type based on weight, spawn it at top."""
    weights = [ct["weight"] for ct in COIN_TYPES]
    coin_type = random.choices(COIN_TYPES, weights=weights)[0]
    r = coin_type["radius"]
    x = random.randint(r, WIDTH - r)
    rect = pygame.Rect(x - r, -r * 2, r * 2, r * 2)
    return {"rect": rect, "type": coin_type}

def draw_car(rect, color):
    pygame.draw.rect(screen, color, rect, border_radius=6)
    inner = rect.inflate(-10, -20)
    pygame.draw.rect(screen, (180, 220, 255), inner, border_radius=4)

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == SPAWN_ENEMY:
            enemies.append(spawn_enemy())
        if event.type == SPAWN_COIN:
            coins.append(spawn_coin())

    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]  and player.left  > 0:        player.x -= PLAYER_SPEED
    if keys[pygame.K_RIGHT] and player.right < WIDTH:     player.x += PLAYER_SPEED
    if keys[pygame.K_UP]    and player.top   > 0:         player.y -= PLAYER_SPEED
    if keys[pygame.K_DOWN]  and player.bottom < HEIGHT:   player.y += PLAYER_SPEED

    
    for e in enemies[:]:
        e.y += enemy_speed
        if e.top > HEIGHT:
            enemies.remove(e)
        elif player.colliderect(e):
            running = False

    
    for c in coins[:]:
        c["rect"].y += enemy_speed
        if c["rect"].top > HEIGHT:
            coins.remove(c)
        elif player.colliderect(c["rect"]):
            coins.remove(c)
            coin_score += c["type"]["value"]
            
            if coin_score % ENEMY_BOOST_EVERY == 0:
                enemy_speed += 1

    
    screen.fill(GRAY)
    
    for y in range(0, HEIGHT, 60):
        pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 3, y, 6, 30))

    draw_car(player, GREEN)
    for e in enemies:
        draw_car(e, RED)

    
    for c in coins:
        r = c["type"]["radius"]
        cx = c["rect"].centerx
        cy = c["rect"].centery
        pygame.draw.circle(screen, c["type"]["color"], (cx, cy), r)
        
        val_txt = font.render(str(c["type"]["value"]), True, BLACK)
        screen.blit(val_txt, (cx - val_txt.get_width() // 2, cy - val_txt.get_height() // 2))

    
    hud_l = font.render(f"Speed: {enemy_speed}", True, WHITE)
    hud_r = font.render(f"Coins: {coin_score}", True, (255, 215, 0))
    screen.blit(hud_l, (10, 10))
    screen.blit(hud_r, (WIDTH - hud_r.get_width() - 10, 10))

    pygame.display.flip()


screen.fill(BLACK)
go  = font.render("GAME OVER", True, RED)
sc  = font.render(f"Coins collected: {coin_score}", True, WHITE)
screen.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT // 2 - 30))
screen.blit(sc, (WIDTH // 2 - sc.get_width() // 2, HEIGHT // 2 + 10))
pygame.display.flip()
pygame.time.wait(2500)
pygame.quit()
