import pygame
import os
from utils import load_image, load_font, sound_manager, load_card_images
from itertools import combinations
from collections import Counter
from keras.models import load_model  # type: ignore
import joblib
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class HandScreen:
    def __init__(self, carta_1, carta_2, num_rivales):
        
        # Fondo
        self.background = load_image(os.path.join(BASE_DIR, '..', 'assets', 'img', 'background', 'poker_table.png'), (800, 600))

         # Fuentes
        self.main_font = load_font(os.path.join(BASE_DIR, '..', 'assets', 'fonts', 'poker_font.ttf'), 28)
        self.small_font = load_font(os.path.join(BASE_DIR, '..', 'assets', 'fonts', 'poker_font.ttf'), 22)

        # Coordenadas para las cartas del jugador
        self.player_card_positions = [
            (335, 500), 
            (405, 500)
        ]

        # Posiciones y tamaños de los placeholders
        self.card_width, self.card_height = 60, 90
        self.margin = 10  
        self.start_x = 190 
        self.start_y = 250

        # Coordenadas para las cartas comunitarias
        self.card_positions = [
            (self.start_x, self.start_y),  # Flop carta 1
            (self.start_x + self.card_width + self.margin, self.start_y),  # Flop carta 2
            (self.start_x + 2 * (self.card_width + self.margin), self.start_y),  # Flop carta 3
            (self.start_x + 3 * (self.card_width + 2 * self.margin), self.start_y),  # Turn
            (self.start_x + 4 * (self.card_width + 3 * self.margin), self.start_y),  # River
        ]

        # Estado de las cartas
        self.selected_cards = [carta_1, carta_2]  # Cartas del jugador
        self.community_cards = [None] * 5  # Para guardar las cartas seleccionadas
        self.current_card_index = 0  # Índice de la carta comunitaria activa

        # Numero de rivales
        self.num_rivales = num_rivales

        # Cargamos las cartas para la mesa
        self.card_images = {}
        load_card_images(self.card_images, BASE_DIR, size=(self.card_width, self.card_height))

        # Cargamos las cartas para el panel de selección
        self.panel_card_images = {}
        load_card_images(self.panel_card_images, BASE_DIR)

        # Estado del panel de selección
        self.showing_panel = False
        self.card_rects = [] 

         # Botón para predecir mano
        self.prediction_button = pygame.Rect(320, 365, 160, 40)
        self.button_text = load_font(os.path.join(os.path.dirname(__file__), '..', 'assets', 'fonts', 'poker_font.ttf'), 24).render("Predicción", True, (255, 255, 255))
        self.enable_button = False
        self.visible_button = True

        # Cambiar el tamaño de la imagen del botón
        self.back_button_image = load_image(os.path.join(BASE_DIR, '..', 'assets', 'img', 'icons', 'back.png'), (60, 60)) 
        self.back_button_rect = self.back_button_image.get_rect(topright=(800 - 20, 20))


        # Cargamos el modelo y el escalador
        self.model = load_model(os.path.join(BASE_DIR, '..', 'models', 'poker_model.keras'))
        self.scaler = joblib.load(os.path.join(BASE_DIR, '..', 'models', 'scaler.pkl'))

        self.prediction_result = None # Resultado de la predicción

    def handle_events(self, event):
        # Si el panel de selección está activo
        if self.showing_panel:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect, card_id in self.card_rects:
                    if rect.collidepoint(event.pos) and card_id not in self.selected_cards:
                        # Seleccionamos la carta y cerramos el panel
                        self.community_cards[self.current_card_index] = card_id
                        self.selected_cards.append(card_id)
                        self.current_card_index += 1

                        # Habilitamos el botón si se han seleccionado 5 cartas
                        if all(self.community_cards):
                            self.enable_button = True

                        if self.current_card_index >= len(self.card_positions):
                            self.current_card_index = len(self.card_positions) - 1
                            self.showing_panel = False
                        else:
                            self.showing_panel = False
                        break
        else:
            if event.type == pygame.MOUSEBUTTONDOWN:
                
                if self.current_card_index < len(self.card_positions):
                    
                    # Habilitamos el panel si se hace clic en el placeholder activo
                    placeholder_x, placeholder_y = self.card_positions[self.current_card_index]
                    placeholder_rect = pygame.Rect(placeholder_x, placeholder_y, self.card_width, self.card_height)
                    if placeholder_rect.collidepoint(event.pos):
                        self.showing_panel = True

                if self.prediction_button.collidepoint(event.pos) and self.enable_button:
                    sound_manager.play_sound("button")
                    self.predict_hand()
                
                if self.back_button_rect.collidepoint(event.pos):
                    sound_manager.play_sound("button")
                    from screens.preflop_screen import PreflopScreen
                    return PreflopScreen()
    
        return self

    def predict_hand(self):    
        
        mano_final = obtener_mejor_mano(self.selected_cards)[1]             
        entrada_manual = {
            "carta_1": int(self.selected_cards[0]),
            "carta_2": int(self.selected_cards[1]),
            "num_rivales": self.num_rivales,
            "mano_preflop": clasificar_mano_preflop(self.selected_cards),
            "flop_1": int(self.community_cards[0]),
            "flop_2": int(self.community_cards[1]),
            "flop_3": int(self.community_cards[2]),
            "mano_flop": clasificar_mano(
                [int(self.selected_cards[0]), int(self.selected_cards[1])] + self.community_cards[:3])[0],
            "turn": int(self.community_cards[3]),
            "mano_turn": clasificar_mano(
                [int(self.selected_cards[0]), int(self.selected_cards[1])] + self.community_cards[:4])[0],
            "river": int(self.community_cards[4]),
            "mano_river": clasificar_mano(
                [int(self.selected_cards[0]), int(self.selected_cards[1])] + self.community_cards)[0],
            "carta_final_1": int(mano_final[0]),
            "carta_final_2": int(mano_final[1]),
            "carta_final_3": int(mano_final[2]),
            "carta_final_4": int(mano_final[3]),
            "carta_final_5": int(mano_final[4])
        }

        columnas = [
            "carta_1", "carta_2", "num_rivales", "mano_preflop",
            "flop_1", "flop_2", "flop_3", "mano_flop", "turn", "mano_turn",
            "river", "mano_river",
            "carta_final_1", "carta_final_2", "carta_final_3",
            "carta_final_4", "carta_final_5"
        ]

        entrada_df = pd.DataFrame([entrada_manual], columns=columnas)
        entrada_scaled = self.scaler.transform(entrada_df)

        # Predicción
        probabilidades = self.model.predict(entrada_scaled, verbose=0)
        clase_predicha = np.argmax(probabilidades)

        clases = ['Derrota', 'Empate', 'Victoria']
        resultado = {
            "Derrota": probabilidades[0][0],
            "Empate": probabilidades[0][1],
            "Victoria": probabilidades[0][2],
            "Clase": clases[clase_predicha]
        }
        self.prediction_result = resultado
        return resultado

    def draw(self, screen):
        screen.blit(self.background, (0, 0))

        # Placeholders
        for i, (x, y) in enumerate(self.card_positions):
            color = (200, 200, 200) if i == self.current_card_index else (150, 150, 150)
            pygame.draw.rect(screen, color, (x, y, self.card_width, self.card_height), border_radius=8)
            pygame.draw.rect(screen, (0, 0, 0), (x, y, self.card_width, self.card_height), 2, border_radius=8)

            # Mostramos la carta seleccionada en el placeholder
            if self.community_cards[i]:
                card_image = self.card_images[self.community_cards[i]]
                screen.blit(card_image, (x, y))

        # Cartas del jugador
        for i, (x, y) in enumerate(self.player_card_positions):
            if i < len(self.selected_cards):
                card_image = self.card_images[self.selected_cards[i]]
                screen.blit(card_image, (x, y))

        # Panel de selección de cartas
        if self.showing_panel:
            self.visible_button = False
            self.draw_card_selection_panel(screen)
        else:
            self.visible_button = True

        # Mostramos el botón para la predicción
        if self.visible_button:
            # Dibujamos el botón Atrás
            screen.blit(self.back_button_image, self.back_button_rect.topleft)
            if self.enable_button:
                pygame.draw.rect(screen, (34, 193, 34), self.prediction_button, border_radius=10)  
            else:
                pygame.draw.rect(screen, (169, 169, 169), self.prediction_button, border_radius=10)  
            screen.blit(self.button_text, (self.prediction_button.x + 25, self.prediction_button.y + 8)) 

        # Mostramos los resultados de la predicción
        if self.prediction_result:
            result_text = (
                f"Derrota: {self.prediction_result['Derrota']:.2%} | "
                f"Empate: {self.prediction_result['Empate']:.2%} | "
                f"Victoria: {self.prediction_result['Victoria']:.2%}"
            )
            result_surface = self.small_font.render(result_text, True, (255, 255, 255))
            screen.blit(result_surface, (190, 200)) 

        pygame.display.flip()

    def draw_card_selection_panel(self, screen):
        # Dimensiones del panel
        panel_width, panel_height = 770, 550
        panel_x, panel_y = (800 - panel_width) // 2, (600 - panel_height) // 2

        # Fondo
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))  
        screen.blit(overlay, (0, 0))

        # Fondo del panel
        panel_color = (200, 200, 200, 200)  
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill(panel_color)
        screen.blit(panel_surface, (panel_x, panel_y))

        # Dimensiones de las cartas
        card_width, card_height = 50, 75
        margin_x, margin_y = 10, 10
        rows, cols = 4, 13

        total_width = (card_width + margin_x) * cols - margin_x
        total_height = (card_height + margin_y) * rows - margin_y
        start_x = panel_x + (panel_width - total_width) // 2
        start_y = panel_y + (panel_height - total_height) // 2

        # Cartas disponibles
        self.card_rects = []
        card_id_list = [f"{value}{suit}" for suit in ["1", "2", "3", "4"] for value in range(2, 15)]
        card_id_list = [card for card in card_id_list if card not in self.selected_cards]

        for i, card_id in enumerate(card_id_list):
            row = i // cols
            col = i % cols
            x_pos = start_x + col * (card_width + margin_x)
            y_pos = start_y + row * (card_height + margin_y)

            card_image = self.panel_card_images[card_id]
            screen.blit(card_image, (x_pos, y_pos))
            card_rect = pygame.Rect(x_pos, y_pos, card_width, card_height)
            self.card_rects.append((card_rect, card_id))

        instruction_text = self.main_font.render("Selecciona una carta", True, (0, 0, 0))
        instruction_rect = instruction_text.get_rect(center=(400, panel_y + 20))
        screen.blit(instruction_text, instruction_rect)

