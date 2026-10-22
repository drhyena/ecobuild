import sys
sys.dont_write_bytecode = True


import pygame
import random
from astar import *
from config import WIDTH, HEIGHT, TILE_SIZE, GRID_WIDTH, GRID_HEIGHT, NOISE_SCALE,WORLD_SEED, MAX_VEG_COUNT
from world import World
from veg import Veg
from interactions import *
from creature import Creature
from Predator import Predator
from Prey import Prey
from renderer import Renderer
from logger import Logger

pygame.init()


clock = pygame.time.Clock()

log = Logger()
world = World(GRID_WIDTH, GRID_HEIGHT, TILE_SIZE,NOISE_SCALE,
    WORLD_SEED)

renderer = Renderer(WIDTH,HEIGHT,world.tile_size)

interactmanager = InteractionSystem(world)

# Creating Creature and Vegetation objects
world.set_maptypes()

def create_creatures_random(num_predators, num_prey):

    predators = [
        Predator(*random.choice(tuple(world.land_tiles)), world, interactmanager,log)
        for _ in range(num_predators)
    ]

    prey = [
        Prey(*random.choice(tuple(world.land_tiles)),world,  interactmanager,log)
        for _ in range(num_prey)
    ]

    creatures = predators + prey

    return predators, prey, creatures

predators, prey, creatures = create_creatures_random(10, 100)
#creatures = [Creature(*random.choice(tuple(world.land_tiles)), world, interactmanager) for _ in range(10)]

#creatures = [       Predator(*random.choice(tuple(world.land_tiles)), world, interactmanager) for _ in range(10]
world.creature_list = set(creatures)
world.set_position_dict()

for c in creatures:
    log.log_creature(c)



def create_veg_random(n):
    return [Veg(*random.choice(tuple(world.land_tiles))) for _ in range(n)]


vege = create_veg_random(25)
world.veg_list = vege
for v in world.veg_list:
    world.set_max_tiles(v)

world.set_v_position_dict()

#veg spawning
VEG_SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(VEG_SPAWN_EVENT, 500)
# MAIN GAME LOOP    
running = True
while running:
    renderer.screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == VEG_SPAWN_EVENT and len(world.veg_list)<MAX_VEG_COUNT  :
            veg = Veg(*random.choice(tuple(world.land_tiles)))
            vege.append(veg)  
            world.update_v_position_dict(veg)
            world.set_max_tiles(veg)

    
    renderer.draw_world(world.grid_width,world.grid_height,world.shore_tiles,world.map_grid)
    #calling all creature related functions.
    # world.creature_list is the source of truth: births (ReproductionManager.mate) add to it
    # and deaths remove from it. Work on a snapshot so changes mid-frame are safe: newborns
    # join next frame, and anything that dies mid-frame is skipped by the alive checks.
    creatures = [c for c in world.creature_list if c.vitals.alive]
    for c in creatures:
        if c.vitals.alive:
            c.update()
    for c in creatures:
        if c.vitals.alive:
            c.status_checker()
    for c in creatures:
        if c.vitals.alive:
            c.movement_decider()
    for c in creatures:
        if c.vitals.alive:
            renderer.draw_creature(c)
    world.creature_list.difference_update([c for c in creatures if not c.vitals.alive])  # purge the dead
    print(f" the total no:of creatures is : {len(world.creature_list)}")


    for v in vege:
        renderer.draw_veg(v)

    renderer.flip()
    dt_ms = clock.tick(60)
    world.dt = dt_ms/1000
    world.sim_time += world.dt
    next_sample = 0

    if world.sim_time>= next_sample:
        log.log_total_dataframe(world)

pygame.quit()

log.plot_population(log)
log.plot_avg_speed()