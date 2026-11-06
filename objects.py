import pygame, random, math, heapq, assets

# Object setup
WIDTH, HEIGHT = 1280, 960

class camera():
    def __init__(self, attached = None):
        self.position = pygame.Vector2(0, 0)
        self.attached = attached
    def attach(self, other):
        self.attached = other
    def position_on_camera(self, other):
        return round(other.position + pygame.Vector2(WIDTH / 2, HEIGHT / 2) - self.position)
    def update(self):
        if self.attached is not None:
            self.position = self.attached.position + pygame.Vector2(self.attached.width / 2, self.attached.height / 2)
        else:
            self.position = pygame.Vector2(0, 0)

class player():
    def __init__(self):
        self.width, self.height = 80, 120
        self.position = pygame.Vector2(0, 0)
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        self.speed = 300
        self.image = "player_front"
    def update(self, dt):
        keys = pygame.key.get_pressed()
        move_left = (keys[pygame.K_LEFT] or keys[pygame.K_a]) and not (keys[pygame.K_RIGHT] or keys[pygame.K_d])
        move_right = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and not (keys[pygame.K_LEFT] or keys[pygame.K_a])
        move_up = (keys[pygame.K_UP] or keys[pygame.K_w]) and not (keys[pygame.K_DOWN] or keys[pygame.K_s])
        move_down = (keys[pygame.K_DOWN] or keys[pygame.K_s]) and not (keys[pygame.K_UP] or keys[pygame.K_w])
        velocity = pygame.Vector2(0, 0)
        if move_left:
            velocity.x = -1
            self.image = "player_left"
        elif move_right:
            velocity.x = 1
            self.image = "player_right"
        if move_up:
            velocity.y = -1
            self.image = "player_back"
        elif move_down:
            velocity.y = 1
            self.image = "player_front"
        if velocity.length() > 0:
            self.position += velocity.normalize() * self.speed * dt
        self.rect.topleft = self.position
    def draw(self, surface, camera):
        draw_position = camera.position_on_camera(self)
        image = assets.images[self.image]
        scaled_image = pygame.transform.scale(image, (self.width, self.height))
        surface.blit(scaled_image, draw_position)

class door():
    def __init__(self):
        self.position = pygame.Vector2(-140, -500)
        self.width, self.height = 1083 / 3, 833 / 3
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        self.space_was_held = False
    def enter(self, player):
        keys = pygame.key.get_pressed()
        space_held = keys[pygame.K_SPACE]
        entered = self.rect.colliderect(player.rect) and space_held and not self.space_was_held
        self.space_was_held = space_held
        return entered
    def update(self, dt):
        self.rect.topleft = self.position
    def draw(self, surface, camera):
        draw_position = camera.position_on_camera(self)
        image = assets.images["door"]
        scaled_image = pygame.transform.scale(image, (self.width, self.height))
        surface.blit(scaled_image, draw_position)

class floor():
    def __init__(self):
        self.dimensions = (20, 15)
        self.grid = [
            [0 for y in range(self.dimensions[1])] for x in range(self.dimensions[0])
        ]
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                self.grid[x][y] = random.randint(1, 3)
        self.tile_width = WIDTH / self.dimensions[0]
        self.tile_height = HEIGHT / self.dimensions[1]
        self.grid_tiles = [
            [
                grid_tile(
                    self.grid[x][y], x, y, self.tile_width, self.tile_height
                ) for y in range(self.dimensions[1])
            ] for x in range(self.dimensions[0])
        ]
    def tile_to_position(self, xytuple):
        return pygame.Vector2(self.tile_width * xytuple[0], self.tile_height * xytuple[1])
    def is_tile_outside_bounds(self, xytuple):
        return xytuple[0] >= self.dimensions[0] or xytuple[0] < 0 or xytuple[1] >= self.dimensions[1] or xytuple[1] < 0
    def tile_to_value(self, xytuple):
        return self.grid[xytuple[0]][xytuple[1]]
    def update(self, dt):
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                self.grid_tiles[x][y].update(dt)
    def draw(self, surface):
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                self.grid_tiles[x][y].draw(surface)

