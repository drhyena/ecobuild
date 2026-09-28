from astar import astar
import random


class Movement:
    def __init__(self):
        self._mode = None

    def _set_mode(self, c, mode):
        """A pixel_target belongs to the movement mode that created it.
        When the mode changes (wander / path / step), drop the stale one."""
        if self._mode != mode:
            self._mode = mode
            c.targeting.pixel_target = None

    def movement_decider(self, c):
        print(f"{c} has entered movement decider with path {c.targeting.path}")
        print(bool(c.targeting.target))
        if c.targeting.target is None:
            self.wander_randomly(c)
        else:
            if not c.targeting.path:
                self.set_path(c)
                if c.targeting.path:
                    print(f"path set for {c}")
                return

        if c.targeting.path:
            self.follow_path(c)

    def notify_travel(self, c, target):
        """Called by interaction manager to assign a travel target."""
        if not c.targeting.target:  # don't override if already heading somewhere
            c.targeting.target = target
            c.targeting.path = []

    def wander_randomly(self, c):
        self._set_mode(c, "wander")
        dx, dy = random.choice(c.world.get_neighbors(c.x, c.y))
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

    # uses vectors to travel between two tiles. basis for pixel based travel
    def pixel_traversal(self, c, dt, pixel_target):
        vector_to_target = (pixel_target[0] - c.px, pixel_target[1] - c.py)
        v_mag = (vector_to_target[0] ** 2 + vector_to_target[1] ** 2) ** (1 / 2)

        v_dir_x = vector_to_target[0] / v_mag
        print("v_dirx", v_dir_x)

        v_dir_y = vector_to_target[1] / v_mag
        print("v-diry", v_dir_y)

        print("pixel target:", pixel_target)

        if (c.px, c.py) != pixel_target:
            c.prev_px = c.px
            c.prev_py = c.py
            c.px = round(c.px + c.genome.speed * v_dir_x * c.world.dt, None)
            c.py = round(c.py + c.genome.speed * v_dir_y * c.world.dt, None)
            print(c.px, c.py)
            print("p chanegd")

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


class ThirstBehavior:
    def handle_thirst(self, c):
        self.drink_water(c)

    def drink_water(self, c):
        if c.status == "thirsty":
            print("drinking")
            c.vitals.thirst = 100
            c.times_drank += 1

    def handle_thirsty_state(self, c):
        if c.targeting.target:
            print(f"{c}has thirst target")
            print(c.targeting.target)
            return
        c.update_perceived_tiles()
        c.targeting.target = c.world.find_closest_shore(
            c.x, c.y, c.targeting.perceived_tiles
        )
        print(f"{c}entered handle thirsty")


class PreyMovement(Movement):
    def movement_decider(self, c):
        if c.targeting.target is None:
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
    def handle_hunger(self, c, veg_list, creature_list):
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
                c.interaction_manager.kill_veg(
                    c.targeting.target_veg, veg_list, creature_list
                )

    def eat_veg(self, c):
        if c.status == "hungry":
            c.vitals.hunger = 100
            c.times_ate += 1

    def handle_hungry_state(self, c, veg, creature_list):
        if c.targeting.target:
            return
        c.update_perceived_tiles()
        c.targeting.target_veg = c.world.find_closest_veg(
            veg, c.x, c.y, c.targeting.perceived_tiles
        )
        if c.targeting.target_veg is None:
            c.targeting.target = None
            return
        if not c.interaction_manager.veg_is_being_targeted(c, creature_list):
            c.targeting.target = (c.targeting.target_veg.v_x, c.targeting.target_veg.v_y)
            c.last_retarget_time = c.world.sim_time


class PredatorMovement(Movement):
    def movement_decider(self, c):
        if c.targeting.target is None:
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
    def handle_hunger(self, c, creature_list):
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

            c.interaction_manager.kill_creature(
                c.targeting.target_creature,
                creature_list
            )

            # Clear hunt lock
            c.targeting.target_creature = None
            c.targeting.target = None
            c.targeting.path = []

    def eat_prey(self, c):
        if c.status in ["hungry", "hunting"]:
            c.vitals.hunger = 100
            c.times_ate += 1
            c.targeting.target_creature.alive = False

    def notify_prey(self, c):
        if c.targeting.target_creature:
            c.interaction_manager.notify_prey(
                c,
                c.targeting.target_creature
            )

    def handle_hungry_state(self, c, creature_list):
        if c.targeting.target_creature or c.targeting.target:
            return

        c.update_perceived_tiles()

        c.targeting.target_creature = c.world.find_closest_prey(
            c,
            creature_list
        )

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


class PredatorHuntingBehaviour:
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