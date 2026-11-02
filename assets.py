import pygame

# Asset managers
images = {}
sounds = {}

def load_assets():
    # Images
    images["favicon"] = pygame.image.load("assets/images/favicon.png")
    images["heart"] = pygame.image.load("assets/images/heart.png").convert_alpha()
    # Sounds excluding music
    sounds["death"] = pygame.mixer.Sound("assets/sounds/death.ogg")
    sounds["death"].set_volume(1)