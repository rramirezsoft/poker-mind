import pygame
import os
import random 

def load_image(image_path, scale=None):
    """Cargar y escalar una imagen desde la ruta especificada."""
    image = pygame.image.load(os.path.abspath(image_path)).convert_alpha()
    if scale:
        image = pygame.transform.scale(image, scale)
    return image

def load_font(path, size):
    return pygame.font.Font(path, size)

def load_card_images(card_images, BASE_DIR, size=(50, 75)):
    card_folder = os.path.join(BASE_DIR, '..', 'assets', 'img', 'cards')
    for filename in os.listdir(card_folder):
        if filename.endswith(".png"):
            card_id = filename.split(".")[0]      
            card_image = load_image(os.path.join(card_folder, filename), size)
            card_images[card_id] = card_image

class SoundManager:
    def __init__(self):
        pygame.mixer.init() 
        self.music_files = []  
        self.sound_effects = {} 

    def load_music(self, music_folder):
        """Carga los archivos de música desde una carpeta."""
        self.music_files = [
            os.path.join(music_folder, f"0{i}.mp3") for i in range(1, 5)
        ]
    
    def play_music(self, loops=-1, start=0.0):
        """Reproduce la música de fondo de forma aleatoria en bucle."""
        if not self.music_files:
            print("No hay música cargada.")
            return
        
        random.shuffle(self.music_files)
        pygame.mixer.music.load(self.music_files[0])
        pygame.mixer.music.play(loops=loops, start=start)
    
    def stop_music(self):
        """Detiene la música de fondo."""
        pygame.mixer.music.stop()

    def load_sound(self, sound_name, sound_path):
        """Carga un efecto de sonido."""
        if sound_name not in self.sound_effects:
            self.sound_effects[sound_name] = pygame.mixer.Sound(sound_path)
    
    def play_sound(self, sound_name):
        """Reproduce un efecto de sonido."""
        if sound_name in self.sound_effects:
            self.sound_effects[sound_name].play()
        else:
            print(f"El efecto de sonido {sound_name} no está cargado.")
    
    def stop_sound(self, sound_name):
        """Detiene un efecto de sonido (si es posible)."""
        if sound_name in self.sound_effects:
            self.sound_effects[sound_name].stop()

sound_manager = SoundManager()

