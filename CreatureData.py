from dataclasses import dataclass

@dataclass
class Vitals:
    hunger : float = 100
    thirst : float = 100
    
    def decay(self, hunger_rate=1, thirst_rate=2):
        self.hunger -= hunger_rate
        self.thirst -= thirst_rate
    
    
    
@dataclass
class Genome:
    pass