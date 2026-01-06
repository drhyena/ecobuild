import pygame
class Veg:
    def __init__(self, v_x, v_y):
        self.v_x = v_x
        self.v_y = v_y
        self.status = "alive"

    def draw(self, screen, TILE_SIZE):
        if self.status == "alive":
            pygame.draw.circle(
                screen,
                (255, 0, 0),
                (
                    self.v_x * TILE_SIZE + TILE_SIZE // 2,
                    self.v_y * TILE_SIZE + TILE_SIZE // 2
                ),
                5
            )
    def confirm_eaten(self):
        self.status="dead"
        print("veg died")