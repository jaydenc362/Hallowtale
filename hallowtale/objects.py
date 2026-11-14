import pygame, random, math, heapq, assets

# Object setup
WIDTH, HEIGHT = 1280, 960

class camera:
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

class player:
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

class door:
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
    def update(self):
        self.rect.topleft = self.position
    def draw(self, surface, camera):
        draw_position = camera.position_on_camera(self)
        image = assets.images["door"]
        scaled_image = pygame.transform.scale(image, (self.width, self.height))
        surface.blit(scaled_image, draw_position)

class floor:
    def __init__(self):
        self.dimensions = (20, 15)
        self.grid = [
            [random.randint(1, 3) for y in range(self.dimensions[1])] for x in range(self.dimensions[0])
        ]
        self.tile_width = WIDTH / self.dimensions[0]
        self.tile_height = HEIGHT / self.dimensions[1]
        self.grid_tiles = [
            [
                grid_tile(
                    self, x, y
                ) for y in range(self.dimensions[1])
            ] for x in range(self.dimensions[0])
        ]
    def tile_to_position(self, xytuple):
        return pygame.Vector2(self.tile_width * xytuple[0], self.tile_height * xytuple[1])
    def is_tile_outside_bounds(self, xytuple):
        return xytuple[0] >= self.dimensions[0] or xytuple[0] < 0 or xytuple[1] >= self.dimensions[1] or xytuple[1] < 0
    def tile_to_value(self, xytuple):
        return self.grid[xytuple[0]][xytuple[1]]
    def manhattan_distance(self, xytuple1, xytuple2):
        x = abs(xytuple2[0] - xytuple1[0])
        y = abs(xytuple2[1] - xytuple1[1])
        return x + y
    def update(self, dt):
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                self.grid_tiles[x][y].update(dt)
    def draw(self, surface):
        for x in range(self.dimensions[0]):
            for y in range(self.dimensions[1]):
                self.grid_tiles[x][y].draw(surface)

class grid_tile:
    def __init__(self, floor, x, y):
        self.position = pygame.Vector2(x * floor.tile_width, y * floor.tile_height)
        self.width, self.height = floor.tile_width, floor.tile_height
        self.value = floor.grid[x][y]
        self.color = (
            round(60 * self.value),
            round(30 * self.value),
            50
        )
        self.timer = -x + y
        self.sine = math.sin(self.timer)
        self.cosine = math.cos(self.timer)
    def draw_target_highlight(self, surface, color):
        draw_rect_scale = 0.9
        draw_rect = (
            round(self.position.x + self.width * ((1 - draw_rect_scale) / 2) + self.cosine * 5),
            round(self.position.y + self.height * ((1 - draw_rect_scale) / 2) + self.sine * 5),
            round(self.width * draw_rect_scale), round(self.height * draw_rect_scale)
        )
        pygame.draw.rect(surface, color, draw_rect, 3)
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
        draw_rect = (
            round(self.position.x + self.cosine * 5),
            round(self.position.y + self.sine * 5),
            round(self.width), round(self.height)
        )
        pygame.draw.rect(surface, self.color, draw_rect)

class heart:
    def __init__(self, floor):
        self.width, self.height = floor.tile_width, floor.tile_height
        self.position = floor.tile_to_position((0, 14))
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
        self.health = 3
    def reached_next_tile(self, floor):
        target = floor.tile_to_position(self.next_tile)
        dx, dy = self.current_direction or (0, 0)
        if dx != 0:
            return (self.position.x - target.x) * dx >= 0
        if dy != 0:
            return (self.position.y - target.y) * dy >= 0
        return False
    def move(self, dt, floor, dx, dy):
        step = self.speed * dt
        target = floor.tile_to_position(self.next_tile)
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
            self.position = floor.tile_to_position(self.next_tile)
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
        draw_width, draw_height = 30, 30
        scaled_image = pygame.transform.scale(image, (draw_width, draw_height))
        draw_position = self.position + pygame.Vector2(
            (self.width - draw_width) / 2,
            (self.height - draw_height) / 2,
        )
        surface.blit(scaled_image, draw_position)

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