# FUNCIONES PARA EVALUAR LA MEJOR MANO POSIBLE

def clasificar_mano(cartas):
    # Pasamos las cartas a enteros
    cartas = [int(carta) for carta in cartas]

    # Extraemos valores y palos de las cartas
    valores = [carta // 10 for carta in cartas] 
    palos = [carta % 10 for carta in cartas]

    # Frecuencia de los valores de las cartas
    conteo_valores = Counter(valores)
    conteo_palos = Counter(palos)

    # Verificaciones
    es_color = len(conteo_palos) == 1
    valores.sort()

    # Escalera
    es_escalera = len(conteo_valores) == 5 and (max(valores) - min(valores)) == 4
    
    # Caso especial escalera A, 2, 3, 4, 5
    if set(valores) == {14, 2, 3, 4, 5}:
        es_escalera = True
        valores = [5, 4, 3, 2, 1]

    # Evaluamos las manos
    if es_color and es_escalera:
        if set(valores) == {14, 13, 12, 11, 10}:
            return (10, valores, "Escalera Real")
        return (9, valores, "Escalera de Color")
    elif 4 in conteo_valores.values():
        return (8, valores, "Póker")
    elif 3 in conteo_valores.values() and 2 in conteo_valores.values():
        return (7, valores, "Full House")
    elif es_color:
        return (6, valores, "Color")
    elif es_escalera:
        return (5, valores, "Escalera")
    elif 3 in conteo_valores.values():
        return (4, valores, "Trío")
    elif list(conteo_valores.values()).count(2) == 2:
        return (3, valores, "Doble Pareja")
    elif 2 in conteo_valores.values():
        return (2, valores, "Pareja")
    else:
        return (1, valores, "Carta Alta")

def clasificar_mano_preflop(cartas):
    # Si las dos cartas tienen el mismo valor, es una pareja
    if cartas[0][:-1] == cartas[1][:-1]:
        tipo = 2
    else:
        # Comprobamos si son del mismo palo
        if cartas[0][-1] == cartas[1][-1]:
            tipo = 1
        else:
            tipo = 0
    
    return tipo

def obtener_mejor_mano(cartas):
    combinaciones_manos = combinations(cartas, 5)
    
    # Evaluamos una mano con desempate por kicker
    def evaluar_mano(c):
        clasificacion, valores, _ = clasificar_mano(c)
        return (clasificacion, valores)  # Clasificación principal y desempate por valores

    # Seleccionamos la mejor mano considerando clasificación y desempates
    mejor_mano = max(combinaciones_manos, key=evaluar_mano)
    return clasificar_mano(mejor_mano), mejor_mano
