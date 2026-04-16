import pygame

class Ball:
    def __init__(self, x, y, radius, color, speed):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed = speed

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (self.x, self.y), self.radius)

    def move(self, dx, dy, screen_width, screen_height):
        new_x = self.x + dx * self.speed
        new_y = self.y + dy * self.speed

        if self.radius <= new_x <= screen_width - self.radius:
            self.x = new_x
        if self.radius <= new_y <= screen_height - self.radius:
            self.y = new_y