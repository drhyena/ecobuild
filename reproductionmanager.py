from Predator import Predator
from Prey import Prey

class ReproductionManager:
    def check_if_mature(c):
         return c.vitals.age>10


    def check_if_ready_to_reproduce(self,c):
         if self.check_if_mature(c) and c.hunger>80 and c.thirst>80 and c.reproduction.possible_mate:
              return True

    def check_if_ready_to_seek_mate(self,c):
         if self.check_if_mature(c) and c.genome.reproductive_interval < c.reproduction.last_time_since_mating:
              return True
              
              

    def check_for_viable_mate(self,c):
         c.reproduction.possible_mate = c.world.find_closest_mate()
                            

    def set_midpoint(self,c,test_path1,test_path2):
         c.targeting.target = test_path1[0]
         c.reproduction.possible_mate.targeting.target = test_path2[0]
         c.targeting.path = test_path1
         c.reproduction.possible_mate.targeting.target_path = test_path2

    def check_if_creatures_are_at_mating_point(self,c):
         mate = c.reproduction.possible_mate
         if c.targeting.target == (c.x,c.y) and mate.targeting.target == (mate.x,mate.y):
              return True

     
     
     
     def mate(c):
         if c.genome.type in ["prey","creature"]:
              c.world.creature_list.append(Prey())
              
         