import pygame
import random
from astar import *
from config import WIDTH, HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, MAX_VEG_COUNT, NOISE_SCALE, NOISE_OCTAVES,NOISE_PERSISTENCE, NOISE_LACUNARITY,WORLD_SEED
from world import World
from veg import Veg
from creature import Creature
from interactions import *
from astarmanager import *
import time
import gc

gc.disable()

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
clock = pygame.time.Clock()


world = World(GRID_WIDTH, GRID_HEIGHT, TILE_SIZE,NOISE_SCALE, NOISE_OCTAVES,
    NOISE_PERSISTENCE, NOISE_LACUNARITY,
    WORLD_SEED)
interactmanager = InteractionSystem(world)

astarmanager = Astarmanager()
# Creating Creature and Vegetation objects
world.set_maptypes()
def create_creatures_random(n):
    return [Creature(*random.choice(tuple(world.land_tiles)),world) for _ in range(n)]
def create_veg_random(n):
    return [Veg(*random.choice(tuple(world.land_tiles))) for _ in range(n)]

vege = create_veg_random(100)
creatures = create_creatures_random(10)


# MAIN GAME LOOP    
running = True
while running:
    start = time.time()
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    world.draw_map(screen)
    #calling all creature related functions.5
    for c in creatures:
        c.update(world,interactmanager,vege,creatures)
    for c in creatures:   
        c.status_checker(world,interactmanager,vege,creatures)    
    for c in creatures:       
        c.movement_decider(world,screen)
    print("c")
    for c in creatures:       
        c.draw(screen, TILE_SIZE)


    for v in vege:
        v.draw(screen, TILE_SIZE)

    pygame.display.flip()
    clock.tick(6)
    print("Frame time:", time.time() - start)

pygame.quit()
