import random


class GeneticManager:
    # Oversees how genes get passed on. Acts as a balancer of sorts: without balance, creatures simply get stronger, faster, longer ranged etc

    def __init__(self):
        self.mutation_chance = 0.5
        self.mutation_range = 0.5
        self.compensate_nerfs = False  # if True, a nerf gives back the reverse tradeoff

        # When the key gene is buffed, linked genes move in this direction (+1 goes up, -1 goes down)
        self.tradeoffs = {
            "speed": { "hunger_limit": -1, "max_hunger": -1},
            "perceptive_radius": {"speed": -1, "max_hunger": -1},
            "reproductive_interval": { "max_hunger": -1},
            "max_hunger": {"speed": -1},
        }

        # Decides if a change in a gene is a buff. Lower reproductive_interval is a buff
        self.is_buff = {
            "speed": lambda pre, new: new > pre,
            "perceptive_radius": lambda pre, new: new > pre,
            "reproductive_interval": lambda pre, new: new < pre,
            "hunger_limit": lambda pre, new: new > pre,
            "max_hunger": lambda pre, new: new > pre,
        }

        # Floors so mutations and penalties can't push a gene to zero or below
        self.min_values = {
            "speed": 0.1,
            "perceptive_radius": 1.0,
            "reproductive_interval": 1.0,
            "hunger_limit": 0.1,
            "max_hunger": 1.0,
        }

    # ---------- entry point ----------

    def reproduce(self, c):
        """Run all five steps and return the newborn child.
        Pass a mate for two parents, or leave it out for one."""
        mate = c.reproduction.current_mate
        parents = [c] if mate is None else [c, mate]
        pre = self.mix_genes(parents)
        mutated = self.mutate_genes(pre)
        buffs, nerfs = self.find_changes(pre, mutated)
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
        """Step 2. Each gene has a chance to change by +/- (0 - mutation_range)."""
        mutated = dict(pre)
        for gene in pre:
            if random.random() < self.mutation_chance:
                change = random.uniform(0, self.mutation_range) * random.choice((-1, 1))
                mutated[gene] = self._clamp(gene, pre[gene] + change)
        return mutated

    def find_changes(self, pre, mutated):
        """Step 3. Sorts changed genes into buffs and nerfs.
        Returns (buffs, nerfs), each a dict of {gene: size of the change}."""
        buffs, nerfs = {}, {}
        for gene in mutated:
            if gene not in self.is_buff or mutated[gene] == pre[gene]:
                continue
            size = abs(mutated[gene] - pre[gene])
            if self.is_buff[gene](pre[gene], mutated[gene]):
                buffs[gene] = size
            else:
                nerfs[gene] = size
        return buffs, nerfs

    def apply_tradeoffs(self, mutated, buffs, nerfs):
        """Step 4. Applies the hardcoded nerfs, scaled to the size of each buff.
        Works on a copy, so penalties never count as mutations themselves."""
        final = dict(mutated)

        for gene, size in buffs.items():
            for linked, direction in self.tradeoffs[gene].items():
                if linked not in final:  # genome doesn't have this gene
                    continue
                final[linked] += direction * size

        if self.compensate_nerfs:
            for gene, size in nerfs.items():
                for linked, direction in self.tradeoffs[gene].items():
                    if linked in final:
                        final[linked] -= direction * size

        for gene in final:
            final[gene] = self._clamp(gene, final[gene])
        return final

    def birth(self, c, genome):
        """Step 5. The child is the same class as the parent, with the final genes."""
        child = type(c)(c.x, c.y, c.world, c.interaction_manager)
        for name, value in genome.items():
            if isinstance(getattr(c.genome, name), int):  # keep int genes as ints
                value = max(1, round(value))
            setattr(child.genome, name, value)
        child.genome.generation = self.set_generation(c)
        return child

    # ---------- helpers ----------

    def _clamp(self, gene, value):
        if gene in self.min_values:
            return max(value, self.min_values[gene])
        return value

    def set_generation(self,c):
       return max(c.genome.generation,c.reproduction.current_mate.genome.generation)