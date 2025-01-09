import pygame
import os
from utils import load_image, load_font, sound_manager, load_card_images
from screens.preflop_screen import PreflopScreen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class TitleScreen():
    def __init__(self):
        # Imgaen de fondo y fuentes
        self.background = load_image(os.path.join(BASE_DIR, '..', 'assets', 'img', 'background', 'background_title.png'), (800, 600))
        self.font_title = load_font(os.path.join(BASE_DIR, '..', 'assets', 'fonts', 'poker_font.ttf'), 90)
        self.font_button = load_font(os.path.join(BASE_DIR, '..', 'assets', 'fonts', 'poker_font.ttf'), 36)

        # Título del juego con sombra
        self.title_text = self.font_title.render("Poker Mind", True, (255, 255, 255))
        self.title_shadow = self.font_title.render("Poker Mind", True, (0, 0, 0))  

        # Botón "Entrar"
        self.button_rect = pygame.Rect(300, 450, 200, 60)
        self.button_color = (30, 136, 229)  
        self.button_hover_color = (50, 150, 255) 
        self.button_sound = sound_manager.load_sound("button", os.path.join(BASE_DIR,"..", "assets", "sounds", "sfx", "click.mp3"))

        # Texto del botón
        self.button_text = self.font_button.render("Comenzar", True, (255, 255, 255))
        self.text_rect = self.button_text.get_rect(center=self.button_rect.center)

        # Cartas de la baraja
        self.card_images = {}
        load_card_images(self.card_images, BASE_DIR)

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.button_rect.collidepoint(event.pos):
                sound_manager.play_sound("button")
                return PreflopScreen()
        return self

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        # Título con sombra
        screen.blit(self.title_shadow, (self.title_text.get_rect(center=(400, 150)).x + 3, self.title_text.get_rect(center=(400, 150)).y + 3))
        screen.blit(self.title_text, self.title_text.get_rect(center=(400, 150)))

        # Mostramos las cartas de Full House
        full_house_cards = ['141', '143', '144', '132', '134']

        card_width, card_height = 80, 120 
        margin = 15  
        total_width = (card_width * 5) + (margin * 4)  
        start_x = (800 - total_width) // 2 
        start_y = 250  

        # Dibujar las cartas
        for i, card_id in enumerate(full_house_cards):
            card_image = self.card_images[card_id]
            
            card_image = load_image(os.path.join(BASE_DIR, '..', 'assets', 'img', 'cards', f"{card_id}.png"), (card_width, card_height))

            x_pos = start_x + i * (card_width + margin)
            card_rect = pygame.Rect(x_pos, start_y, card_width, card_height)
            screen.blit(card_image, card_rect)  # Dibujar la carta

        # Dibuja el botón con efectos
        if self.button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, self.button_hover_color, self.button_rect, border_radius=15)
        else:
            pygame.draw.rect(screen, self.button_color, self.button_rect, border_radius=15)
        
        screen.blit(self.button_text, self.text_rect)  # Texto del botón

        pygame.display.flip()
