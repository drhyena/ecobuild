import pygame
import random
from astar import *
from config import WIDTH, HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, MAX_VEG_COUNT, NOISE_SCALE, NOISE_OCTAVES,NOISE_PERSISTENCE, NOISE_LACUNARITY,WORLD_SEED
from world import World
from veg import Veg
from creature import Creature
from interactions import *
import time
from Predator import Predator
from Prey import Prey
from renderer import Renderer

pygame.init()
renderer = Renderer(WIDTH,HEIGHT)

clock = pygame.time.Clock()


world = World(GRID_WIDTH, GRID_HEIGHT, TILE_SIZE,NOISE_SCALE, NOISE_OCTAVES,
    NOISE_PERSISTENCE, NOISE_LACUNARITY,
    WORLD_SEED)
interactmanager = InteractionSystem(world)

# Creating Creature and Vegetation objects
world.set_maptypes()

def create_creatures_random(num_predators, num_prey):

    predators = [
        Predator(*random.choice(tuple(world.land_tiles)), interactmanager)
        for _ in range(num_predators)
    ]

    prey = [
        Prey(*random.choice(tuple(world.land_tiles)), interactmanager)
        for _ in range(num_prey)
    ]

    creatures = predators + prey

    return predators, prey, creatures

predators, preys, creatures = create_creatures_random(5, 25)

def create_veg_random(n):
    return [Veg(*random.choice(tuple(world.land_tiles))) for _ in range(n)]

vege = create_veg_random(15)

#veg spawning
VEG_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(VEG_SPAWN_EVENT, 5000)
# MAIN GAME LOOP    
running = True
while running:
    start = time.time()
    renderer.screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == VEG_SPAWN_EVENT:
            vege.append(Veg(*random.choice(tuple(world.land_tiles))))  
            print("veg spawned") 
    
    renderer.draw_world(world.grid_width,world.grid_height,world.tile_size,world.shore_tiles,world.map_grid)
    #calling all creature related functions.
    for c in creatures:
        c.update(world, vege, creatures)
    for c in creatures:   
        c.status_checker(world, vege, creatures)    
    for c in creatures:       
        c.movement_decider(world, renderer.screen)
    for c in creatures:  
        renderer.draw_creature(c,TILE_SIZE)     
    


    for v in vege:
        v.draw(screen, TILE_SIZE)

    renderer.flip()
    pygame.display.flip()
    clock.tick(5)
    print("Frame time:", time.time() - start)

pygame.quit()