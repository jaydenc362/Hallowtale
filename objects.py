import pygame
import assets

# Object setup
WIDTH, HEIGHT = 1280, 960

class camera():
    def __init__(self, attached = None):
        self.position = pygame.Vector2(0, 0)
        self.attached = attached
    def attach(self, other):
        self.attached = other
    def position_on_camera(self, other):
        return other.position + pygame.Vector2(WIDTH / 2, HEIGHT / 2) - self.position
    def update(self):
        if self.attached is not None:
            self.position = self.attached.position + pygame.Vector2(self.attached.width / 2, self.attached.height / 2)
        else:
            self.position = pygame.Vector2(0, 0)

class player():
    def __init__(self):
        self.width, self.height = 100, 100
        self.position = pygame.Vector2(0, 0)
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        self.speed = 300
    def update(self, dt):
        keys = pygame.key.get_pressed()
        move_left = (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not (keys[pygame.K_RIGHT] or keys[pygame.K_d])
        move_right = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not (keys[pygame.K_LEFT] or keys[pygame.K_a])
        move_up = (keys[pygame.K_UP] or keys[pygame.K_w]) and not (keys[pygame.K_DOWN] or keys[pygame.K_s])
        move_down = (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not (keys[pygame.K_UP] or keys[pygame.K_w])
        if move_left:
            self.position.x -= self.speed * dt
        elif move_right:
            self.position.x += self.speed * dt
        if move_up:
            self.position.y -= self.speed * dt
        elif move_down:
            self.position.y += self.speed * dt
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
    def draw(self, surface, camera):
        draw_position = camera.position_on_camera(self)
        pygame.draw.rect(
            surface, (255, 255, 0), (
                draw_position.x, draw_position.y,
                self.width, self.height
            )
        )

class door():
    def __init__(self):
        self.position = pygame.Vector2(-25, -350)
        self.width = 150
        self.height = 300
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
    def enter(self, player):
        keys = pygame.key.get_pressed()
        return self.rect.colliderect(player.rect) and keys[pygame.K_SPACE]
    def update(self, dt):
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
    def draw(self, surface, camera):
        draw_position = camera.position_on_camera(self)
        pygame.draw.rect(
            surface, (155, 100, 0), (
                draw_position.x, draw_position.y,
                self.width, self.height
            )
        )

class floor():
    def __init__(self):
        self.dimensions = (20, 15)
        self.grid = [[0] * self.dimensions[0]] * self.dimensions[1]
        self.tile_width = WIDTH / self.dimensions[0]
        self.tile_height = HEIGHT / self.dimensions[1]
        self.color = (60, 60, 60)
    def tile_to_position(self, x, y):
        return pygame.Vector2(self.tile_width * x, self.tile_height * y)
    def is_tile_outside_bounds(self, x, y):
        return x >= self.dimensions[0] or x < 0 or y >= self.dimensions[1] or y < 0
    def draw(self, surface):
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                pygame.draw.circle(
                    surface, self.color, (
                        x * self.tile_width + self.tile_width / 2,
                        y * self.tile_height + self.tile_height / 2
                    ), self.tile_width / 2 * 1.08
                )

class heart():
    def __init__(self, floor):
        self.width, self.height = 30, 30
        self.position_offset = pygame.Vector2((floor.tile_width - self.width) / 2, (floor.tile_height - self.height) / 2)
        self.position = floor.tile_to_position(0, 14) + self.position_offset
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        self.speed = 500
        self.current_direction, self.next_direction = None, None
        self.current_tile, self.next_tile = (0, 14), (0, 14)
        self.directions = [
            ((-1, 0), (pygame.K_LEFT, pygame.K_a)),
            ((1, 0), (pygame.K_RIGHT, pygame.K_d)),
            ((0, -1), (pygame.K_UP, pygame.K_w)),
            ((0, 1), (pygame.K_DOWN, pygame.K_s)),
        ]
    def reached_next_tile(self, floor):
        target = floor.tile_to_position(self.next_tile[0], self.next_tile[1]) + self.position_offset
        dx, dy = self.current_direction or (0, 0)
        if dx != 0:
            return (self.position.x - target.x) * dx >= 0
        if dy != 0:
            return (self.position.y - target.y) * dy >= 0
        return False
    def update(self, dt, floor):
        keys = pygame.key.get_pressed()
        for direction, keys_to_check in self.directions:
            if any(keys[key] for key in keys_to_check):
                self.next_direction = direction
                if self.current_direction is None:
                    self.current_direction = direction
                break
        if self.reached_next_tile(floor):
            self.position = floor.tile_to_position(self.next_tile[0], self.next_tile[1]) + self.position_offset
            self.current_tile = self.next_tile
            self.current_direction = self.next_direction
            dx, dy = self.current_direction or (0, 0)
            self.next_tile = (self.current_tile[0] + dx, self.current_tile[1] + dy)
            if floor.is_tile_outside_bounds(self.next_tile[0], self.next_tile[1]):
                self.next_tile = self.current_tile
                self.current_direction = None
        dx, dy = self.current_direction or (0, 0)
        self.position.x += dx * self.speed * dt
        self.position.y += dy * self.speed * dt
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
    def draw(self, surface):
        image = assets.images["heart"]
        scaled_image = pygame.transform.scale(image, (self.width, self.height))
        surface.blit(scaled_image, self.position)