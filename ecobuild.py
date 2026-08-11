import pygame
import random
from astar import *
from config import WIDTH, HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, MAX_VEG_COUNT, NOISE_SCALE, NOISE_OCTAVES,NOISE_PERSISTENCE, NOISE_LACUNARITY,WORLD_SEED
from world import World
from veg import Veg
from interactions import *
from Predator import Predator
from Prey import Prey
from renderer import Renderer

pygame.init()


clock = pygame.time.Clock()


world = World(GRID_WIDTH, GRID_HEIGHT, TILE_SIZE,NOISE_SCALE,
    WORLD_SEED)

renderer = Renderer(WIDTH,HEIGHT,world.tile_size)

interactmanager = InteractionSystem(world)

# Creating Creature and Vegetation objects
world.set_maptypes()

def create_creatures_random(num_predators, num_prey):

    predators = [
        Predator(*random.choice(tuple(world.land_tiles)), world, interactmanager)
        for _ in range(num_predators)
    ]

    prey = [
        Prey(*random.choice(tuple(world.land_tiles)),world,  interactmanager)
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
    renderer.screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == VEG_SPAWN_EVENT:
            vege.append(Veg(*random.choice(tuple(world.land_tiles))))  
            print("veg spawned") 
    
    renderer.draw_world(world.grid_width,world.grid_height,world.shore_tiles,world.map_grid)
    #calling all creature related functions.
    for c in creatures:
        c.update( vege, creatures)
    for c in creatures:   
        c.status_checker(world, vege, creatures)    
    for c in creatures:       
        c.movement_decider(world)
    for c in creatures:  
        renderer.draw_creature(c)     
    


    for v in vege:
        renderer.draw_veg(v)

    renderer.flip()
    dt_ms = clock.tick(5)
    world.dt = dt_ms

pygame.quit()