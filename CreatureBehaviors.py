from astar import astar
import random
class Movement:
    def movement_decider(c, world):
            if c.targeting.target is None:
                c.wander_randomly(world)
            else:
                if not c.targeting.path:
                    c.set_path(world)
                    return
    
                if c.targeting.path:
                    c.follow_path(world.tile_size)
    
    def notify_travel(c, target):
            """Called by interaction manager to assign a travel target."""
            if not c.targeting.target:  # don't override if already heading somewhere
                c.targeting.target = target
                c.targeting.path = []
    
    def wander_randomly(c, world):
            dx, dy = random.choice(world.get_neighbors(c.x, c.y))
            if world.is_walkable(dx, dy):
                c.prev_x, c.prev_y = c.x, c.y
                c.x, c.y = dx, dy
                
                
    def set_path(c, world):
            if c.targeting.target:
                c.targeting.path = astar(
                    (c.x, c.y),
                    (c.targeting.target[0], c.targeting.target[1]),
                    world.map_grid,
                    world.grid_width,
                    world.grid_height,
                )
                if not c.targeting.path:
                    c.targeting.target = None
    
    
    #finds paths between two tiles. basis for pixel based travel
    def pixel_path_finder(c):
        pass
    
    
    def follow_path(c,dt):
        
                c.prev_x, c.prev_y = c.x, c.y
                pixels_travelled = c.speed * dt
                
                
                c.x, c.y = c.targeting.path.pop(0)

class PredatorMovement(Movement):
    pass

class PreyMovement(Movement):
    pass



class PreyHungerBehavior:
    pass

class PredatorHungerBehavior:
    pass

class ThirstBehavior:
    pass

class PredatorHuntingBehaviour:
    pass