class boss:
    def __init__(self, floor, xytuple):
        self.width, self.height = floor.tile_width, floor.tile_height
        self.current_tile = xytuple
        self.target_tile = self.current_tile
        self.position = floor.tile_to_position(self.current_tile)
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        self.health = 100
        self.base_speed = 300
        self.speed = self.base_speed
        self.moving = False
        self.path = astar_path(floor.grid, self.current_tile, self.target_tile)
        if self.path:
            self.path.pop(0)
        self.markov = markov_first_order()
        self.n_moves_ahead = 1
        self.timer = 0
        self.sine = math.sin(self.timer)
        self.on_cooldown = False
        self.cooldown_time = 2
        self.cooldown_timer = 0
    def follow_path(self, dt, floor, heart):
        # Update path
        if not self.path:
            predicted_tile = self.markov.predict_heart_n_tiles_ahead(heart, floor, self.n_moves_ahead)
            if predicted_tile is not None:
                self.target_tile = predicted_tile
                self.markov.record_prediction(
                    predicted_tile,
                    self.n_moves_ahead
                )
            self.path = astar_path(floor.grid, self.current_tile, self.target_tile)
            if self.path:
                self.path.pop(0)
            if not self.path:
                return
        # Follow
        step = self.speed * dt
        next_tile = self.path[0]
        target = floor.tile_to_position(next_tile)
        distance = target - self.position
        if distance.length() <= step:
            self.position = pygame.Vector2(target)
            self.current_tile = next_tile
            predicted_tile = self.markov.predict_heart_n_tiles_ahead(heart, floor, self.n_moves_ahead)
            if predicted_tile is not None:
                self.target_tile = predicted_tile
                self.markov.record_prediction(
                    predicted_tile,
                    self.n_moves_ahead
                )
            self.path = astar_path(floor.grid, next_tile, self.target_tile)
            if self.path:
                self.path.pop(0)
        else:
            self.position += distance.normalize() * step
    def damage_player(self, dt, floor, heart):
        if self.on_cooldown:
            self.cooldown_timer += dt
            if self.cooldown_timer < self.cooldown_time:
                return
            self.cooldown_timer = 0
            self.on_cooldown = False
        directions = [(0, 0), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1)]
        for dx, dy in directions:
            tile = (self.current_tile[0] + dx, self.current_tile[1] + dy)
            if floor.is_tile_outside_bounds(tile):
                continue
            if heart.current_tile == tile:
                self.on_cooldown = True
                heart.health -= 1
                break
    def update(self, dt, floor, heart):
        self.timer += dt * 4
        self.sine = math.sin(self.timer)
        self.speed = self.base_speed / math.sqrt(floor.tile_to_value(self.current_tile))
        # FSM logic for each state
        if self.health >= 70:
            self.n_moves_ahead = 1
        elif self.health >= 30:
            self.n_moves_ahead = 2
        else:
            self.n_moves_ahead = 3
        # FSM logic for all states
        self.markov.update(heart)
        self.follow_path(dt, floor, heart)
        self.rect.topleft = self.position
        self.damage_player(dt, floor, heart)
    def draw(self, surface, floor, debug_mode):
        # Target highlight
        if debug_mode:
            target_tile_grid_tile = floor.grid_tiles[self.target_tile[0]][self.target_tile[1]]
            target_tile_grid_tile.draw_target_highlight(surface, (255, 255, 0))
        # Boss
        image = assets.images["boss"]
        draw_width = self.width * 587 / 425 * 3
        draw_height = self.height * 3
        scaled_image = pygame.transform.scale(image, (draw_width, draw_height + self.sine * 25))
        draw_position = self.position - pygame.Vector2(
            (draw_width - self.width) / 2,
            (draw_height - self.height) / 2 + round(self.sine * 25))
        surface.blit(scaled_image, draw_position)

