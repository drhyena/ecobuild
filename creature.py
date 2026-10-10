import pygame
from CreatureData import Vitals, Genome, Targeting, Reproduction, Migration
from CreatureBehaviors import PreyMovement, ThirstBehavior, PreyHungerBehavior, ReproductionBehavior
from reproductionmanager import ReproductionManager


class Creature:
    def __init__(self, x, y, world, interaction_manager, vitals=None, genome=None,
                 targeting=None, reproduction=None,
                 movement=None, hunger_behavior=None, thirst_behavior=None,
                 hunting_behavior=None, reproductionmanager=None,
                 reproduction_behavior=None, migration=None):
        self.x, self.y = x, y
        self.world = world
        self.px = x*self.world.tile_size + self.world.tile_size//2
        self.py = y*self.world.tile_size + self.world.tile_size//2
        self.status = ""
        self.vitals = vitals if vitals is not None else Vitals()
        self.genome = genome if genome is not None else Genome()
        self.targeting = targeting if targeting is not None else Targeting()
        self.reproduction = reproduction if reproduction is not None else Reproduction()

        # behavior components (swap these to PredatorMovement()/PredatorHungerBehavior()
        # when constructing a predator creature)
        self.movement = movement if movement is not None else PreyMovement()
        self.hunger_behavior = hunger_behavior if hunger_behavior is not None else PreyHungerBehavior()
        self.thirst_behavior = thirst_behavior if thirst_behavior is not None else ThirstBehavior()
        self.hunting_behavior = hunting_behavior
        self.reproductionmanager = reproductionmanager if reproductionmanager is not None else ReproductionManager()
        self.reproduction_behavior = reproduction_behavior if reproduction_behavior is not None else ReproductionBehavior()
        self.migration = migration if migration is not None else Migration()
        self.migration.last_resource_time = self.world.sim_time
        self.migration.last_redirect_time = self.world.sim_time

        self.targeting.target = None
        self.targeting.target_veg = None
        self.targeting.pixel_target = None
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
        self.alive = True
        self.species = "creature"
        self.prev_x, self.prev_y = self.x, self.y
        self.prev_px, self.prev_py = self.px, self.py

        # log attributes. Additional data
        self.times_drank = 0
        self.creatures_killed = 0
        self.times_ate = 0

        # time attributes
        self.birth_time = self.world.sim_time
        self.retarget_interval = 5
        self.last_retarget_time = self.world.sim_time

    # -------------------------
    # MAIN UPDATE LOOP
    # -------------------------

    def update(self):
        self.update_perceived_tiles()
        self.update_needs()
        self.update_state()
        self.resolve_interaction()
        self.check_death()
        print(f"current px:{self.px},py:{self.py}")
        if not self.alive:
            print(self, "died while", self.status)

    # -------------------------
    # VITALS / NEEDS
    # -------------------------

    def update_needs(self):
        self.vitals.hunger -= self.genome.hunger_rate*self.world.dt*1.5
        self.vitals.thirst -= self.genome.thirst_rate*self.world.dt*1.5
        self.vitals.age = self.world.sim_time - self.birth_time
        self.reproduction.time_since_last_mating +=  self.world.dt

    def check_essentials(self):
        return {
            "thirsty": max(0, (self.genome.thirst_threshold - self.vitals.thirst) / self.genome.thirst_threshold),
            "hungry": max(0, (self.genome.hunger_threshold - self.vitals.hunger) / self.genome.hunger_threshold),
            "wandering": 0.05,
        }

    def get_essential_state_decision(self):
        utilities = self.check_essentials()
        return max(utilities, key=utilities.get)

    def get_non_essential_state_decision(self):
        rm = self.reproductionmanager
        if self.reproduction.current_mate is None:
            if not (rm.check_if_ready_to_seek_mate(self) and rm.check_if_well_fed(self)):
                return
            rm.check_for_viable_mate(self)
            if rm.check_if_ready_to_reproduce(self):
                self.status = "mating"

    def validate_mate(self):
        """Drop the mating plan if the partner has died."""
        mate = self.reproduction.current_mate
        if mate is not None and not mate.alive:
            self.reproductionmanager.cancel_mating(self)

    # -------------------------
    # MIGRATION (state helpers)
    # -------------------------

    def is_needy(self):
        return (self.vitals.thirst < self.genome.thirst_threshold
                or self.vitals.hunger < self.genome.hunger_threshold)

    def sees_food(self):
        return self.world.find_closest_veg(
            self.x, self.y, self.targeting.perceived_tiles) is not None

    def sees_needed_resource(self):
        """True if whatever this creature is short of is within its perception."""
        if self.vitals.thirst < self.genome.thirst_threshold:
            if self.world.find_closest_shore(
                    self.x, self.y, self.targeting.perceived_tiles) is not None:
                return True
        if self.vitals.hunger < self.genome.hunger_threshold:
            return self.sees_food()
        return False

    def check_migration(self):
        """Hold the 'no food/water found' clock at zero while needs are met.
        Once hungry/thirsty for too long without a target, start migrating."""
        now = self.world.sim_time
        if self.status not in ("hungry", "thirsty"):
            self.migration.last_resource_time = now
        elif now - self.migration.last_resource_time >= self.movement.MIGRATE_AFTER:
            self.status = "migrating"

    def update_state(self):
        self.validate_mate()
        was_migrating = self.status == "migrating"
        self.status = self.get_essential_state_decision()
        self.vitals.age = self.world.sim_time - self.birth_time
        if self.reproduction.current_mate is not None:
            self.status = "mating"
        elif was_migrating and self.is_needy():
            self.status = "migrating"  # stays until handle_migrate_state ends it
        else:
            self.check_migration()
            if self.status == "wandering":
                self.get_non_essential_state_decision()
        print(self.status)

    def check_death(self):
        if self.vitals.hunger <= 0 or self.vitals.thirst <= 0:
            print(f"{self} died at hunger:{self.vitals.hunger}")
            self.interaction_manager.kill_creature(self)

    # -------------------------
    # INTERACTION RESOLUTION (delegates to hunger/thirst behavior components)
    # -------------------------

    def resolve_interaction(self):
        if self.status == "mating":
            self.reproduction_behavior.handle_mating(self)
            return

        if self.interaction_manager.is_on_target(self):
            if self.status == "hungry":
                self.hunger_behavior.handle_hunger(self)
            elif self.status == "thirsty":
                self.thirst_behavior.handle_thirst(self)

    # -------------------------
    # REPRODUCTION
    # -------------------------

    def check_if_ready_for_a_mate(self):
        rm = self.reproductionmanager
        return rm.check_if_ready_to_seek_mate(self) and rm.check_if_well_fed(self)

    # -------------------------
    # SIGNAL
    # -------------------------

    def creature_receive_signal(self, from_, tile, signal_type=None):
        self.signal = {"type": signal_type, "from": from_, "tile": tile}

    # -------------------------
    # PERCEPTION
    # -------------------------

    def update_perceived_tiles(self):
        self.targeting.perceived_tiles.clear()
        self.targeting.perceived_tiles = [
            (self.x + dx, self.y + dy)
            for dx, dy in self.genome.perceptive_radius
            if 0 <= self.x + dx < self.world.grid_width
            and 0 <= self.y + dy < self.world.grid_height
        ]

    # -------------------------
    # TARGET DECISION (delegates to hunger/thirst behavior components)
    # -------------------------

    def status_checker(self):
        if self.status == "hungry":
            self.hunger_behavior.handle_hungry_state(self)
        elif self.status == "thirsty":
            self.thirst_behavior.handle_thirsty_state(self)
        elif self.status == "migrating":
            self.movement.handle_migrate_state(self)
        elif self.status == "mating":
            self.reproduction_behavior.handle_mating_state(self)
        else:
            self.targeting.target = None

    # -------------------------
    # MOVEMENT (delegates to movement behavior component)
    # -------------------------

    def movement_decider(self):
        self.movement.movement_decider(self)

    def notify_travel(self, target):
        self.movement.notify_travel(self, target)