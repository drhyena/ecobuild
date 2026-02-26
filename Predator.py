from creature import *

class Predator(Creature):
    def __init__(self, x, y, interaction_manager):
        super().__init__(x, y, interaction_manager)
        self.target_creature = None
        self.iq = 0.7

    # PREDATOR SPECIFIC UPDATE MODIFICATIONS.
    def handle_hunger(self, interactionmanager, creature_list):
        if self.target_creature and self.target.alive:
            if self.target.claimed_by is None:
                self.target.targetted_by = self
                self.eat_prey()
                interactionmanager.kill_creature(self.target_creature,creature_list)
    
    def eat_prey(self):
        if self.status == "hungry":
            self.hunger = 100
            self.target.alive = False
            
    
    def handle_hungry_state(self, world, interactionmanager, creature_list):

        if self.target_creature:
            return

        self.update_perceived_tiles(world)

        self.target_creature = world.find_closest_prey(self,creature_list)
        

        if self.target_creature is None:
            self.target = None
            return

        if not interactionmanager.veg_is_being_targeted(
            self, creature_list
        ):
            self.target = (
                self.target_veg.v_x,
                self.target_veg.v_y,
            )
    
    
    
    def find_creature(self, creature_list, world):
        self.target_creature = world.findcreaturetarget(
            self, creature_list
        )

    def follow_prey(self):
        if self.target_creature:
            pass