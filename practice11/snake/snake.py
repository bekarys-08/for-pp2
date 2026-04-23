import pygame
import random
import time

pygame.init()

CELL  = 20
COLS, ROWS = 30, 30
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake – Practice 11")

BLACK   = (0,   0,   0)
GREEN   = (50,  200, 50)
DGREEN  = (30,  140, 30)
WHITE   = (255, 255, 255)
GRAY    = (80,  80,  80)

clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 30)

UP, DOWN, LEFT, RIGHT = (0,-1), (0,1), (-1,0), (1,0)
FOOD_PER_LEVEL = 3


FOOD_TYPES = [
    {"color": (220, 50, 50),  "points": 10, "weight": 60, "lifetime": 8},   
    {"color": (255, 165, 0),  "points": 25, "weight": 30, "lifetime": 5},   
    {"color": (180, 50, 220), "points": 50, "weight": 10, "lifetime": 3},   
]

def free_cell(snake, foods):
    """Pick a grid cell not on the snake or existing food."""
    occupied = set(snake) | {f["pos"] for f in foods}
    while True:
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if pos not in occupied:
            return pos

def new_food(snake, foods):
    """Create a new food item with random type based on weight."""
    weights = [ft["weight"] for ft in FOOD_TYPES]
    ft = random.choices(FOOD_TYPES, weights=weights)[0]
    return {
        "pos":       free_cell(snake, foods),
        "color":     ft["color"],
        "points":    ft["points"],
        "lifetime":  ft["lifetime"],
        "spawned_at": time.time(),  
    }

def reset():
    snake = [(COLS // 2, ROWS // 2)]
    direction = RIGHT
    foods = [new_food(snake, [])]
    return snake, direction, foods, 0, 1, 0, 8

snake, direction, foods, score, level, food_eaten, speed = reset()


FOOD_SPAWN_MS = 4000
last_food_spawn = pygame.time.get_ticks()

running = True
while running:
    clock.tick(speed)
    now = time.time()
    now_ms = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP    and direction != DOWN:  direction = UP
            if event.key == pygame.K_DOWN  and direction != UP:    direction = DOWN
            if event.key == pygame.K_LEFT  and direction != RIGHT: direction = LEFT
            if event.key == pygame.K_RIGHT and direction != LEFT:  direction = RIGHT

    
    foods = [f for f in foods if now - f["spawned_at"] < f["lifetime"]]

    
    if now_ms - last_food_spawn > FOOD_SPAWN_MS and len(foods) < 3:
        foods.append(new_food(snake, foods))
        last_food_spawn = now_ms

    
    if not foods:
        foods.append(new_food(snake, []))

    
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    
    if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):
        running = False; continue
    
    if head in snake:
        running = False; continue

    snake.insert(0, head)

    
    ate = None
    for f in foods:
        if head == f["pos"]:
            ate = f
            break

    if ate:
        score += ate["points"] * level
        food_eaten += 1
        foods.remove(ate)
        foods.append(new_food(snake, foods))  
        if food_eaten % FOOD_PER_LEVEL == 0:
            level += 1
            speed += 2
    else:
        snake.pop()

    
    screen.fill(BLACK)
    pygame.draw.rect(screen, GRAY, (0, 0, WIDTH, HEIGHT), CELL)

    
    for i, seg in enumerate(snake):
        color = GREEN if i == 0 else DGREEN
        pygame.draw.rect(screen, color,
                         (seg[0]*CELL, seg[1]*CELL, CELL, CELL), border_radius=4)

    
    for f in foods:
        fx, fy = f["pos"][0]*CELL + CELL//2, f["pos"][1]*CELL + CELL//2
        pygame.draw.circle(screen, f["color"], (fx, fy), CELL//2 - 2)

        
        elapsed  = now - f["spawned_at"]
        fraction = max(0, 1 - elapsed / f["lifetime"])
        bar_w    = int(CELL * fraction)
        pygame.draw.rect(screen, (255, 80, 80),
                         (f["pos"][0]*CELL, f["pos"][1]*CELL - 5, CELL, 4))
        pygame.draw.rect(screen, (80, 255, 80),
                         (f["pos"][0]*CELL, f["pos"][1]*CELL - 5, bar_w, 4))

    
    hud = font.render(f"Score: {score}   Level: {level}", True, WHITE)
    screen.blit(hud, (10, 5))

    pygame.display.flip()


screen.fill(BLACK)
go = font.render("GAME OVER", True, (220, 50, 50))
sc = font.render(f"Score: {score}  Level: {level}", True, WHITE)
screen.blit(go, (WIDTH//2 - go.get_width()//2, HEIGHT//2 - 30))
screen.blit(sc, (WIDTH//2 - sc.get_width()//2, HEIGHT//2 + 10))
pygame.display.flip()
pygame.time.wait(2500)
pygame.quit()
