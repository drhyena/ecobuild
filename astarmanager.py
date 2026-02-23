from collections import deque
from astar import *

class Astarmanager:
    def __init__(self):
        self.calls_this_tick = 0
        self.max_calls_per_tick = 3
        self.creature_q= deque()
        
    def creature_queue_adder(self,creature,world):
        if creature.target is None:
            pass
        else:
            print("added creature")
            self.creature_q.append(creature)
        
    def process_request(self,creature,world):
        if creature.target is None:
            return None
        else:
            print("returning path")
            return astar(
                            (creature.x, creature.y),
                            (creature.target[0], creature.target[1]),
                            world.map_grid,
                            world.grid_width,
                            world.grid_height)
    
    def Astaraccess(self, world):
        while self.creature_q and self.calls_this_tick < self.max_calls_per_tick:
            self.calls_this_tick += 1
            creature = self.creature_q.popleft()
            self.process_request(creature, world)
            
        