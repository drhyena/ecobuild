from creature import Creature
from CreatureBehaviors import PreyMovement


class Prey(Creature):

    def __init__(self, x, y, world, interaction_manager):
        super().__init__(x, y, world, interaction_manager, movement=PreyMovement())
        self.species = "prey"
        self.genome.iq = 0.4
        self.genome.speed = 20
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

        predator = self.targeting.targeted_by

        # Release a predator that died or is no longer hunting this prey
        if predator is not None and (
            not predator.alive or predator.targeting.target_creature is not self
        ):
            self.targeting.targeted_by = None
            predator = None

        # Fleeing preempts everything, even a target already being walked to
        if predator is not None:
            if self.status != "fleeing":
                self.status = "fleeing"
                self.targeting.target = None
                self.targeting.target_veg = None
                self.targeting.path = []
            return

        if self.status == "fleeing":
            self.status = "wandering"
            self.targeting.target = None

        if not self.targeting.target:
            if self.vitals.thirst < self.genome.thirst_threshold:
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