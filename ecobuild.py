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

world = World(GRID_WIDTH, GRID_HEIGHT, TILE_SIZE,NOISE_SCALE, NOISE_OCTAVES,
    NOISE_PERSISTENCE, NOISE_LACUNARITY,
    WORLD_SEED)

# Creating Creature and Vegetation objects
def create_creatures_random(n):
    return [Creature(*random.choice(world.return_land())) for _ in range(n)]
def create_veg_random(n):
    return [Veg(*random.choice(world.return_land())) for _ in range(n)]

vege = create_veg_random(10)
creatures = create_creatures_random(5)


# MAIN GAME LOOP    
running = True
while running:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
    world.draw_map(screen)
    #calling all creature related functions.
    for c in creatures:
        c.update(world)
    for c in creatures:   
        c.status_checker(world,vege)    
    for c in creatures:
        c.movement_decider(world,screen)
    for c in creatures:       
        c.draw(screen, TILE_SIZE)


    for v in vege:
        v.draw(screen, TILE_SIZE)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
