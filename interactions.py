
# c is the creature which calls the functions.


class InteractionSystem:
    def __init__(self, world):
        self.world = world

    
    def is_on_target(c):
        return (c.x, c.y) == c.target

   
    def check_for_creatures_in_perspective_tiles(c1, creature_list):
        perceived_creatures = []
        for c in creature_list:
            if c is not c1 and (c.x, c.y) in c1.perceived_tiles:
                perceived_creatures.append(c)
        return perceived_creatures


    def veg_is_being_targeted(c, perceived_creatures):
        if c.target is None:
            return False

        for other in perceived_creatures:
            if other.target == c.target and other is not c:
                return True
        return False
    
    def kill_veg(c,v):
        
    

    
    

             
             
             