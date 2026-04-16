import pygame

playlist = ["track1.mp3", "track2.mp3"]
current_index = 0

def play_track():
    if playlist:
        pygame.mixer.music.load("music/" + playlist[current_index])
        pygame.mixer.music.play()

def next_track():
    global current_index
    if playlist:
        current_index = (current_index + 1) % len(playlist)
        play_track()

def prev_track():
    global current_index
    if playlist:
        current_index = (current_index - 1) % len(playlist)
        play_track()

def toggle_pause():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
    else:
        pygame.mixer.music.unpause()
        