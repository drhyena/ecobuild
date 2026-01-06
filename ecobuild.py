import pygame
import random
from astar import *
from config import WIDTH, HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, MAX_VEG_COUNT, NOISE_SCALE, NOISE_OCTAVES,NOISE_PERSISTENCE, NOISE_LACUNARITY,WORLD_SEED
from world import World
from veg import Veg
from creature import Creature

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

VEG_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(VEG_SPAWN_EVENT, 10 * 1000)

world = World(GRID_HEIGHT, GRID_WIDTH, TILE_SIZE,NOISE_SCALE, NOISE_OCTAVES,
    NOISE_PERSISTENCE, NOISE_LACUNARITY,
    WORLD_SEED)
map_grid = world.map_grid

land_positions = world.return_land()
water_positions = world.return_water()
shore_positions = world.return_shore_tiles(land_positions,water_positions)

def create_creatures_random(n):
    return [Creature(*random.choice(land_positions)) for _ in range(n)]


def create_veg_random(n):
    return [Veg(*random.choice(land_positions)) for _ in range(n)]



vege = create_veg_random(10)
creatures = create_creatures_random(5)

def eating_handler():
    for ce in creatures:
        for ve in vege:
            if (ce.x,ce.y) == (ve.v_x,ve.v_y) and ve.status == "alive" and ce.status in("hungry","super hungry"):
                ce.eat_veg()
                ve.confirm_eaten()

def drinking_handler():
    print("x")
    for ce in creatures:
        if  (ce.x,ce.y) == ce.target:
            ce.drink_water()


    
running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == VEG_SPAWN_EVENT and len(vege) < MAX_VEG_COUNT:
            vege.append(Veg(*random.choice(land_positions)))

    world.draw_map(screen)
    eating_handler()
    for c in creatures:
        c.status_setter()
    for c in creatures:   
        c.status_checker()    
    for c in creatures:
        c.state_machine() 
    for c in creatures:       
        c.draw(screen, TILE_SIZE)

    for v in vege:
        v.draw(screen, TILE_SIZE)

    pygame.display.flip()
    clock.tick(2)

pygame.quit()
