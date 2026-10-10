import random


class ReproductionManager:

    # ---------- readiness checks ----------

    def check_if_mature(self, c):
        return c.vitals.age > 10

    def check_if_well_fed(self, c):
        return c.vitals.hunger > 80 and c.vitals.thirst > 80

    def check_if_ready_to_seek_mate(self, c):
        return bool(
            self.check_if_mature(c)
            and c.genome.reproductive_interval < c.reproduction.time_since_last_mating
        )

    def check_if_ready_to_reproduce(self, c):
        return bool(
            c.reproduction.current_mate
            and self.check_if_ready_to_seek_mate(c)
            and self.check_if_well_fed(c)
        )

    # ---------- finding / meeting a mate ----------

    def check_for_viable_mate(self, c):
        c.reproduction.current_mate = c.world.find_closest_mate(c, c.world.creature_list)

    @staticmethod
    def split_path(path):
        """Split a path into two halves that share the midpoint tile.
        Returns (path[:mid+1], path[mid:] reversed). Both end on the midpoint."""
        mid = len(path) // 2
        return path[:mid + 1], path[mid:][::-1]

    def set_midpoint(self, c, test_path1, test_path2):
        mate = c.reproduction.current_mate
        mate.reproduction.current_mate = c
        midpoint = tuple(test_path1[-1])  # both halves end on the same tile
        halves = (test_path1, test_path2)

        # Each creature walks the half that starts nearest to itself, so this
        # works whichever end of the path astar puts the start tile on.
        def start_dist(creature, half):
            return (half[0][0] - creature.x) ** 2 + (half[0][1] - creature.y) ** 2

        c_idx = min((0, 1), key=lambda i: start_dist(c, halves[i]))
        for creature, path in ((c, halves[c_idx]), (mate, halves[1 - c_idx])):
            creature.targeting.target = midpoint
            creature.targeting.mating_point = midpoint
            creature.targeting.path = list(path)

    def check_if_creatures_are_at_mating_point(self, c):
        mate = c.reproduction.current_mate
        point = c.targeting.mating_point
        return bool(
            mate
            and point
            and (c.x, c.y) == point
            and (mate.x, mate.y) == point
        )

    def cancel_mating(self, c):
        """Drop the mating plan for c and its partner (if any)."""
        partner = c.reproduction.current_mate
        for creature in (c, partner):
            if creature is None:
                continue
            creature.reproduction.current_mate = None
            creature.reproduction.seeking_mate = False
            creature.reproduction.ready_to_mate = False
            creature.targeting.mating_point = None
            creature.targeting.target = None
            creature.targeting.path = []

    # ---------- reproduction ----------

    def mate(self, c):
        # imported here to avoid a circular import (creature -> this module)
        from Predator import Predator
        from Prey import Prey

        partner = c.reproduction.current_mate
        if partner is None:
            return []

        cls = Predator if c.species == "predator" else Prey
        children = []

        for _ in range(c.genome.fertility):
            child = cls(c.x, c.y, c.world, c.interaction_manager)

            # Crossover + mutation on numeric genes
            for name, value in vars(c.genome).items():
                if isinstance(value, bool) or not isinstance(value, (int, float)):
                    continue
                gene = random.choice([value, getattr(partner.genome, name, value)])
                if random.random() < 0.1:  # 10% mutation chance
                    gene *= random.uniform(0.9, 1.1)
                if isinstance(value, int):  # keep int genes as ints
                    gene = max(1, round(gene))
                setattr(child.genome, name, gene)

            c.world.creature_list.append(child)
            children.append(child)

        # Reset both parents (also stops the partner's own mate() call
        # from producing a second litter)
        self.cancel_mating(c)
        for parent in (c, partner):
            parent.reproduction.time_since_last_mating = 0
            parent.vitals.hunger = max(0, parent.vitals.hunger - 30)  # tune as needed
            parent.vitals.thirst = max(0, parent.vitals.thirst - 30)

        return children