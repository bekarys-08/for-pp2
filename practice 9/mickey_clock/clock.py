import pygame
import math
from datetime import datetime

class MickeyClock:
    def __init__(self, center_x, center_y):
        self.center = (center_x, center_y)
        
        try:
            self.bg_img = pygame.image.load("c:/Users/10W030825/Desktop/for pp2/practice 9/mickey_clock/images/mickey_hand.png").convert()
            self.bg_img = pygame.transform.scale(self.bg_img, (600, 600))
        except Exception:
            self.bg_img = pygame.Surface((600, 600))
            self.bg_img.fill((255, 255, 255))

    def draw_hand(self, surface, color, length, width, angle_degrees):
        angle_radians = math.radians(angle_degrees - 90)
        
        end_x = self.center[0] + length * math.cos(angle_radians)
        end_y = self.center[1] + length * math.sin(angle_radians)
        
        pygame.draw.line(surface, color, self.center, (end_x, end_y), width)

    def draw(self, surface):
        surface.blit(self.bg_img, (0, 0))
        
        current_time = datetime.now()
        sec_angle = current_time.second * 6
        min_angle = current_time.minute * 6 + (current_time.second * 0.1)

        self.draw_hand(surface, (0, 0, 0), length=150, width=8, angle_degrees=min_angle)
        self.draw_hand(surface, (255, 0, 0), length=200, width=3, angle_degrees=sec_angle)
        
        pygame.draw.circle(surface, (50, 50, 50), self.center, 12)