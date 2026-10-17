import matplotlib.pyplot as plt
import pandas as pd


class Logger:
    # genes read off each creature's genome (these are also the gene columns in creature_frame)
    GENES = ["iq", "size", "perceptive_radius", "hunger_threshold", "thirst_threshold",
             "speed", "hunger_rate", "thirst_rate", "max_hunger", "max_thirst",
             "fertility", "reproductive_interval"]

    def __init__(self):
        # time and counts
        self.time = 0
        self.creature_count = 0
        self.predator_count = 0
        self.prey_count = 0
        self.vegetation_count = 0
 
        # running totals
        self.births = 0
        self.deaths_starved = 0
        self.deaths_thirst = 0
        self.deaths_eaten = 0
        self.predators_mated = 0
        self.prey_mated = 0
        self.veg_ate = 0
        self.creatures_ate = 0
        self.times_drank = 0
        self.hunts_started = 0
        self.mutations_buff = 0
        self.mutations_nerf = 0
 
        # vitals per species
        self.prey_avg_hunger = 0
        self.prey_avg_thirst = 0
        self.prey_avg_age = 0
        self.predator_avg_hunger = 0
        self.predator_avg_thirst = 0
        self.predator_avg_age = 0
 
        # generations
        self.avg_generation = 0
        self.max_generation = 0
 
        # creatures in each status
        self.status_hungry = 0
        self.status_thirsty = 0
        self.status_wandering = 0
        self.status_hunting = 0
        self.status_fleeing = 0
        self.status_dispersing = 0
        self.status_retreating = 0
        self.status_migrating = 0
        self.status_mating = 0
 
        # prey genes
        self.prey_iq = 0
        self.prey_size = 0
        self.prey_perceptive_radius = 0
        self.prey_hunger_threshold = 0
        self.prey_thirst_threshold = 0
        self.prey_speed = 0
        self.prey_hunger_rate = 0
        self.prey_thirst_rate = 0
        self.prey_max_hunger = 0
        self.prey_max_thirst = 0
        self.prey_fertility = 0
        self.prey_reproductive_interval = 0
 
        # predator genes
        self.predator_iq = 0
        self.predator_size = 0
        self.predator_perceptive_radius = 0
        self.predator_hunger_threshold = 0
        self.predator_thirst_threshold = 0
        self.predator_speed = 0
        self.predator_hunger_rate = 0
        self.predator_thirst_rate = 0
        self.predator_max_hunger = 0
        self.predator_max_thirst = 0
        self.predator_fertility = 0
        self.predator_reproductive_interval = 0


        #shows the state of the ENTIRE SIM every 5 seconds.
        self.total_dataframe = {
            # time and counts
            "time": [],
            "creature_count": [],
            "predator_count": [],
            "prey_count": [],
            "vegetation_count": [],
            # running totals
            "births": [],
            "deaths_starved": [],
            "deaths_thirst": [],
            "deaths_eaten": [],
            "predators_mated": [],
            "prey_mated": [],
            "veg_ate": [],
            "creatures_ate": [],
            "times_drank": [],
            "hunts_started": [],
            "mutations_buff": [],
            "mutations_nerf": [],
            # vitals per species
            "prey_avg_hunger": [],
            "prey_avg_thirst": [],
            "prey_avg_age": [],
            "predator_avg_hunger": [],
            "predator_avg_thirst": [],
            "predator_avg_age": [],
            # generations
            "avg_generation": [],
            "max_generation": [],
            # creatures in each status
            "status_hungry": [],
            "status_thirsty": [],
            "status_wandering": [],
            "status_hunting": [],
            "status_fleeing": [],
            "status_dispersing": [],
            "status_retreating": [],
            "status_migrating": [],
            "status_mating": [],
            # prey genes
            "prey_iq": [],
            "prey_size": [],
            "prey_perceptive_radius": [],
            "prey_hunger_threshold": [],
            "prey_thirst_threshold": [],
            "prey_speed": [],
            "prey_hunger_rate": [],
            "prey_thirst_rate": [],
            "prey_max_hunger": [],
            "prey_max_thirst": [],
            "prey_fertility": [],
            "prey_reproductive_interval": [],
            # predator genes
            "predator_iq": [],
            "predator_size": [],
            "predator_perceptive_radius": [],
            "predator_hunger_threshold": [],
            "predator_thirst_threshold": [],
            "predator_speed": [],
            "predator_hunger_rate": [],
            "predator_thirst_rate": [],
            "predator_max_hunger": [],
            "predator_max_thirst": [],
            "predator_fertility": [],
            "predator_reproductive_interval": [],
        }
 
        # one row per creature that ever lived
        self.creature_frame = {
            # identity and lineage
            "creature_id": [],
            "species": [],
            "generation": [],
            "parent_a_id": [],
            "parent_b_id": [],
            # life events
            "birth_time": [],
            "death_time": [],
            "cause_of_death": [],
            # lifetime counters
            "times_ate": [],
            "times_drank": [],
            "creatures_killed": [],
            "children_count": [],
            # genes
            "iq": [],
            "size": [],
            "perceptive_radius": [],
            "hunger_threshold": [],
            "thirst_threshold": [],
            "speed": [],
            "hunger_rate": [],
            "thirst_rate": [],
            "max_hunger": [],
            "max_thirst": [],
            "fertility": [],
            "reproductive_interval": [],
        }



    def build_data_fram(self):
        df = pd.DataFrame(self.total_dataframe)
        return df

    def build_creature_frame(self):
        df = pd.DataFrame(self.creature_lis)

    def get_creature_data(self):
        pass

    def log_creature(self, c):
        """Fills in creature_frame. Call it once when a creature is born to add its row, and once
        more when it dies with a cause_of_death ("starved", "thirst" or "eaten") to finish the row.
        parents are the two parents' creature_ids (None for the creatures the sim starts with)."""
        frame = self.creature_frame
        ids = frame["creature_id"]

        # first time we see this creature: add its row
        if c.logging.id not in ids:

            frame["creature_id"].append(c.genome.id)
            frame["species"].append(c.genome.type)
            frame["generation"].append(c.genome.generation)
            frame["parent_a_id"].append(c.logging.parents[0])
            frame["parent_b_id"].append(c.logging.parents[1])
            frame["birth_time"].append(c.logging.birth_time)
            frame["death_time"].append(None)
            frame["cause_of_death"].append(None)
            for key in ("times_ate", "times_drank", "creatures_killed", "children_count"):
                frame[key].append(0)
            for gene in self.GENES:
                frame[gene].append(getattr(c.genome, gene))  # genes never change after birth

        # refresh the counters, and close the row if the creature just died
        row = ids.index(c.creature_id)
        frame["times_ate"][row] = c.logging.times_ate
        frame["times_drank"][row] = c.logging.times_drank
        frame["creatures_killed"][row] = c.logging.creatures_killed
        frame["children_count"][row] = len(c.reproduction.children)
        if c.logging.cause_of_death is not None:
            frame["death_time"][row] = c.logging.death_time
            frame["cause_of_death"][row] = c.logging.cause_of_death

    def log_total_dataframe(self, world):
        """Takes one sample of the whole sim and adds a row to total_dataframe. Call it every 5 s
        of sim time. Counts, ages, generations, deaths and genes are worked out from creature_frame.
        Hunger, thirst and statuses aren't stored there, so they are read off the living creatures.
        A species with nobody alive logs empty (NaN) averages instead of 0."""
        frame = self.creature_frame
        now = world.sim_time

        def mean(values):
            values = list(values)
            return sum(values) / len(values) if values else None

        alive = [i for i, t in enumerate(frame["death_time"]) if t is None]
        prey = [i for i in alive if frame["species"][i] == "prey"]
        predators = [i for i in alive if frame["species"][i] == "predator"]

        # from creature_frame
        self.time = now
        self.creature_count = len(alive)
        self.prey_count = len(prey)
        self.predator_count = len(predators)

        self.births = sum(1 for p in frame["parent_a_id"] if p is not None)  # starting creatures have no parents
        self.deaths_starved = frame["cause_of_death"].count("starved")
        self.deaths_thirst = frame["cause_of_death"].count("thirst")
        self.deaths_eaten = frame["cause_of_death"].count("eaten")

        self.prey_avg_age = mean(now - frame["birth_time"][i] for i in prey)
        self.predator_avg_age = mean(now - frame["birth_time"][i] for i in predators)
        self.avg_generation = mean(frame["generation"][i] for i in alive)
        self.max_generation = max((frame["generation"][i] for i in alive), default=None)

        for gene in self.GENES:
            setattr(self, f"prey_{gene}", mean(frame[gene][i] for i in prey))
            setattr(self, f"predator_{gene}", mean(frame[gene][i] for i in predators))

        # from the living creatures (not stored in creature_frame)
        live = [c for c in world.creature_list if c.alive]
        prey_live = [c for c in live if c.species == "prey"]
        predator_live = [c for c in live if c.species == "predator"]

        self.prey_avg_hunger = mean(c.vitals.hunger for c in prey_live)
        self.prey_avg_thirst = mean(c.vitals.thirst for c in prey_live)
        self.predator_avg_hunger = mean(c.vitals.hunger for c in predator_live)
        self.predator_avg_thirst = mean(c.vitals.thirst for c in predator_live)

        for status in ("hungry", "thirsty", "wandering", "hunting", "fleeing",
                       "dispersing", "retreating", "migrating", "mating"):
            setattr(self, f"status_{status}", sum(1 for c in live if c.status == status))

        # add this sample to the history. the running totals that aren't worked out above
        # (veg_ate, creatures_ate, times_drank, hunts_started, mutations_*, *_mated,
        # vegetation_count) are whatever the rest of the sim last set on the logger
        for key in self.total_dataframe:
            self.total_dataframe[key].append(getattr(self, key))