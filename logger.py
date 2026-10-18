import matplotlib.pyplot as plt
import pandas as pd


class Logger:
    # genes read off each creature's genome (these are also the gene columns in creature_frame)
    # NOTE: "size" is not a field on Genome yet; it logs as None until you add it.
    GENES = ["iq", "size", "perceptive_radius", "hunger_threshold", "thirst_threshold",
             "speed", "hunger_rate", "thirst_rate", "max_hunger", "max_thirst",
             "fertility", "reproductive_interval"]

    # the sim writes "hunger" and "hunted"; the logger's columns use "starved" and "eaten"
    CAUSE_ALIASES = {"hunger": "starved", "hunted": "eaten"}

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

        # shows the state of the ENTIRE SIM every 5 seconds.
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

        # creature_id -> row number, so lookups are O(1) instead of list.index()
        self._row_of = {}

    def build_data_frame(self):
        return pd.DataFrame(self.total_dataframe)

    build_data_fram = build_data_frame  # keep the old (misspelled) name working

    def build_creature_frame(self):
        return pd.DataFrame(self.creature_frame)

    def get_creature_data(self):
        pass

    @staticmethod
    def _parent_ids(parents):
        """Return (parent_a_id, parent_b_id). Accepts a set, list or tuple of creatures or ids.
        An empty collection (starting creatures) gives (None, None). A set has no order, so for
        sets the pair is sorted to keep the result stable."""
        if not parents:
            return None, None
        ids = [getattr(p, "genome", p) for p in parents]
        ids = [getattr(g, "id", g) for g in ids]
        if isinstance(parents, (set, frozenset)):
            ids = sorted(ids, key=lambda i: (i is None, i))
        a = ids[0] if len(ids) > 0 else None
        b = ids[1] if len(ids) > 1 else None
        return a, b

    def log_creature(self, c):
        """Fills in creature_frame. Call it once when a creature is born to add its row, and once
        more when it dies with a cause_of_death ("starved", "thirst" or "eaten") to finish the row.
        parents are the two parents' creature_ids (None for the creatures the sim starts with)."""
        frame = self.creature_frame
        cid = c.genome.id

        # first time we see this creature: add its row
        if cid not in self._row_of:
            parent_a, parent_b = self._parent_ids(c.logging.parents)

            self._row_of[cid] = len(frame["creature_id"])
            frame["creature_id"].append(cid)
            frame["species"].append(c.genome.type)
            frame["generation"].append(c.genome.generation)
            frame["parent_a_id"].append(parent_a)
            frame["parent_b_id"].append(parent_b)
            frame["birth_time"].append(c.logging.birth_time)
            frame["death_time"].append(None)
            frame["cause_of_death"].append(None)
            for key in ("times_ate", "times_drank", "creatures_killed", "children_count"):
                frame[key].append(0)
            for gene in self.GENES:
                frame[gene].append(getattr(c.genome, gene, None))  # genes never change after birth

        # refresh the counters, and close the row if the creature just died
        row = self._row_of[cid]
        frame["times_ate"][row] = c.logging.times_ate
        frame["times_drank"][row] = c.logging.times_drank
        frame["creatures_killed"][row] = c.logging.creatures_killed
        frame["children_count"][row] = len(c.reproduction.children)

        cause = c.logging.cause_of_death
        if cause:  # "" / None both mean "still alive"
            frame["death_time"][row] = c.logging.death_time
            frame["cause_of_death"][row] = self.CAUSE_ALIASES.get(cause, cause)

    def log_total_dataframe(self, world):
        """Takes one sample of the whole sim and adds a row to total_dataframe. Call it every 5 s
        of sim time. Counts, ages, generations, deaths and genes are worked out from creature_frame.
        Hunger, thirst and statuses aren't stored there, so they are read off the living creatures.
        A species with nobody alive logs empty (NaN) averages instead of 0."""
        frame = self.creature_frame
        now = world.sim_time

        def mean(values):
            values = [v for v in values if v is not None]  # skip missing genes (e.g. iq=None)
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
        prey_live = [c for c in live if c.genome.type == "prey"]
        predator_live = [c for c in live if c.genome.type == "predator"]

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

    def plot_population(self, log_scale=False, save_path=None, show=True):
        """Plot prey, predator and total population against sim time.

        Reads the samples that Logger.log_total_dataframe() has collected.
        log_scale=True helps when prey vastly outnumber predators.
        save_path: if given, the figure is saved there (e.g. "population.png").
        """
        df = self.build_data_frame()
        if df.empty:
            print("No samples logged yet - call logger.log_total_dataframe(world) first.")
            return None

        fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True,
                                      gridspec_kw={"height_ratios": [3, 2]})
        ax.plot(df["time"], df["creature_count"], label="Total", color="black", linewidth=2)
        ax.plot(df["time"], df["prey_count"], label="Prey", color="tab:green")
        ax.plot(df["time"], df["predator_count"], label="Predators", color="tab:red")

        if log_scale:
            ax.set_yscale("log")
        ax.set_ylabel("Population" + (" (log scale)" if log_scale else ""))
        ax.set_title("Population over time")
        ax.grid(True, alpha=0.3)
        ax.legend()

        # deaths in each sample interval (the death columns are running totals, so take the
        # difference between samples). A prey crash shows up here even when samples are sparse.
        cols = ["deaths_starved", "deaths_thirst", "deaths_eaten"]
        per_interval = df[cols].diff().fillna(df[cols])
        ax2.stackplot(df["time"], [per_interval[c] for c in cols],
                      labels=["Starved", "Thirst", "Eaten"],
                      colors=["tab:orange", "tab:blue", "tab:red"], alpha=0.8)
        ax2.set_xlabel("Sim time (s)")
        ax2.set_ylabel("Deaths per sample")
        ax2.set_title("Deaths per sample interval, by cause")
        ax2.grid(True, alpha=0.3)
        ax2.legend(loc="upper left")
        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=150)
        if show:
            plt.show()
        return fig

    def plot_avg_speed(self, save_path=None, show=True):
        """Plot the average speed of living prey and predators against sim time.

        Uses the prey_speed / predator_speed columns that log_total_dataframe() fills in.
        A species with nobody alive at a sample has no average, so its line has a gap there.
        """
        df = self.build_data_frame()
        if df.empty:
            print("No samples logged yet - call logger.log_total_dataframe(world) first.")
            return None

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df["time"], df["prey_speed"], label="Prey", color="tab:green")
        ax.plot(df["time"], df["predator_speed"], label="Predators", color="tab:red")

        ax.set_xlabel("Sim time (s)")
        ax.set_ylabel("Average speed")
        ax.set_title("Average speed over time")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=150)
        if show:
            plt.show()
        return fig