class mini_boss:
    def __init__(self, floor, xytuple, color):
        self.width, self.height = floor.tile_width, floor.tile_height
        self.current_tile = xytuple
        self.target_tile = self.current_tile
        self.position = floor.tile_to_position(self.current_tile)
        self.rect = pygame.Rect(self.position.x, self.position.y, self.width, self.height)
        self.color = color
        self.base_speed = 200
        self.speed = self.base_speed
        self.moving = False
        self.path = astar_path(floor.grid, self.current_tile, self.target_tile)
        if self.path:
            self.path.pop(0)
        self.timer = 0
        self.sine = math.sin(self.timer)
        self.on_cooldown = False
        self.cooldown_time = 2
        self.cooldown_timer = 0
        self.state = "wander"
    def follow_path(self, dt, floor, heart):
        # Update path if necessary
        if not self.path:
            if self.state == "wander":
                x = random.randint(0, floor.dimensions[0] - 1)
                y = random.randint(0, floor.dimensions[1] - 1)
                self.target_tile = (x, y)
            elif self.state == "attack":
                self.target_tile = heart.current_tile
                self.base_speed = 200
            elif self.state == "super_attack":
                self.target_tile = heart.current_tile
                self.base_speed = 400
            self.path = astar_path(floor.grid, self.current_tile, self.target_tile)
            if self.path:
                self.path.pop(0)
            if not self.path:
                return
        # Follow
        step = self.speed * dt
        next_tile = self.path[0]
        target = floor.tile_to_position(next_tile)
        distance = target - self.position
        if distance.length() <= step:
            self.position = pygame.Vector2(target)
            self.current_tile = next_tile
            # Update path if wanted
            if self.state == "attack":
                self.target_tile = heart.current_tile
                self.base_speed = 200
            elif self.state == "super_attack":
                self.target_tile = heart.current_tile
                self.base_speed = 400
            self.path = astar_path(floor.grid, next_tile, self.target_tile)
            if self.path:
                self.path.pop(0)
        else:
            self.position += distance.normalize() * step
    def damage_player(self, dt, heart):
        if self.on_cooldown:
            self.cooldown_timer += dt
            if self.cooldown_timer < self.cooldown_time:
                return
            self.cooldown_timer = 0
            self.on_cooldown = False
        if heart.current_tile == self.current_tile:
            self.on_cooldown = True
            heart.health -= 1
    def update(self, dt, floor, boss, heart):
        self.timer += dt * 4
        self.sine = math.sin(self.timer)
        self.speed = self.base_speed / math.sqrt(floor.tile_to_value(self.current_tile))
        # FSM logic for each state
        if floor.manhattan_distance(self.current_tile, heart.current_tile) >= 7:
            self.state = "wander"
        else:
            self.state = "attack"
        if boss.health < 30:
            self.state = "super_attack"
        # FSM logic for all states
        self.follow_path(dt, floor, heart)
        self.rect.topleft = self.position
        self.damage_player(dt, heart)
    def draw(self, surface, floor, debug_mode):
        # Target highlight
        if debug_mode:
            target_tile_grid_tile = floor.grid_tiles[self.target_tile[0]][self.target_tile[1]]
            target_tile_grid_tile.draw_target_highlight(surface, self.color)
        # Boss
        image = assets.images["mini_boss"]
        draw_width = self.width * 518 / 482
        draw_height = self.height
        scaled_image = pygame.transform.scale(image, (draw_width, draw_height + self.sine * 25))
        draw_position = self.position - pygame.Vector2(
            (draw_width - self.width) / 2,
            (draw_height - self.height) / 2 + round(self.sine * 25))
        surface.blit(scaled_image, draw_position)

