import pygame
import math
import time


class Clock:
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
        self.font = pygame.font.SysFont('Arial', 36, bold=True)
        self.minute_hand = self.make_hand(int(radius * 0.6), 6, (200, 0, 0))
        self.second_hand = self.make_hand(int(radius * 0.75), 3, (0, 0, 200))

    def make_hand(self, length, width, color):
        surf = pygame.Surface((width * 2 + 1, length * 2), pygame.SRCALPHA)
        cx = width
        cy = length
        pygame.draw.line(surf, color, (cx, cy), (cx, cy - length), width)
        pygame.draw.circle(surf, color, (cx, cy - length), width)
        return surf

    def draw_hand(self, screen, hand_surf, angle):
        rotated = pygame.transform.rotate(hand_surf, angle)
        rect = rotated.get_rect(center=self.center)
        screen.blit(rotated, rect)

    def draw(self, screen):
        now = time.localtime()
        minutes = now.tm_min
        seconds = now.tm_sec

        pygame.draw.circle(screen, (255, 255, 255), self.center, self.radius)
        pygame.draw.circle(screen, (0, 0, 0), self.center, self.radius, 3)

        for i in range(60):
            angle = math.radians(i * 6 - 90)
            r1 = self.radius - (15 if i % 5 == 0 else 8)
            r2 = self.radius - 3
            w = 2 if i % 5 == 0 else 1
            p1 = (self.center[0] + r1 * math.cos(angle),
                  self.center[1] + r1 * math.sin(angle))
            p2 = (self.center[0] + r2 * math.cos(angle),
                  self.center[1] + r2 * math.sin(angle))
            pygame.draw.line(screen, (0, 0, 0), p1, p2, w)

        min_angle = -(minutes * 6 + seconds * 0.1)
        self.draw_hand(screen, self.minute_hand, min_angle)

        sec_angle = -(seconds * 6)
        self.draw_hand(screen, self.second_hand, sec_angle)

        pygame.draw.circle(screen, (50, 50, 50), self.center, 6)

        time_str = f"{minutes:02d}:{seconds:02d}"
        text = self.font.render(time_str, True, (0, 0, 0))
        rect = text.get_rect(center=(self.center[0], self.center[1] + self.radius + 40))
        screen.blit(text, rect)