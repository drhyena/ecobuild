from dataclasses import dataclass, field

@dataclass
class Vitals:
    hunger: float = 100
    thirst: float = 100
    age : float = 0




@dataclass
class Targeting:
    target: tuple = None
    path: list = field(default_factory=list)
    perceived_tiles: set = field(default_factory=list)
    target_veg: object = None
    target_creature: object = None
    targeted_by: object = None
    pixel_target: tuple = None
    


@dataclass
class Reproduction:
    seeking_mate: bool = False
    ready_to_mate: bool = False
    time_since_last_mating: int = 0
    current_mate = object = None


@dataclass
class Genome:
    iq: float = None
    perceptive_radius: list = field(default_factory=list)
    hunger_threshold: float = 20
    thirst_threshold: float = 30
    speed: float = 10
    hunger_rate : int = 1
    thirst_rate : int = 2    
    max_hunger: float = 100
    max_thirst: float = 100
    fertility: int = 1 #no:of offspring per mating
    reproductive_interval: int = 10 # time it takes for a creature to be ready_to_mate again.

