import random


class GeneticManager:
    # Oversees how genes get passed on. Acts as a balancer of sorts: without balance, creatures simply get stronger, faster, longer ranged etc

    def __init__(self):
        self.mutation_chance = 0.5   # chance that each evolving gene mutates at a birth
        self.mutation_range = 0.10   # biggest change is +/- this fraction of the gene's value
        self.compensate_nerfs = False  # if True, a nerf gives back the reverse tradeoff

        # Only these genes mutate. Everything else numeric (generation, energy_*) is just inherited.
        self.evolving = {
            "speed", "perceptive_radius", "hunger_threshold", "thirst_threshold",
            "hunger_rate", "thirst_rate", "max_hunger", "max_thirst",
            "fertility", "reproductive_interval", "iq",
        }

        # When the key gene is buffed, linked genes move in this direction (+1 goes up, -1 goes down).
        # The size of the move is the buff's size as a fraction of the gene's value.
        self.tradeoffs = {
            "speed": {"hunger_threshold": -1, "max_hunger": -1},
            "perceptive_radius": {"speed": -1, "max_hunger": -1},
            "reproductive_interval": {"max_hunger": -1},
            "max_hunger": {"speed": -1},
        }

        # Decides if a change in a gene is a buff. Lower reproductive_interval is a buff
        self.is_buff = {
            "speed": lambda pre, new: new > pre,
            "perceptive_radius": lambda pre, new: new > pre,
            "reproductive_interval": lambda pre, new: new < pre,
            "hunger_threshold": lambda pre, new: new > pre,
            "max_hunger": lambda pre, new: new > pre,
        }

        # Floors and ceilings so mutations and penalties can't push a gene to zero, below zero,
        # or off the scale. The ceilings are generous starting points: tune them.
        self.min_values = {
            "speed": 1.0,
            "perceptive_radius": 2.0,
            "reproductive_interval": 1.0,
            "hunger_threshold": 5.0,
            "thirst_threshold": 5.0,
            "hunger_rate": 0.1,
            "thirst_rate": 0.1,
            "max_hunger": 20.0,
            "max_thirst": 20.0,
            "fertility": 1.0,
            "iq": 0.05,
        }
        self.max_values = {
            "speed": 60.0,
            "perceptive_radius": 25.0,
            "reproductive_interval": 60.0,
            "hunger_rate": 3.0,
            "thirst_rate": 5.0,
            "max_hunger": 300.0,
            "max_thirst": 300.0,
            "fertility": 6.0,
            "iq": 0.95,
        }

        # A hunger/thirst threshold can't go above this fraction of its max (it would mean
        # the creature is permanently hungry or thirsty)
        self.max_threshold_fraction = 0.8

    # ---------- entry point ----------

    def reproduce(self, c):
        """Run all five steps and return the newborn child.
        Pass a mate for two parents, or leave it out for one."""
        mate = c.reproduction.current_mate
        parents = [c] if mate is None else [c, mate]
        pre = self.mix_genes(parents)
        mutated = self.mutate_genes(pre)
        buffs, nerfs = self.find_changes(pre, mutated)
        self.count_mutations(c, buffs, nerfs)
        final = self.apply_tradeoffs(mutated, buffs, nerfs)
        return self.birth(c, final)

    # ---------- the five steps ----------

    def mix_genes(self, parents):
        """Step 1. Each numeric gene comes from a random parent. Returns the pre-mutated genes.
        Genes are read off the genome object with vars(), as it is a dataclass."""
        pre = {}
        for name, value in vars(parents[0].genome).items():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            pre[name] = getattr(random.choice(parents).genome, name, value)
        return pre

    def mutate_genes(self, pre):
        """Step 2. Each evolving gene has a chance to change by up to +/- mutation_range of its
        own value, so big and small genes mutate on the same scale. Whole-number genes change
        in whole steps: a small change rounds up or down at random (in proportion to its size),
        so they still mutate, just rarely when the gene is small."""
        mutated = dict(pre)
        for gene in pre:
            if gene not in self.evolving or random.random() >= self.mutation_chance:
                continue
            fraction = random.uniform(0, self.mutation_range) * random.choice((-1, 1))
            change = pre[gene] * fraction
            if self._is_int(pre[gene]):
                change = self._stochastic_round(change)
            mutated[gene] = self._clamp(gene, pre[gene] + change)
        return mutated

    def find_changes(self, pre, mutated):
        """Step 3. Sorts changed genes into buffs and nerfs.
        Returns (buffs, nerfs), each a dict of {gene: size of the change as a fraction of
        the gene's value before mutation}."""
        buffs, nerfs = {}, {}
        for gene in mutated:
            if gene not in self.is_buff or mutated[gene] == pre[gene] or pre[gene] == 0:
                continue
            size = abs(mutated[gene] - pre[gene]) / abs(pre[gene])
            if self.is_buff[gene](pre[gene], mutated[gene]):
                buffs[gene] = size
            else:
                nerfs[gene] = size
        return buffs, nerfs

    def apply_tradeoffs(self, mutated, buffs, nerfs):
        """Step 4. Applies the hardcoded nerfs, scaled to the size of each buff.
        Works on a copy, so penalties never count as mutations themselves."""
        final = dict(mutated)

        for gene, fraction in buffs.items():
            for linked, direction in self.tradeoffs.get(gene, {}).items():
                if linked not in final:  # genome doesn't have this gene
                    continue
                final[linked] *= max(0.0, 1 + direction * fraction)

        if self.compensate_nerfs:
            for gene, fraction in nerfs.items():
                for linked, direction in self.tradeoffs.get(gene, {}).items():
                    if linked in final:
                        final[linked] *= max(0.0, 1 - direction * fraction)

        return self._clamp_all(final)

    def birth(self, c, genome):
        """Step 5. The child is the same class as the parent, with the final genes."""
        child = type(c)(c.x, c.y, c.world, c.interaction_manager,c.log)
        for name, value in genome.items():
            if isinstance(getattr(c.genome, name), int):  # keep int genes as ints
                value = max(1, round(value))
            setattr(child.genome, name, value)
        child.genome.generation = self.set_generation(c)
        child.logging.parents = {c.genome.id,c.reproduction.current_mate.genome.id}
        c.log.log_creature(child)
        return child

    # ---------- helpers ----------

    def count_mutations(self, c, buffs, nerfs):
        """Adds this birth's buffed and nerfed genes to the logger's running totals."""
        c.log.mutations_buff += len(buffs)
        c.log.mutations_nerf += len(nerfs)

    def _is_int(self, value):
        return isinstance(value, int) and not isinstance(value, bool)

    def _stochastic_round(self, x):
        """Rounds toward a whole number at random, so the average result equals x."""
        sign = 1 if x >= 0 else -1
        whole = int(abs(x))
        if random.random() < abs(x) - whole:
            whole += 1
        return sign * whole

    def _clamp(self, gene, value):
        if gene in self.min_values:
            value = max(value, self.min_values[gene])
        if gene in self.max_values:
            value = min(value, self.max_values[gene])
        return value

    def _clamp_all(self, genes):
        for gene in genes:
            genes[gene] = self._clamp(gene, genes[gene])
        for threshold, maximum in (("hunger_threshold", "max_hunger"),
                                   ("thirst_threshold", "max_thirst")):
            if threshold in genes and maximum in genes:
                genes[threshold] = min(genes[threshold],
                                       self.max_threshold_fraction * genes[maximum])
        return genes

    def set_generation(self,c):
        mate = c.reproduction.current_mate
        generations = [c.genome.generation]
        if mate is not None:
            generations.append(mate.genome.generation)
        return max(generations) + 1