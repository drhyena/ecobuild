from astar import astar
import random
import pygame


class Movement:
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
            c.px = round(c.px + c.speed * v_dir_x * c.world.dt, None)
            c.py = round(c.py + c.speed * v_dir_y * c.world.dt, None)
            print(c.px, c.py)
            print("p chanegd")

    def follow_path(self, c):
        print(f"{c} has entered follow path")

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
        return start + (end - start) * t

    def lerp_prep(self, c, target):
        step = c.speed * c.world.dt
        distance = ((target[0] - c.px) ** 2 + (target[1] - c.py) ** 2) ** (1 / 2)

        if step >= distance:
            return 1
        else:
            return step / distance

    def at_pixel_target(self, c):
        if (c.px, c.py) == c.targeting.pixel_target:
            return True

    def check_if_new_tile(self, c):
        tile_x = (c.px - c.world.tile_size) / c.world.tile_size
        tile_y = (c.py - c.world.tile_size) / c.world.tile_size

        if (tile_x, tile_y) != (c.prev_x, c.prev_y):
            return True


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

    def hunting_movement(self, c):
        c.prev_x, c.prev_y = c.x, c.y
        c.x, c.y = c.targeting.target


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
        c.prev_x, c.prev_y = c.x, c.y
        c.x, c.y = c.targeting.target

    def handle_flee_state(self, c):
        # Predator gone
        if not c.targeting.targeted_by or not c.targeting.targeted_by.alive:
            c.targeting.targeted_by = None
            c.targeting.target = None
            return
        if random.random() < (1 - c.genome.iq):
            return
        predator = c.targeting.targeted_by

        dx = c.x - predator.x
        dy = c.y - predator.y

        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

        # IQ-based directional distortion
        if random.random() < (1 - c.genome.iq):
            step_x, step_y = step_y, step_x

        new_x = c.x + step_x
        new_y = c.y + step_y

        if c.world.is_walkable(new_x, new_y):
            c.targeting.target = (new_x, new_y)
        else:
            c.targeting.target = None


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


class PreyHungerBehavior:
    def handle_hunger(self, c, veg_list, creature_list):
        now = pygame.time.get_ticks()
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
            c.last_retarget_time = pygame.time.get_ticks()


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
        now = pygame.time.get_ticks()
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

        # --- Compute velocity of prey ---
        vx = target_creature.x - target_creature.prev_x
        vy = target_creature.y - target_creature.prev_y

        # Prediction horizon (can scale with IQ later)
        k = 2

        pred_x = target_creature.x + vx * k
        pred_y = target_creature.y + vy * k

        # Clamp to world bounds
        pred_x = max(0, min(c.world.grid_width - 1, pred_x))
        pred_y = max(0, min(c.world.grid_height - 1, pred_y))

        # --- Choose neighbour minimizing distance to predicted position ---
        best_tile = None
        best_score = float("inf")

        for nx, ny in c.world.get_neighbors(c.x, c.y):
            if not c.world.is_walkable(nx, ny):
                continue

            dist = abs(nx - pred_x) + abs(ny - pred_y)

            if dist < best_score:
                best_score = dist
                best_tile = (nx, ny)

        c.targeting.target = best_tile