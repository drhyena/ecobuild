from creature import Creature
from CreatureBehaviors import PreyMovement


class Prey(Creature):

    def __init__(self, x, y, world, interaction_manager):
        super().__init__(x, y, world, interaction_manager, movement=PreyMovement())
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
    # State Dispatcher (delegates to behavior components)
    # -------------------------------------------------

    def status_checker(self, veg, creature_list):

        if self.status == "hungry":
            self.hunger_behavior.handle_hungry_state(self, veg, creature_list)

        elif self.status == "thirsty":
            self.thirst_behavior.handle_thirsty_state(self)

        elif self.status == "fleeing":
            self.movement.handle_flee_state(self)

        else:
            self.targeting.target = None