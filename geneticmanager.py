import random


class GeneticManager:
    # oversees how genes get passed on. acts as a balancer of sorts. without balance, creatures simply get stronger, faster, longer ranged etc
    def __init__(self):
        self.mutation_chance = 0.10
        self.mutation_range = 0.5
        self.compensate_nerfs = False  # if true, a nerf gives back the reverse tradeoff

        # when the key gene is buffed, linked genes move in this direction (+1 goes up, -1 goes down)
        self.tradeoffs = {
            "speed": {"health": -1, "hunger_limit": -1, "max_hunger": -1},
            "health": {"speed": -1, "hunger_limit": +1, "max_hunger": +1},
            "perceptive_radius": {"speed": -1, "max_hunger": -1},
            "reproductive_interval": {"health": -1, "max_hunger": -1},
            "hunger_limit": {"health": -1},
            "max_hunger": {"speed": -1},
        }

        # decides if a change in a gene is a buff. lower reproductive_interval is a buff
        self.is_buff = {
            "speed": lambda pre, new: new > pre,
            "health": lambda pre, new: new > pre,
            "perceptive_radius": lambda pre, new: new > pre,
            "reproductive_interval": lambda pre, new: new < pre,
            "hunger_limit": lambda pre, new: new > pre,
            "max_hunger": lambda pre, new: new > pre,
        }

        # floors so mutations and penalties can't push a gene to zero or below
        self.min_values = {
            "speed": 0.1,
            "health": 1.0,
            "perceptive_radius": 1.0,
            "reproductive_interval": 1.0,
            "hunger_limit": 0.1,
            "max_hunger": 1.0,
        }

    def reproduce(self, c, mate=None):
        """Called by creature to make a child. Pass a mate for two parents."""
        parents = [c] if mate is None else [c, mate]
        pre = self.mix_genes(parents)
        mutated = self.mutate_genes(pre)
        buffs, nerfs = self.find_changes(pre, mutated)
        final = self.apply_tradeoffs(mutated, buffs, nerfs)
        return self.birth(c, final)

    # step 1. each gene comes from a random parent
    def mix_genes(self, parents):
        pre = {}
        for gene in parents[0].genome:
            pre[gene] = random.choice(parents).genome[gene]
        return pre

    # step 2. each gene has a chance to change by +/- (0 - mutation_range)
    def mutate_genes(self, pre):
        mutated = dict(pre)
        for gene in pre:
            if random.random() < self.mutation_chance:
                change = random.uniform(0, self.mutation_range) * random.choice((-1, 1))
                mutated[gene] = self._clamp(gene, pre[gene] + change)
                print(f"{gene} mutated by {change:+.2f}")
        return mutated

    # step 3. sorts changed genes into buffs and nerfs, value is the size of the change
    def find_changes(self, pre, mutated):
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

    # step 4. applies the hardcoded nerfs. works on a copy so penalties never count as mutations
    def apply_tradeoffs(self, mutated, buffs, nerfs):
        final = dict(mutated)

        for gene, size in buffs.items():
            for linked, direction in self.tradeoffs[gene].items():
                final[linked] += direction * size
                print(f"{gene} buffed -> {linked} {direction * size:+.2f}")

        if self.compensate_nerfs:
            for gene, size in nerfs.items():
                for linked, direction in self.tradeoffs[gene].items():
                    final[linked] -= direction * size

        for gene in final:
            final[gene] = self._clamp(gene, final[gene])
        return final

    # step 5. child is the same class as the parent
    def birth(self, c, genome):
        child = type(c)(c.x, c.y, c.world, c.interaction_manager)
        child.genome = genome
        return child

    def _clamp(self, gene, value):
        if gene in self.min_values:
            return max(value, self.min_values[gene])
        return value