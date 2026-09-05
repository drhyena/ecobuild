import pygame


class Renderer:
    def __init__(self,WIDTH,HEIGHT,tile_size):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
        self.tile_size= tile_size
       
        
        
    def draw_creature(self,c):
        if c.species == "prey": # temorary check. will be based on CreatureBehaviors later on
            pygame.draw.circle(
                        self.screen,
                        (255, 255, 255),
                        (
                            c.px,
                            c.px,
                        ),
                    5,
                    )
        else:
            pygame.draw.circle(
                                          self.screen,
                                          (0, 255, 0),
                                          (
                                               c.px ,
                                               c.py,
                                          ),
                                          5,
                                      )  
        font = pygame.font.Font(None, 16)
        text = font.render(c.status, True, (255, 255, 255))
        self.screen.blit(
                    text,
                    (c.x * self.tile_size, c.y * self.tile_size - 10),
                )
        
    def draw_world(self,grid_width,grid_height,shore_tiles,map_grid):
        for x in range(grid_width):
            for y in range(grid_height):

                if (x, y) in shore_tiles:
                    color = (194, 178, 128)  # sandy
                elif map_grid[x][y] == "water":
                    color = (30, 90, 160)
                else:
                    color = (40, 160, 60)

                pygame.draw.rect(
                    self.screen,
                    color,
                    (
                        x * self.tile_size,
                        y * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )
                )
    
    def draw_veg(self,veg):
        if veg.alive:
            pygame.draw.circle(
                self.screen,
                (255, 0, 0),
                (
                    veg.v_x * self.tile_size + self.tile_size // 2,
                    veg.v_y * self.tile_size + self.tile_size // 2
                ),
                1
            )
    
    
    def flip(self):
        pygame.display.flip()