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

    def notify_travel(self, c, target):
        """Called by interaction manager to assign a travel target."""
        if not c.targeting.target:  # don't override if already heading somewhere
            c.targeting.target = target
            c.targeting.path = []
    
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
            c.world.update_position_dict(c)
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


    def follow_path(self, c):
        self._set_mode(c, "path")

        if not c.targeting.pixel_target:
            c.targeting.pixel_target = (
                c.targeting.path[0][0] * c.world.tile_size + c.world.tile_size // 2,
                c.targeting.path[0][1] * c.world.tile_size + c.world.tile_size // 2,
            )

        if c.targeting.pixel_target:
            t = self.lerp_prep(c, c.targeting.pixel_target)
            c.px = self.lerp(c.px, c.targeting.pixel_target[0], t)
            c.py = self.lerp(c.py, c.targeting.pixel_target[1], t)

        if self.at_pixel_target(c):
            c.prev_x, c.prev_y = c.x, c.y
            c.x, c.y = c.targeting.path.pop(0)
            c.world.update_position_dict(c)
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
            c.world.update_position_dict(c)
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

        if not test_path or len(test_path) - 1 > c.reproductionmanager.MAX_MATE_PATH:
            # unreachable or too far to walk: drop the plan and don't pair these two again for a
            # while (they're free to look for someone else straight away)
            c.reproductionmanager.reject(c, mate)
            c.reproductionmanager.cancel_mating(c)
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
            c.vitals.thirst = 100
            c.logging.times_drank += 1

    def handle_thirsty_state(self, c):
        if c.targeting.target:
            return
        c.update_perceived_tiles()
        c.targeting.target = c.world.find_closest_shore(
            c.x, c.y, c.targeting.perceived_tiles
        )


class PreyMovement(Movement):
    def movement_decider(self, c):
        if c.status == "mating":
            self.mating_movement(c)
        elif c.status == "dispersing":
            self.flee_movement(c)
        elif c.status == "retreating":
            self.retreat_movement(c)
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
        if not predator or not predator.vitals.alive:
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

    # ---------------- herd alarm ----------------

    DISPERSE_SCATTER = 0.5  # chance a dispersing prey takes any tile that isn't closer, not just the farthest

    def handle_disperse_state(self, c):
        """Step away from the predator that raised the alarm. Like handle_flee_state,
        but sometimes takes a sideways step so the herd fans out instead of running in a line."""
        predator = c.targeting.alarm_source
        if not predator or not predator.vitals.alive:
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

        best = max(options + [here], key=dist2)
        if random.random() < self.DISPERSE_SCATTER:
            pool = [t for t in options if dist2(t) >= dist2(here)]
            best = random.choice(pool) if pool else best

        c.targeting.target = best

    def handle_retreat_state(self, c):
        """Called from status_checker while retreating. Holds still once it reaches the point."""
        t = c.targeting
        if t.target is not None and (c.x, c.y) == t.target:
            t.target = None
            t.path = []

    def retreat_movement(self, c):
        t = c.targeting
        if t.target is None or (c.x, c.y) == t.target:
            return  # at the retreat point (or nothing to head for): hold still
        if not t.path:
            self.set_path(c)
            if t.target is None:  # no route to the point: give up, check_alarm goes back to dispersing
                t.retreat_point = None
            return
        self.follow_path(c)


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
            c.logging.times_ate += 1

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


class PredatorMovement(Movement):
    def movement_decider(self, c):
        if c.status == "mating":
            self.mating_movement(c)
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

    POUNCE_RANGE = 4  # pixels

    def hunting_movement(self, c):
        if self.pounce(c):
            return
        if not c.targeting.target:
            return
        self.move_to_tile(c, c.targeting.target)
        self.pounce(c)  # the step may have closed the gap

    def pounce(self, c):
        prey = c.targeting.target_creature
        if prey is None or not prey.vitals.alive:
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
            and c.targeting.target_creature.vitals.alive
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
            c.logging.times_ate += 1
            c.logging.creatures_killed +=1
            c.logging.times_hunted_succesfully += 1
            c.targeting.target_creature.logging.cause_of_death = "hunted"
            c.targeting.target_creature.logging.death_time = c.world.sim_time
            c.targeting.target_creature.vitals.alive = False

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


class PredatorHuntingBehaviour:

    # ---------------- herd alarm ----------------

    ALARM_RADIUS = 10       # tiles (square, like perception): prey this close to the hunter get alarmed
    ALARM_DURATION = 6      # s the alarm lasts. every new hunt by the same predator renews it
    RETREAT_CHANCE = 0.4    # fraction of alarmed prey that go on to flee to the retreat point
    RETREAT_DELAY = 1.5     # s spent dispersing before those prey head for the point
    RETREAT_DISTANCE = 15   # tiles from the predator to the retreat point

    def alarm_nearby_prey(self, c):
        """Called when a predator starts hunting. Every prey close by starts dispersing from it,
        and a random few of them then head for one shared retreat point."""
        now = c.world.sim_time
        target = c.targeting.target_creature  # the hunted prey already flees on its own
        herd = [
            o for o in c.world.creature_list
            if o.genome.type == "prey" and o.vitals.alive and o is not target
            and max(abs(o.x - c.x), abs(o.y - c.y)) <= self.ALARM_RADIUS
        ]

        for prey in herd:
            prey.targeting.alarm_until = now + self.ALARM_DURATION  # also renews prey that are already running

        fresh = [o for o in herd if o.targeting.alarm_source is not c]
        if not fresh:
            return

        point = self.find_retreat_point(c, fresh)
        for prey in fresh:
            t = prey.targeting
            t.alarm_source = c
            t.retreat_point = point if random.random() < self.RETREAT_CHANCE else None
            t.retreat_time = now + self.RETREAT_DELAY


    def find_retreat_point(self, c, herd):
        """A walkable tile RETREAT_DISTANCE from the predator, on the far side of the herd.
        Returns None if there isn't one."""
        world = c.world

        # direction from the predator through the middle of the herd
        dx = sum(o.x for o in herd) / len(herd) - c.x
        dy = sum(o.y for o in herd) / len(herd) - c.y
        length = (dx ** 2 + dy ** 2) ** 0.5
        if length == 0:  # herd is right on top of the predator, any direction will do
            dx, dy = random.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
        else:
            dx, dy = dx / length, dy / length

        x = max(0, min(world.grid_width - 1, round(c.x + dx * self.RETREAT_DISTANCE)))
        y = max(0, min(world.grid_height - 1, round(c.y + dy * self.RETREAT_DISTANCE)))

        # the exact spot may be water: take the closest walkable tile around it
        for radius in range(6):
            ring = [
                (x + ox, y + oy)
                for ox in range(-radius, radius + 1)
                for oy in range(-radius, radius + 1)
                if max(abs(ox), abs(oy)) == radius
                and 0 <= x + ox < world.grid_width
                and 0 <= y + oy < world.grid_height
                and world.is_walkable(x + ox, y + oy)
            ]
            if ring:
                return random.choice(ring)
        return None

    def handle_hunting_state(self, c): 
        now = c.world.sim_time
        #if c.vitals.energy <=0:
        if now - c.last_retarget_time >= c.retarget_interval:
                c.last_retarget_time = now
                c.targeting.target_creature = None
                c.targeting.target = None
                c.targeting.path = []
     

        if not c.targeting.target_creature or not c.targeting.target_creature.vitals.alive:
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