import random
import pygame
import math
import gc
from astar import *
gc.disable()


class Creature:
    def __init__(self, x, y, interaction_manager):
        self.x, self.y = x, y
        self.thirst = 100
        self.hunger = 100
        self.target = None
        self.target_veg = None
        self.path = []
        self.status = ""
        self.perceptive_radius = [
            (dx, dy)
            for dx in range(-10, 11)
            for dy in range(-10, 11)
            if not (dx == 0 and dy == 0)
        ]
        self.perceived_tiles = []
        self.signal = {"type": None, "from": None, "tile": None}
        self.interaction_manager = interaction_manager
        self.iq = 0.0
        self.world = None
        self.alive = True

    # -------------------------
    # ACTIONS
    # -------------------------

    def drink_water(self):
        if self.status == "thirsty":
            print("drinking")
            self.thirst = 100

    def eat_veg(self):
        if self.status == "hungry":
            self.hunger = 100
            self.target_veg.alive = False

    # -------------------------
    # UPDATED STATE MACHINE CORE
    # -------------------------

    def update(self, world, interactionmanager, veg_list, creature_list):
        self.world = world

        self.update_needs()
        self.update_state()
        self.update_perceived_tiles(world)
        self.resolve_interaction(interactionmanager, veg_list, creature_list)
        self.check_death(interactionmanager, creature_list)

    def update_needs(self):
        self.hunger -= 1
        self.thirst -= 2
        print("thirst", self.thirst, "hunger:", self.hunger)

    def update_state(self):
        if not self.target:
            if self.thirst < 30:
                self.status = "thirsty"
            elif self.hunger < 20:
                self.status = "hungry"
            else:
                self.status = "wandering"

    def resolve_interaction(self, interactionmanager, veg_list, creature_list):
        if interactionmanager.is_on_target(self):

            if self.status == "hungry":
                self.handle_hunger(interactionmanager, veg_list, creature_list)

            elif self.status == "thirsty":
                self.handle_thirst()

            

    def handle_hunger(self, interactionmanager, veg_list, creature_list):
        if self.target_veg and self.target_veg.alive:
            if self.target_veg.claimed_by is None:
                self.target_veg.claimed_by = self
                self.eat_veg()
                interactionmanager.kill_veg(
                    self.target_veg, veg_list, creature_list
                )

    def handle_thirst(self):
        self.drink_water()

    def check_death(self, interactionmanager, creature_list):
        if self.hunger <= 0 or self.thirst <= 0:
            interactionmanager.kill_creature(self, creature_list)

    # -------------------------
    # SIGNAL
    # -------------------------

    def creature_receive_signal(self, from_, tile):
        self.signal = {"type": type, "from": from_, "tile": tile}

    # -------------------------
    # PERCEPTION
    # -------------------------

    def update_perceived_tiles(self, world):
        self.perceived_tiles.clear()
        self.perceived_tiles = [
            (self.x + dx, self.y + dy)
            for dx, dy in self.perceptive_radius
            if 0 <= self.x + dx < world.grid_width
            and 0 <= self.y + dy < world.grid_height
        ]

    # -------------------------
    # TARGET DECISION
    # -------------------------

    def status_checker(self, world, interactionmanager, veg, creature_list):

        if self.status == "hungry":
            self.handle_hungry_state(world, interactionmanager, veg, creature_list)

        elif self.status == "thirsty":
            self.handle_thirsty_state(world)
        else:
            self.target = None

    def handle_thirsty_state(self, world):

            print("checking for shore")

            if self.target:
                print(self.target)
                return

            self.update_perceived_tiles(world)

            self.target = world.find_closest_shore(
                self.x, self.y, self.perceived_tiles
            )

    def handle_hungry_state(self, world, interactionmanager, veg, creature_list):

        if self.target:
            return

        self.update_perceived_tiles(world)

        self.target_veg = world.find_closest_veg(
            veg, self.x, self.y, self.perceived_tiles
        )

        if self.target_veg is None:
            self.target = None
            return

        if not interactionmanager.veg_is_being_targeted(
            self, creature_list
        ):
            self.target = (
                self.target_veg.v_x,
                self.target_veg.v_y,
            )
    # -------------------------
    # MOVEMENT
    # -------------------------

    def movement_decider(self, world, screen):

        if self.target is None:
            print("target and path no")
            self.wander_randomly(world)
        else:
            print("yas", self.path)

            if not self.path:
                print("target yes, but no path yet")
                self.set_path(world)
                return

            if self.path:
                print("following path")
                self.follow_path(screen, world.tile_size)

    def wander_randomly(self, world):
        print("wandering")
        dx, dy = random.choice(world.get_neighbors(self.x, self.y))
        if world.is_walkable(dx, dy):
            self.x, self.y = dx, dy

    def set_path(self, world):
        if self.target:
            self.path = astar(
                (self.x, self.y),
                (self.target[0], self.target[1]),
                world.map_grid,
                world.grid_width,
                world.grid_height,
            )
            print("yessir", self.path)

            if not self.path:
                self.target = None

    def follow_path(self, screen, tile_size):
        if self.path:
            print(self.path)

            points = [
                (
                    x * tile_size + tile_size // 2,
                    y * tile_size + tile_size // 2,
                )
                for (x, y) in self.path
            ]

            if len(points) > 1:
                pygame.draw.lines(screen, (255, 0, 0), False, points, 2)

            self.x, self.y = self.path.pop(0)

    # -------------------------
    # DRAW
    # -------------------------

    def draw(self, screen, tile_size):
        pygame.draw.circle(
            screen,
            (0, 255, 0),
            (
                self.x * tile_size + tile_size // 2,
                self.y * tile_size + tile_size // 2,
            ),
            5,
        )

        font = pygame.font.Font(None, 16)
        text = font.render(self.status, True, (255, 255, 255))
        screen.blit(
            text,
            (self.x * tile_size, self.y * tile_size - 10),
        )




