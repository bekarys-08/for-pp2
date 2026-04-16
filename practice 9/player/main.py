import pygame
import player

pygame.init()
screen = pygame.display.set_mode((400, 200))
pygame.display.set_caption("Music Player")

font = pygame.font.Font(None, 30)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: player.play_track()
            if event.key == pygame.K_s: pygame.mixer.music.stop()
            if event.key == pygame.K_SPACE: player.toggle_pause()
            if event.key == pygame.K_n: player.next_track()
            if event.key == pygame.K_b: player.prev_track()

    screen.fill((255, 255, 255))

    text = font.render("P:play, Space:stop, n, b: next", True, (0, 0, 0))
    screen.blit(text, (20, 60))
    

    if player.playlist:
        track_name = font.render(f"Track: {player.playlist[player.current_index]}", True, (0, 0, 255))
        screen.blit(track_name, (20, 40))

    pygame.display.flip()

pygame.quit()