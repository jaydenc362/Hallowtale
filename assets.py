import pygame

# Asset managers
images = {}
sounds = {}

def load_assets():
    # Images
    images["favicon"] = pygame.image.load("assets/images/favicon.png")
    images["door"] = pygame.image.load("assets/images/door.png")
    images["heart"] = pygame.image.load("assets/images/heart.png").convert_alpha()
    images["player_front"] = pygame.image.load("assets/images/player_front.png").convert_alpha()
    images["player_back"] = pygame.image.load("assets/images/player_back.png").convert_alpha()
    images["player_left"] = pygame.image.load("assets/images/player_left.png").convert_alpha()
    images["player_right"] = pygame.image.load("assets/images/player_right.png").convert_alpha()
    # Sounds excluding music
    sounds["death"] = pygame.mixer.Sound("assets/sounds/death.ogg")
    sounds["death"].set_volume(1)