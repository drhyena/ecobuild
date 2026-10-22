import math
import os

import matplotlib.pyplot as plt
import numpy as np
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
        live = [c for c in world.creature_list if c.vitals.alive]
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

    # ------------------------------------------------------------------
    # charts and summary
    # ------------------------------------------------------------------
    # plot_all_stats() builds all of these in one go. Each one can also be called on its own:
    # every plot_* method takes save_path / show, and returns the figure (None if no data yet).

    SPECIES_COLOURS = {"prey": "tab:green", "predator": "tab:red"}
    CAUSES = ["starved", "thirst", "eaten"]
    CAUSE_COLOURS = {"starved": "tab:orange", "thirst": "tab:blue", "eaten": "tab:red"}
    STATUSES = ["wandering", "hungry", "thirsty", "hunting", "fleeing", "dispersing",
                "retreating", "migrating", "mating"]
    STATUS_COLOURS = {"wandering": "#9aa5b1", "hungry": "tab:orange", "thirsty": "tab:blue",
                      "hunting": "tab:red", "fleeing": "tab:purple", "dispersing": "tab:olive",
                      "retreating": "tab:brown", "migrating": "tab:cyan", "mating": "tab:pink"}

    def _finish(self, fig, save_path, show):
        fig.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=150)
        if show:
            plt.show()
        return fig

    def _samples(self):
        """The 5-second samples as a DataFrame with every column numeric (None -> NaN).
        Returns None when nothing has been logged yet."""
        df = self.build_data_frame()
        if df.empty:
            print("No samples logged yet - call logger.log_total_dataframe(world) first.")
            return None
        return df.apply(pd.to_numeric, errors="coerce")

    def _creatures(self):
        """creature_frame as a DataFrame with numeric columns, plus 'lifespan' (NaN while alive)
        and 'born' (False for the creatures the sim started with). None if nobody is logged."""
        df = self.build_creature_frame()
        if df.empty:
            print("No creatures logged yet.")
            return None
        numeric = ["birth_time", "death_time", "generation", "times_ate", "times_drank",
                   "creatures_killed", "children_count"] + self.GENES
        for col in numeric:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df["lifespan"] = df["death_time"] - df["birth_time"]
        df["born"] = df["parent_a_id"].notna()
        return df

    @staticmethod
    def _label(name):
        return name.replace("_", " ").capitalize()

    def plot_genes(self, save_path=None, show=True):
        """One small chart per gene: the average value among living prey and predators over time.
        This is where evolution shows up (e.g. speed creeping upwards)."""
        df = self._samples()
        if df is None:
            return None

        genes = [g for g in self.GENES
                 if df[f"prey_{g}"].notna().any() or df[f"predator_{g}"].notna().any()]
        if not genes:
            return None
        cols = 3
        rows = math.ceil(len(genes) / cols)
        fig, axes = plt.subplots(rows, cols, figsize=(14, 3.1 * rows), sharex=True, squeeze=False)

        for ax, gene in zip(axes.flat, genes):
            for species, colour in self.SPECIES_COLOURS.items():
                ax.plot(df["time"], df[f"{species}_{gene}"], color=colour,
                        label=species.capitalize())
            ax.set_title(self._label(gene))
            ax.grid(True, alpha=0.3)
        for ax in axes.flat[len(genes):]:
            ax.set_visible(False)
        for ax in axes[-1]:
            ax.set_xlabel("Sim time (s)")
        axes[0][0].legend()
        fig.suptitle("Average gene values of living creatures")
        return self._finish(fig, save_path, show)

    def plot_vitals(self, save_path=None, show=True):
        """Average hunger, thirst and age of living prey and predators over time."""
        df = self._samples()
        if df is None:
            return None

        panels = [("hunger", "Average hunger", (0, 100)),
                  ("thirst", "Average thirst", (0, 100)),
                  ("age", "Average age (s)", None)]
        fig, axes = plt.subplots(len(panels), 1, figsize=(10, 9), sharex=True)
        for ax, (stat, title, limits) in zip(axes, panels):
            for species, colour in self.SPECIES_COLOURS.items():
                ax.plot(df["time"], df[f"{species}_avg_{stat}"], color=colour,
                        label=species.capitalize())
            ax.set_title(title)
            if limits:
                ax.set_ylim(*limits)
            ax.grid(True, alpha=0.3)
        axes[0].legend()
        axes[-1].set_xlabel("Sim time (s)")
        return self._finish(fig, save_path, show)

    def plot_activity(self, save_path=None, show=True):
        """How many creatures are in each status over time (stacked), so you can see what the
        population is spending its time on. Statuses nobody ever had are left out."""
        df = self._samples()
        if df is None:
            return None

        used = [s for s in self.STATUSES if df[f"status_{s}"].fillna(0).sum() > 0]
        if not used:
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.stackplot(df["time"], [df[f"status_{s}"].fillna(0) for s in used],
                     labels=[s.capitalize() for s in used],
                     colors=[self.STATUS_COLOURS[s] for s in used], alpha=0.9)
        ax.set_xlabel("Sim time (s)")
        ax.set_ylabel("Creatures")
        ax.set_title("What creatures are doing (all species)")
        ax.grid(True, alpha=0.3)
        ax.legend(loc="upper left", ncol=2)
        return self._finish(fig, save_path, show)

    def plot_births_deaths(self, save_path=None, show=True):
        """Births per sample interval for each species, and deaths per interval split by cause for
        prey and predators separately. Shows which side is growing and what is holding it back."""
        df = self._samples()
        cf = self._creatures()
        if df is None or cf is None:
            return None

        edges = [0.0] + list(df["time"])  # one bin per sample interval
        x = df["time"]
        fig, axes = plt.subplots(3, 1, figsize=(10, 10), sharex=True)

        ax = axes[0]
        for species, colour in self.SPECIES_COLOURS.items():
            born = cf[(cf["species"] == species) & cf["born"]]["birth_time"].dropna()
            counts, _ = np.histogram(born, bins=edges)
            ax.plot(x, counts, color=colour, label=species.capitalize())
        ax.set_title("Births per sample interval")
        ax.set_ylabel("Births")
        ax.grid(True, alpha=0.3)
        ax.legend()

        for ax, (species, colour) in zip(axes[1:], self.SPECIES_COLOURS.items()):
            dead = cf[(cf["species"] == species) & cf["death_time"].notna()]
            series = []
            for cause in self.CAUSES:
                times = dead[dead["cause_of_death"] == cause]["death_time"]
                series.append(np.histogram(times, bins=edges)[0])
            ax.stackplot(x, series, labels=[c.capitalize() for c in self.CAUSES],
                         colors=[self.CAUSE_COLOURS[c] for c in self.CAUSES], alpha=0.85)
            ax.set_title(f"{species.capitalize()} deaths per sample interval, by cause")
            ax.set_ylabel("Deaths")
            ax.grid(True, alpha=0.3)
            ax.legend(loc="upper left")
        axes[-1].set_xlabel("Sim time (s)")
        return self._finish(fig, save_path, show)

    def plot_generations(self, save_path=None, show=True):
        """Average and highest generation among the living, and the running count of gene
        mutations that were buffs vs nerfs."""
        df = self._samples()
        if df is None:
            return None

        fig, (ax, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
        ax.plot(df["time"], df["avg_generation"], label="Average", color="tab:blue")
        ax.plot(df["time"], df["max_generation"], label="Highest", color="black")
        ax.set_ylabel("Generation")
        ax.set_title("Generations alive")
        ax.grid(True, alpha=0.3)
        ax.legend()

        ax2.plot(df["time"], df["mutations_buff"], label="Buffs", color="tab:green")
        ax2.plot(df["time"], df["mutations_nerf"], label="Nerfs", color="tab:red")
        ax2.set_xlabel("Sim time (s)")
        ax2.set_ylabel("Mutations (running total)")
        ax2.set_title("Mutations")
        ax2.grid(True, alpha=0.3)
        ax2.legend()
        return self._finish(fig, save_path, show)

    def plot_lifespans(self, save_path=None, show=True):
        """Histogram of how long each species lived before dying, stacked by cause of death.
        Only creatures that have died are counted."""
        cf = self._creatures()
        if cf is None:
            return None

        fig, axes = plt.subplots(2, 1, figsize=(10, 8))
        for ax, species in zip(axes, self.SPECIES_COLOURS):
            dead = cf[(cf["species"] == species) & cf["lifespan"].notna()]
            ax.set_title(f"{species.capitalize()} lifespans")
            ax.set_xlabel("Lifespan (s)")
            ax.set_ylabel("Creatures")
            ax.grid(True, alpha=0.3)
            if dead.empty:
                ax.text(0.5, 0.5, "nobody has died yet", ha="center", va="center",
                        transform=ax.transAxes)
                continue
            groups = [dead[dead["cause_of_death"] == c]["lifespan"] for c in self.CAUSES]
            keep = [(g, c) for g, c in zip(groups, self.CAUSES) if len(g)]
            ax.hist([g for g, _ in keep], bins=20, stacked=True,
                    label=[c.capitalize() for _, c in keep],
                    color=[self.CAUSE_COLOURS[c] for _, c in keep], alpha=0.85)
            ax.legend()
        return self._finish(fig, save_path, show)

    def plot_selection(self, genes=("speed", "perceptive_radius", "hunger_threshold",
                                    "thirst_threshold"), save_path=None, show=True):
        """For each species and gene: gene value vs number of children, one dot per creature that
        has died (so unfinished lives don't count as childless), with a straight-line trend.
        An upward line means that gene is being selected for."""
        cf = self._creatures()
        if cf is None:
            return None

        fig, axes = plt.subplots(2, len(genes), figsize=(4 * len(genes), 7), squeeze=False)
        rng = np.random.default_rng(0)  # fixed jitter so the picture doesn't change between calls
        for row, (species, colour) in zip(axes, self.SPECIES_COLOURS.items()):
            sub = cf[(cf["species"] == species) & cf["death_time"].notna()]
            for ax, gene in zip(row, genes):
                ax.set_title(f"{species.capitalize()}: {self._label(gene)}")
                ax.set_xlabel(self._label(gene))
                ax.set_ylabel("Children")
                ax.grid(True, alpha=0.3)
                x, y = sub[gene], sub["children_count"]
                ok = x.notna() & y.notna()
                x, y = x[ok], y[ok]
                if x.empty:
                    ax.text(0.5, 0.5, "no data", ha="center", va="center", transform=ax.transAxes)
                    continue
                ax.scatter(x, y + rng.uniform(-0.15, 0.15, len(y)), s=12, alpha=0.4, color=colour)
                if x.nunique() > 2:
                    slope, intercept = np.polyfit(x, y, 1)
                    xs = np.linspace(x.min(), x.max(), 50)
                    ax.plot(xs, slope * xs + intercept, color="black", linewidth=1.5)
        fig.suptitle("Does a gene pay off? (children vs gene value, creatures that have died)")
        return self._finish(fig, save_path, show)

    def summary(self, print_it=True):
        """Totals for each species, worked out from creature_frame. Returns
        {species: {stat: value}}; prints it as a table too unless print_it=False."""
        cf = self._creatures()
        if cf is None:
            return {}

        out = {}
        for species in self.SPECIES_COLOURS:
            sub = cf[cf["species"] == species]
            if sub.empty:
                continue
            dead = sub[sub["death_time"].notna()]
            alive = sub[sub["death_time"].isna()]
            causes = dead["cause_of_death"].value_counts()
            stats = {
                "ever lived": len(sub),
                "alive now": len(alive),
                "born in the sim": int(sub["born"].sum()),
                "died": len(dead),
                "  starved": int(causes.get("starved", 0)),
                "  thirst": int(causes.get("thirst", 0)),
                "  eaten": int(causes.get("eaten", 0)),
                "avg lifespan (s)": dead["lifespan"].mean() if len(dead) else None,
                "longest life (s)": dead["lifespan"].max() if len(dead) else None,
                "avg meals eaten": sub["times_ate"].mean(),
                "avg drinks": sub["times_drank"].mean(),
                "avg children": sub["children_count"].mean(),
                "highest generation": sub["generation"].max(),
            }
            if species == "predator":
                stats["avg kills"] = sub["creatures_killed"].mean()
            for gene in self.GENES:  # current averages of the living
                if alive[gene].notna().any():
                    stats[f"avg {gene.replace('_', ' ')} (alive)"] = alive[gene].mean()
            out[species] = stats

        if print_it:
            self._print_summary(out)
        return out

    @staticmethod
    def _print_summary(summary):
        def fmt(v):
            if v is None or (isinstance(v, float) and v != v):
                return "-"
            return f"{v:.2f}" if isinstance(v, float) else str(v)

        species = list(summary)
        stats = list(dict.fromkeys(k for s in species for k in summary[s]))
        width = max(len(k) for k in stats) + 2
        print("\n" + "SIM SUMMARY".ljust(width) + "".join(s.capitalize().rjust(12) for s in species))
        print("-" * (width + 12 * len(species)))
        for k in stats:
            print(k.ljust(width) + "".join(fmt(summary[s].get(k)).rjust(12) for s in species))
        print()

    def plot_all_stats(self, save_dir=None, show=True, log_scale=False):
        """Every relevant chart plus the summary table, in one call: population, births and deaths,
        genes, vitals, activity, generations, lifespans and selection.
        save_dir: if given, each chart is saved there as a PNG (the folder is created).
        show: open all the charts at the end (one plt.show() for the lot).
        log_scale: log y-axis on the population chart (handy when prey dwarf predators)."""
        if not self.total_dataframe["time"]:
            print("No samples logged yet - call logger.log_total_dataframe(world) first.")
            return {}
        if save_dir:
            os.makedirs(save_dir, exist_ok=True)

        def path(name):
            return os.path.join(save_dir, name + ".png") if save_dir else None

        self.summary()
        figures = {
            "population": self.plot_population(log_scale=log_scale, save_path=path("population"), show=False),
            "births_deaths": self.plot_births_deaths(save_path=path("births_deaths"), show=False),
            "genes": self.plot_genes(save_path=path("genes"), show=False),
            "vitals": self.plot_vitals(save_path=path("vitals"), show=False),
            "activity": self.plot_activity(save_path=path("activity"), show=False),
            "generations": self.plot_generations(save_path=path("generations"), show=False),
            "lifespans": self.plot_lifespans(save_path=path("lifespans"), show=False),
            "selection": self.plot_selection(save_path=path("selection"), show=False),
        }
        figures = {name: fig for name, fig in figures.items() if fig is not None}
        if show and figures:
            plt.show()
        return figures

    def plot_avg_speed(self, show=True, **kwargs):
        """Old name, kept so existing calls still work. It now shows every stat (plot_all_stats)."""
        return self.plot_all_stats(show=show, **kwargs)