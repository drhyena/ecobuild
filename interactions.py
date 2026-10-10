# c is the creature which calls the functions.


class InteractionSystem:
    def __init__(self, world):
        self.world = world

    
    def is_on_target(self,c):
        return (c.x, c.y) == c.targeting.target

   
    def check_for_creatures_in_perspective_tiles(self,c1):
        perceived_creatures = []
        for c in self.world.creature_list:
            if c is not c1 and (c.x, c.y) in c1.targeting.perceived_tiles:
                perceived_creatures.append(c)
        return perceived_creatures
    
    def if_any_creature_in_perspective_tiles(self,c1,c2):
        if (c2.x,c2.y) in c1.targeting.perceived_tiles:
            return True

    def create_new_creature(self,c):
        pass        
    
    def veg_is_being_targeted(self, c):
        if c.targeting.target_veg is None:
            return False

        for other in self.world.creature_list:
            if other == c:
                continue

            if other.targeting.target_veg is not None and other.targeting.target_veg == c.targeting.target_veg:
                return True

        return False

    
    
    def kill_veg(self, veg):
        if veg in self.world.veg_list:
            veg.alive = False
            veg.claimed_by = None
            self.world.veg_list.remove(veg)

        for creature in self.world.creature_list:
            if creature.targeting.target_veg == veg:
                creature.targeting.target_veg = None
    
    def kill_creature(self,creature):
        if creature in self.world.creature_list:
            self.world.creature_list.remove(creature)
       

    def notify_prey(self,predator,prey):
            prey.get_predator(predator)
        
        
    def is_on_target_creature(self,prey,predator):
        if (prey.x,prey.y) == (predator.x,predator.y):
            return True