import pygame
import math
import sys
from datetime import datetime
from collections import deque

pygame.init()

WIDTH, HEIGHT = 950, 650
TOOLBAR_H = 80
CANVAS_Y = TOOLBAR_H

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paint")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
GRAY = (180, 180, 180)
DARK = (60, 60, 60)

font = pygame.font.SysFont('Arial', 13)
text_font = pygame.font.SysFont('Arial', 22)

COLORS = [BLACK, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, ORANGE, WHITE]

PEN, LINE, RECT, SQUARE, CIRCLE, RTRI, ETRI, RHOMB, ERASER, FILL, TEXT = (
    'Pen', 'Line', 'Rect', 'Square', 'Circle', 'RTri', 'ETri', 'Rhomb',
    'Eraser', 'Fill', 'Text')
TOOLS = [PEN, LINE, RECT, SQUARE, CIRCLE, RTRI, ETRI, RHOMB, ERASER, FILL, TEXT]
SHAPES = {LINE, RECT, SQUARE, CIRCLE, RTRI, ETRI, RHOMB}

SIZES = {1: 2, 2: 5, 3: 10}

canvas = pygame.Surface((WIDTH, HEIGHT - TOOLBAR_H))
canvas.fill(WHITE)

current_color = BLACK
current_tool = PEN
brush_key = 2
drawing = False
start_pos = None

text_mode = False
text_pos = None
text_buffer = ''


def brush():
    return SIZES[brush_key]


def square_rect(s, e):
    dx, dy = e[0] - s[0], e[1] - s[1]
    side = min(abs(dx), abs(dy))
    sx = s[0] + (side if dx >= 0 else -side)
    sy = s[1] + (side if dy >= 0 else -side)
    return pygame.Rect(min(s[0], sx), min(s[1], sy), side, side)


def right_tri(s, e):
    return [s, (e[0], s[1]), (e[0], e[1])]


def equi_tri(s, e):
    w = abs(e[0] - s[0])
    xl = min(s[0], e[0])
    h = w * math.sqrt(3) / 2
    if e[1] < s[1]:
        yb = max(s[1], e[1])
        return [(xl, yb), (xl + w, yb), (xl + w / 2, yb - h)]
    yt = min(s[1], e[1])
    return [(xl, yt + h), (xl + w, yt + h), (xl + w / 2, yt)]


def rhomb_pts(s, e):
    cx, cy = (s[0] + e[0]) / 2, (s[1] + e[1]) / 2
    return [(cx, min(s[1], e[1])), (max(s[0], e[0]), cy),
            (cx, max(s[1], e[1])), (min(s[0], e[0]), cy)]


def draw_shape(surf, tool, color, s, e, w):
    if tool == LINE:
        pygame.draw.line(surf, color, s, e, w)
    elif tool == RECT:
        x = min(s[0], e[0]); y = min(s[1], e[1])
        pygame.draw.rect(surf, color, (x, y, abs(e[0] - s[0]), abs(e[1] - s[1])), w)
    elif tool == SQUARE:
        pygame.draw.rect(surf, color, square_rect(s, e), w)
    elif tool == CIRCLE:
        cx, cy = (s[0] + e[0]) // 2, (s[1] + e[1]) // 2
        r = max(abs(e[0] - s[0]), abs(e[1] - s[1])) // 2
        if r > 0:
            pygame.draw.circle(surf, color, (cx, cy), r, w)
    elif tool == RTRI:
        pygame.draw.polygon(surf, color, right_tri(s, e), w)
    elif tool == ETRI:
        pygame.draw.polygon(surf, color, equi_tri(s, e), w)
    elif tool == RHOMB:
        pygame.draw.polygon(surf, color, rhomb_pts(s, e), w)


# bucket fill, BFS over pixels with same color
def flood_fill(surf, pos, new_color):
    target = surf.get_at(pos)
    nc = (*new_color, 255) if len(new_color) == 3 else new_color
    if tuple(target) == tuple(nc):
        return
    w, h = surf.get_size()
    q = deque([pos])
    seen = set()
    while q:
        x, y = q.popleft()
        if (x, y) in seen or x < 0 or y < 0 or x >= w or y >= h:
            continue
        if tuple(surf.get_at((x, y))) != tuple(target):
            continue
        seen.add((x, y))
        surf.set_at((x, y), nc)
        q.append((x + 1, y))
        q.append((x - 1, y))
        q.append((x, y + 1))
        q.append((x, y - 1))


def save_canvas():
    name = f"paint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    pygame.image.save(canvas, name)
    print(f"data: saved as {name}")


