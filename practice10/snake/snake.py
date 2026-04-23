import pygame
import random

pygame.init()

CELL  = 20
COLS, ROWS = 30, 30
WIDTH, HEIGHT = COLS * CELL, ROWS * CELL
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")


BLACK  = (0, 0, 0)
GREEN  = (50, 200, 50)
DGREEN = (30, 140, 30)
RED    = (220, 50, 50)
WHITE  = (255, 255, 255)
YELLOW = (255, 215, 0)

clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 32)


UP    = (0, -1)
DOWN  = (0,  1)
LEFT  = (-1, 0)
RIGHT = (1,  0)
FOOD_PER_LEVEL = 3  

def free_cell(snake):
    """Pick a random grid cell that is not occupied by the snake."""
    while True:
        pos = (random.randint(1, COLS - 2), random.randint(1, ROWS - 2))
        if pos not in snake:
            return pos

def reset():
    """Return the initial game state."""
    snake = [(COLS // 2, ROWS // 2)]
    direction = RIGHT
    food = free_cell(snake)
    score = 0
    level = 1
    food_eaten = 0
    speed = 8
    return snake, direction, food, score, level, food_eaten, speed

snake, direction, food, score, level, food_eaten, speed = reset()
running = True

while running:
    clock.tick(speed)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            
            if event.key == pygame.K_UP    and direction != DOWN:  direction = UP
            if event.key == pygame.K_DOWN  and direction != UP:    direction = DOWN
            if event.key == pygame.K_LEFT  and direction != RIGHT: direction = LEFT
            if event.key == pygame.K_RIGHT and direction != LEFT:  direction = RIGHT

    
    head = (snake[0][0] + direction[0], snake[0][1] + direction[1])

    
    if not (0 <= head[0] < COLS and 0 <= head[1] < ROWS):
        running = False
        continue

    
    if head in snake:
        running = False
        continue

    snake.insert(0, head)

    if head == food:
       
        score += 10 * level
        food_eaten += 1
        food = free_cell(snake) 
        
        if food_eaten % FOOD_PER_LEVEL == 0:
            level += 1
            speed += 2  
    else:
        snake.pop() 
    
    screen.fill(BLACK)

    
    pygame.draw.rect(screen, (80, 80, 80), (0, 0, WIDTH, HEIGHT), CELL)

    
    for i, seg in enumerate(snake):
        color = GREEN if i == 0 else DGREEN
        rect = pygame.Rect(seg[0] * CELL, seg[1] * CELL, CELL, CELL)
        pygame.draw.rect(screen, color, rect, border_radius=4)

    
    fx, fy = food[0] * CELL + CELL // 2, food[1] * CELL + CELL // 2
    pygame.draw.circle(screen, RED, (fx, fy), CELL // 2 - 2)

    
    hud = font.render(f"Score: {score}   Level: {level}", True, WHITE)
    screen.blit(hud, (10, 5))

    pygame.display.flip()


screen.fill(BLACK)
go  = font.render("GAME OVER", True, RED)
sc  = font.render(f"Score: {score}  Level: {level}", True, WHITE)
screen.blit(go, (WIDTH // 2 - go.get_width() // 2, HEIGHT // 2 - 30))
screen.blit(sc, (WIDTH // 2 - sc.get_width() // 2, HEIGHT // 2 + 10))
pygame.display.flip()
pygame.time.wait(2500)
pygame.quit()
