from dataclasses import dataclass, field




@dataclass
class Genome:
    iq: float = None
    perceptive_radius: int = 10
    hunger_threshold: float = 20
    thirst_threshold: float = 30
    speed: float = 10
    hunger_rate: int = 1
    thirst_rate: int = 2
    max_energy: float = 100
    energy_drain_rate : float = 2
    energy_regen_rate : float = 10
    max_hunger: float = 100
    max_thirst: float = 100
    fertility: int = 1  # no. of offspring per mating
    reproductive_interval: float = 5  # time before a creature is ready to mate again
    type: str = "creature"
    generation : int = 0
    id: int = None 

@dataclass
class Vitals:
    hunger: float = 100
    thirst: float = 100
    age: float = 0
    energy:float = Genome.max_energy
    alive : bool = True


@dataclass
class Targeting:
    target: tuple = None
    path: list = field(default_factory=list)
    perceived_tiles: list = field(default_factory=list)
    target_veg: object = None
    target_creature: object = None
    targeted_by: object = None
    pixel_target: tuple = None
    mating_point: tuple = None
    alarm_source: object = None  # predator that started hunting nearby (None = no alarm)
    alarm_until: float = 0  # sim_time the alarm runs out
    retreat_point: tuple = None  # shared point some prey flee to (None = just disperse)
    retreat_time: float = 0  # sim_time those prey stop dispersing and head for the point


@dataclass
class Reproduction:
    seeking_mate: bool = False
    ready_to_mate: bool = False
    time_since_last_mating: int = 0
    current_mate: object = None
    paired_at: float = 0  # sim_time the current pairing started (for the mating timeout)
    rejected: dict = field(default_factory=dict)  # creature -> sim_time until which we won't pair with it again
    children :set =  field(default_factory=set)


@dataclass
class Logging:
    birth_time : float = 0
    death_time: float = 0
    creatures_killed : int = 0
    times_ate : int= 0
    times_drank : int =0

    times_hunted: int =0
    times_hunted_succesfully: int = 0
    failed_hunts : int = 0

    cause_of_death : str = ""

    parents :list = field(default_factory=list)


    @property
    def times_hunt_failed(self):
        return self.times_hunted - self.times_hunted_succesfully