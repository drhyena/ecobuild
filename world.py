import random
import pygame
from noise import pnoise2


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
        self.noise_octaves = noise_octaves
        self.noise_persistence = noise_persistence
        self.noise_lacunarity = noise_lacunarity

        self.seed = world_seed if world_seed is not None else random.randint(0, 10000)

        self.map_grid = self.generate_world()

        self.land_tiles= None
        self.water_tiles = None
        self.shore_tiles= None

    def generate_world(self):
        world = [
            [None for _ in range(self.grid_height)]
            for _ in range(self.grid_width)
        ]

        for x in range(self.grid_width):
            for y in range(self.grid_height):
                nx = x / self.noise_scale
                ny = y / self.noise_scale

                warp_x = pnoise2(nx + 100, ny + 100) * 8
                warp_y = pnoise2(nx - 100, ny - 100) * 8

                n = pnoise2(
                    nx + warp_x,
                    ny + warp_y,
                    octaves=self.noise_octaves,
                    persistence=self.noise_persistence,
                    lacunarity=self.noise_lacunarity,
                    base=self.seed
                )

                world[x][y] = "water" if -0.15 < n < -0.05 else "land"

        return world

    def return_land(self):
        if self.land_tiles == None :

            self.land_tiles= [
                (x, y)
                for x in range(self.grid_width)
                for y in range(self.grid_height)
                if self.map_grid[x][y] == "land"
            ]
            return self.land_tiles

    def return_water(self):
        if self.water_tiles == None:

            self.water_tiles= [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if self.map_grid[x][y] == "water"
        ]
            return self.water_tiles
        


    def return_shore_tiles(self,land,water):
        
        shore = []

        for x, y in land:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    if (x + dx, y + dy) in water:
                        shore.append((x, y))
                        break
                else:
                    continue
                break

        return shore
    

    def is_walkable(self,x,y):
         if self.map_grid[x][y] == "land":
             return True
                
                 
                 
            

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

    def find_closest_veg(self, veg_list,x,y,perceptive_radius):
        perceived_tiles =[ (dx, dy)
                                    for dx 
                                    for dy in range(-5, 6)
                                    if not (dx == 0 and dy == 0)
        ]
        target_veg = None
        min_distance = float("inf")
 
        for v in veg_list:
                if v.status != "alive":
                    continue
                if (v.v_x, v.v_y) in adjacent_tiles:
                    dx = x - v.v_x
                    dy = x- v.v_y
                    distance = (dx * dx + dy * dy) ** 0.5

                    if distance < min_distance:
                        min_distance = distance
                        target_veg = (x, y)
                    
                if target_veg:
                    return target_veg
                
        return False
    
    def find_closest_shore(self,x,y):
        adjacent_tiles= self.get_neighbors(x,y)
        closest_shore = None
        min_distance = float("inf")


        valid_tiles = [tile for tile in adjacent_tiles if tile in self.shore_tiles]

        for x, y in valid_tiles:
            dx = x - self.x
            dy = y - self.y
            distance = (dx * dx + dy * dy) ** 0.5

            if distance < min_distance:
                min_distance = distance
                closest_shore = (x, y)

        if closest_shore:
            return closest_shore
            

        


    
    def draw_map(self, screen):
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                tile = self.map_grid[x][y]
                color = (30, 90, 160) if tile == "water" else (40, 160, 60)
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
