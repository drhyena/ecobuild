from creature import *
import random

class Prey(Creature):

    def __init__(self, x, y, interaction_manager):
        super().__init__(x, y, interaction_manager)
        self.species = "prey"
        self.targetted_by = None
        self.iq = 0.4

    # -------------------------------------------------
    # Predator Awareness
    # -------------------------------------------------

    def get_predator(self, predator):
        self.targetted_by = predator if predator else None

    # -------------------------------------------------
    # State Logic
    # -------------------------------------------------

    def update_state(self):

        if not self.target:
            if self.targetted_by:
                self.status = "fleeing"

            elif self.thirst < 30:
                self.status = "thirsty"

            elif self.hunger < 20:
                self.status = "hungry"

            else:
                self.status = "wandering"

    # -------------------------------------------------
    # State Dispatcher
    # -------------------------------------------------

    def status_checker(self, world, veg, creature_list):

        if self.status == "hungry":
            self.handle_hungry_state(world, veg, creature_list)

        elif self.status == "thirsty":
            self.handle_thirsty_state(world)

        elif self.status == "fleeing":
            self.handle_flee_state(world)

        else:
            self.target = None

    # -------------------------------------------------
    # Dynamic Flee Logic (No Best Tile)
    # -------------------------------------------------

    def handle_flee_state(self, world):

    # Predator gone
        if not self.targetted_by or not self.targetted_by.alive:
            self.targetted_by = None
            self.target = None
            return
        if random.random()<(1- self.iq):
            return
        predator = self.targetted_by

        dx = self.x - predator.x
        dy = self.y - predator.y

        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

        # IQ-based directional distortion
        if random.random() < (1 - self.iq):
            step_x, step_y = step_y, step_x

        new_x = self.x + step_x
        new_y = self.y + step_y

        if world.is_walkable(new_x, new_y):
            self.target = (new_x, new_y)
        else:
            self.target = None

    # -------------------------------------------------
    # Movement
    # -------------------------------------------------
    def flee_movement(self):

        if not self.target:
            return

        self.prev_x, self.prev_y = self.x, self.y
        self.x, self.y = self.target
    
    def movement_decider(self, world, screen):

   

        if self.target is None:
           
            self.wander_randomly(world)
        elif self.status == "fleeing":
            self.flee_movement()
            
        else:
            if not self.path:
               
                self.set_path(world)
                return

            if self.path:
                
                self.follow_path(screen, world.tile_size)
                
                
    