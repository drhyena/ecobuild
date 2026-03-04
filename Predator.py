from creature import *

class Predator(Creature):

    def __init__(self, x, y, interaction_manager):
        super().__init__(x, y, interaction_manager)
        self.species = "predator"
        self.target_creature = None
        self.iq = 0.7


    # -------------------------
    # STATE OVERRIDE
    # -------------------------

    def update_state(self):

        # If actively hunting
        if self.target_creature:
            self.status = "hunting"
            return

        # Normal need-based logic
        if not self.target:
            if self.thirst < 30:
                self.status = "thirsty"
            elif self.hunger < 50:
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
            self.target_creature
            and self.target_creature.alive
            and self.interaction_manager.is_on_target_creature(
                self.target_creature, self
            )
            and self.target_creature.targetted_by == self
        ):
            self.eat_prey()

            self.interaction_manager.kill_creature(
                self.target_creature,
                creature_list
            )

            # Clear hunt lock
            self.target_creature = None
            self.target = None
            self.path = []


    def eat_prey(self):
        if self.status in ["hungry", "hunting"]:
            self.hunger = 100
            self.target_creature.alive = False


    # -------------------------
    # HUNT INITIATION
    # -------------------------

    def notify_prey(self):
        if self.target_creature:
            self.interaction_manager.notify_prey(
                self,
                self.target_creature
            )


    # -------------------------
    # STATUS CHECKER OVERRIDE
    # -------------------------

    def status_checker(self, world, veg, creature_list):

        if self.status == "hungry":
            self.handle_hungry_state(world, creature_list)

        elif self.status == "thirsty":
            self.handle_thirsty_state(world)

        elif self.status == "hunting":
            self.handle_hunting_state(world)
            

        else:
            self.target = None


    # -------------------------
    # FIND PREY
    # -------------------------

    def handle_hungry_state(self, world, creature_list):

        if self.target_creature or self.target:
            return

        self.update_perceived_tiles(world)

        self.target_creature = world.find_closest_prey(
            self,
            creature_list
        )

        if self.target_creature is None:
            self.target = None
            return

        # Inform prey it is being hunted
        self.notify_prey()

        


    # -------------------------
    # ACTIVE HUNTING
    # -------------------------


    def handle_hunting_state(self, world):

        if not self.target_creature or not self.target_creature.alive:
            self.target_creature = None
            self.target = None
            return

        target_creature = self.target_creature

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

        self.target = best_tile
        
    def hunting_movement(self):
        self.prev_x, self.prev_y = self.x,self.y
        self.x,self.y = self.target
        
    def movement_decider(self, world, screen):

        if self.target is None:
           
            self.wander_randomly(world)
        elif self.status == "hunting":
            self.hunting_movement()
        else:
           

            if not self.path:
               
                self.set_path(world)
                return

            if self.path:
                
                self.follow_path(screen, world.tile_size)
       
    def draw(self, screen, tile_size):
        pygame.draw.circle(
            screen,
            (255, 255, 255),
            (
                self.x * tile_size + tile_size // 2,
                self.y * tile_size + tile_size // 2,
            ),
            5,
        )

        font = pygame.font.Font(None, 16)
        text = font.render(self.status, True, (255, 255, 255))
        screen.blit(
            text,
            (self.x * tile_size, self.y * tile_size - 10),
        )    
        
        