class grid_tile():
    def __init__(self, value, x, y, tile_width, tile_height):
        self.position = pygame.Vector2(x * tile_width, y * tile_height)
        self.tile_width, self.tile_height = tile_width, tile_height
        self.value = value
        self.color = (
            round(60 * self.value),
            round(30 * self.value),
            50
        )
        self.timer = -x + y
        self.sine = math.sin(self.timer)
        self.cosine = math.cos(self.timer)
    def draw_boss_target_highlight(self, surface):
        pygame.draw.circle(
            surface, (255, 255, 0), (
                self.position.x + self.tile_width / 2 + self.sine * 5,
                self.position.y + self.tile_height / 2 + self.cosine * 5
            ), self.tile_width / 2 * 0.9 + self.sine * 3, 3
        )
    def update(self, dt):
        self.timer += dt * 3
        self.sine = math.sin(self.timer)
        self.cosine = math.cos(self.timer)
        self.color = (
            round(60 * self.value + self.sine * 10),
            round(30 * self.value + self.sine * 10),
            round(50 + self.sine * 5)
        )
    def draw(self, surface):
        pygame.draw.circle(
            surface, self.color, (
                self.position.x + self.tile_width / 2 + self.sine * 5,
                self.position.y + self.tile_height / 2 + self.cosine * 5
            ), self.tile_width / 2 * 1.1 + self.sine * 3
        )

class heart():
    def __init__(self, floor):
        self.width, self.height = 30, 30
        self.position_offset = pygame.Vector2((floor.tile_width - self.width) / 2, (floor.tile_height - self.height) / 2)
        self.position = floor.tile_to_position((0, 14)) + self.position_offset
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        self.speed = 500
        self.current_direction, self.next_direction, self.last_direction = None, None, None
        self.current_tile, self.next_tile = (0, 14), (0, 14)
        self.directions = [
            ((-1, 0), (pygame.K_LEFT, pygame.K_a)),
            ((1, 0), (pygame.K_RIGHT, pygame.K_d)),
            ((0, -1), (pygame.K_UP, pygame.K_w)),
            ((0, 1), (pygame.K_DOWN, pygame.K_s)),
        ]
    def reached_next_tile(self, floor):
        target = floor.tile_to_position(self.next_tile) + self.position_offset
        dx, dy = self.current_direction or (0, 0)
        if dx != 0:
            return (self.position.x - target.x) * dx >= 0
        if dy != 0:
            return (self.position.y - target.y) * dy >= 0
        return False
    def move(self, dt, floor, dx, dy):
        step = self.speed * dt
        target = floor.tile_to_position(self.next_tile) + self.position_offset
        distance = target - self.position
        if dx != 0:
            if abs(distance.x) <= step:
                self.position.x = target.x
            else:
                self.position.x += dx * step
        elif dy != 0:
            if abs(distance.y) <= step:
                self.position.y = target.y
            else:
                self.position.y += dy * step
    def update(self, dt, floor):
        keys = pygame.key.get_pressed()
        for direction, keys_to_check in self.directions:
            if any(keys[key] for key in keys_to_check):
                self.next_direction = direction
                if self.current_direction is None:
                    self.current_direction = direction
                break
        if self.reached_next_tile(floor):
            self.position = floor.tile_to_position(self.next_tile) + self.position_offset
            self.current_tile = self.next_tile
            self.last_direction = self.current_direction
            self.current_direction = self.next_direction
            dx, dy = self.current_direction or (0, 0)
            self.next_tile = (self.current_tile[0] + dx, self.current_tile[1] + dy)
            if floor.is_tile_outside_bounds(self.next_tile):
                self.next_tile = self.current_tile
                self.current_direction = None
        dx, dy = self.current_direction or (0, 0)
        self.speed = 500 / math.sqrt(floor.tile_to_value(self.current_tile))
        self.move(dt, floor, dx, dy)
        self.rect.topleft = self.position
    def draw(self, surface):
        image = assets.images["heart"]
        scaled_image = pygame.transform.scale(image, (self.width, self.height))
        surface.blit(scaled_image, self.position)

