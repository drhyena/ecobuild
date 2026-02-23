import random
import pygame
import math
import gc
from astar import *
gc.disable()


class Creature:
    def __init__(self, x, y,world):
        self.x, self.y = x, y
        self.thirst = 100
        self.hunger = 30
        self.target = None
        self.path = []
        self.status = ""
        self.perceptive_radius = [
                                    (dx, dy)
                                    for dx in range(-10, 11)
                                    for dy in range(-10, 11)
                                    if not (dx == 0 and dy == 0)
        ]
        self.perceived_tiles = []
    
    

   
    
        
# Actions. This area reprents the actions of a creature. Overlaps with state machine. 
    def drink_water(self):
            if self.status == "thirsty":
                print("drinking")
                self.thirst = 100
            
    def eat_veg(self):
        if self.status in ("hungry"):
            print("eating")
            self.hunger = 100
    
    def drink_water(self,closest_shore):
        if (self.x,self.y) == closest_shore:
            self.thirst == 100
            
   
                     
# state machine core. This area is the "brain" of the creature. 
    def update(self,world,interactionmanager):
        self.hunger =self.hunger -1
        self.thirst = self.thirst -3
        if not self.target: 
            if self.hunger<20:
                self.status = "hungry"

            else:
                self.status = "wandering"
        self.update_perceived_tiles(world)
        

        if interactionmanager.is_on_target():
            if self.status == "hungry":
                self.hunger = 100
            if self.status == "thirsty":
                print("Thirst restored")
                self.thirst = 100
           
                
               
    def update_perceived_tiles(self, world):
        self.perceived_tiles.clear()
        self.perceived_tiles = [
            (self.x + dx, self.y + dy)
            for dx, dy in self.perceptive_radius
            if 0 <= self.x + dx < world.grid_width
            and 0 <= self.y + dy < world.grid_height
        ]
    
    def status_checker(self,world,veg):
        if self.status == "hungry":
           if not self.target:
            self.update_perceived_tiles(world)
            target_veg = world.find_closest_veg(veg,self.x,self.y,self.perceived_tiles)
            if target_veg is not None:
                self.target = (target_veg.v_x,target_veg.v_y)
            else:
                self.target = None
                
        elif self.status == "thirsty":
            print("checking for shore")        
            if not self.target:
                self.update_perceived_tiles(world)
                self.target = world.find_closest_shore(self.x,self.y,self.perceived_tiles)
            else:
                 print(self.target)
        

    def movement_decider(self,world,screen):
        if self.target is None:
            print("target and path no")
            self.wander_randomly(world)
        else:
            print("yas",self.path)
            if not self.path:
                print("target yes, but no path yet")
                self.set_path(world)    
                return        
               
            if self.path:
                print("following path")
                self.follow_path(screen,world.tile_size)
             
           
    
    def wander_randomly(self,world): 
        print("wandering")
        dx, dy = random.choice(world.get_neighbors(self.x,self.y))
        if world.is_walkable(dx,dy):
                self.x, self.y = dx, dy
                                           
    def set_path(self,world):
        if self.target:      
            self.path = astar((self.x, self.y),
                            (self.target[0], self.target[1]),
                            world.map_grid,
                            world.grid_width,
                            world.grid_height)
            print("yessir",self.path)
      
            if not self.path:
                 self.target = None
                                                            
    def follow_path(self, screen, tile_size):
        if self.path:
            print(self.path)
            # Draw path (visual debug)
            points = [
                (x * tile_size + tile_size // 2,
                y * tile_size + tile_size // 2)
                for (x, y) in self.path
            ]

            if len(points) > 1:
                pygame.draw.lines(screen, (255, 0, 0), False, points, 2)

            # Move creature
            self.x, self.y = self.path.pop(0)
          

              

        

    def draw(self, screen, tile_size):
        pygame.draw.circle(
            screen,
            (0, 255, 0),
            (self.x * tile_size + tile_size // 2,
             self.y * tile_size + tile_size // 2),
            5
        )
        font = pygame.font.Font(None, 16)
        text = font.render(self.status, True, (255, 255, 255))
        screen.blit(text, (self.x * tile_size, self.y * tile_size - 10))


