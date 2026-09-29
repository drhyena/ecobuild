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
         pass
              
              
              
         
         