import pygame
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
        self.font = pygame.font.Font(None, 100)
        self.log = [
            "\pause",
            "Hallowtale",
            "By Jayden Chan",
            "\n",
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
            elif self.log[i] == "\n":
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
        self.entering = False
        self.entering_time = 1
        self.entering_timer = 0
        self.flicker_time = 0.1
        self.flicker_timer = 0
        self.show_heart = False
    def transition(self, dt):
        if self.entering:
            self.entering_timer += dt
            self.flicker_timer += dt
            if self.entering_timer >= self.entering_time:
                return boss_gs()
            if self.flicker_timer >= self.flicker_time:
                self.flicker_timer = 0
                self.show_heart = not self.show_heart
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
            self.entering = True
            self.player.speed = 0
        return self.transition(dt)
    def draw(self, surface):
        surface.fill((0, 0, 0))
        self.door.draw(surface, self.camera)
        self.player.draw(surface, self.camera, self.show_heart)

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