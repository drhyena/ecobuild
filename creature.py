import random
import pygame
from astar import *
from CreatureData import Vitals, Genome, Targeting, Reproduction


class Creature:
    def __init__(self, px,py,x, y, interaction_manager, vitals=None, genome=None, targeting=None, reproduction=None):
        self.x, self.y = x, y
        self.px,self.py = x//2, y//2
        self.status = ""
        self.vitals = vitals if vitals is not None else Vitals()
        self.genome = genome if genome is not None else Genome()
        self.targeting = targeting if targeting is not None else Targeting()
        self.reproduction = reproduction if reproduction is not None else Reproduction()

        self.targeting.target = None
        self.targeting.target_veg = None
        self.targeting.target_creature = None
        self.targeting.targeted_by = None
        self.targeting.path = []
        self.genome.perceptive_radius = [
            (dx, dy)
            for dx in range(-10, 11)
            for dy in range(-10, 11)
            if not (dx == 0 and dy == 0)
        ]
        self.targeting.perceived_tiles = []

        self.signal = {"type": None, "from": None, "tile": None}
        self.interaction_manager = interaction_manager
        self.world = None
        self.alive = True
        self.species = "creature"
        self.prev_x, self.prev_y = self.x, self.y
        self.prev_px,self.prev_py=self.px,self.py

        # log attributes. Additional data
        self.times_drank = 0
        self.creatures_killed = 0
        self.times_ate = 0

        # time attributes
        self.birth_time = pygame.time.get_ticks()
        self.retarget_interval = 5000
        self.last_retarget_time = pygame.time.get_ticks()

    # -------------------------
    # MAIN UPDATE LOOP
    # -------------------------

    def update(self, world, veg_list, creature_list):
        self.world = world
        self.update_perceived_tiles(world)
        self.update_needs()
        self.update_state()
        self.resolve_interaction(veg_list, creature_list)
        self.check_death(creature_list)
        if not self.alive:
            print(self, "died while", self.status)

    # -------------------------
    # VITALS / NEEDS
    # -------------------------

    def update_needs(self):
        self.vitals.hunger -= 1
        self.vitals.thirst -= 2

    def check_essentials(self):
        return {
            "thirsty": max(0, (self.genome.thirst_threshold - self.vitals.thirst) / self.genome.thirst_threshold),
            "hungry": max(0, (self.genome.hunger_threshold - self.vitals.hunger) / self.genome.hunger_threshold),
            "wandering": 0.05,
        }

    def get_essential_state_decision(self):
        utilities = self.check_essentials()
        return max(utilities, key=utilities.get)

    def update_state(self):
        # Split into two - essential and non-essential. Essentials will include hunger and thirst and the like.
        # Non-essentials will include reproduction and the like. Non-essentials will require essentials to be fulfilled.
        # ESSENTIALS
        self.status = self.get_essential_state_decision()

    def check_death(self, creature_list):
        if self.vitals.hunger <= -20 or self.vitals.thirst <= 0:
            print(f"{self} died at hunger:{self.vitals.hunger}")
            self.interaction_manager.kill_creature(self, creature_list)

    # -------------------------
    # ACTIONS
    # -------------------------

    def drink_water(self):
        if self.status == "thirsty":
            print("drinking")
            self.vitals.thirst = 100
            self.times_drank += 1

    def eat_veg(self):
        if self.status == "hungry":
            self.vitals.hunger = 100
            self.times_ate += 1

    # -------------------------
    # INTERACTION RESOLUTION
    # -------------------------

    def resolve_interaction(self, veg_list, creature_list):
        if self.interaction_manager.is_on_target(self):
            if self.status == "hungry":
                self.handle_hunger(veg_list, creature_list)
            elif self.status == "thirsty":
                self.handle_thirst()

    def handle_hunger(self, veg_list, creature_list):
        now = pygame.time.get_ticks()
        if now - self.last_retarget_time >= self.retarget_interval:
            self.last_retarget_time = now
            self.targeting.target = None
            self.targeting.target_veg = None
            self.targeting.path = []

        if self.targeting.target_veg and self.targeting.target_veg.alive:
            if self.targeting.target_veg.claimed_by is None:
                self.targeting.target_veg.claimed_by = self
                self.eat_veg()
                self.interaction_manager.kill_veg(
                    self.targeting.target_veg, veg_list, creature_list
                )

    def handle_thirst(self):
        self.drink_water()

    # -------------------------
    # REPRODUCTION
    # -------------------------

    def check_if_ready_for_a_mate(self):
        if self.reproduction.time_since_last_mating == self.reproduction.reproductive_interval:
            if self.times_ate > 0 and self.times_drank > 0:
                return True

    # -------------------------
    # SIGNAL
    # -------------------------

    def creature_receive_signal(self, from_, tile):
        self.signal = {"type": type, "from": from_, "tile": tile}

    # -------------------------
    # PERCEPTION
    # -------------------------

    def update_perceived_tiles(self, world):
        self.targeting.perceived_tiles.clear()
        self.targeting.perceived_tiles = [
            (self.x + dx, self.y + dy)
            for dx, dy in self.genome.perceptive_radius
            if 0 <= self.x + dx < world.grid_width
            and 0 <= self.y + dy < world.grid_height
        ]

    # -------------------------
    # TARGET DECISION
    # -------------------------

    def status_checker(self, world, veg, creature_list):
        if self.status == "hungry":
            self.handle_hungry_state(world, veg, creature_list)
        elif self.status == "thirsty":
            self.handle_thirsty_state(world)
        else:
            self.targeting.target = None

    def handle_thirsty_state(self, world):
        if self.targeting.target:
            return
        self.update_perceived_tiles(world)
        self.targeting.target = world.find_closest_shore(
            self.x, self.y, self.targeting.perceived_tiles
        )

    def handle_hungry_state(self, world, veg, creature_list):
        if self.targeting.target:
            return
        self.update_perceived_tiles(world)
        self.targeting.target_veg = world.find_closest_veg(
            veg, self.x, self.y, self.targeting.perceived_tiles
        )
        if self.targeting.target_veg is None:
            self.targeting.target = None
            return
        if not self.interaction_manager.veg_is_being_targeted(self, creature_list):
            self.targeting.target = (self.targeting.target_veg.v_x, self.targeting.target_veg.v_y)

    # -------------------------
    # MOVEMENT
    # -------------------------

    def movement_decider(self, world, screen):
        if self.targeting.target is None:
            self.wander_randomly(world)
        else:
            if not self.targeting.path:
                self.set_path(world)
                return

            if self.targeting.path:
                self.follow_path(screen, world.tile_size)

    def notify_travel(self, target):
        """Called by interaction manager to assign a travel target."""
        if not self.targeting.target:  # don't override if already heading somewhere
            self.targeting.target = target
            self.targeting.path = []

    def wander_randomly(self, world):
        dx, dy = random.choice(world.get_neighbors(self.x, self.y))
        if world.is_walkable(dx, dy):
            self.prev_x, self.prev_y = self.x, self.y
            self.x, self.y = dx, dy

    def set_path(self, world):
        if self.targeting.target:
            self.targeting.path = astar(
                (self.x, self.y),
                (self.targeting.target[0], self.targeting.target[1]),
                world.map_grid,
                world.grid_width,
                world.grid_height,
            )
            if not self.targeting.path:
                self.targeting.target = None

    def follow_path(self):
        if self.targeting.path:

            self.prev_x, self.prev_y = self.x, self.y
            self.x, self.y = self.targeting.path.pop(0)

