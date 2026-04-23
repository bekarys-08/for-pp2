import pygame
import math

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint – Practice 11")

PALETTE = [
    (0,   0,   0),   (255, 255, 255), (220, 50,  50),
    (50,  200, 50),  (50,  100, 220), (255, 215, 0),
    (150, 50,  200), (255, 140, 0),   (0,   200, 200),
    (180, 90,  40),
]

TOOLBAR_H   = 70
SWATCH_SIZE = 40

current_color = (0, 0, 0)
brush_size    = 8
tool          = "pencil"
drawing       = False
start_pos     = (0, 0)

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 20)


TOOLS = [
    ("Pencil",   "pencil"),
    ("Eraser",   "eraser"),
    ("Rect",     "rect"),
    ("Square",   "square"),
    ("Circle",   "circle"),
    ("RTri",     "rtri"),    
    ("ETri",     "etri"),    
    ("Rhombus",  "rhombus"),
]

def draw_toolbar():
    pygame.draw.rect(screen, (45, 45, 45), (0, 0, WIDTH, TOOLBAR_H))
    
    for i, col in enumerate(PALETTE):
        x = 10 + i * (SWATCH_SIZE + 4)
        pygame.draw.rect(screen, col, (x, 12, SWATCH_SIZE, SWATCH_SIZE))
        if col == current_color:
            pygame.draw.rect(screen, WHITE, (x, 12, SWATCH_SIZE, SWATCH_SIZE), 3)
    
    for i, (label, t) in enumerate(TOOLS):
        col = (90, 170, 90) if tool == t else (75, 75, 75)
        row = i // 4
        col_idx = i % 4
        bx = 465 + col_idx * 80
        by = 8 + row * 28
        pygame.draw.rect(screen, col, (bx, by, 74, 22), border_radius=4)
        txt = font.render(label, True, WHITE)
        screen.blit(txt, (bx + 4, by + 4))
    size_txt = font.render(f"Size:{brush_size} Scroll=resize C=clear", True, (160, 160, 160))
    screen.blit(size_txt, (788, 28))

WHITE = (255, 255, 255)

def get_tool_click(mx, my):
    for i, (_, t) in enumerate(TOOLS):
        row = i // 4
        col_idx = i % 4
        bx = 465 + col_idx * 80
        by = 8 + row * 28
        if bx <= mx <= bx + 74 and by <= my <= by + 22:
            return t
    return None

def get_color_click(mx, my):
    for i, col in enumerate(PALETTE):
        x = 10 + i * (SWATCH_SIZE + 4)
        if x <= mx <= x + SWATCH_SIZE and 12 <= my <= 12 + SWATCH_SIZE:
            return col
    return None


def draw_square(surf, color, p1, p2, lw):
    """Draw a square using the shorter side."""
    side = min(abs(p2[0]-p1[0]), abs(p2[1]-p1[1]))
    sx = p1[0] if p2[0] >= p1[0] else p1[0] - side
    sy = p1[1] if p2[1] >= p1[1] else p1[1] - side
    pygame.draw.rect(surf, color, (sx, sy, side, side), lw)

def draw_right_triangle(surf, color, p1, p2, lw):
    """Right-angle triangle: right angle at bottom-left."""
    pts = [p1, (p1[0], p2[1]), p2]
    pygame.draw.polygon(surf, color, pts, lw)

def draw_equilateral_triangle(surf, color, p1, p2, lw):
    """Equilateral triangle with base from p1 to p2."""
    bx1, by = p1
    bx2     = p2[0]
    h = int(abs(bx2 - bx1) * math.sqrt(3) / 2)
    apex_x = (bx1 + bx2) // 2
    apex_y = by - h
    pts = [(bx1, by), (bx2, by), (apex_x, apex_y)]
    pygame.draw.polygon(surf, color, pts, lw)

def draw_rhombus(surf, color, p1, p2, lw):
    """Rhombus centered between p1 and p2."""
    cx = (p1[0] + p2[0]) // 2
    cy = (p1[1] + p2[1]) // 2
    hw = abs(p2[0] - p1[0]) // 2  
    hh = abs(p2[1] - p1[1]) // 2  
    pts = [(cx, cy - hh), (cx + hw, cy), (cx, cy + hh), (cx - hw, cy)]
    pygame.draw.polygon(surf, color, pts, lw)

def render_shape(surf, t, color, p1, p2, lw):
    """Dispatch shape drawing to the correct function."""
    if   t == "rect":    pygame.draw.rect(surf, color,
                             (min(p1[0],p2[0]), min(p1[1],p2[1]),
                              abs(p2[0]-p1[0]), abs(p2[1]-p1[1])), lw)
    elif t == "square":  draw_square(surf, color, p1, p2, lw)
    elif t == "circle":
        cx = (p1[0]+p2[0])//2; cy = (p1[1]+p2[1])//2
        r  = max(abs(p2[0]-p1[0]), abs(p2[1]-p1[1]))//2
        pygame.draw.circle(surf, color, (cx, cy), r, lw)
    elif t == "rtri":    draw_right_triangle(surf, color, p1, p2, lw)
    elif t == "etri":    draw_equilateral_triangle(surf, color, p1, p2, lw)
    elif t == "rhombus": draw_rhombus(surf, color, p1, p2, lw)

SHAPE_TOOLS = {"rect", "square", "circle", "rtri", "etri", "rhombus"}

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                canvas.fill(WHITE)

        if event.type == pygame.MOUSEWHEEL:
            brush_size = max(1, min(50, brush_size + event.y))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if my < TOOLBAR_H:
                t = get_tool_click(mx, my)
                c = get_color_click(mx, my)
                if t: tool = t
                if c: current_color = c
            else:
                drawing   = True
                start_pos = (mx, my - TOOLBAR_H)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and drawing:
            drawing = False
            ex, ey = pygame.mouse.get_pos()
            ey -= TOOLBAR_H
            if tool in SHAPE_TOOLS:
                render_shape(canvas, tool, current_color, start_pos, (ex, ey), brush_size)

        if event.type == pygame.MOUSEMOTION and drawing:
            mx, my = pygame.mouse.get_pos()
            cy = my - TOOLBAR_H
            if cy > 0:
                if tool == "pencil":
                    pygame.draw.circle(canvas, current_color, (mx, cy), brush_size//2)
                elif tool == "eraser":
                    pygame.draw.circle(canvas, WHITE, (mx, cy), brush_size)

    
    screen.fill(WHITE)
    screen.blit(canvas, (0, TOOLBAR_H))

    
    if drawing and tool in SHAPE_TOOLS:
        mx, my = pygame.mouse.get_pos()
        ey = my - TOOLBAR_H
        
        tmp = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H), pygame.SRCALPHA)
        render_shape(tmp, tool, current_color, start_pos, (mx, ey), brush_size)
        screen.blit(tmp, (0, TOOLBAR_H))

    draw_toolbar()
    pygame.display.flip()

pygame.quit()
