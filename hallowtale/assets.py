import pygame

# Asset managers
images = {}
sounds = {}

def load_assets():
    # Images
    images["favicon"] = pygame.image.load("assets/images/favicon.png")
    images["door"] = pygame.image.load("assets/images/door.png")
    images["heart"] = pygame.image.load("assets/images/heart.png").convert_alpha()
    images["boss"] = pygame.image.load("assets/images/boss/boss.png").convert_alpha()
    images["boss_slashed"] = pygame.image.load("assets/images/boss/boss_slashed.png").convert_alpha()
    images["boss_dead"] = pygame.image.load("assets/images/boss/boss_dead.png").convert_alpha()
    images["mini_boss"] = pygame.image.load("assets/images/mini_boss.png").convert_alpha()
    images["player_front"] = pygame.image.load("assets/images/player/player_front.png").convert_alpha()
    images["player_back"] = pygame.image.load("assets/images/player/player_back.png").convert_alpha()
    images["player_left"] = pygame.image.load("assets/images/player/player_left.png").convert_alpha()
    images["player_right"] = pygame.image.load("assets/images/player/player_right.png").convert_alpha()
    images["heal_player"] = pygame.image.load("assets/images/items/heal_player.png").convert_alpha()
    images["damage_boss"] = pygame.image.load("assets/images/items/damage_boss.png").convert_alpha()
    images["damage_boss_big"] = pygame.image.load("assets/images/items/damage_boss_big.png").convert_alpha()
    images["damage_player"] = pygame.image.load("assets/images/items/damage_player.png").convert_alpha()
    images["damage_player_big"] = pygame.image.load("assets/images/items/damage_player_big.png").convert_alpha()
    # Sounds excluding music
    sounds["boss_hurt"] = pygame.mixer.Sound("assets/sounds/boss_hurt.ogg")
    sounds["death"] = pygame.mixer.Sound("assets/sounds/death.ogg")
    sounds["door"] = pygame.mixer.Sound("assets/sounds/door.ogg")
    sounds["heavy"] = pygame.mixer.Sound("assets/sounds/heavy.ogg")
    sounds["intro"] = pygame.mixer.Sound("assets/sounds/intro.ogg")
    sounds["player_healed"] = pygame.mixer.Sound("assets/sounds/player_healed.ogg")
    sounds["player_hurt"] = pygame.mixer.Sound("assets/sounds/player_hurt.ogg")
    sounds["select"] = pygame.mixer.Sound("assets/sounds/select.ogg")
    sounds["start"] = pygame.mixer.Sound("assets/sounds/start.ogg")
    sounds["victory"] = pygame.mixer.Sound("assets/sounds/victory.ogg")
    sounds["death"].set_volume(1)