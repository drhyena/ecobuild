from creature import *

class Predator(Creature):

    def __init__(self, x, y, world,interaction_manager):
        super().__init__(x, y, world, interaction_manager)
        self.species = "predator"
        self.genome.iq = 0.7
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
    # EAT PREY (override)
    # Must match base signature
    # -------------------------

    def resolve_interaction(self, veg_list, creature_list):
        if self.interaction_manager.is_on_target(self):

            if self.status in ["hungry","hunting"]:
                self.handle_hunger( creature_list)

            elif self.status == "thirsty":
                self.handle_thirst()
   
    def handle_hunger(self, creature_list):

        # Ensure we are actually on the prey
        if (
            self.targeting.target_creature
            and self.targeting.target_creature.alive
            and self.interaction_manager.is_on_target_creature(
                self.targeting.target_creature, self
            )
            and self.targeting.target_creature.targeting.targeted_by == self
        ):
            self.eat_prey()

            self.interaction_manager.kill_creature(
                self.targeting.target_creature,
                creature_list
            )

            # Clear hunt lock
            self.targeting.target_creature = None
            self.targeting.target = None
            self.targeting.path = []


    def eat_prey(self):
        if self.status in ["hungry", "hunting"]:
            self.vitals.hunger = 100
            self.times_ate += 1
            self.targeting.target_creature.alive = False


    # -------------------------
    # HUNT INITIATION
    # -------------------------

    def notify_prey(self):
        if self.targeting.target_creature:
            self.interaction_manager.notify_prey(
                self,
                self.targeting.target_creature
            )


    # -------------------------
    # STATUS CHECKER OVERRIDE
    # -------------------------

    def status_checker(self, veg, creature_list):

      
        if self.status == "hungry":
            self.handle_hungry_state(creature_list)
        elif self.status == "thirsty":
            self.handle_thirsty_state()
        elif self.status == "hunting":
            self.handle_hunting_state()

        else:
            self.targeting.target = None


    # -------------------------
    # FIND PREY
    # -------------------------

    def handle_hungry_state(self, world, creature_list):

        if self.targeting.target_creature or self.targeting.target:
            return

        self.update_perceived_tiles(world)

        self.targeting.target_creature = world.find_closest_prey(
            self,
            creature_list
        )

        if self.targeting.target_creature is None:
            self.targeting.target = None
            print("predator's prey none")
            return

        test_path = astar(
            (self.x, self.y),
            (self.targeting.target_creature.x, self.targeting.target_creature.y),
            self.world.map_grid,
            self.world.grid_width,
            self.world.grid_height
        )

        if not test_path:
            self.targeting.target_creature = None
            self.targeting.target = None
            return
        
        
        # Inform prey it is being hunted
        self.notify_prey()

    # -------------------------
    # ACTIVE HUNTING
    # -------------------------


    def handle_hunting_state(self, world):

        now = pygame.time.get_ticks()
        if now - self.last_retarget_time >= self.retarget_interval:
            self.last_retarget_time = now
            self.targeting.target_creature = None
            self.targeting.target = None
            self.targeting.path = []
        
        if not self.targeting.target_creature or not self.targeting.target_creature.alive:
            self.targeting.target_creature = None
            self.targeting.target = None
            return

        target_creature = self.targeting.target_creature

        # --- Compute velocity of prey ---
        vx = target_creature.x - target_creature.prev_x
        vy = target_creature.y - target_creature.prev_y

        # Prediction horizon (can scale with IQ later)
        k = 2

        pred_x = target_creature.x + vx * k
        pred_y = target_creature.y + vy * k

        # Clamp to world bounds
        pred_x = max(0, min(world.grid_width - 1, pred_x))
        pred_y = max(0, min(world.grid_height - 1, pred_y))

        # --- Choose neighbour minimizing distance to predicted position ---
        best_tile = None
        best_score = float("inf")

        for nx, ny in world.get_neighbors(self.x, self.y):
            if not world.is_walkable(nx, ny):
                continue

            dist = abs(nx - pred_x) + abs(ny - pred_y)

            if dist < best_score:
                best_score = dist
                best_tile = (nx, ny)

        self.targeting.target = best_tile
        
    def hunting_movement(self):
        self.prev_x, self.prev_y = self.x, self.y
        self.x, self.y = self.targeting.target
        
    def movement_decider(self, world):

        if self.targeting.target is None:
           
            self.wander_randomly(world)
        elif self.status == "hunting":
            self.hunting_movement()
        else:
           

            if not self.targeting.path:
               
                self.set_path(world)
                return

            if self.targeting.path:
                
                self.follow_path()
       
    