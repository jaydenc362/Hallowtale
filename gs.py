import pygame, assets
from objects import player, door, camera, floor, heart, boss

# Game state setup
WIDTH, HEIGHT = 1280, 960

class gs:
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
            "/pause",
            "Hallowtale",
            "By Jayden Chan",
            "",
            "Press [ Enter ]",
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
            if self.log[i] == "/pause":
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
        if self.player.position.y <= -340:
            self.player.position.y = -340
        elif self.player.position.y >= 100:
            self.player.position.y = 100
        if self.player.position.x <= -300:
            self.player.position.x = -300
        elif self.player.position.x >= 300:
            self.player.position.x = 300
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
        self.heart_width, self.heart_height = 30, 30
        self.heart_speed = 2000
        self.flicker_time = 0.1
        self.flicker_timer = 0
        self.flicker_count = 4
        self.heart_offset = ((1280 / 20) - self.heart_width) / 2
        self.heart_position = pygame.Vector2(
            WIDTH / 2 - self.heart_width / 2 + self.heart_offset,
            HEIGHT / 2 - self.heart_height / 2 + self.heart_offset
        )
        self.heart_target_position = pygame.Vector2(0, HEIGHT - self.heart_height)
        self.finished = False
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return menu_gs()
        return self
    def move_heart(self, dt):
        distance = self.heart_target_position - self.heart_position
        step = self.heart_speed * dt
        if distance.length() <= step:
            self.heart_position = pygame.Vector2(self.heart_target_position)
            self.finished = True
        else:
            self.heart_position += distance.normalize() * step
    def update(self, dt):
        self.flicker_timer += dt
        if self.flicker_timer >= self.flicker_time:
            self.flicker_timer = 0
            self.flicker_count = max(0, self.flicker_count - 1)
        if self.flicker_count <= 0:
            self.move_heart(dt)
        if self.finished:
            return boss_gs()
    def draw(self, surface):
        if self.flicker_count % 2 == 0:
            image = assets.images["heart"]
            scaled_image = pygame.transform.scale(image, (30, 30))
            surface.blit(scaled_image, self.heart_position)

class boss_gs(gs):
    def __init__(self):
        self.floor = floor()
        self.heart = heart(self.floor)
        self.boss = boss(self.floor, self.heart)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return menu_gs()
        return self
    def update(self, dt):
        self.heart.update(dt, self.floor)
        self.boss.update(dt, self.floor, self.heart)
        self.floor.update(dt)
        if self.heart.health <= 0:
            return menu_gs()
    def draw(self, surface):
        surface.fill((60, 30, 50))
        self.floor.draw(surface)
        self.boss.draw(surface, self.floor)
        self.heart.draw(surface)