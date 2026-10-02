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
         c.targeting.target = test_path1[len(test_path1)-1]
         c.reproduction.possible_mate.targeting.target = test_path2[len(test_path2)-1]
         c.targeting.path = test_path1
         c.reproduction.possible_mate.targeting.target_path = test_path2

         