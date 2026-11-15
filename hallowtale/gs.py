import pygame, assets, random
from objects import camera, player, door, floor, heart, boss, mini_boss, item

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
            "[ enter ] >> Entrance",
            "[ r ] >> More Rewards",
            "[ h ] >> More Hazards",
        ]
        self.log_time = 1
        self.log_timer = 0
        self.log_index = 0
        self.log_offset = 30
        self.log_color = (255, 255, 255)
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        pygame.mixer.music.load("assets/sounds/premonition.ogg")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return entrance_gs("normal")
                elif event.key == pygame.K_r:
                    return entrance_gs("easy")
                elif event.key == pygame.K_h:
                    return entrance_gs("hard")
        return self
    def update(self, dt):
        if self.log[self.log_index] == "/skip":
            self.log_index = min(self.log_index + 1, len(self.log) - 1)
            return
        self.log_timer += dt
        if self.log_timer >= self.log_time:
            self.log_timer = 0
            self.log_index = min(self.log_index + 1, len(self.log) - 1)
            while self.log_index < len(self.log) - 1 and self.log[self.log_index] == "":
                self.log_index += 1
    def draw(self, surface):
        surface.fill((0, 0, 0))
        j = 0
        for i in range(self.log_index + 1):
            if self.log[i] == "/pause":
                continue
            elif self.log[i] == "/skip":
                j += 1
                continue
            text_surface = self.font.render(self.log[i], True, self.log_color)
            text_position = (self.log_offset, self.log_offset + self.font.get_height() * j)
            surface.blit(text_surface, text_position)
            j += 1

class entrance_gs(gs):
    def __init__(self, difficulty):
        self.player = player()
        self.door = door()
        self.camera = camera(self.player)
        self.difficulty = difficulty
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        assets.sounds["intro"].play()
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
        self.door.update()
        if self.door.enter(self.player):
            assets.sounds["intro"].play()
            return transition_gs(self.difficulty)
    def draw(self, surface):
        surface.fill((0, 0, 0))
        self.door.draw(surface, self.camera)
        self.player.draw(surface, self.camera)
        
class transition_gs(gs):
    def __init__(self, difficulty):
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
        self.difficulty = difficulty
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        assets.sounds["door"].play()
        assets.sounds["start"].play()
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
            return boss_gs(self.difficulty)
    def draw(self, surface):
        if self.flicker_count % 2 == 0:
            image = assets.images["heart"]
            scaled_image = pygame.transform.scale(image, (30, 30))
            surface.blit(scaled_image, self.heart_position)

class boss_gs(gs):
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.floor = floor()
        self.heart = heart(self.floor)
        self.boss = boss(self.floor, (17, 2))
        self.mini_bosses = [
            mini_boss(self.floor, (17, 4), (255, 155, 155)),
            mini_boss(self.floor, (17, 5), (155, 255, 155)),
            mini_boss(self.floor, (17, 6), (155, 155, 255)),
        ]
        self.items = item.item_list
        item.item_list.clear()
        n_items = 20
        if self.difficulty == "hard":
            n_items = 60
        for _ in range(n_items):
            x = random.randint(0, self.floor.dimensions[0] - 1)
            y = random.randint(0, self.floor.dimensions[1] - 1)
            self.items.append(item(self.floor, (x, y), self.difficulty))
        self.font = pygame.font.Font("assets/fonts/upheavtt.ttf", 30)
        self.log = [
            "Player Health: " + str(self.heart.health),
            "Boss Health: " + str(self.boss.health),
        ]
        self.log_color = (255, 255, 255)
        self.log_offset = 30
        self.debug_mode = False
        pygame.mixer.stop()
        pygame.mixer.music.load("assets/sounds/ghost_fight.ogg")
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return menu_gs()
                elif event.key == pygame.K_F1 or event.key == pygame.K_TAB:
                    self.debug_mode = not self.debug_mode
        return self
    def update(self, dt):
        self.heart.update(dt, self.floor)
        self.boss.update(dt, self.floor, self.heart)
        for m in self.mini_bosses:
            m.update(dt, self.floor, self.boss, self.heart)
        self.floor.update(dt)
        n_items = len(self.items)
        for i in self.items[:]:
            i.update(dt, self.heart, self.boss)
        if len(self.items) < n_items:
            x = random.randint(0, self.floor.dimensions[0] - 1)
            y = random.randint(0, self.floor.dimensions[1] - 1)
            self.items.append(item(self.floor, (x, y), self.difficulty))
        self.log = [
            "Player Health: " + str(self.heart.health),
            "Boss Health: " + str(self.boss.health),
        ]
        self.debug_log = [
            "Player Health: " + str(self.heart.health),
            "Boss Health: " + str(self.boss.health),
            "Boss Markov Accuracy: " + self.boss.markov.format_accuracy(),
            "Miniboss R state: " + self.mini_bosses[0].state,
            "Miniboss G state: " + self.mini_bosses[1].state,
            "Miniboss B state: " + self.mini_bosses[2].state,
        ]
        if self.heart.health <= 0:
            return death_gs(self.difficulty)
        if self.boss.health <= 0:
            return boss_death_gs()
    def draw(self, surface):
        surface.fill((60, 30, 50))
        self.floor.draw(surface)
        for i in self.items[:]:
            i.draw(surface)
        for m in self.mini_bosses:
            m.draw(surface, self.floor, self.debug_mode)
        self.boss.draw(surface, self.floor, self.debug_mode)
        self.heart.draw(surface)
        # Stats
        text_position = (20, 20)
        if self.debug_mode:
            for i in range(len(self.debug_log)):
                text_surface = self.font.render(self.debug_log[i], True, self.log_color)
                text_position = (self.log_offset, self.log_offset + self.font.get_height() * i)
                surface.blit(text_surface, text_position)
        else:
            for i in range(len(self.log)):
                text_surface = self.font.render(self.log[i], True, self.log_color)
                text_position = (self.log_offset, self.log_offset + self.font.get_height() * i)
                surface.blit(text_surface, text_position)

