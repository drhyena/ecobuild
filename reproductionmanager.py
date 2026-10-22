import random


class ReproductionManager:
    # A mate must be this close (in tiles, straight line) to be picked. Kept well under
    # the perception radius, which would otherwise pair creatures from across the map.
    MAX_MATE_DISTANCE = 10
    # The walk to the partner (A* path length, in tiles) may not exceed this, so a lake or
    # wall between two nearby creatures can't turn into a long trek.
    MAX_MATE_PATH = 10
    # Hunger and thirst each parent loses when mating.
    MATE_COST = 10
    # Seconds of hunger/thirst drain a creature must be able to absorb on top of MATE_COST
    # before it starts a pairing, so it doesn't drop below its hungry/thirsty threshold on
    # the way to the meeting point and abandon the plan.
    MATING_WALK_ALLOWANCE = 5
    # Print a line whenever a pairing forms, is dropped, or produces offspring.
    DEBUG = True
    # A pairing that hasn't ended in mating after this many seconds is dropped.
    MATING_TIMEOUT = 10
    # After a failed pairing (unreachable, too far to walk, timed out) the two won't be
    # paired with each other again for this many seconds.
    REJECT_TIME = 30

    def __init__(self):
        self.matecounter = 0


    def check_if_mature(self, c):
        return c.vitals.age > 10

    # needed to START a pairing: enough hunger/thirst to pay the cost and still sit above
    # the hungry/thirsty thresholds afterwards
    def check_if_well_fed(self, c):
        g, v = c.genome, c.vitals
        # drain per second matches Creature.update_needs
        hunger_walk = g.hunger_rate * 1.5 * self.MATING_WALK_ALLOWANCE
        thirst_walk = g.thirst_rate * 1.5 * self.MATING_WALK_ALLOWANCE
        return bool(
            v.hunger >= g.hunger_threshold + self.MATE_COST + hunger_walk
            and v.thirst >= g.thirst_threshold + self.MATE_COST + thirst_walk
        )

    def debug(self, msg):
        if self.DEBUG:
            print(f"[mating] {msg}")

    # needed to KEEP a pairing alive: not hungry/thirsty, and still able to pay the cost
    # without dying. Deliberately lower than check_if_well_fed so a pairing doesn't drop
    # and re-form every frame.
    def check_if_can_afford_mating(self, c):
        g, v = c.genome, c.vitals
        return bool(
            v.hunger >= max(g.hunger_threshold, self.MATE_COST + 1)
            and v.thirst >= max(g.thirst_threshold, self.MATE_COST + 1)
        )

    def check_if_mating_timed_out(self, c):
        r = c.reproduction
        if r.paired_at == 0:  # pairing made somewhere else: start the clock now
            r.paired_at = c.world.sim_time
        return c.world.sim_time - r.paired_at > self.MATING_TIMEOUT

    def reject(self, c, other):
        """Stop c and other from being paired with each other for REJECT_TIME seconds."""
        now = c.world.sim_time
        for a, b in ((c, other), (other, c)):
            rejected = a.reproduction.rejected
            for k in [k for k, until in rejected.items() if until <= now]:
                del rejected[k]  # forget expired entries
            rejected[b] = now + self.REJECT_TIME

    def is_rejected(self, c, other):
        return c.reproduction.rejected.get(other, 0) > c.world.sim_time

    # mature, and enough time has passed since the last mating
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

    def check_if_both_are_ready_to_reproduce(self,c):
        return (self.check_if_ready_to_reproduce(c) and self.check_if_ready_to_reproduce(c.reproduction.current_mate))

    def check_for_viable_mate(self, c):
        """Called by interaction manager to look for the closest mate."""
        possible_mate = c.world.find_closest_mate(c)  # already filtered for readiness
        if possible_mate:
            c.reproduction.current_mate = possible_mate
            possible_mate.reproduction.current_mate = c
            c.reproduction.paired_at = possible_mate.reproduction.paired_at = c.world.sim_time
            self.debug(f"{c.genome.id} paired with {possible_mate.genome.id}")

    # splits a path into two halves that share the midpoint tile. both end on the midpoint
    @staticmethod
    def split_path(path):
        mid = len(path) // 2
        return path[:mid + 1], path[mid:][::-1]

    def set_midpoint(self, c, test_path1, test_path2):
        """Called once a mate is found. Sends both creatures to meet at the midpoint."""
        mate = c.reproduction.current_mate
        mate.reproduction.current_mate = c
        midpoint = tuple(test_path1[-1])  # both halves end on the same tile
        halves = (test_path1, test_path2)

        # each creature walks the half that starts nearest to itself, so this
        # works whichever end of the path astar puts the start tile on
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
            creature.reproduction.paired_at = 0
            creature.targeting.mating_point = None
            creature.targeting.target = None
            creature.targeting.path = []

    def mate(self, c):
        """Called when both creatures are at the mating point. Returns the children."""
        # imported here to avoid a circular import (creature -> this module)
        from Predator import Predator
        from Prey import Prey

        partner = c.reproduction.current_mate
        if partner is None:
            return []

        children = []

        for _ in range(c.genome.fertility):
            child = c.geneticmanager.reproduce(c)
            c.reproduction.children.add(child)
            partner.reproduction.children.add(child)

            c.world.creature_list.add(child)
            children.append(child)


        self.debug(f"{c.genome.id} x {partner.genome.id} mated at {c.targeting.mating_point}: "
                   f"fertility={c.genome.fertility}, born={len(children)}, "
                   f"creature_list={type(c.world.creature_list).__name__}({len(c.world.creature_list)})")

        # reset both parents. cancel_mating also stops the partner's own
        # mate() call from producing a second litter
        self.cancel_mating(c)
        for parent in (c, partner):
            parent.reproduction.time_since_last_mating = 0
            parent.vitals.hunger = max(0, parent.vitals.hunger - self.MATE_COST)
            parent.vitals.thirst = max(0, parent.vitals.thirst - self.MATE_COST)

        return children