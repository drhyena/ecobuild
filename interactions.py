# c is the creature which calls the functions.


class InteractionSystem:
    def __init__(self, world):
        self.world = world

    
    def is_on_target(self,c):
        return (c.x, c.y) == c.targeting.target


    
    def veg_is_being_targeted(self, c):
        if c.targeting.target_veg is None:
            return False
        veg = c.targeting.target_veg
        for tile in veg.tiles_within_max_perceivable_radius:     
            other = self.world.position_dict[tile]
            if other is not None:
                if other == c:
                    continue
                if other.targeting.target_veg is not None and other.targeting.target_veg == c.targeting.target_veg:
                    return True

        return False

    
    
    def kill_veg(self, veg):
        if veg in self.world.veg_list:
            veg.alive = False
            c = veg.claimed_by
            c.targeting.target_veg = None 
            veg.claimed_by = None
            self.world.veg_list.remove(veg)
            self.world.remove_v_position_from_dict(veg)
    
    def kill_creature(self,creature):
        if creature in self.world.creature_list:
            creature.vitals.alive = False
            creature.log.log_creature(creature)

            self.world.creature_list.remove(creature)
            self.world.remove_c_position_from_dict(creature)
       

    def notify_prey(self,predator,prey):
            prey.get_predator(predator)
        
        
    def is_on_target_creature(self,prey,predator):
        if (prey.x,prey.y) == (predator.x,predator.y):
            return True