
# c is the creature which calls the functions.


class InteractionSystem:
    def __init__(self, world):
        self.world = world

    
    def is_on_target(self,c):
        return (c.x, c.y) == c.target

   
    def check_for_creatures_in_perspective_tiles(c1, creature_list):
        perceived_creatures = []
        for c in creature_list:
            if c is not c1 and (c.x, c.y) in c1.perceived_tiles:
                perceived_creatures.append(c)
        return perceived_creatures


    def veg_is_being_targeted(self,c,creature_list):
        perceived_creatures = self.check_for_creatures_in_perspective_tiles(c,creature_list)
        for other in perceived_creatures:
            if other.target_veg.v_x == c.target_veg.v_x and other.target_veg.v_y == c.target_veg.v_y :
                return True
        return False

    
    
    def kill_veg(self,veg,veg_List):
        veg_List.remove(veg)
    
    def kill_creature(self,creature,creature_list):
        creature_list.remove(creature)

    
   
        
    

    
    

             
             
             