from creature import Creature
from CreatureBehaviors import PredatorMovement, PredatorHungerBehavior, PredatorHuntingBehaviour
from itertools import count
from SpecificGenome import predator_genome


class Predator(Creature):
    id_counter = count()

    def __init__(self, x, y, world, interaction_manager,log):
        super().__init__(
            x, y, world, interaction_manager,log,
            movement=PredatorMovement(),genome= predator_genome(),
            hunger_behavior=PredatorHungerBehavior(),
            hunting_behavior=PredatorHuntingBehaviour(),
        )

        self.genome.id = "predator" + str(next(self.id_counter))

    # -------------------------
    # STATE OVERRIDE
    # -------------------------

    def update_state(self):
        self.validate_mate()

        # If actively hunting
        if self.targeting.target_creature:
            if self.status != "hunting":
                self.hunting_behavior.alarm_nearby_prey(self)  # nearby prey react the moment the hunt starts
            self.status = "hunting"
            return

        # Has a partner: walking to / waiting at the mating point
        if self.reproduction.current_mate is not None:
            self.status = "mating"
            return

        # Migrating: stays in this state until handle_migrate_state ends it
        if self.status == "migrating":
            return

        # Normal need-based logic
        if not self.targeting.target:
            if self.vitals.thirst < self.genome.thirst_threshold:
                self.status = "thirsty"
            elif self.vitals.hunger < self.genome.hunger_threshold:
                self.status = "hungry"
            else:
                self.status = "wandering"
                self.get_non_essential_state_decision()

            self.check_migration()

    # -------------------------
    # EAT PREY (override — delegates to hunger_behavior)
    # -------------------------

    def resolve_interaction(self):
        if self.status == "mating":
            self.reproduction_behavior.handle_mating(self)
            return

        if self.interaction_manager.is_on_target(self):

            if self.status in ["hungry", "hunting"]:
                self.hunger_behavior.handle_hunger(self)

            elif self.status == "thirsty":
                self.thirst_behavior.handle_thirst(self)

    # -------------------------
    # HUNT INITIATION
    # -------------------------

    def notify_prey(self):
        self.hunger_behavior.notify_prey(self)

    # -------------------------
    # FOOD CHECK OVERRIDE (a predator's food is prey)
    # -------------------------

    def sees_food(self):
        return self.world.find_closest_prey(self) is not None

    # -------------------------
    # STATUS CHECKER OVERRIDE (delegates to behavior components)
    # -------------------------

    def status_checker(self):

        if self.status == "hungry":
            self.hunger_behavior.handle_hungry_state(self)
        elif self.status == "thirsty":
            self.thirst_behavior.handle_thirsty_state(self)
        elif self.status == "hunting":
            self.hunting_behavior.handle_hunting_state(self)
        elif self.status == "migrating":
            self.movement.handle_migrate_state(self)
        elif self.status == "mating":
            self.reproduction_behavior.handle_mating_state(self)

        else:
            self.targeting.target = None