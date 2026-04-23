import pygame

pygame.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")


PALETTE = [
    (0,   0,   0),    # Black
    (255, 255, 255),  # White
    (220, 50,  50),   # Red
    (50,  200, 50),   # Green
    (50,  100, 220),  # Blue
    (255, 215, 0),    # Yellow
    (150, 50,  200),  # Purple
    (255, 140, 0),    # Orange
    (0,   200, 200),  # Cyan
    (180, 90,  40),   # Brown
]

TOOLBAR_H = 70       
SWATCH_SIZE = 40      

current_color = (0, 0, 0)
brush_size    = 8
tool          = "pencil"   
drawing       = False
start_pos     = (0, 0)


canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H))
canvas.fill((255, 255, 255))

clock = pygame.time.Clock()
font  = pygame.font.SysFont(None, 22)

def draw_toolbar():
    """Draw the toolbar at the top of the screen."""
    pygame.draw.rect(screen, (45, 45, 45), (0, 0, WIDTH, TOOLBAR_H))

   
    for i, col in enumerate(PALETTE):
        x = 10 + i * (SWATCH_SIZE + 5)
        pygame.draw.rect(screen, col, (x, 10, SWATCH_SIZE, SWATCH_SIZE))
        
        if col == current_color:
            pygame.draw.rect(screen, (255, 255, 255), (x, 10, SWATCH_SIZE, SWATCH_SIZE), 3)

    
    tools = [("Pencil", "pencil"), ("Eraser", "eraser"),
             ("Rect",   "rect"),   ("Circle", "circle")]
    btn_x = 530
    for label, t in tools:
        color = (100, 180, 100) if tool == t else (80, 80, 80)
        pygame.draw.rect(screen, color, (btn_x, 15, 75, 32), border_radius=5)
        txt = font.render(label, True, (255, 255, 255))
        screen.blit(txt, (btn_x + 8, 22))
        btn_x += 85

    size_txt = font.render(f"Size: {brush_size}", True, (200, 200, 200))
    screen.blit(size_txt, (820, 20))
    hint = font.render("Scroll=size  C=clear", True, (150, 150, 150))
    screen.blit(hint, (820, 42))

def get_tool_from_click(mx, my):
    """Return which tool was clicked, or None."""
    tools = ["pencil", "eraser", "rect", "circle"]
    btn_x = 530
    for t in tools:
        if btn_x <= mx <= btn_x + 75 and 15 <= my <= 47:
            return t
        btn_x += 85
    return None

def get_color_from_click(mx, my):
    """Return color from palette click, or None."""
    for i, col in enumerate(PALETTE):
        x = 10 + i * (SWATCH_SIZE + 5)
        if x <= mx <= x + SWATCH_SIZE and 10 <= my <= 10 + SWATCH_SIZE:
            return col
    return None

running = True
preview_surf = None  

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                canvas.fill((255, 255, 255))  

        if event.type == pygame.MOUSEWHEEL:
            brush_size = max(1, min(50, brush_size + event.y))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if my < TOOLBAR_H:
                clicked_tool  = get_tool_from_click(mx, my)
                clicked_color = get_color_from_click(mx, my)
                if clicked_tool:
                    tool = clicked_tool
                if clicked_color:
                    current_color = clicked_color
            else:
                drawing   = True
                start_pos = (mx, my - TOOLBAR_H)

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if drawing:
                drawing = False
                ex, ey = pygame.mouse.get_pos()
                ey -= TOOLBAR_H
                if tool == "rect":
                    x = min(start_pos[0], ex)
                    y = min(start_pos[1], ey)
                    w = abs(ex - start_pos[0])
                    h = abs(ey - start_pos[1])
                    pygame.draw.rect(canvas, current_color, (x, y, w, h), brush_size)
                elif tool == "circle":
                    cx = (start_pos[0] + ex) // 2
                    cy = (start_pos[1] + ey) // 2
                    r  = max(abs(ex - start_pos[0]), abs(ey - start_pos[1])) // 2
                    pygame.draw.circle(canvas, current_color, (cx, cy), r, brush_size)

        if event.type == pygame.MOUSEMOTION and drawing:
            mx, my = event.pos
            cy = my - TOOLBAR_H
            if cy > 0:
                if tool == "pencil":
                    pygame.draw.circle(canvas, current_color, (mx, cy), brush_size // 2)
                elif tool == "eraser":
                    pygame.draw.circle(canvas, (255, 255, 255), (mx, cy), brush_size)

    
    screen.fill((255, 255, 255))
    screen.blit(canvas, (0, TOOLBAR_H))

    
    if drawing and tool in ("rect", "circle"):
        mx, my = pygame.mouse.get_pos()
        ey = my - TOOLBAR_H
        if tool == "rect":
            x = min(start_pos[0], mx)
            y = min(start_pos[1], ey) + TOOLBAR_H
            w = abs(mx - start_pos[0])
            h = abs(ey - start_pos[1])
            pygame.draw.rect(screen, current_color, (x, y, w, h), brush_size)
        elif tool == "circle":
            cx = (start_pos[0] + mx) // 2
            cy = (start_pos[1] + ey) // 2 + TOOLBAR_H
            r  = max(abs(mx - start_pos[0]), abs(ey - start_pos[1])) // 2
            pygame.draw.circle(screen, current_color, (cx, cy), r, brush_size)

    draw_toolbar()
    pygame.display.flip()

pygame.quit()
