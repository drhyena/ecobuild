from CreatureData import Genome

# Sample starting genomes, loosely modelled on a herbivore (deer/antelope-like) and a
# pack carnivore (wolf-like). They are factory functions, not shared instances, so every
# creature gets its own Genome object (a shared dataclass instance would be mutated by all).
# Numbers are in the sim's own units; tune them against your grid size and dt.


def prey_genome():
    return Genome(
        type="prey",
        iq=0.4,
        perceptive_radius=12,       # wide-set eyes, constant scanning for danger
        speed=24,
        hunger_threshold=20,        # grazes only when fairly hungry
        thirst_threshold=30,
        hunger_rate=1.5,
        thirst_rate=2.0,
        max_hunger=100,
        max_thirst=100,
        fertility=1,                # r-strategy: more offspring, breeds more often
        reproductive_interval=3,
        generation=0,
    )


def predator_genome():
    return Genome(
        type="predator",
        iq=0.7,                     # hunting needs planning and cooperation
        perceptive_radius=15,
        speed=32,                   # faster than prey, but only ~1.3x (real predators rarely
                                    # outrun prey by much over distance)
        hunger_threshold=50,        # starts hunting early; a hunt can take a while to succeed
        thirst_threshold=30,
        hunger_rate= 1.2,            # lower energy burn per unit of food than a small herbivore
        thirst_rate=1.5,
        max_hunger=100,
        max_thirst=100,
        fertility=1,                # K-strategy: few offspring, long gap between litters
        reproductive_interval=5,
        generation=0,
    )