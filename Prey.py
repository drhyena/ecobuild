from creature import *
import random

class Prey(Creature):

    def __init__(self, x, y, interaction_manager):
        super().__init__(x, y, interaction_manager)
        self.species = "prey"
        self.genome.iq = 0.4
        self.genome.hunger_threshold = 20
        self.genome.thirst_threshold = 30

    # -------------------------------------------------
    # Predator Awareness
    # -------------------------------------------------

    def get_predator(self, predator):
        self.targeting.targeted_by = predator if predator else None

    # -------------------------------------------------
    # State Logic
    # -------------------------------------------------

    def update_state(self):

        if not self.targeting.target:
            if self.targeting.targeted_by:
                self.status = "fleeing"
            elif self.vitals.thirst < self.genome.thirst_threshold:
                self.status = "thirsty"

            elif self.vitals.hunger < self.genome.hunger_threshold:
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
            self.targeting.target = None

    # -------------------------------------------------
    # Dynamic Flee Logic (No Best Tile)
    # -------------------------------------------------

    def handle_flee_state(self, world):

    # Predator gone
        if not self.targeting.targeted_by or not self.targeting.targeted_by.alive:
            self.targeting.targeted_by = None
            self.targeting.target = None
            return
        if random.random() < (1 - self.genome.iq):
            return
        predator = self.targeting.targeted_by

        dx = self.x - predator.x
        dy = self.y - predator.y

        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

        # IQ-based directional distortion
        if random.random() < (1 - self.genome.iq):
            step_x, step_y = step_y, step_x

        new_x = self.x + step_x
        new_y = self.y + step_y

        if world.is_walkable(new_x, new_y):
            self.targeting.target = (new_x, new_y)
        else:
            self.targeting.target = None

    # -------------------------------------------------
    # Movement
    # -------------------------------------------------
    def flee_movement(self):

        if not self.targeting.target:
            return

        self.prev_x, self.prev_y = self.x, self.y
        self.x, self.y = self.targeting.target
    
    def movement_decider(self, world):

   

        if self.targeting.target is None:
           
            self.wander_randomly(world)
        elif self.status == "fleeing":
            self.flee_movement()
            
        else:
            if not self.targeting.path:
               
                self.set_path(world)
                return

            if self.targeting.path:
                
                self.follow_path()