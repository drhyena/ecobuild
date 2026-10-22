from creature import Creature
from CreatureBehaviors import PreyMovement
from itertools import count
from SpecificGenome import prey_genome

class Prey(Creature):
    id_counter = count()


    def __init__(self, x, y, world, interaction_manager,log):
        super().__init__(x, y, world, interaction_manager,log, movement=PreyMovement(),genome=prey_genome())
        self.genome.type = "prey"
        self.genome.iq = 0.4
        self.genome.speed = 20
        self.genome.hunger_threshold = 20
        self.genome.thirst_threshold = 30
        self.genome.id = "prey" + str(next(self.id_counter))
        self.genome.reproductive_interval = 3

    # -------------------------------------------------
    # Predator Awareness
    # -------------------------------------------------

    def get_predator(self, predator):
        self.targeting.targeted_by = predator if predator else None

    # -------------------------------------------------
    # Herd Alarm (a predator nearby started hunting)
    # -------------------------------------------------

    def check_alarm(self):
        """True while this prey is running from a predator that started hunting nearby.
        Everyone disperses first, then the ones picked for it head for the retreat point."""
        t = self.targeting
        predator = t.alarm_source
        if predator is None:
            return False

        # the alarm is over when the predator dies or the alarm runs out
        if not predator.vitals.alive or self.world.sim_time >= t.alarm_until:
            self.end_alarm()
            return False

        if t.retreat_point is not None and self.world.sim_time >= t.retreat_time:
            if self.status != "retreating":
                self.reproductionmanager.cancel_mating(self)  # drop any mating plan
                self.status = "retreating"
                t.target = t.retreat_point
                t.target_veg = None
                t.path = []
        elif self.status != "dispersing":
            self.reproductionmanager.cancel_mating(self)
            self.status = "dispersing"
            t.target = None
            t.target_veg = None
            t.path = []
        return True

    def end_alarm(self):
        t = self.targeting
        t.alarm_source = None
        t.retreat_point = None
        if self.status in ("dispersing", "retreating"):
            self.status = "wandering"
            t.target = None
            t.path = []

    # -------------------------------------------------
    # State Logic
    # -------------------------------------------------

    def update_state(self):
        self.validate_mate()

        predator = self.targeting.targeted_by

        # Release a predator that died or is no longer hunting this prey
        if predator is not None and (
            not predator.vitals.alive or predator.targeting.target_creature is not self
        ):
            self.targeting.targeted_by = None
            predator = None

        # Fleeing preempts everything, even a target already being walked to
        if predator is not None:
            if self.status != "fleeing":
                self.reproductionmanager.cancel_mating(self)  # drop any mating plan
                self.status = "fleeing"
                self.targeting.target = None
                self.targeting.target_veg = None
                self.targeting.path = []
            return

        if self.status == "fleeing":
            self.status = "wandering"
            self.targeting.target = None

        # A predator started hunting nearby: disperse, and some of us retreat to a point
        if self.check_alarm():
            return

        # Has a partner: walking to / waiting at the mating point
        if self.reproduction.current_mate is not None:
            self.status = "mating"
            return

        if not self.targeting.target:
            if self.vitals.thirst < self.genome.thirst_threshold:
                self.status = "thirsty"

            elif self.vitals.hunger < self.genome.hunger_threshold:
                self.status = "hungry"

            else:
                self.status = "wandering"
                self.get_non_essential_state_decision()

    # -------------------------------------------------
    # State Dispatcher (delegates to behavior components)
    # -------------------------------------------------

    def status_checker(self):

        if self.status == "hungry":
            self.hunger_behavior.handle_hungry_state(self)

        elif self.status == "thirsty":
            self.thirst_behavior.handle_thirsty_state(self)

        elif self.status == "fleeing":
            self.movement.handle_flee_state(self)

        elif self.status == "dispersing":
            self.movement.handle_disperse_state(self)

        elif self.status == "retreating":
            self.movement.handle_retreat_state(self)

        elif self.status == "mating":
            self.reproduction_behavior.handle_mating_state(self)

        else:
            self.targeting.target = None