class death_gs(gs):
    def __init__(self, difficulty):
        self.font = pygame.font.Font("assets/fonts/upheavtt.ttf", 100)
        self.log = [
            "/pause",
            "You died...",
            "Stay determined!",
            "/skip",
            "[ enter ] >> Entrance",
            "[ esc ] >> Menu",
        ]
        self.log_time = 1
        self.log_timer = 0
        self.log_index = 0
        self.log_offset = 30
        self.log_color = (255, 255, 255)
        self.difficulty = difficulty
        pygame.mixer.stop()
        pygame.mixer.music.stop()
        assets.sounds["death"].play()
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return entrance_gs(self.difficulty)
                elif event.key == pygame.K_ESCAPE:
                    return menu_gs()
        return self
    def update(self, dt):
        if self.log[self.log_index] == "/skip":
            self.log_index = min(self.log_index + 1, len(self.log) - 1)
            return
        self.log_timer += dt
        if self.log_timer >= self.log_time:
            self.log_timer = 0
            self.log_index = min(self.log_index + 1, len(self.log) - 1)
            while self.log_index < len(self.log) - 1 and self.log[self.log_index] == "":
                self.log_index += 1
    def draw(self, surface):
        surface.fill((0, 0, 0))
        j = 0
        for i in range(self.log_index + 1):
            if self.log[i] == "/pause":
                continue
            elif self.log[i] == "/skip":
                j += 1
                continue
            text_surface = self.font.render(self.log[i], True, self.log_color)
            text_position = (self.log_offset, self.log_offset + self.font.get_height() * j)
            surface.blit(text_surface, text_position)
            j += 1

class boss_death_gs(gs):
    def __init__(self):
        self.timer = 0
        self.time = 5
        self.image = "boss"
        self.position = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.sound_index = 0
        pygame.mixer.music.stop()
        pygame.mixer.stop()
    def update(self, dt):
        self.timer += dt
        if self.timer >= self.time:
            return victory_gs()
        # Image
        if self.timer >= 3:
            if self.sound_index == 1:
                assets.sounds["victory"].play()
            self.sound_index = 2
        elif self.timer >= 1.5:
            self.image = "boss_dead"
        elif self.timer >= 1:
            self.image = "boss_slashed"
            if self.sound_index == 0:
                assets.sounds["heavy"].play()
            self.sound_index = 1
    def draw(self, surface):
        image = assets.images[self.image]
        scaled_image = pygame.transform.scale(image, (587, 425))
        draw_position = self.position - pygame.Vector2(
            scaled_image.get_width() / 2,
            scaled_image.get_height() / 2
        )
        surface.blit(scaled_image, draw_position)

class victory_gs(gs):
    def __init__(self):
        self.font = pygame.font.Font("assets/fonts/upheavtt.ttf", 100)
        self.log = [
            "/pause",
            "/skip", "/skip", "/skip", "/skip",
            "         HALLOWTALE",
        ]
        self.log_time = 1
        self.log_timer = 0
        self.log_index = 0
        self.log_offset = 30
        self.log_color = (255, 255, 255)
        pygame.mixer.music.stop()
        pygame.mixer.stop()
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return menu_gs()
        return self
    def update(self, dt):
        if self.log[self.log_index] == "/skip":
            self.log_index = min(self.log_index + 1, len(self.log) - 1)
            return
        self.log_timer += dt
        if self.log_timer >= self.log_time:
            self.log_timer = 0
            self.log_index = min(self.log_index + 1, len(self.log) - 1)
            if self.log_index == 1:
                assets.sounds["intro"].play()
            while self.log_index < len(self.log) - 1 and self.log[self.log_index] == "":
                self.log_index += 1
    def draw(self, surface):
        surface.fill((0, 0, 0))
        j = 0
        for i in range(self.log_index + 1):
            if self.log[i] == "/pause":
                continue
            elif self.log[i] == "/skip":
                j += 1
                continue
            text_surface = self.font.render(self.log[i], True, self.log_color)
            text_position = (self.log_offset, self.log_offset + self.font.get_height() * j)
            surface.blit(text_surface, text_position)
            j += 1