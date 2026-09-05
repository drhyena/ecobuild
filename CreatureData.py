from dataclasses import dataclass, field

@dataclass
class Vitals:
    hunger: float = 100
    thirst: float = 100

    def decay(self, hunger_rate=1, thirst_rate=2):
        self.hunger -= hunger_rate
        self.thirst -= thirst_rate


@dataclass
class Targeting:
    target: tuple = None
    path: list = field(default_factory=list)
    perceived_tiles: list = field(default_factory=list)
    target_veg: object = None
    target_creature: object = None
    targeted_by: object = None
    pixel_target: tuple = None
    


@dataclass
class Reproduction:
    reproductive_interval: int = 10000
    seeking_mate: bool = False
    ready_to_mate: bool = False
    time_since_last_mating: int = 0


@dataclass
class Genome:
    iq: float = None
    perceptive_radius: list = field(default_factory=list)
    hunger_threshold: float = 20
    thirst_threshold: float = 30
    speed: float = 10