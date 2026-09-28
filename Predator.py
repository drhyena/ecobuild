from creature import Creature
from CreatureBehaviors import PredatorMovement, PredatorHungerBehavior, PredatorHuntingBehaviour


class Predator(Creature):

    def __init__(self, x, y, world, interaction_manager):
        super().__init__(
            x, y, world, interaction_manager,
            movement=PredatorMovement(),
            hunger_behavior=PredatorHungerBehavior(),
            hunting_behavior=PredatorHuntingBehaviour(),
        )
       
        self.species = "predator"
        self.genome.iq = 0.7
        self.genome.speed = 40
        self.genome.hunger_threshold = 50
        self.genome.thirst_threshold = 30

    # -------------------------
    # STATE OVERRIDE
    # -------------------------

    def update_state(self):

        # If actively hunting
        if self.targeting.target_creature:
            self.status = "hunting"
            return

        # Normal need-based logic
        if not self.targeting.target:
            if self.vitals.thirst < self.genome.thirst_threshold:
                self.status = "thirsty"
            elif self.vitals.hunger < self.genome.hunger_threshold:
                self.status = "hungry"
            else:
                self.status = "wandering"

    # -------------------------
    # EAT PREY (override — delegates to hunger_behavior)
    # -------------------------

    def resolve_interaction(self, veg_list, creature_list):
        if self.interaction_manager.is_on_target(self):

            if self.status in ["hungry", "hunting"]:
                self.hunger_behavior.handle_hunger(self, creature_list)

            elif self.status == "thirsty":
                self.thirst_behavior.handle_thirst(self)

    # -------------------------
    # HUNT INITIATION
    # -------------------------

    def notify_prey(self):
        self.hunger_behavior.notify_prey(self)

    # -------------------------
    # STATUS CHECKER OVERRIDE (delegates to behavior components)
    # -------------------------

    def status_checker(self, veg, creature_list):

        if self.status == "hungry":
            self.hunger_behavior.handle_hungry_state(self, creature_list)
        elif self.status == "thirsty":
            self.thirst_behavior.handle_thirsty_state(self)
        elif self.status == "hunting":
            self.hunting_behavior.handle_hunting_state(self)

        else:
            self.targeting.target = None