class markov_first_order:
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
        # Stats
        self.total_predictions = 0
        self.correct_predictions = 0
        self.accuracy = 0
        self.pending_predictions = []
        self.move_count = 0
        self.last_prediction_move_count = None
        self.last_accuracy_tile = None
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
    def record_prediction(self, predicted_tile, n):
        if self.last_prediction_move_count == self.move_count:
            return
        self.pending_predictions.append([
            predicted_tile,
            self.move_count + n
        ])
        self.last_prediction_move_count = self.move_count
    def update_accuracy(self, heart):
        if self.last_accuracy_tile is None:
            self.last_accuracy_tile = heart.current_tile
            return
        if heart.current_tile != self.last_accuracy_tile:
            self.move_count += 1
            self.last_accuracy_tile = heart.current_tile
        for prediction in self.pending_predictions[:]:
            predicted_tile = prediction[0]
            target_move_count = prediction[1]
            if self.move_count >= target_move_count:
                self.total_predictions += 1
                if predicted_tile == heart.current_tile:
                    self.correct_predictions += 1
                self.pending_predictions.remove(prediction)
        if self.total_predictions > 0:
            self.accuracy = self.correct_predictions / self.total_predictions
    def format_accuracy(self):
        return str(round(self.accuracy * 100, 3)) + "%"
    def predict_heart_n_tiles_ahead(self, heart, floor, n):
        direction = heart.current_direction
        if direction is None:
            direction = heart.last_direction
            if direction is None:
                return None
        def find_path(direction, tile, steps):
            if steps == 0:
                return (1, tile)
            row = self.heart_behavior[self.directions.index(direction)]
            if sum(row) == 0:
                return (0, tile)
            best_probability = 0
            best_tile = None
            for i in range(4):
                if row[i] == 0:
                    continue
                probability = row[i] / sum(row)
                next_direction = self.directions[i]
                next_tile = (
                    tile[0] + next_direction[0],
                    tile[1] + next_direction[1]
                )
                if floor.is_tile_outside_bounds(next_tile):
                    continue
                future_probability, future_tile = find_path(
                    next_direction, next_tile, steps - 1
                )
                total_probability = probability * future_probability
                if total_probability > best_probability:
                    best_probability = total_probability
                    best_tile = future_tile
            return (best_probability, best_tile)
        probability, predicted_tile = find_path(
            direction, heart.current_tile, n
        )
        return predicted_tile
    def update(self, heart):
        self.update_heart_behavior(heart)
        self.update_accuracy(heart)

class item:
    item_list = []
    def __init__(self, floor, xytuple):
        self.position = pygame.Vector2(xytuple[0] * floor.tile_width, xytuple[1] * floor.tile_height)
        self.tile = xytuple
        self.width, self.height = floor.tile_width, floor.tile_height
        self.types = [
            "heal_player",
            "damage_boss",
            "damage_boss_big",
            "damage_player",
            "damage_player_big",
        ]
        self.type_weights = [4, 7, 1, 4, 1]
        self.type = random.choices(self.types, self.type_weights)[0]
        self.timer = floor.grid_tiles[self.tile[0]][self.tile[1]].timer
        self.sine = math.sin(self.timer)
        self.cosine = math.cos(self.timer)
    def get_collected(self, heart, boss):
        if heart.current_tile == self.tile:
            self.item_list.remove(self)
            if self.type == "heal_player":
                heart.health += 1
            elif self.type == "damage_boss":
                boss.health = max(0, boss.health - 3)
            elif self.type == "damage_boss_big":
                boss.health = max(0, boss.health - 10)
            elif self.type == "damage_player":
                heart.health = max(0, heart.health - 1)
            elif self.type == "damage_player_big":
                heart.health = max(0, heart.health - 3)
    def update(self, dt, heart, boss):
        self.timer += dt * 3
        self.sine = math.sin(self.timer)
        self.cosine = math.cos(self.timer)
        self.get_collected(heart, boss)
    def draw(self, surface):
        image = assets.images[self.type]
        scaled_image = pygame.transform.scale(image, (self.width, self.height))
        if self.type == "damage_player" or self.type == "damage_player_big":
            draw_position = pygame.Vector2(
                round(self.position.x + self.cosine * 5),
                round(self.position.y + self.sine * 5)
            )
        else:
            draw_position = pygame.Vector2(
                round(self.position.x),
                round(self.position.y + self.sine * 10)
            )
        surface.blit(scaled_image, draw_position)