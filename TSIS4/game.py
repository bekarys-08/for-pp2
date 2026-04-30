import pygame
import random

WIDTH, HEIGHT = 800, 600
BLOCK_SIZE = 20
BASE_SPEED = 10


C_BG = (30, 30, 30)
C_GRID = (50, 50, 50)
C_FOOD_NORMAL = (200, 0, 0)
C_FOOD_WEIGHTED = (255, 215, 0) # Gold
C_POISON = (139, 0, 0) # Dark Red
C_OBSTACLE = (100, 100, 100) # Gray
C_PW_SPEED = (0, 255, 255) # Cyan
C_PW_SLOW = (0, 0, 255) # Blue
C_PW_SHIELD = (255, 0, 255) # Magenta

def run_game(screen, settings, personal_best):
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 36)
    
    
    snake = [[WIDTH//2, HEIGHT//2], [WIDTH//2 - BLOCK_SIZE, HEIGHT//2], [WIDTH//2 - 2*BLOCK_SIZE, HEIGHT//2]]
    dx, dy = BLOCK_SIZE, 0
    snake_color = tuple(settings["snake_color"])
    
    
    score = 0
    level = 1
    food_eaten_this_level = 0
    current_speed = BASE_SPEED
    
    
    obstacles = []
    def generate_obstacles():
        obs = []
        if level >= 3:
            num_obs = level * 2
            for _ in range(num_obs):
                while True:
                    ox = random.randrange(0, WIDTH, BLOCK_SIZE)
                    oy = random.randrange(0, HEIGHT, BLOCK_SIZE)
                    
                    if not (WIDTH//2 - 100 <= ox <= WIDTH//2 + 100 and HEIGHT//2 - 100 <= oy <= HEIGHT//2 + 100):
                        obs.append([ox, oy])
                        break
        return obs
    
    obstacles = generate_obstacles()

    def get_random_pos():
        while True:
            x = random.randrange(0, WIDTH, BLOCK_SIZE)
            y = random.randrange(0, HEIGHT, BLOCK_SIZE)
            if [x, y] not in snake and [x, y] not in obstacles:
                return [x, y]

    
    food = get_random_pos()
    food_type = "normal"
    food_timer = 0
    poison = get_random_pos() if random.random() < 0.3 else None

    
    powerup = None
    powerup_type = None
    powerup_spawn_time = 0
    active_effect = None
    effect_end_time = 0
    shield_active = False

    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and dy == 0: dx, dy = 0, -BLOCK_SIZE
                elif event.key == pygame.K_DOWN and dy == 0: dx, dy = 0, BLOCK_SIZE
                elif event.key == pygame.K_LEFT and dx == 0: dx, dy = -BLOCK_SIZE, 0
                elif event.key == pygame.K_RIGHT and dx == 0: dx, dy = BLOCK_SIZE, 0

        
        new_head = [snake[0][0] + dx, snake[0][1] + dy]

         
        collision = False
        if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
            collision = True
        if new_head in snake or new_head in obstacles:
            collision = True

        if collision:
            if shield_active:
                shield_active = False
                active_effect = None
                
                if new_head[0] < 0: new_head[0] = WIDTH - BLOCK_SIZE
                elif new_head[0] >= WIDTH: new_head[0] = 0
                elif new_head[1] < 0: new_head[1] = HEIGHT - BLOCK_SIZE
                elif new_head[1] >= HEIGHT: new_head[1] = 0
                else: 
                    
                    continue 
            else:
                running = False 
                continue

        snake.insert(0, new_head)

        
        if new_head == food:
            if settings["sound"]: pass 
            if food_type == "normal": score += 10
            elif food_type == "weighted": score += 30
            
            food_eaten_this_level += 1
            if food_eaten_this_level >= 5: 
                level += 1
                food_eaten_this_level = 0
                obstacles = generate_obstacles()
            
            
            food = get_random_pos()
            rand_val = random.random()
            if rand_val < 0.2:
                food_type = "weighted"
                food_timer = current_time + 5000 
            else:
                food_type = "normal"
            
           
            poison = get_random_pos() if random.random() < 0.3 else None

        else:
            snake.pop() 

        
        if poison and new_head == poison:
            if settings["sound"]: pass 
            if len(snake) > 0: snake.pop()
            if len(snake) > 0: snake.pop()
            poison = None
            if len(snake) <= 1:
                running = False 
                continue

       
       
        if powerup is None and random.random() < 0.01:
            powerup = get_random_pos()
            powerup_type = random.choice(["speed", "slow", "shield"])
            powerup_spawn_time = current_time
        
        
        if powerup and current_time - powerup_spawn_time > 8000:
            powerup = None
            
       
        if powerup and new_head == powerup:
            if settings["sound"]: pass # pygame.mixer.Sound('powerup.wav').play()
            active_effect = powerup_type
            effect_end_time = current_time + 5000 # 5 second duration
            if powerup_type == "shield": shield_active = True
            powerup = None
            
        
        if active_effect and active_effect != "shield" and current_time > effect_end_time:
            active_effect = None
            
        
        fps = BASE_SPEED + (level * 2)
        if active_effect == "speed": fps += 10
        elif active_effect == "slow": fps = max(5, fps - 5)

        
        if food_type == "weighted" and current_time > food_timer:
            food = get_random_pos()
            food_type = "normal"

        
        screen.fill(C_BG)
        if settings["grid_overlay"]:
            for x in range(0, WIDTH, BLOCK_SIZE): pygame.draw.line(screen, C_GRID, (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, BLOCK_SIZE): pygame.draw.line(screen, C_GRID, (0, y), (WIDTH, y))

        
        for obs in obstacles:
            pygame.draw.rect(screen, C_OBSTACLE, (obs[0], obs[1], BLOCK_SIZE, BLOCK_SIZE))

        
        color = C_FOOD_WEIGHTED if food_type == "weighted" else C_FOOD_NORMAL
        pygame.draw.rect(screen, color, (food[0], food[1], BLOCK_SIZE, BLOCK_SIZE))

        
        if poison:
            pygame.draw.rect(screen, C_POISON, (poison[0], poison[1], BLOCK_SIZE, BLOCK_SIZE))

        
        if powerup:
            c = C_PW_SPEED if powerup_type == "speed" else C_PW_SLOW if powerup_type == "slow" else C_PW_SHIELD
            pygame.draw.rect(screen, c, (powerup[0], powerup[1], BLOCK_SIZE, BLOCK_SIZE))

        
        for idx, segment in enumerate(snake):
            c = snake_color
            if shield_active and idx == 0: c = C_PW_SHIELD # Show shield on head
            pygame.draw.rect(screen, c, (segment[0], segment[1], BLOCK_SIZE, BLOCK_SIZE))

        
        hud_text = font.render(f"Score: {score}  Level: {level}  Best: {personal_best}", True, (255, 255, 255))
        screen.blit(hud_text, (10, 10))
        
        if active_effect:
            eff_text = font.render(f"Active: {active_effect.upper()}", True, (255, 255, 0))
            screen.blit(eff_text, (WIDTH - 200, 10))

        pygame.display.flip()
        clock.tick(fps)

    return score, level