import pygame
import numpy as np
import random
import heapq

# Initialize Pygame
pygame.init()
WIDTH, HEIGHT = 900, 700
TILE_SIZE = 10
GRID_WIDTH, GRID_HEIGHT = WIDTH // TILE_SIZE, HEIGHT // TILE_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Generate a random map with 30% water
map_grid = np.random.choice(["land", "water"], size=(GRID_WIDTH, GRID_HEIGHT), p=[0.7, 0.3])

# Store land positions for fast lookup
land_positions = np.array(np.where(map_grid == "land")).T

# Set timer for vegetation spawning every 10 seconds
VEG_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(VEG_SPAWN_EVENT, 10 * 1000)  # 10 seconds (1000 ms per second)

MAX_VEG_COUNT = 100  # Limit for vegetation to prevent overflow

def draw_map():
    """Draws the entire map once for better performance."""
    land_color = (34, 139, 34)
    water_color = (0, 0, 255)
    for (x, y) in land_positions:
        pygame.draw.rect(screen, land_color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            if map_grid[x, y] == "water":
                pygame.draw.rect(screen, water_color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

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
        self.hunger = 100  
        self.target_veg = None
        self.path = []
        self.status = "Idle"  
        self.stuck_counter = 0  
        self.last_pos = (x, y)
        self.adjacent_tiles = [(self.x + dx, self.y + dy) for  dx   in  range(-2,3) for dy in range(-2,3) ]
    def find_closest_veg(self):
        """Finds the closest vegetation."""
        for i in vege:
            if i in self.adjacent_tiles:
                self.a_star_path(i.v_x, i.v_y)
            else:
                return
            



    def a_star_path(self, target_x, target_y):
        """Finds the shortest path to target using A* with diagonal movement."""
        def heuristic(a, b):
            return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev distance for diagonals

        open_set = []
        heapq.heappush(open_set, (0, (self.x, self.y)))
        came_from = {}
        g_score = {node: float('inf') for node in np.ndindex(GRID_WIDTH, GRID_HEIGHT)}
        g_score[(self.x, self.y)] = 0
        f_score = {node: float('inf') for node in np.ndindex(GRID_WIDTH, GRID_HEIGHT)}
        f_score[(self.x, self.y)] = heuristic((self.x, self.y), (target_x, target_y))

        directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]  # 8 directions

        while open_set:
            _, current = heapq.heappop(open_set)
            if current == (target_x, target_y):
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                self.path = path[::-1]
                return

            for dx, dy in directions:
                neighbor = (current[0] + dx, current[1] + dy)
                if 0 <= neighbor[0] < GRID_WIDTH and 0 <= neighbor[1] < GRID_HEIGHT and map_grid[neighbor] != "water":
                    tentative_g_score = g_score[current] + 1
                    if tentative_g_score < g_score[neighbor]:
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, (target_x, target_y))
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

    def move(self):
        """Handles movement logic."""
        if self.hunger < 40:
            print("hungry")
            self.find_closest_veg()
            
            if self.path:
                self.x, self.y = self.path.pop(0)
                if (self.x, self.y) == (self.target_veg.v_x, self.target_veg.v_y):
                    self.hunger = 100  
                    self.target_veg.status = "dead"  
                    self.target_veg = None
                    self.path = []
                    self.status = "Eating"
                    print("eating...")

        else:
            self.status = "Idle"
            if (self.x, self.y) == self.last_pos:
                self.stuck_counter += 1
            else:
                self.stuck_counter = 0
            self.last_pos = (self.x, self.y)

            if self.stuck_counter < 10:
                dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)])
                new_x, new_y = self.x + dx, self.y + dy
                if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT and map_grid[new_x, new_y] != "water":
                    self.x, self.y = new_x, new_y
            self.hunger-=1

    def drink_water(self):
        """Replenish thirst if water is nearby."""
       
        if self.thirst<40:
            if any(0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and map_grid[x, y] == "water" for x, y in adjacent_tiles):
                self.thirst = 100
                self.status = "Drinking"
            else:
                self.thirst -= 1

    def draw(self):
        """Draws the creature and status text."""
        pygame.draw.circle(screen, (0, 255, 0), (self.x * TILE_SIZE + TILE_SIZE // 2, self.y * TILE_SIZE + TILE_SIZE // 2), 5)
        font = pygame.font.Font(None, 16)
        text = font.render(self.status, True, (255, 255, 255))
        screen.blit(text, (self.x * TILE_SIZE, self.y * TILE_SIZE - 10))

# Initialize simulation
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

    draw_map()
    creatures = [c for c in creatures if c.hunger > 0 and c.thirst > 0]  
    for c in creatures:
        c.move()
        c.drink_water()
        c.draw()

    for v in vege:
        v.draw()

    pygame.display.flip()
    clock.tick(20)

pygame.quit()
