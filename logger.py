import matplotlib.pyplot as plt
import pandas as pd


class Logger:
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
        self.prey_energy = 0
        self.prey_energy_regen = 0
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
        self.predator_energy = 0
        self.predator_energy_regen = 0
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
        
        self.creature_list = None

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
            "prey_iq  ": [],
            "prey_iq  ": [],
            "prey_size  ": [],
            "prey_size  ": [],
            "prey_energy  ": [],
            "prey_energy  ": [],
            "prey_energy_regen  ": [],
            "prey_energy_regen  ": [],
            "prey_perceptive_radius  ": [],
            "prey_perceptive_radius  ": [],
            "prey_hunger_threshold  ": [],
            "prey_hunger_threshold  ": [],
            "prey_thirst_threshold  ": [],
            "prey_thirst_threshold  ": [],
            "prey_speed  ": [],
            "prey_speed  ": [],
            "prey_hunger_rate  ": [],
            "prey_hunger_rate  ": [],
            "prey_thirst_rate  ": [],
            "prey_thirst_rate  ": [],
            "prey_max_hunger  ": [],
            "prey_max_hunger  ": [],
            "prey_max_thirst  ": [],
            "prey_max_thirst  ": [],
            "prey_fertility  ": [],
            "prey_fertility  ": [],
            "prey_reproductive_interval  ": [],
            "prey_reproductive_interval  ": [],
            # predator genes
            "predator_iq  ": [],
            "predator_iq  ": [],
            "predator_size  ": [],
            "predator_size  ": [],
            "predator_energy  ": [],
            "predator_energy  ": [],
            "predator_energy_regen  ": [],
            "predator_energy_regen  ": [],
            "predator_perceptive_radius  ": [],
            "predator_perceptive_radius  ": [],
            "predator_hunger_threshold  ": [],
            "predator_hunger_threshold  ": [],
            "predator_thirst_threshold  ": [],
            "predator_thirst_threshold  ": [],
            "predator_speed  ": [],
            "predator_speed  ": [],
            "predator_hunger_rate  ": [],
            "predator_hunger_rate  ": [],
            "predator_thirst_rate  ": [],
            "predator_thirst_rate  ": [],
            "predator_max_hunger  ": [],
            "predator_max_hunger  ": [],
            "predator_max_thirst  ": [],
            "predator_max_thirst  ": [],
            "predator_fertility  ": [],
            "predator_fertility  ": [],
            "predator_reproductive_interval  ": [],
            "predator_reproductive_interval  ": [],
        }



    def build_data_fram(self):
        df = pd.DataFrame(self.total_dataframe)
        return df

    def build_creature_frame(self):
        df = pd.DataFrame(self.creature_lis)