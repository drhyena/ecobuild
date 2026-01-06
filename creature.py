import random
import pygame
import math
from astar import  *

class Creature:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.thirst = 40
        self.hunger = 100
        self.target = None
        self.path = []
        self.status = ""
        self.adjacent_tiles = []
        self.next_tiles = []

    def update_adjacent_tiles(self, grid_width, grid_height):
        self.adjacent_tiles = [
            (self.x + dx, self.y + dy)
            for dx in range(-10, 11)
            for dy in range(-10, 11)
            if 0 <= self.x + dx < grid_width and 0 <= self.y + dy < grid_height
        ]

        self.next_tiles = [
            (self.x + dx, self.y + dy)
            for dx in range(-1, 2)
            for dy in range(-1, 2)
            if 0 <= self.x + dx < grid_width and 0 <= self.y + dy < grid_height
        ]

    def find_closest_veg(self, veg_list, grid_width, grid_height):
        self.update_adjacent_tiles(grid_width, grid_height)
        for v in veg_list:
            if v.status != "alive":
                continue
            if (v.v_x, v.v_y) in self.adjacent_tiles:
                self.target = v
                return True
               
        return False
    

    
    def status_setter(self):
        self.hunger = self.hunger - 1
        self.thirst = self.thirst -3
        if self.hunger < 20:
            self.status = "hungry"
        elif self.thirst < 30:
            self.status = "thirsty"
        else:
            self.status = "wandering"
        print(self.thirst)

    def status_checker(self,world):
        if self.status == "wandering":
            self.wander_randomly(world)
        if self.status == "hungry":
            self.find_closest_veg()
        if self.status == "thirsty":
            self.target = world.find_closest_shore()


    def state_machine(self,grid_width,grid_height,map_grid):
        if not self.target:
            self.wander_randomly(grid_width,grid_height,map_grid)
        else:
            self.seek_target()
            self.follow_path()
        


    def wander_randomly(self, grid_width, grid_height, map_grid,world):
        dx, dy = random.choice(world.get_neighbours)
        new_x, new_y = self.x + dx, self.y + dy
        if world.is_walkable(dx,dy):
                self.x, self.y = new_x, new_y

    
    def drink_water(self,closest_shore):
        if (self.x,self.y) == closest_shore:
            self.thirst == 100

    



    def seek_target(self,veg_list,water_list, map_grid, grid_width, grid_height,shore_list
                ):
        if self.path:
            return 
        if self.status in ("hungry","super hungry"):
            if self.find_closest_veg(veg_list, grid_width, grid_height):
                self.path = astar(
                            (self.x, self.y),
                            (self.target.v_x, self.target.v_y),
                            map_grid,
                            grid_width,
                            grid_height,
                    )
            return     
        if self.status == "thirsty":
            print(self.status)
            print("x")
            if self.find_closest_shore(shore_list,grid_width,grid_height):
                print("pathing to")
                self.path = astar((self.x,self.y), (self.target[0],self.target[1]),
                                map_grid,
                                grid_width,
                                grid_height
                               )
                                           
    def drink_water(self):
        if self.status == "thirsty":
            print("drinking")
            self.thirst = 100
            
    def eat_veg(self):
        if self.status in ("hungry", "super hungry"):
            print("eating")
            self.hunger = 100

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


