#file that contains the details of the world.
import numpy as np
import pygame
class World:
    def __init__(self,GRID_HEIGHT,GRID_WIDTH,TILE_SIZE):
        self.GRID_HEIGHT = GRID_HEIGHT
        self.GRID_WIDTH = GRID_WIDTH 
        self.TILE_SIZE = TILE_SIZE
        self.map_grid = np.random.choice(["land", "water"], size=(self.GRID_WIDTH, self.GRID_HEIGHT), p=[0.9, 0.1])
        self.land_positions = list(map(tuple, np.array(np.where(self.map_grid == "land")).T))
        self.water_positions = list(map(tuple, np.array(np.where(self.map_grid == "water")).T))
        
    def draw_map(self,screen):        
        """Draws the entire map once for better performance."""        
        land_color = (34, 139, 34)
        water_color = (0, 0, 255)
        for (x, y) in self.land_positions:
            pygame.draw.rect(screen, land_color, (x * self.TILE_SIZE, y * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))
        for x in range(self.GRID_WIDTH):
            for y in range(self.GRID_HEIGHT):
                if self.map_grid[x, y] == "water":
                    pygame.draw.rect(screen, water_color, (x * self.TILE_SIZE, y * self.TILE_SIZE, self.TILE_SIZE, self.TILE_SIZE))

    def return_land(self):
        return self.land_positions 
    
    def return_water(self):
        return self.water_positions
    def return_map(self):
        return self.map_grid