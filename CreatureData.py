from dataclasses import dataclass, field


@dataclass
class Vitals:
    hunger: float = 100
    thirst: float = 100
    age: float = 0


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
    stalk_target: object = None  # prey being shadowed (never alerted)


@dataclass
class Reproduction:
    seeking_mate: bool = False
    ready_to_mate: bool = False
    time_since_last_mating: int = 0
    current_mate: object = None


@dataclass
class Migration:
    direction: tuple = None          # current compass heading (dx, dy)
    last_redirect_time: float = 0    # sim_time of the last heading change
    last_resource_time: float = 0    # sim_time food/water was last found, eaten or drunk


@dataclass
class Genome:
    iq: float = None
    perceptive_radius: list = 10
    hunger_threshold: float = 20
    thirst_threshold: float = 30
    speed: float = 10
    hunger_rate: int = 1
    thirst_rate: int = 2
    max_hunger: float = 100
    max_thirst: float = 100
    fertility: int = 1  # no. of offspring per mating
    reproductive_interval: int = 10  # time before a creature is ready to mate again
    type: str = "creature"