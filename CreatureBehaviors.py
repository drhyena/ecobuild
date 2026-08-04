
class Movement:
    def movement_decider(self, world, screen):
            if self.targeting.target is None:
                self.wander_randomly(world)
            else:
                if not self.targeting.path:
                    self.set_path(world)
                    return
    
                if self.targeting.path:
                    self.follow_path(screen, world.tile_size)
    
    def notify_travel(self, target):
            """Called by interaction manager to assign a travel target."""
            if not self.targeting.target:  # don't override if already heading somewhere
                self.targeting.target = target
                self.targeting.path = []
    
    def wander_randomly(self, world):
            dx, dy = random.choice(world.get_neighbors(self.x, self.y))
            if world.is_walkable(dx, dy):
                self.prev_x, self.prev_y = self.x, self.y
                self.x, self.y = dx, dy
    
    def set_path(self, world):
            if self.targeting.target:
                self.targeting.path = astar(
                    (self.x, self.y),
                    (self.targeting.target[0], self.targeting.target[1]),
                    world.map_grid,
                    world.grid_width,
                    world.grid_height,
                )
                if not self.targeting.path:
                    self.targeting.target = None
    
    def follow_path(self, screen, tile_size):
            if self.targeting.path:
                points = [
                    (
                        x * tile_size + tile_size // 2,
                        y * tile_size + tile_size // 2,
                    )
                    for (x, y) in self.targeting.path
                ]

                if len(points) > 1:
                    pygame.draw.lines(screen, (255, 0, 0), False, points, 2)
    
                self.prev_x, self.prev_y = self.x, self.y
                self.x, self.y = self.targeting.path.pop(0)

class PredatorMovement(Movement):
    pass

class PreyMovement(Movement):



class PreyHungerBehavior:
    pass

class PredatorHungerBehavior:
    pass

class ThirstBehavior:
    pass

class PredatorHuntingBehaviour:
    pass