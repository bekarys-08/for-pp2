import pygame
import random
from config import *
class Snake:

    def __init__(self, color=GREEN):
        self.color = color
        self.reset()

    def reset(self):
        sx, sy = GRID_W // 2, GRID_H // 2
        self.body      = [(sx, sy), (sx-1, sy), (sx-2, sy)]
        self.direction = RIGHT
        self.next_dir  = RIGHT
        self._grow_by  = 0

    def change_direction(self, d):
        opposite = (-self.direction[0], -self.direction[1])
        if d != opposite:
            self.next_dir = d

    def move(self):
        self.direction = self.next_dir
        hx, hy = self.body[0]
        new_head = (hx + self.direction[0], hy + self.direction[1])
        self.body.insert(0, new_head)
        if self._grow_by > 0:
            self._grow_by -= 1
        else:
            self.body.pop()

    def grow(self, amount=1):
        self._grow_by += amount

    def shrink(self, amount=2):
        for _ in range(amount):
            if len(self.body) > 1:
                self.body.pop()
        return len(self.body) > 1

    def check_wall(self):
        hx, hy = self.body[0]
        return hx < 0 or hx >= GRID_W or hy < 0 or hy >= GRID_H

    def check_self(self):
        return self.body[0] in self.body[1:]

    def check_obstacle(self, obstacles):
        return self.body[0] in obstacles

    def draw(self, surface, grid_show):
        for i, (x, y) in enumerate(self.body):
            rect = pygame.Rect(
                x * GRID_SIZE,
                y * GRID_SIZE + UI_HEIGHT,
                GRID_SIZE - 1, GRID_SIZE - 1
            )
            col = DARK_GREEN if i == 0 else self.color
            pygame.draw.rect(surface, col, rect)
            if i == 0:   # eyes on head
                ex = rect.x + (8 if self.direction == RIGHT else
                                2 if self.direction == LEFT  else 5)
                ey = rect.y + (8 if self.direction == DOWN  else
                                2 if self.direction == UP    else 5)
                pygame.draw.circle(surface, BLACK, (ex, ey), 2)

class Food:
    TYPES = [
        {"name": "Small",  "weight": 5,  "color": GREEN,  "life": 10000},
        {"name": "Medium", "weight": 10, "color": YELLOW, "life": 7000 },
        {"name": "Large",  "weight": 15, "color": RED,    "life": 5000 },
    ]
    _font = None

    def __init__(self):
        if Food._font is None:
            Food._font = pygame.font.SysFont("Arial", 12, bold=True)
        self.pos  = (0, 0)
        self.kind = None
        self.born = 0

    def spawn(self, occupied):
        self.kind = random.choice(self.TYPES)
        self.born = pygame.time.get_ticks()
        self.pos  = _random_free(occupied)

    def expired(self):
        return pygame.time.get_ticks() - self.born > self.kind["life"]

    def time_frac(self):
        elapsed = pygame.time.get_ticks() - self.born
        return max(0.0, 1.0 - elapsed / self.kind["life"])

    def draw(self, surface):
        x, y = self.pos
        rect = pygame.Rect(x*GRID_SIZE, y*GRID_SIZE + UI_HEIGHT,
                           GRID_SIZE-1, GRID_SIZE-1)
        pygame.draw.rect(surface, self.kind["color"], rect)
        # timer bar above cell
        frac = self.time_frac()
        bar_col = (int(255*(1-frac)), int(255*frac), 0)
        pygame.draw.rect(surface, DARK_GRAY, (rect.x, rect.y-4, GRID_SIZE-1, 3))
        pygame.draw.rect(surface, bar_col,   (rect.x, rect.y-4, int((GRID_SIZE-1)*frac), 3))
        lbl = Food._font.render(str(self.kind["weight"]), True, BLACK)
        surface.blit(lbl, lbl.get_rect(center=rect.center))

class PoisonFood:
    _font = None

    def __init__(self):
        if PoisonFood._font is None:
            PoisonFood._font = pygame.font.SysFont("Arial", 12, bold=True)
        self.pos  = None
        self.born = 0
        self.life = 8000    # 8 seconds

    def spawn(self, occupied):
        self.pos  = _random_free(occupied)
        self.born = pygame.time.get_ticks()

    def expired(self):
        return pygame.time.get_ticks() - self.born > self.life

    def draw(self, surface):
        if self.pos is None:
            return
        x, y = self.pos
        rect = pygame.Rect(x*GRID_SIZE, y*GRID_SIZE + UI_HEIGHT,
                           GRID_SIZE-1, GRID_SIZE-1)
        pygame.draw.rect(surface, DARK_RED, rect)
        lbl = PoisonFood._font.render("✕", True, WHITE)
        surface.blit(lbl, lbl.get_rect(center=rect.center))

class PowerUp:
    TYPES = {
        "speed":  {"color": ORANGE, "label": "▶▶", "duration": 5000},
        "slow":   {"color": CYAN,   "label": "▶",  "duration": 5000},
        "shield": {"color": PURPLE, "label": "◈",  "duration": 0   },  # until triggered
    }
    _font = None

    def __init__(self):
        if PowerUp._font is None:
            PowerUp._font = pygame.font.SysFont("Arial", 13, bold=True)
        self.pos   = None
        self.kind  = None
        self.born  = 0
        self.field_life = 8000   # disappears from field after 8 s

    def spawn(self, occupied):
        self.kind = random.choice(list(self.TYPES.keys()))
        self.pos  = _random_free(occupied)
        self.born = pygame.time.get_ticks()

    def field_expired(self):
        return (self.pos is not None and
                pygame.time.get_ticks() - self.born > self.field_life)

    def draw(self, surface):
        if self.pos is None:
            return
        x, y = self.pos
        rect = pygame.Rect(x*GRID_SIZE, y*GRID_SIZE + UI_HEIGHT,
                           GRID_SIZE-1, GRID_SIZE-1)
        info = self.TYPES[self.kind]
        pygame.draw.rect(surface, info["color"], rect, border_radius=4)
        pygame.draw.rect(surface, WHITE, rect, 1, border_radius=4)
        lbl = PowerUp._font.render(info["label"], True, WHITE)
        surface.blit(lbl, lbl.get_rect(center=rect.center))

def make_obstacles(level, snake_body):
    if level < 3:
        return set()
    count   = min((level - 2) * 3, 20)
    blocked = set(snake_body)
    hx, hy = snake_body[0]
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            blocked.add((hx+dx, hy+dy))
    result = set()
    attempts = 0
    while len(result) < count and attempts < 500:
        attempts += 1
        x = random.randint(0, GRID_W-1)
        y = random.randint(0, GRID_H-1)
        if (x, y) not in blocked:
            result.add((x, y))
    return result

def draw_obstacles(surface, obstacles):
    for (x, y) in obstacles:
        rect = pygame.Rect(x*GRID_SIZE, y*GRID_SIZE + UI_HEIGHT,
                           GRID_SIZE-1, GRID_SIZE-1)
        pygame.draw.rect(surface, GRAY, rect)
        pygame.draw.rect(surface, WHITE, rect, 1)

def _random_free(occupied):
    while True:
        pos = (random.randint(0, GRID_W-1), random.randint(0, GRID_H-1))
        if pos not in occupied:
            return pos