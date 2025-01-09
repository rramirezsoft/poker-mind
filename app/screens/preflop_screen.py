import pygame
import os
from utils import load_image, load_font, load_card_images, sound_manager
from screens.hand_screen import HandScreen

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class PreflopScreen():
    def __init__(self):
        # Cargamos el fonto de pantalla y la fuente
        self.background = load_image(os.path.join(BASE_DIR, '..', 'assets', 'img', 'background', 'background_menu.png'), (800, 600))
        self.font = load_font(os.path.join(BASE_DIR, '..', 'assets', 'fonts', 'poker_font.ttf'), 74)
        
        # Cartas de la baraja
        self.card_images = {}
        self.card_rects = []
        load_card_images(self.card_images, BASE_DIR)

        # Área de selección
        self.selected_cards = []

        # Entrada para el número de rivales
        self.rivals_input = ""  
        self.input_active = False  
        self.input_rect = pygame.Rect(525, 470, 200, 40)  

        # Botón de continuar
        self.continue_button = pygame.Rect(325, 540, 150, 40)  # Rectángulo del botón
        self.button_text = load_font(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'poker_font.ttf'), 24).render("Continuar", True, (255, 255, 255))

        # Tamaño de fuente
        self.main_font = load_font(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'poker_font.ttf'), 30)
        self.secondary_font = load_font(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'poker_font.ttf'), 24)

        # Colores
        self.selected_border_color = (255, 215, 0) 

    def handle_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Manejo de selección de cartas
            for rect, card_id in self.card_rects:
                if rect.collidepoint(event.pos):
                    self.handle_card_selection(card_id)

            # Activamos cuadro de texto si se hace clic en él
            if self.input_rect.collidepoint(event.pos):
                self.input_active = True
            else:
                self.input_active = False

            # Si todo está corréctamente seleccionado, pasamos a la siguiente pantalla
            if self.continue_button.collidepoint(event.pos) and len(self.selected_cards) == 2 and self.rivals_input.isdigit() and 1 <= int(self.rivals_input) <= 8:
                sound_manager.play_sound("button")
                return HandScreen(self.selected_cards[0], self.selected_cards[1], int(self.rivals_input))

        # Capturamos entrada de texto
        if event.type == pygame.KEYDOWN and self.input_active:
            if event.key == pygame.K_BACKSPACE:
                self.rivals_input = self.rivals_input[:-1]  
            elif event.unicode.isdigit() and len(self.rivals_input) < 1:
                self.rivals_input += event.unicode

        return self

    def handle_card_selection(self, card_id):
        if card_id in self.selected_cards:
            self.selected_cards.remove(card_id)
        elif len(self.selected_cards) < 2:  # Tiene que haber 2 cartas seleccionadas
            self.selected_cards.append(card_id)

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        # Mostramos las cartas en la pantalla
        card_width, card_height = 50, 75  
        margin_x, margin_y = 10, 10  
        rows, cols = 4, 13 

        # Las centramos en la pantalla
        total_width = (card_width + margin_x) * cols - margin_x
        total_height = (card_height + margin_y) * rows - margin_y
        start_x = (800 - total_width) // 2  
        start_y = (600 - total_height) // 2 - 50 

        self.card_rects = []
        card_id_list = []

        # Ordenamos las cartas por palo y valor (Picas, Tréboles, Diamantes, Corazones)
        palos = ['♠', '♣', '♦', '♥']
        palo_map = {'♠': 1, '♣': 2, '♦': 3, '♥': 4}
        
        for palo in palos:
            for valor in range(2, 15):  # De 2 a A (valor 14)
                card_id = f'{valor}{palo_map[palo]}'
                card_id_list.append(card_id)

        card_index = 0
        # Organizamos las cartas en 4 filas y 13 columnas
        for row in range(rows):
            for col in range(cols):
                card_id = card_id_list[card_index]
                card_image = self.card_images[card_id]
                x_pos = start_x + col * (card_width + margin_x)
                y_pos = start_y + row * (card_height + margin_y)
                card_rect = pygame.Rect(x_pos, y_pos, card_width, card_height)
                self.card_rects.append((card_rect, card_id))

                # Mostrar la carta
                if card_id in self.selected_cards:
                    # Borde dorado y sutil para la carta seleccionada
                    pygame.draw.rect(screen, self.selected_border_color, card_rect, 4) 
                screen.blit(card_image, card_rect)
                card_index += 1

        # Texto de arriba
        main_text = self.main_font.render("Selecciona tus 2 cartas iniciales", True, (255, 255, 255))
        instruction_rect = main_text.get_rect(center=(400, start_y - 40))
        screen.blit(main_text, instruction_rect)

        # Texto de cartas seleccionadas
        selected_cards_text = self.secondary_font.render("Cartas seleccionadas:", True, (255, 255, 255))
        screen.blit(selected_cards_text, (30, 430))

        # Dibujamos las cartas seleccionadas
        selected_start_x = 30  
        selected_start_y = 470
        selected_margin = 20
        card_width, card_height = 60, 90

        for i, card_id in enumerate(self.selected_cards):
            card_image = self.card_images[card_id]
            scaled_card = load_image(os.path.join(BASE_DIR, '..', 'assets', 'img', 'cards', f'{card_id}.png'), (card_width, card_height))
            x_pos = selected_start_x + i * (card_width + selected_margin)
            y_pos = selected_start_y
            screen.blit(scaled_card, (x_pos, y_pos))

        # Mostramos el cuadro de texto para los rivales
        input_color = (219, 232, 221) if self.input_active else (255, 255, 255)  
        pygame.draw.rect(screen, input_color, self.input_rect, border_radius=10) 
        pygame.draw.rect(screen, (0, 0, 0), self.input_rect, 2, border_radius=10)
        rivals_text = self.secondary_font.render(self.rivals_input, True, (0, 0, 0))
        screen.blit(rivals_text, (self.input_rect.x + 10, self.input_rect.y + 5))


        # Mostramos el texto
        rivals_label = self.secondary_font.render("Número de rivales (1-8):", True, (255, 255, 255))
        screen.blit(rivals_label, (self.input_rect.x, self.input_rect.y - 40))

        # Mostramos el botón de continuar
        if len(self.selected_cards) == 2 and self.rivals_input.isdigit() and 1 <= int(self.rivals_input) <= 8:
            pygame.draw.rect(screen, (34, 193, 34), self.continue_button, border_radius=10)  
        else:
            pygame.draw.rect(screen, (169, 169, 169), self.continue_button, border_radius=10)  
        screen.blit(self.button_text, (self.continue_button.x + 25, self.continue_button.y + 8)) 

        pygame.display.flip()



