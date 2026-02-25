
# c is the creature which calls the functions.


class InteractionSystem:
    def __init__(self, world):
        self.world = world

    
    def is_on_target(self,c):
        return (c.x, c.y) == c.target

   
    def check_for_creatures_in_perspective_tiles(self,c1, creature_list):
        perceived_creatures = []
        for c in creature_list:
            if c is not c1 and (c.x, c.y) in c1.perceived_tiles:
                perceived_creatures.append(c)
        return perceived_creatures
    
    

    
    def send_best_tile_signal(self,predator,best_tile):
        predator.predator_receive_signal("target_tile","prey",best_tile)
        

        
        

            



    def veg_is_being_targeted(self, c, creature_list):
        if c.target_veg is None:
            return False

        for other in creature_list:
            if other == c:
                continue

            if other.target_veg is not None and other.target_veg == c.target_veg:
                return True

        return False

    
    
    def kill_veg(self, veg, veg_list, creature_list):
        if veg in veg_list:
            veg_list.remove(veg)

        # Remove from any creature targeting it
        for creature in creature_list:
            if creature.target_veg == veg:
                creature.target_veg = None
                
    
    def kill_creature(self,creature,creature_list):
        creature_list.remove(creature)
 


    
   
        
    

    
    

             
             
             