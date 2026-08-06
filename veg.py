import pygame
class Veg:
    def __init__(self, v_x, v_y):
        self.v_x = v_x
        self.v_y = v_y
        self.alive = True
        self.claimed_by = None

    
    