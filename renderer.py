import pygame


class Renderer:
    def __init__(self, WIDTH, HEIGHT, tile_size):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.tile_size = tile_size

        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.Font(None, 16)  # created once (it was rebuilt for every creature, every frame)
        self._labels = {}                       # status text -> already-rendered surface
        self._world_surface = None              # terrain, drawn once and reused
        self.show_labels = True                 # set False to skip the status text entirely

    def _label(self, text):
        surf = self._labels.get(text)
        if surf is None:
            surf = self.font.render(text, True, (255, 255, 255))
            self._labels[text] = surf
        return surf

    def draw_creature(self, c):
        # temorary check. will be based on CreatureBehaviors later on
        color = (255, 255, 255) if c.genome.type == "predator" else (0, 255, 0)
        pygame.draw.circle(self.screen, color, (c.px, c.py), 5)

        if self.show_labels:
            self.screen.blit(
                self._label(c.status),
                (c.x * self.tile_size, c.y * self.tile_size - 10),
            )

    def draw_world(self, grid_width, grid_height, shore_tiles, map_grid):
        # the terrain never changes, so it is drawn tile by tile once and then just blitted
        if self._world_surface is None:
            self._world_surface = self._build_world_surface(
                grid_width, grid_height, shore_tiles, map_grid)
        self.screen.blit(self._world_surface, (0, 0))

    def invalidate_world(self):
        """Call this if the terrain ever changes (water drying up, tiles edited, ...)."""
        self._world_surface = None

    def _build_world_surface(self, grid_width, grid_height, shore_tiles, map_grid):
        surface = pygame.Surface((grid_width * self.tile_size, grid_height * self.tile_size))
        shore = set(shore_tiles)  # membership test on a list is a slow linear scan
        for x in range(grid_width):
            for y in range(grid_height):
                if (x, y) in shore:
                    color = (194, 178, 128)  # sandy
                elif map_grid[x][y] == "water":
                    color = (30, 90, 160)
                else:
                    color = (40, 160, 60)

                pygame.draw.rect(
                    surface,
                    color,
                    (
                        x * self.tile_size,
                        y * self.tile_size,
                        self.tile_size,
                        self.tile_size
                    )
                )
        return surface.convert()

    def draw_veg(self, veg):
        if veg.alive:
            pygame.draw.circle(
                self.screen,
                (255, 0, 0),
                (
                    veg.v_x * self.tile_size + self.tile_size // 2,
                    veg.v_y * self.tile_size + self.tile_size // 2
                ),
                5
            )

    def flip(self):
        pygame.display.flip()