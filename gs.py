import pygame
import assets
from objects import player
from objects import door
from objects import camera
from objects import floor
from objects import heart

class gs():
    def handle_events(self, events):
        pass
    def update(self, dt):
        pass
    def draw(self, surface):
        pass

class menu_gs(gs):
    def __init__(self):
        self.font = pygame.font.Font("assets/fonts/upheavtt.ttf", 100)
        self.log = [
            "\pause",
            "Hallowtale",
            "By Jayden Chan",
            "",
            "Press [enter]",
        ]
        self.log_time = 1
        self.log_timer = 0
        self.log_index = 0
        self.log_offset = 30
        self.log_color = (255, 255, 255)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return entrance_gs()
        return self
    def update(self, dt):
        self.log_timer += dt
        if self.log_timer >= self.log_time:
            self.log_timer = 0
            self.log_index = min(self.log_index + 1, len(self.log) - 1)
    def draw(self, surface):
        surface.fill((0, 0, 0))
        j = 0
        for i in range(self.log_index + 1):
            if self.log[i] == "\pause":
                continue
            elif self.log[i] == "":
                self.log_timer = 1
            text_surface = self.font.render(self.log[i], True, self.log_color)
            text_position = (self.log_offset, self.log_offset + self.font.get_height() * j)
            surface.blit(text_surface, text_position)
            j += 1

class entrance_gs(gs):
    def __init__(self):
        self.player = player()
        self.door = door()
        self.camera = camera(self.player)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return menu_gs()
        return self
    def update(self, dt):
        self.player.update(dt)
        self.camera.update()
        self.door.update(dt)
        if self.door.enter(self.player):
            return transition_gs()
    def draw(self, surface):
        surface.fill((0, 0, 0))
        self.door.draw(surface, self.camera)
        self.player.draw(surface, self.camera)
        
class transition_gs(gs):
    def __init__(self):
        self.flicker_time = 0.1
        self.flicker_timer = 0
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return menu_gs()
        return self
    def update(self, dt):
        return boss_gs()
    def draw(self, surface):
        image = assets.images["heart"]
        scaled_image = pygame.transform.scale(image, (30, 30))
        surface.blit(scaled_image, (0, 0))

class boss_gs(gs):
    def __init__(self):
        self.floor = floor()
        self.heart = heart(self.floor)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return menu_gs()
        return self
    def update(self, dt):
        self.heart.update(dt, self.floor)
    def draw(self, surface):
        surface.fill((50, 50, 50))
        self.floor.draw(surface)
        self.heart.draw(surface)