def draw_toolbar():
    pygame.draw.rect(screen, DARK, (0, 0, WIDTH, TOOLBAR_H))
    x = 8
    for t in TOOLS:
        rect = pygame.Rect(x, 6, 58, 22)
        bg = WHITE if t == current_tool else GRAY
        pygame.draw.rect(screen, bg, rect)
        pygame.draw.rect(screen, BLACK, rect, 1)
        screen.blit(font.render(t, True, BLACK), (x + 4, 10))
        x += 62

    x = 8
    for c in COLORS:
        r = pygame.Rect(x, 34, 20, 20)
        pygame.draw.rect(screen, c, r)
        pygame.draw.rect(screen, WHITE if c == current_color else BLACK, r,
                         2 if c == current_color else 1)
        x += 24

    x = 240
    for k in (1, 2, 3):
        r = pygame.Rect(x, 34, 30, 20)
        pygame.draw.rect(screen, WHITE if k == brush_key else GRAY, r)
        pygame.draw.rect(screen, BLACK, r, 1)
        screen.blit(font.render(f"{k}: {SIZES[k]}", True, BLACK), (x + 2, 38))
        x += 34

    info = "Ctrl+S save  |  C clear  |  1/2/3 brush  |  Esc text cancel"
    screen.blit(font.render(info, True, GRAY), (360, 38))

    pygame.draw.rect(screen, current_color, (WIDTH - 40, 8, 25, 25))
    pygame.draw.rect(screen, WHITE, (WIDTH - 40, 8, 25, 25), 1)


def tool_at(pos):
    x = 8
    for t in TOOLS:
        if pygame.Rect(x, 6, 58, 22).collidepoint(pos):
            return t
        x += 62
    return None


def color_at(pos):
    x = 8
    for c in COLORS:
        if pygame.Rect(x, 34, 20, 20).collidepoint(pos):
            return c
        x += 24
    return None


def size_at(pos):
    x = 240
    for k in (1, 2, 3):
        if pygame.Rect(x, 34, 30, 20).collidepoint(pos):
            return k
        x += 34
    return None


def cpos(pos):
    return (pos[0], pos[1] - CANVAS_Y)


def commit_text():
    global text_mode, text_buffer, text_pos
    if text_buffer and text_pos:
        surf = text_font.render(text_buffer, True, current_color)
        canvas.blit(surf, text_pos)
    text_mode = False
    text_buffer = ''
    text_pos = None


def run():
    global current_color, current_tool, brush_key, drawing, start_pos
    global text_mode, text_pos, text_buffer

    clock = pygame.time.Clock()
    prev = None
    snap = None

    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif ev.type == pygame.KEYDOWN:
                ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL
                if ctrl and ev.key == pygame.K_s:
                    save_canvas()
                    continue
                if text_mode:
                    if ev.key == pygame.K_RETURN:
                        commit_text()
                    elif ev.key == pygame.K_ESCAPE:
                        text_mode = False
                        text_buffer = ''
                        text_pos = None
                    elif ev.key == pygame.K_BACKSPACE:
                        text_buffer = text_buffer[:-1]
                    else:
                        if ev.unicode and ev.unicode.isprintable():
                            text_buffer += ev.unicode
                    continue
                if ev.key == pygame.K_c:
                    canvas.fill(WHITE)
                elif ev.key in (pygame.K_1, pygame.K_KP1):
                    brush_key = 1
                elif ev.key in (pygame.K_2, pygame.K_KP2):
                    brush_key = 2
                elif ev.key in (pygame.K_3, pygame.K_KP3):
                    brush_key = 3

            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if ev.pos[1] < TOOLBAR_H:
                    t = tool_at(ev.pos)
                    if t:
                        if text_mode:
                            commit_text()
                        current_tool = t
                    c = color_at(ev.pos)
                    if c:
                        current_color = c
                    sk = size_at(ev.pos)
                    if sk:
                        brush_key = sk
                else:
                    if text_mode:
                        commit_text()
                    if current_tool == FILL:
                        flood_fill(canvas, cpos(ev.pos), current_color)
                    elif current_tool == TEXT:
                        text_mode = True
                        text_pos = cpos(ev.pos)
                        text_buffer = ''
                    else:
                        drawing = True
                        start_pos = cpos(ev.pos)
                        prev = start_pos
                        if current_tool in SHAPES:
                            snap = canvas.copy()

            elif ev.type == pygame.MOUSEBUTTONUP:
                if drawing:
                    cp = cpos(ev.pos)
                    if current_tool in SHAPES:
                        draw_shape(canvas, current_tool, current_color,
                                   start_pos, cp, brush())
                    drawing = False
                    start_pos = None
                    prev = None
                    snap = None

            elif ev.type == pygame.MOUSEMOTION:
                if drawing and ev.pos[1] >= CANVAS_Y:
                    cp = cpos(ev.pos)
                    if current_tool == PEN:
                        if prev:
                            pygame.draw.line(canvas, current_color, prev, cp, brush())
                        prev = cp
                    elif current_tool == ERASER:
                        if prev:
                            pygame.draw.line(canvas, WHITE, prev, cp, brush() * 3)
                        prev = cp

        screen.fill(DARK)

        # show preview while dragging shape
        if drawing and snap and current_tool in SHAPES:
            tmp = snap.copy()
            draw_shape(tmp, current_tool, current_color,
                       start_pos, cpos(pygame.mouse.get_pos()), brush())
            screen.blit(tmp, (0, CANVAS_Y))
        else:
            screen.blit(canvas, (0, CANVAS_Y))

        if text_mode and text_pos:
            tx, ty = text_pos
            preview = text_font.render(text_buffer + '|', True, current_color)
            screen.blit(preview, (tx, ty + CANVAS_Y))

        draw_toolbar()
        pygame.display.flip()
        clock.tick(60)


if __name__ == '__main__':
    run()