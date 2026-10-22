import pygame
from CreatureData import Vitals, Genome, Targeting, Reproduction, Logging
from CreatureBehaviors import PreyMovement, ThirstBehavior, PreyHungerBehavior, ReproductionBehavior
from reproductionmanager import ReproductionManager
from geneticmanager import GeneticManager

_OFFSETS = {}
def get_offsets(radius):
        offsets = _OFFSETS.get(radius)
        if offsets is None:
            offsets = [(dx, dy)
                    for dx in range(-radius, radius + 1)
                    for dy in range(-radius, radius + 1)
                    if not (dx == 0 and dy == 0)]
            _OFFSETS[radius] = offsets
        return offsets


class Creature:
    def __init__(self, x, y, world, interaction_manager,log, logging = None, vitals=None, genome=None,
                 targeting=None, reproduction=None,
                 movement=None, hunger_behavior=None, thirst_behavior=None,
                 hunting_behavior=None, reproductionmanager=None,
                 reproduction_behavior=None, geneticmanager = None, ):
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
        self.geneticmanager = geneticmanager if geneticmanager is not None else GeneticManager()

        self.logging = logging if logging is not None else Logging()


        self.signal = {"type": None, "from": None, "tile": None}
        self.interaction_manager = interaction_manager
        self.log = log
        self.prev_x, self.prev_y = self.x, self.y
        self.prev_px, self.prev_py = self.px, self.py

        # log attributes. Additional data
        self.logging.times_drank = 0
        self.logging.creatures_killed = 0
        self.logging.times_ate = 0
        self.logging.birth_time = self.world.sim_time

        self.retarget_interval = 5
        self.last_retarget_time = self.world.sim_time
        self._perception_key = None

    # -------------------------
    # MAIN UPDATE LOOP
    # -------------------------

    def update(self):
        self.update_perceived_tiles()
        self.update_needs()
        self.update_state()
        self.resolve_interaction()
        self.check_death()

    # -------------------------
    # VITALS / NEEDS
    # -------------------------

    def update_needs(self):
        self.vitals.hunger -= self.genome.hunger_rate*self.world.dt*1.5
        self.vitals.thirst -= self.genome.thirst_rate*self.world.dt*1.5
        self.vitals.age = self.world.sim_time - self.logging.birth_time
        self.reproduction.time_since_last_mating +=  self.world.dt

        #if self.status in ("hunting","fleeing"):
            #self.vitals.energy -= self.genome.energy_drain_rate*self.world.dt*1.5

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
        """Drop the mating plan if it can no longer work out: the partner died, either
        creature can't afford mating any more (hungry/thirsty), or it's taking too long."""
        mate = self.reproduction.current_mate
        if mate is None:
            return
        rm = self.reproductionmanager
        if not mate.vitals.alive:
            rm.cancel_mating(self)
        elif rm.check_if_mating_timed_out(self):
            rm.reject(self, mate)  # don't immediately re-pair with the same partner
            rm.cancel_mating(self)
        elif not (rm.check_if_can_afford_mating(self) and rm.check_if_can_afford_mating(mate)):
            rm.cancel_mating(self)

    def sees_food(self):
        return self.world.find_closest_veg(
            self.x, self.y, self.targeting.perceived_tiles) is not None

    def update_state(self):
        self.validate_mate()
        self.status = self.get_essential_state_decision()
        self.vitals.age = self.world.sim_time - self.logging.birth_time
        if self.reproduction.current_mate is not None and self.reproductionmanager.check_if_both_are_ready_to_reproduce():
            self.status = "mating"
        elif self.status == "wandering":
            self.get_non_essential_state_decision()

    def check_death(self):
        if self.vitals.age >= 100:
            self.logging.cause_of_death = "age"
            self.logging.death_time = self.world.sim_time
            self.interaction_manager.kill_creature(self)            

        
        elif self.vitals.hunger <= 0 :
            self.logging.cause_of_death = "hunger"

            self.logging.death_time = self.world.sim_time
            self.interaction_manager.kill_creature(self)
            
        elif self.vitals.thirst <= 0:
            self.logging.cause_of_death = "thirst"
            self.logging.death_time = self.world.sim_time
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

# Drop-in replacement for Creature.update_perceived_tiles in creature.py.
#
# Two changes:
#   1. The (dx, dy) offsets only depend on the radius, so they are built once per radius
#      and shared by every creature.
#   2. The tile list only depends on (x, y, radius). A creature stays on one tile for many
#      frames, so the list is rebuilt only when it changes tile (or its radius changes).
#
# Setup:
#   - paste _OFFSETS and get_offsets above the Creature class (module level)
#   - add   self._perception_key = None   anywhere in Creature.__init__
#   - replace the old update_perceived_tiles method with the one below
#
# Check first: nothing else should modify targeting.perceived_tiles in place
# (e.g. .remove() or .append()), because the list is now reused between frames.
# The radius must stay an int (range() needs it), which it is after Genome/GeneticManager rounding.

    



    # inside class Creature:
    def update_perceived_tiles(self):
        key = (self.x, self.y, self.genome.perceptive_radius)
        if key == self._perception_key:
            return  # same tile, same radius: the old list is still right
        self._perception_key = key

        x, y = self.x, self.y
        w, h = self.world.grid_width, self.world.grid_height
        self.targeting.perceived_tiles = [
            (x + dx, y + dy)
            for dx, dy in get_offsets(self.genome.perceptive_radius)
            if 0 <= x + dx < w and 0 <= y + dy < h
        ]
        # -------------------------
        # TARGET DECISION (delegates to hunger/thirst behavior components)
        # -------------------------

    def status_checker(self):
        if self.status == "hungry":
            self.hunger_behavior.handle_hungry_state(self)
        elif self.status == "thirsty":
            self.thirst_behavior.handle_thirsty_state(self)
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