# A* pathfinding
def astar_path(grid, start, target):
    if start == target:
        return [start]
    frontier = []
    heapq.heappush(frontier, (0, start))
    came_from = {start: None}
    cost_so_far = {start: 0}
    while frontier:
        priority, current = heapq.heappop(frontier)
        cx, cy = current
        heuristic = abs(target[0] - cx) + abs(target[1] - cy)
        if priority > cost_so_far[current] + heuristic:
            continue
        if current == target:
            break
        cx, cy = current
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_node = (cx + dx, cy + dy)
            nx, ny = next_node
            if 0 <= nx < len(grid) and 0 <= ny < len(grid[0]):
                new_cost = cost_so_far[current] + grid[nx][ny]
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    heuristic = abs(target[0] - nx) + abs(target[1] - ny)
                    priority = new_cost + heuristic
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current
    if target not in came_from:
        return []
    path = []
    curr = target
    while curr is not None:
        path.append(curr)
        curr = came_from[curr]
    path.reverse()
    return path

class boss():
    def __init__(self, floor, heart):
        self.width, self.height = 30, 30
        self.position_offset = pygame.Vector2(
            (floor.tile_width - self.width) / 2,
            (floor.tile_height - self.height) / 2
        )
        self.current_tile = (19, 0)
        self.target_tile = self.current_tile
        self.position = floor.tile_to_position(self.current_tile) + self.position_offset
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        self.speed = 100
        self.moving = False
        self.path = astar_path(floor.grid, self.current_tile, self.target_tile)
        if self.path:
            self.path.pop(0)
        self.markov = markov()
    def follow_path(self, dt, floor, heart):
        # Update path
        if not self.path:
            predicted_tile = self.markov.predict_heart_next_tile(heart, floor)
            if predicted_tile is not None:
                self.target_tile = predicted_tile
            self.path = astar_path(floor.grid, self.current_tile, self.target_tile)
            if self.path:
                self.path.pop(0)
            if not self.path:
                return
        # Follow
        step = self.speed * dt
        next_tile = self.path[0]
        target = floor.tile_to_position(next_tile) + self.position_offset
        distance = target - self.position
        if distance.length() <= step:
            self.position = pygame.Vector2(target)
            self.current_tile = next_tile
            predicted_tile = self.markov.predict_heart_next_tile(heart, floor)
            if predicted_tile is not None:
                self.target_tile = predicted_tile
            self.path = astar_path(floor.grid, next_tile, self.target_tile)
            if self.path:
                self.path.pop(0)
        else:
            self.position += distance.normalize() * step
    def update(self, dt, floor, heart):
        self.speed = 100 / math.sqrt(floor.tile_to_value(self.current_tile))
        self.markov.update(heart)
        self.follow_path(dt, floor, heart)
        self.rect.topleft = self.position
    def draw(self, surface, floor):
        pygame.draw.rect(
            surface, (255, 255, 0), (
                self.position.x, self.position.y,
                self.width, self.height
            )
        )
        target_tile_grid_tile = floor.grid_tiles[self.target_tile[0]][self.target_tile[1]]
        target_tile_grid_tile.draw_boss_target_highlight(surface)

class markov():
    def __init__(self):
        self.directions = [
            (0, -1), # Up
            (0, 1), # Down
            (-1, 0), # Left
            (1, 0), # Right
        ]
        self.heart_behavior = [
            # To up, down, left, right
            [0, 0, 0, 0], # From up
            [0, 0, 0, 0], # From down
            [0, 0, 0, 0], # From left
            [0, 0, 0, 0], # From right
        ]
        self.last_observed_tile = None
    def update_heart_behavior(self, heart):
        if heart.last_direction is None:
            return
        if heart.current_direction is None:
            return
        if heart.current_tile == self.last_observed_tile:
            return
        previous_index = self.directions.index(heart.last_direction)
        current_index = self.directions.index(heart.current_direction)
        self.heart_behavior[previous_index][current_index] += 1
        self.last_observed_tile = heart.current_tile
    def predict_heart_next_tile(self, heart, floor):
        direction = heart.current_direction
        if direction is None:
            direction = heart.last_direction
            if direction is None:
                return None
        row = self.heart_behavior[self.directions.index(direction)]
        if sum(row) == 0:
            return None
        column_index = row.index(max(row))
        predicted_direction = self.directions[column_index]
        predicted_next_tile = (
            heart.current_tile[0] + predicted_direction[0],
            heart.current_tile[1] + predicted_direction[1]
        )
        if floor.is_tile_outside_bounds(predicted_next_tile):
            return None
        return predicted_next_tile
    def update(self, heart):
        self.update_heart_behavior(heart)