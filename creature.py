import random
import pygame
import math
from astar import  *

class Creature:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.thirst = 100
        self.hunger = 100
        self.target = None
        self.path = []
        self.status = ""
        self.perceptive_radius = [
                                    (dx, dy)
                                    for dx in range(-5, 6)
                                    for dy in range(-5, 6)
                                    if not (dx == 0 and dy == 0)
                                ]
        self.perceived_tiles = []
    
    

   
    def update_perceived_tiles(self, world):
        self.perceived_tiles = [
            (self.x + dx, self.y + dy)
            for dx, dy in self.perceptive_radius
            if 0 <= self.x + dx < world.grid_width
            and 0 <= self.y + dy < world.grid_height
        ]
        
    
    def drink_water(self):
            if self.status == "thirsty":
                print("drinking")
                self.thirst = 100
            
    def eat_veg(self):
        if self.status in ("hungry", "super hungry"):
            print("eating")
            self.hunger = 100
    
    def drink_water(self,closest_shore):
        if (self.x,self.y) == closest_shore:
            self.thirst == 100

    def update(self,world):
        self.hunger =self.hunger -1
        self.thirst = self.thirst -3
        if self.hunger < 20:
            self.status = "hungry"
        elif self.thirst < 30:
            self.status = "thirsty"
        else:
            self.status = "wandering"
        

        self.update_perceived_tiles(world)

    
    def status_checker(self,world,veg):
        if self.status == "hungry":
            self.target = world.find_closest_veg(veg,self.x,self.y,self.perceived_tiles)
        elif self.status == "thirsty":
            self.target = world.find_closest_shore(self.x,self.y,self.perceived_tiles)
        else:
            self.target = None
      


    def movement_decider(self,world,screen):
        if self.target is None:
            self.wander_randomly(world)
        else:
            if not self.path:
                self.set_path(world)
                self.wander_randomly(world)           
               
            if self.path:
                self.follow_path(screen,world.tile_size)
             
           
    
    def wander_randomly(self,world):
        dx, dy = random.choice(world.get_neighbors(self.x,self.y))
        if world.is_walkable(dx,dy):
                self.x, self.y = dx, dy
    


    def set_path(self,world):      
                self.path = astar(
                            (self.x, self.y),
                            (self.target[0], self.target[1]),
                            world.map_grid,
                            world.grid_width,
                            world.grid_height,
                    )     
                if not self.path:
                     self.target = None
        
                               
                                        
    def follow_path(self, screen, tile_size):
        if self.path:
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


