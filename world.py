import random
import pygame
from opensimplex import OpenSimplex


class World:
    def __init__(
        self,
        grid_width,
        grid_height,
        tile_size,
        noise_scale,
        noise_octaves,
        noise_persistence,
        noise_lacunarity,
        world_seed=None
    ):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.tile_size = tile_size

        self.noise_scale = noise_scale

        # Seed handling
        self.seed = world_seed if world_seed is not None else random.randint(0, 10000)

        # Create OpenSimplex generator
        self.noise_gen = OpenSimplex(seed=self.seed)

        # Generate map
        self.map_grid = self.generate_world()

        # Cached tile groups
        self.land_tiles = None
        self.water_tiles = None
        self.shore_tiles = None

        # Precompute tile types
        self.set_maptypes()

    # --------------------------------------------------
    # WORLD GENERATION
    # --------------------------------------------------

    def generate_world(self):
        world = [
            [None for _ in range(self.grid_height)]
            for _ in range(self.grid_width)
        ]

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                nx = x / self.noise_scale
                ny = y / self.noise_scale

                # Domain warping for better terrain shapes
                warp = self.noise_gen.noise2(nx + 50, ny + 50) * 5

                n = self.noise_gen.noise2(nx + warp, ny + warp)

                # Normalize from [-1, 1] → [0, 1]
                n = (n + 1) / 2

                # Water threshold
                world[x][y] = "water" if 0.4 < n < 0.48 else "land"

        return world

    # --------------------------------------------------
    # TILE TYPE CACHING
    # --------------------------------------------------

    def set_maptypes(self):
        self.land_tiles = [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if self.map_grid[x][y] == "land"
        ]

        self.water_tiles = {
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if self.map_grid[x][y] == "water"
        }

        self.shore_tiles = self.compute_shore_tiles()

    def compute_shore_tiles(self):
        shore = set()

        for x, y in self.land_tiles:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue

                    if (x + dx, y + dy) in self.water_tiles:
                        shore.add((x, y))
                        break
                else:
                    continue
                break

        return shore

    # --------------------------------------------------
    # UTILITIES
    # --------------------------------------------------

    def is_walkable(self, x, y):
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            return self.map_grid[x][y] == "land"
        return False

    def get_neighbors(self, x, y):
        offsets = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        neighbors = []

        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                neighbors.append((nx, ny))

        return neighbors

    # --------------------------------------------------
    # SEARCH FUNCTIONS
    # --------------------------------------------------

    def find_closest_veg(self, veg_list, x, y, perceived_tiles):
        target_veg = None
        min_distance = float("inf")

        perceived_set = set(perceived_tiles)

        for v in veg_list:
            if v.alive and (v.v_x, v.v_y) in perceived_set:
                dx = x - v.v_x
                dy = y - v.v_y
                distance = dx * dx + dy * dy

                if distance < min_distance:
                    min_distance = distance
                    target_veg = v

        print("veg:", target_veg.alive if target_veg is not None else "none")
        return target_veg

    def find_closest_shore(self, x, y, perceived_tiles):
        closest_shore = None
        min_distance = float("inf")

        for u, v in perceived_tiles:
            if (u, v) in self.shore_tiles:
                dx = x - u
                dy = y - v
                distance = dx * dx + dy * dy

                if distance < min_distance:
                    min_distance = distance
                    closest_shore = (u, v)

        print("closest shore:", closest_shore)
        return closest_shore

    def find_closest_prey(self, c, creature_list):
        perceived_creatures = self.check_for_creatures_in_perspective_tiles(c, creature_list)

        if not perceived_creatures:
            return None

        closest_creature = None
        min_distance = float('inf')

        for other in perceived_creatures:
            if other == c:
                continue  # don't target itself

            dx = other.x - c.x
            dy = other.y - c.y
            distance = dx * dx + dy * dy  # squared distance (faster than sqrt)

            if distance < min_distance:
                min_distance = distance
                closest_creature = other

        return closest_creature
    
    def compute_best_flee_tile(self, prey, predator):
        if predator is None:
            return None

        neighbors = self.get_neighbors(prey.x, prey.y)

        best_tile = None
        max_dist = -1

        for nx, ny in neighbors:
            if self.is_walkable(nx, ny):
                dx = nx - predator.x
                dy = ny - predator.y
                dist = dx * dx + dy * dy

                if dist > max_dist:
                    max_dist = dist
                    best_tile = (nx, ny)

        return best_tile
    # --------------------------------------------------
    # DRAWING
    # ----------------------------------------
    # ----------

    def draw_map(self, screen):
        for x in range(self.grid_width):
            for y in range(self.grid_height):

                if (x, y) in self.shore_tiles:
                    color = (194, 178, 128)  # sandy
                elif self.map_grid[x][y] == "water":
                    color = (30, 90, 160)
                else:
                    color = (40, 160, 60)

                pygame.draw.rect(
                    screen,
                    color,
                    (
                        x * self.tile_size,
                        y * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )
                )