import pygame


class Renderer:
    def __init__(self,WIDTH,HEIGHT):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT)) 
        
    def draw_creature(self,tile_size):
        pygame.draw.circle(
                    self.screen,
                    (0, 255, 0),
                    (
                        self.x * tile_size + tile_size // 2,
                        self.y * tile_size + tile_size // 2,
                    ),
                    5,
                )        
        font = pygame.font.Font(None, 16)
        text = font.render(self.status, True, (255, 255, 255))
        self.screen.blit(
                    text,
                    (self.x * tile_size, self.y * tile_size - 10),
                )
        
    def draw_world(self,grid_width,grid_height,tile_size,shore_tiles,map_grid):
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
                        x * tile_size,
                        y * tile_size,
                        tile_size,
                        tile_size
                    )
                )
    
    def flip():
        pygame.display.flip()