import pygame
import numpy as np
import random
import heapq
import math 
from astar import *
from config import WIDTH, HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, MAX_VEG_COUNT
from world import World
# Initialize Pygame
pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
# Set timer for vegetation spawning every 10 seconds
VEG_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(VEG_SPAWN_EVENT, 10 * 1000)  # 10 seconds (1000 ms per second)

world = World(GRID_HEIGHT,GRID_WIDTH,TILE_SIZE)
map_grid=world.map_grid
class Veg:
    def __init__(self, v_x, v_y):
        self.v_x, self.v_y = v_x, v_y
        self.status = "alive"

    def draw(self):
        if self.status == "alive":
            pygame.draw.circle(screen, (255, 0, 0),
                               (self.v_x * TILE_SIZE + TILE_SIZE // 2,
                                self.v_y * TILE_SIZE + TILE_SIZE // 2), 5)

class Creature:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.thirst = 100
        self.hunger= 100
        self.target = (0,0)
        self.path = []
        self.status = ""
        # initialize adjacent_tiles
        self.adjacent_tiles = [()]
        self.next_tiles= [()]

    def update_adjacent_tiles(self):
        """Recompute adjacent tiles each time creature moves/checks."""
        self.adjacent_tiles = [(self.x + dx, self.y + dy)for dx in range(-2, 3) for dy in range(-2, 3)if 0 <= self.x + dx < GRID_WIDTH and 0 <= self.y + dy < GRID_HEIGHT]
        self.next_tiles= [(self.x + dx, self.y + dy) for dx in range(-1, 2) for dy in range(-1, 2) if 0 <= self.x + dx < GRID_WIDTH and 0 <= self.y + dy < GRID_HEIGHT]

    def find_closest_veg(self):
        """Finds the closest vegetation. Returns True if there is veg in adjacent tiles (within radius)."""
        # Refresh adjacency
        self.update_adjacent_tiles()
        # scan all veg to find closest; also check if any are inside adjacent_tiles
        for v in vege:
            if v.status != "alive":
                continue
            vx, vy = v.v_x, v.v_y
            # if a veg coord is in adjacent tiles -> immediate detection
            if (vx, vy) in self.adjacent_tiles:
                self.target = v
                print("found adjacent veg at", (vx, vy))
                return True
            else:
                return False

    def find_closest_water(self):
        self.update_adjacent_tiles()
        prob_cords ={}
        dist = 0
        for i in water_positions:
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0),(1, 1), (1, -1), (-1, 1), (-1, -1)])
            x_i,y_i = i[0] + dx, i[1] + dy
            if 0 <= x_i < GRID_WIDTH and 0 <= y_i < GRID_HEIGHT and map_grid[x_i , y_i] == "land":
                dist= math.sqrt((self.x - x_i) ** 2 + (self.y - y_i) ** 2)
                prob_cords.update({(x_i,y_i): dist})
 
    def status_setter(self):
        self.hunger-=2
        self.thirst-=3
        if not self.status:
            if self.hunger<20:
                    self.status="hungry"
            if self.thirst<40:
                    self.status="thirsty"
            if (self.hunger < self.thirst) and self.thirst < 20:
                self.status = "super hungry"
            if (self.hunger > self.thirst) and self.hunger < 20:
                self.status = "super thirsty"
        
        

    
    def wander_randomly(self):
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0),(1, 1), (1, -1), (-1, 1), (-1, -1)])
            new_x, new_y = self.x + dx, self.y + dy
            if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and map_grid[new_x, new_y] != "water":
             self.x, self.y = new_x, new_y
           
            


    def seek_target(self):
        """Find closest veg or water and set path using A*."""
        if self.status == "hungry":
            if self.find_closest_veg():
                self.path = astar((self.x, self.y),(self.target.v_x,self.target.v_y), map_grid,WIDTH, HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, MAX_VEG_COUNT)


        # Later you can add thirst logic hereA
        # if self.thirst < X: ... find water ...


    def follow_path(self):
        """Follow the path from A*."""
        if self.path:
            next_step = self.path.pop(0)
            self.x, self.y = next_step


    def drink_water(self):
        """Replenish thirst if water is nearby."""
        # ensure adjacency is up to date
        self.update_adjacent_tiles()
        if self.thirst < 40:
            if any(0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and map_grid[x, y] == "water"
                   for x, y in self.next_tiles):
                self.thirst += 20
                print("drinking")
                self.status = "Drinking"

    def draw(self):
        """Draws the creature and status text."""
        pygame.draw.circle(screen, (0, 255, 0),
                           (self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2), 5)
        font = pygame.font.Font(None, 16)
        text = font.render(self.status, True, (255, 255, 255))
        screen.blit(text, (self.x * TILE_SIZE, self.y * TILE_SIZE - 10))

# Initialize simulation
land_positions=world.return_land()
water_positions=world.return_water()
creatures = [Creature(*random.choice(land_positions)) for _ in range(5)]
vege = [Veg(*random.choice(land_positions)) for _ in range(50)]

# Game loop
running = True
while running:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == VEG_SPAWN_EVENT and len(vege) < MAX_VEG_COUNT:
            vege.append(Veg(*random.choice(land_positions)))

    world.draw_map(screen)
    creatures = [c for c in creatures if c.thirst]

    for c in creatures:
        c.status = ""  # reset status at start of frame
        c.status_setter()
        c.wander_randomly()
        c.draw()

    for v in vege:
        v.draw()

    pygame.display.flip()
    clock.tick(2)

pygame.quit()

