import random

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

        # Furthest tile (in x or y) the prey perceives; same square as perceived_tiles
        self.perception_range = max(
            max(abs(dx), abs(dy)) for dx, dy in self.genome.perceptive_radius
        )

    # -------------------------------------------------
    # Predator Noticing (any predator in view, not just one hunting this prey)
    # -------------------------------------------------

    NOTICE_INTERVAL = 1.0  # s between IQ checks while a predator is in view
    IQ_CHECK_DC = 0.5      # iq + jitter must reach this to notice
    IQ_JITTER = 0.25       # randomisation added to iq: +/- this much

    def nearby_predators(self):
        """Living predators inside this prey's perceived tiles."""
        r = self.perception_range
        return [
            o for o in self.world.creature_list
            if o.species == "predator" and o.alive
            and max(abs(o.x - self.x), abs(o.y - self.y)) <= r
        ]

    def notices_predators(self):
        """True if a predator is in view AND the prey passes an IQ check.
        The check is iq + random jitter against a difficulty, rolled once per
        NOTICE_INTERVAL while a predator is in view; the result stands until
        the next roll. With the default numbers an iq of 0.4 notices ~30% of
        rolls, 0.6 ~70%, 0.8 always."""
        t = self.targeting
        if not self.nearby_predators():
            t.noticed_predator = False
            t.last_notice_roll = None  # a new sighting rolls straight away
            return False

        now = self.world.sim_time
        if t.last_notice_roll is None or now - t.last_notice_roll >= self.NOTICE_INTERVAL:
            t.last_notice_roll = now
            roll = self.genome.iq + random.uniform(-self.IQ_JITTER, self.IQ_JITTER)
            t.noticed_predator = roll >= self.IQ_CHECK_DC
        return t.noticed_predator

    # -------------------------------------------------
    # Predator Awareness
    # -------------------------------------------------

    def get_predator(self, predator):
        self.targeting.targeted_by = predator if predator else None

    # -------------------------------------------------
    # State Logic
    # -------------------------------------------------

    def update_state(self):
        self.validate_mate()

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
                self.reproductionmanager.cancel_mating(self)  # drop any mating plan
                self.status = "fleeing"
                self.targeting.target = None
                self.targeting.target_veg = None
                self.targeting.path = []
            return

        if self.status == "fleeing":
            self.status = "wandering"
            self.targeting.target = None

        # Noticed a predator nearby: move away from it (drops any mating plan)
        if self.notices_predators():
            if self.status != "evading":
                self.reproductionmanager.cancel_mating(self)
                self.status = "evading"
                self.targeting.target = None
                self.targeting.target_veg = None
                self.targeting.path = []
            return

        if self.status == "evading":
            self.status = "wandering"
            self.targeting.target = None

        # Has a partner: walking to / waiting at the mating point
        if self.reproduction.current_mate is not None:
            self.status = "mating"
            return

        # Migrating: stays in this state until handle_migrate_state ends it
        if self.status == "migrating":
            return

        if not self.targeting.target:
            if self.vitals.thirst < self.genome.thirst_threshold:
                self.status = "thirsty"

            elif self.vitals.hunger < self.genome.hunger_threshold:
                self.status = "hungry"

            else:
                self.status = "wandering"
                self.get_non_essential_state_decision()

            self.check_migration()

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

        elif self.status == "migrating":
            self.movement.handle_migrate_state(self)

        elif self.status == "mating":
            self.reproduction_behavior.handle_mating_state(self)

        else:
            self.targeting.target = None