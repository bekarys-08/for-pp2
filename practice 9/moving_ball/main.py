import pygame
import sys
from ball import Ball

def main():
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Moving Ball Game")
    clock = pygame.time.Clock()

    my_ball = Ball(WIDTH // 2, HEIGHT // 2, 25, (255, 0, 0), 20)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    my_ball.move(0, -1, WIDTH, HEIGHT)
                elif event.key == pygame.K_DOWN:
                    my_ball.move(0, 1, WIDTH, HEIGHT)
                elif event.key == pygame.K_LEFT:
                    my_ball.move(-1, 0, WIDTH, HEIGHT)
                elif event.key == pygame.K_RIGHT:
                    my_ball.move(1, 0, WIDTH, HEIGHT)

        screen.fill((255, 255, 255))
        my_ball.draw(screen)
        pygame.display.flip()
        
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()