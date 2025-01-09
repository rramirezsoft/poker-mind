import pygame
import sys
import os
from utils import sound_manager  
from screens.title_screen import TitleScreen

WIDTH, HEIGHT = 800, 600
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Poker Mind")
    pygame.display.set_icon(pygame.image.load(os.path.join(BASE_DIR, "assets", "img", "res", "icon.png")))

    # Música de fondo
    sound_manager.load_music(os.path.join(BASE_DIR, "assets", "sounds", "music"))
    sound_manager.play_music(loops=-1, start=0.0) 

    current_screen = TitleScreen()

    # Bucle principal
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            new_screen = current_screen.handle_events(event)
            if new_screen is None:
                running = False
            elif new_screen is not current_screen:
                current_screen = new_screen

        if running:
            screen.fill((0, 0, 0))
            current_screen.draw(screen)
            pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

