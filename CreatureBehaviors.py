from astar import astar
import random


class Movement:
    def __init__(self):
        self._mode = None

    def _set_mode(self, c, mode):
        if self._mode != mode:
            self._mode = mode
            c.targeting.pixel_target = None

    def movement_decider(self, c):
        if c.status == "mating":
            self.mating_movement(c)
            return
        if c.status == "migrating":
            self.migrate(c)
            return
        if c.targeting.target is None:
            self.wander_randomly(c)
        else:
            if not c.targeting.path:
                self.set_path(c)
                return
            self.follow_path(c)

    def mating_movement(self, c):
        """Walk the path set by ReproductionManager.set_midpoint, then wait
        at the mating point for the partner."""
        if c.targeting.path:
            self.follow_path(c)

    # ---------------- migration ----------------

    MIGRATE_AFTER = 3                # s hungry/thirsty without finding a resource before migrating
    MIGRATE_REDIRECT_INTERVAL = 10   # s between 1-step (45 degree) heading changes
    # N, NE, E, SE, S, SW, W, NW (y grows downward, so north is -y)
    COMPASS = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]

    def migrate(self, c):
        """Walk tile by tile along the migration heading. Water, the map edge
        or a water corner ahead forces a redirect."""
        m = c.migration
        if m.direction is None:
            self._pick_migration_direction(c)

        # Entering from wandering/path-following must drop that mode's stale
        # pixel_target first, otherwise a mid-step creature gets re-aimed
        # using the wrong coordinates.
        self._set_mode(c, "step")

        # A step already in flight (pixel_target latched) finishes first
        tile = None
        if c.targeting.pixel_target is None:
            if not self._can_step(c, m.direction):
                if not self._redirect_from_obstacle(c):
                    return  # boxed in
            tile = (c.x + m.direction[0], c.y + m.direction[1])
        self.move_to_tile(c, tile)  # tile is ignored while a step is in flight

    def handle_migrate_state(self, c):
        """Called from status_checker while migrating. Ends the trip once the
        needed food/water is in sight; otherwise turns one compass step every
        MIGRATE_REDIRECT_INTERVAL seconds."""
        m = c.migration
        if not c.is_needy() or c.sees_needed_resource():
            m.direction = None
            m.last_resource_time = c.world.sim_time
            c.status = "wandering"
            return
        if m.direction is None:
            self._pick_migration_direction(c)
        elif c.world.sim_time - m.last_redirect_time >= self.MIGRATE_REDIRECT_INTERVAL:
            self._turn(c, random.choice((-1, 1)))

    def _can_step(self, c, d):
        """True if the creature can take one step in direction d. A diagonal
        step also needs both orthogonal tiles clear, so it never cuts across
        the corner of a water tile."""
        world = c.world
        if not world.is_walkable(c.x + d[0], c.y + d[1]):
            return False
        if d[0] and d[1]:
            return (world.is_walkable(c.x + d[0], c.y)
                    and world.is_walkable(c.x, c.y + d[1]))
        return True

    def _pick_migration_direction(self, c):
        m = c.migration
        options = [d for d in self.COMPASS if self._can_step(c, d)]
        m.direction = random.choice(options or self.COMPASS)
        m.last_redirect_time = c.world.sim_time

    def _turn(self, c, steps):
        m = c.migration
        i = self.COMPASS.index(m.direction)
        m.direction = self.COMPASS[(i + steps) % 8]
        m.last_redirect_time = c.world.sim_time

    def _redirect_from_obstacle(self, c):
        """Pick a new open heading, preferring turns of up to 90 degrees."""
        m = c.migration
        i = self.COMPASS.index(m.direction)
        for turns in ((-2, -1, 1, 2), (-3, 3, 4)):
            options = [self.COMPASS[(i + t) % 8] for t in turns
                       if self._can_step(c, self.COMPASS[(i + t) % 8])]
            if options:
                m.direction = random.choice(options)
                m.last_redirect_time = c.world.sim_time
                return True
        return False

    def notify_travel(self, c, target):
        """Called by interaction manager to assign a travel target."""
        if not c.targeting.target:  # don't override if already heading somewhere
            c.targeting.target = target
            c.targeting.path = []

    
    #def wander_to_a_new_region(self,c)

   
   # def wander_state_machine(self,c):
    #    if c.vitals.age %10 == 0:
     #       self.wander_far(_
    
    
    def wander_randomly(self, c):
        self._set_mode(c, "wander")
        dx, dy = random.choice(list(c.world.get_neighbors(c.x, c.y)))
        if c.world.is_walkable(dx, dy):
            if not c.targeting.pixel_target:
                c.targeting.pixel_target = (
                    dx * c.world.tile_size + c.world.tile_size // 2,
                    dy * c.world.tile_size + c.world.tile_size // 2,
                )

        if c.targeting.pixel_target is not None:
            t = self.lerp_prep(c, c.targeting.pixel_target)
            c.px = self.lerp(c.px, c.targeting.pixel_target[0], t)
            c.py = self.lerp(c.py, c.targeting.pixel_target[1], t)

        if self.at_pixel_target(c):
            c.prev_x = c.x
            c.prev_y = c.y
            c.x = (c.targeting.pixel_target[0] - c.world.tile_size // 2) // c.world.tile_size
            c.y = (c.targeting.pixel_target[1] - c.world.tile_size // 2) // c.world.tile_size
            c.targeting.pixel_target = None

    # finds a path through tiles.
    def set_path(self, c):
        if c.targeting.target:
            c.targeting.path = astar(
                (c.x, c.y),
                (c.targeting.target[0], c.targeting.target[1]),
                c.world.map_grid,
                c.world.grid_width,
                c.world.grid_height,
            )
            if not c.targeting.path:
                c.targeting.target = None
                print(f"path not found for {c}")


    def follow_path(self, c):
        print(f"{c} has entered follow path")
        self._set_mode(c, "path")

        if not c.targeting.pixel_target:
            c.targeting.pixel_target = (
                c.targeting.path[0][0] * c.world.tile_size + c.world.tile_size // 2,
                c.targeting.path[0][1] * c.world.tile_size + c.world.tile_size // 2,
            )
            print(f"{c} has found pixel_target at {c.targeting.pixel_target} ")

        if c.targeting.pixel_target:
            t = self.lerp_prep(c, c.targeting.pixel_target)
            c.px = self.lerp(c.px, c.targeting.pixel_target[0], t)
            c.py = self.lerp(c.py, c.targeting.pixel_target[1], t)

        if self.at_pixel_target(c):
            c.prev_x, c.prev_y = c.x, c.y
            c.x, c.y = c.targeting.path.pop(0)
            c.targeting.pixel_target = None

    def lerp(self, start, end, t):
        if t >= 1:
            return end
        return start + (end - start) * t

    def lerp_prep(self, c, target):
        step = c.genome.speed * c.world.dt
        distance = ((target[0] - c.px) ** 2 + (target[1] - c.py) ** 2) ** (1 / 2)

        if step >= distance:
            return 1
        else:
            return step / distance

    def at_pixel_target(self, c):
        if (c.px, c.py) == c.targeting.pixel_target:
            return True

    def move_to_tile(self, c, tile):
        """Pixel-based step toward an adjacent tile (used by fleeing/hunting).
        Latches pixel_target so the step finishes even if `tile` is re-chosen
        mid-step; c.x/c.y only update on arrival."""
        self._set_mode(c, "step")
        ts = c.world.tile_size
        if c.targeting.pixel_target is None:
            c.targeting.pixel_target = (
                tile[0] * ts + ts // 2,
                tile[1] * ts + ts // 2,
            )

        target = c.targeting.pixel_target
        t = self.lerp_prep(c, target)
        c.px = self.lerp(c.px, target[0], t)
        c.py = self.lerp(c.py, target[1], t)

        if self.at_pixel_target(c):
            c.prev_x, c.prev_y = c.x, c.y
            c.x = (target[0] - ts // 2) // ts
            c.y = (target[1] - ts // 2) // ts
            c.targeting.pixel_target = None
            c.targeting.target = None  # step done; the state handler picks the next one

    def check_if_new_tile(self, c):
        tile_x = (c.px - c.world.tile_size) / c.world.tile_size
        tile_y = (c.py - c.world.tile_size) / c.world.tile_size

        if (tile_x, tile_y) != (c.prev_x, c.prev_y):
            return True




class ReproductionBehavior:
    def mating_point_setter(self, c):
        mate = c.reproduction.current_mate
        test_path = astar(
            (c.x, c.y),
            (mate.x, mate.y),
            c.world.map_grid,
            c.world.grid_width,
            c.world.grid_height
        )

        if not test_path:
            # unreachable partner: drop the plan and wait a full interval before retrying
            c.reproductionmanager.cancel_mating(c)
            c.reproduction.time_since_last_mating = 0
            return

        test_path1, test_path2 = c.reproductionmanager.split_path(test_path)
        c.reproductionmanager.set_midpoint(c, test_path1, test_path2)

    def handle_mating_state(self, c):
        """Called from status_checker: plan the meeting point once."""
        if c.reproduction.current_mate is None:
            return
        if not c.targeting.mating_point:
            self.mating_point_setter(c)

    def handle_mating(self, c):
        """Called from resolve_interaction: mate once both creatures are at the mating point."""
        if c.reproduction.current_mate is None:
            return
        if c.reproductionmanager.check_if_creatures_are_at_mating_point(c):
            c.reproductionmanager.mate(c)


class ThirstBehavior:
    def handle_thirst(self, c):
        self.drink_water(c)

    def drink_water(self, c):
        if c.status == "thirsty":
            print("drinking")
            c.vitals.thirst = 100
            c.times_drank += 1
            c.migration.last_resource_time = c.world.sim_time

    def handle_thirsty_state(self, c):
        if c.targeting.target:
            print(f"{c}has thirst target")
            print(c.targeting.target)
            return
        c.update_perceived_tiles()
        c.targeting.target = c.world.find_closest_shore(
            c.x, c.y, c.targeting.perceived_tiles
        )
        if c.targeting.target is not None:
            c.migration.last_resource_time = c.world.sim_time
        print(f"{c}entered handle thirsty")


class PreyMovement(Movement):
    def movement_decider(self, c):
        if c.status == "mating":
            self.mating_movement(c)
        elif c.status == "migrating":
            self.migrate(c)
        elif c.targeting.target is None:
            self.wander_randomly(c)
        elif c.status == "fleeing":
            self.flee_movement(c)
        else:
            if not c.targeting.path:
                self.set_path(c)
                return
            if c.targeting.path:
                self.follow_path(c)

    def flee_movement(self, c):
        if not c.targeting.target:
            return
        self.move_to_tile(c, c.targeting.target)

    def handle_flee_state(self, c):
        predator = c.targeting.targeted_by
        # Predator gone
        if not predator or not predator.alive:
            c.targeting.targeted_by = None
            c.targeting.target = None
            return

        world = c.world
        here = (c.x, c.y)

        def dist2(tile):
            return (tile[0] - predator.x) ** 2 + (tile[1] - predator.y) ** 2

        options = [t for t in world.get_neighbors(c.x, c.y) if world.is_walkable(*t)]
        if not options:
            c.targeting.target = here  # cornered: hold still
            return

        # Best move: farthest from the predator (standing still counts as an option)
        best = max(options + [here], key=dist2)

        # IQ-based mistakes: a panicked step is random but never closer to the predator
        if random.random() < (1 - c.genome.iq):
            pool = [t for t in options if dist2(t) >= dist2(here)]
            best = random.choice(pool) if pool else best

        c.targeting.target = best


class PreyHungerBehavior:
    def handle_hunger(self, c):
        now = c.world.sim_time
        if now - c.last_retarget_time >= c.retarget_interval:
            c.last_retarget_time = now
            c.targeting.target = None
            c.targeting.target_veg = None
            c.targeting.path = []

        if c.targeting.target_veg and c.targeting.target_veg.alive:
            if c.targeting.target_veg.claimed_by is None:
                c.targeting.target_veg.claimed_by = c
                self.eat_veg(c)
                c.interaction_manager.kill_veg(c.targeting.target_veg)

    def eat_veg(self, c):
        if c.status == "hungry":
            c.vitals.hunger = 100
            c.times_ate += 1
            c.migration.last_resource_time = c.world.sim_time

    def handle_hungry_state(self, c):
        if c.targeting.target:
            return
        c.update_perceived_tiles()
        c.targeting.target_veg = c.world.find_closest_veg(
            c.x, c.y, c.targeting.perceived_tiles
        )
        if c.targeting.target_veg is None:
            c.targeting.target = None
            return
        if not c.interaction_manager.veg_is_being_targeted(c):
            c.targeting.target = (c.targeting.target_veg.v_x, c.targeting.target_veg.v_y)
            c.last_retarget_time = c.world.sim_time
            c.migration.last_resource_time = c.world.sim_time


class PredatorMovement(Movement):
    def movement_decider(self, c):
        if c.status == "mating":
            self.mating_movement(c)
        elif c.status == "migrating":
            self.migrate(c)
        elif c.status == "stalking":
            self.stalking(c)
        elif c.targeting.target is None:
            self.wander_randomly(c)
        elif c.status == "hunting":
            self.hunting_movement(c)
        else:
            if not c.targeting.path:
                self.set_path(c)
                return
            if c.targeting.path:
                self.follow_path(c)

    # ---------------- stalking ----------------

    STALK_MIN_DIST = 4  # tiles: closer than this and the predator backs off
    STALK_MAX_DIST = 7  # tiles: farther than this and it closes in
                        # (perception reaches 10 tiles, so this leaves a margin)

    def stalking(self, c):
        """Shadow the stalked prey without alerting it: hold still while it is
        inside the STALK_MIN_DIST..STALK_MAX_DIST band, close in when it drifts
        away, back off if it gets too close. Never sets target_creature and
        never calls notify_prey, so the prey does not flee."""
        prey = c.targeting.stalk_target
        if prey is None:
            self.wander_randomly(c)  # nothing in sight: look around
            return

        self._set_mode(c, "step")
        if c.targeting.pixel_target is not None:
            self.move_to_tile(c, None)  # finish the step in flight
            return

        dist = max(abs(prey.x - c.x), abs(prey.y - c.y))
        if self.STALK_MIN_DIST <= dist <= self.STALK_MAX_DIST:
            return  # comfortable distance: hold position

        ideal = (self.STALK_MIN_DIST + self.STALK_MAX_DIST) // 2

        def gap(tile):
            return abs(max(abs(prey.x - tile[0]), abs(prey.y - tile[1])) - ideal)

        options = [(c.x + dx, c.y + dy) for dx, dy in self.COMPASS
                   if self._can_step(c, (dx, dy))]
        if not options:
            return
        best = min(options, key=lambda t: (gap(t), (t[0] - prey.x) ** 2 + (t[1] - prey.y) ** 2))
        if gap(best) < gap((c.x, c.y)):
            self.move_to_tile(c, best)

    POUNCE_RANGE = 6  # pixels

    def hunting_movement(self, c):
        if self.pounce(c):
            return
        if not c.targeting.target:
            return
        self.move_to_tile(c, c.targeting.target)
        self.pounce(c)  # the step may have closed the gap

    def pounce(self, c):
        prey = c.targeting.target_creature
        if prey is None or not prey.alive:
            return False

        dx = prey.px - c.px
        dy = prey.py - c.py
        if dx * dx + dy * dy > self.POUNCE_RANGE ** 2:
            return False

        c.prev_x, c.prev_y = c.x, c.y
        c.px, c.py = prey.px, prey.py          # pixel position
        c.x, c.y = prey.x, prey.y              # tile position
        c.targeting.pixel_target = None        # cancel any step in progress
        c.targeting.target = (prey.x, prey.y)  # now "on target" for the eat check
        return True

class PredatorHungerBehavior:
    def handle_hunger(self, c):
        # Ensure we are actually on the prey
        if (
            c.targeting.target_creature
            and c.targeting.target_creature.alive
            and c.interaction_manager.is_on_target_creature(
                c.targeting.target_creature, c
            )
            and c.targeting.target_creature.targeting.targeted_by == c
        ):
            self.eat_prey(c)

            c.interaction_manager.kill_creature(c.targeting.target_creature)

            # Clear hunt lock
            c.targeting.target_creature = None
            c.targeting.target = None
            c.targeting.path = []

    def eat_prey(self, c):
        if c.status in ["hungry", "hunting"]:
            c.vitals.hunger = 100
            c.times_ate += 1
            c.targeting.target_creature.alive = False
            c.migration.last_resource_time = c.world.sim_time

    def notify_prey(self, c):
        if c.targeting.target_creature:
            c.interaction_manager.notify_prey(
                c,
                c.targeting.target_creature
            )

    def handle_hungry_state(self, c):
        if c.targeting.target_creature or c.targeting.target:
            return

        c.update_perceived_tiles()

        c.targeting.target_creature = c.world.find_closest_prey(c)

        if c.targeting.target_creature is None:
            c.targeting.target = None
            print("predator's prey none")
            return

        test_path = astar(
            (c.x, c.y),
            (c.targeting.target_creature.x, c.targeting.target_creature.y),
            c.world.map_grid,
            c.world.grid_width,
            c.world.grid_height
        )

        if not test_path:
            c.targeting.target_creature = None
            c.targeting.target = None
            return

        # Inform prey it is being hunted
        self.notify_prey(c)
        c.migration.last_resource_time = c.world.sim_time


class PredatorHuntingBehaviour:
    def handle_stalking_state(self, c):
        """Keep one prey in perception to shadow. Deliberately does not set
        target_creature or notify the prey."""
        prey = c.targeting.stalk_target
        if prey is not None and (
            not prey.alive or (prey.x, prey.y) not in c.targeting.perceived_tiles
        ):
            prey = None  # died or slipped out of perception
        if prey is None:
            prey = c.world.find_closest_prey(c)
        c.targeting.stalk_target = prey

    def handle_hunting_state(self, c):
        now = c.world.sim_time
        if now - c.last_retarget_time >= c.retarget_interval:
            c.last_retarget_time = now
            c.targeting.target_creature = None
            c.targeting.target = None
            c.targeting.path = []

        if not c.targeting.target_creature or not c.targeting.target_creature.alive:
            c.targeting.target_creature = None
            c.targeting.target = None
            return

        target_creature = c.targeting.target_creature
        world = c.world

        # Aim straight at the prey when close; lead it only when it is far away
        dist = max(abs(target_creature.x - c.x), abs(target_creature.y - c.y))
        k = 0 if dist <= 2 else 2

        vx = target_creature.x - target_creature.prev_x
        vy = target_creature.y - target_creature.prev_y

        pred_x = max(0, min(world.grid_width - 1, target_creature.x + vx * k))
        pred_y = max(0, min(world.grid_height - 1, target_creature.y + vy * k))

        here = (c.x, c.y)

        def score(tile):
            # Chebyshev distance to the aim point (no diagonal bias),
            # ties broken by real distance to the prey
            return (
                max(abs(tile[0] - pred_x), abs(tile[1] - pred_y)),
                (tile[0] - target_creature.x) ** 2 + (tile[1] - target_creature.y) ** 2,
            )

        candidates = [t for t in world.get_neighbors(c.x, c.y) if world.is_walkable(*t)]
        candidates.append(here)  # standing still is allowed, so it never steps backwards
        c.targeting.target = min(candidates, key=score)