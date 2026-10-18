import math
import random
from collections import deque
from opensimplex import OpenSimplex


class World:
    def __init__(
        self,
        grid_width,
        grid_height,
        tile_size,
        noise_scale,
        world_seed=None,
        num_lakes=5,
        lake_radius=(5, 9),
        lake_feature_size=12,
        lake_wobble=0.35,
        min_water_body=30,
        min_land_piece=60,
        num_rivers=2,
        river_width=3,
        river_meander=0.25,
        river_feature_size=15,
        ensure_connected=True,
    ):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.tile_size = tile_size

        # noise_scale is kept for compatibility but no longer used: terrain is solid
        # land with deliberately placed lakes (see generate_world).
        self.noise_scale = noise_scale

        # Lake shaping
        self.num_lakes = num_lakes                # how many water bodies
        self.lake_radius = lake_radius            # (min, max) base radius in tiles
        self.lake_feature_size = lake_feature_size  # tiles per wobble in a lake outline
        self.lake_wobble = lake_wobble            # 0 = perfect circles, 0.35 = natural
        self.min_water_body = min_water_body      # water bodies smaller than this are filled in
        self.min_land_piece = min_land_piece      # land pieces smaller than this become water

        # Rivers
        self.num_rivers = num_rivers              # 0 = lakes only
        self.river_width = river_width            # tiles across (keep >= 2 so rivers stay connected)
        self.river_meander = river_meander        # sideways sway as a fraction of river length
        self.river_feature_size = river_feature_size  # tiles per bend
        self.ensure_connected = ensure_connected  # ford any river that cuts the land in two

        # Seed handling
        self.seed = world_seed if world_seed is not None else random.randint(0, 10000)

        # Create OpenSimplex generator
        self.noise_gen = OpenSimplex(seed=self.seed)

        # Generate map
        self.map_grid = self.generate_world()

        # Cached tile groups
        self.land_tiles = None
        self.water_tiles = None
        self.shore_tiles = None

        # Precompute tile types
        self.set_maptypes()
        
        self.dt = 0
        self.sim_time = 0.0

        # Owned by the world. The main loop assigns its own lists here, so these
        # must be the same list objects it appends to (never copies).
        self.creature_list = []
        self.veg_list = []

    # --------------------------------------------------
    # WORLD GENERATION
    # --------------------------------------------------

    def generate_world(self):
        """Solid land with a few well-spread, natural-looking lakes and rivers.

        Thresholding noise can't give both 'few water bodies' and 'water within
        reach of every creature': the low points of smooth noise clump into one
        or two basins, and a thin value band (the old 0.4-0.48) traces contour
        lines, i.e. winding rivers that slice the land into pieces. Placing lakes
        directly keeps one landmass and lets us spread the water out.
        """
        w, h = self.grid_width, self.grid_height
        rng = random.Random(self.seed)  # same seed -> same world

        grid = [["land"] * h for _ in range(w)]

        lakes = self._place_lakes(rng)

        for i, (cx, cy, radius) in enumerate(lakes):
            reach = int(radius * (1 + self.lake_wobble)) + 1
            offset = i * 37.7  # different outline noise for every lake
            for x in range(max(0, cx - reach), min(w, cx + reach + 1)):
                for y in range(max(0, cy - reach), min(h, cy + reach + 1)):
                    n = self.noise_gen.noise2(
                        x / self.lake_feature_size + offset,
                        y / self.lake_feature_size + offset,
                    )
                    if math.hypot(x - cx, y - cy) < radius * (1 + self.lake_wobble * n):
                        grid[x][y] = "water"

        self._carve_rivers(grid, lakes, rng)

        self._remove_small_regions(grid, "water", self.min_water_body)
        self._remove_small_regions(grid, "land", self.min_land_piece)

        if self.ensure_connected:
            self._connect_land(grid)
            self._remove_small_regions(grid, "water", self.min_water_body)
        return grid

    def _place_lakes(self, rng):
        """Lake centres spread as far apart as possible (best-candidate sampling).
        Returns [(x, y, radius), ...] kept clear of the map edge."""
        w, h = self.grid_width, self.grid_height
        lo, hi = self.lake_radius
        lakes = []

        for _ in range(self.num_lakes):
            radius = rng.uniform(lo, hi)
            margin = int(radius * (1 + self.lake_wobble)) + 2
            best, best_gap = None, -1.0
            for _ in range(25):
                x = rng.randint(margin, max(margin, w - 1 - margin))
                y = rng.randint(margin, max(margin, h - 1 - margin))
                gap = min((math.hypot(x - ox, y - oy) for ox, oy, _ in lakes),
                          default=float("inf"))
                if gap > best_gap:
                    best, best_gap = (x, y, radius), gap
            lakes.append(best)

        return lakes

    def _carve_rivers(self, grid, lakes, rng):
        """Meandering rivers. They join neighbouring lakes along a minimum
        spanning tree (a tree has no loops, so rivers on their own never wall
        off a patch of land); if more rivers are requested than there are
        links, the rest drain a lake to the nearest map edge."""
        if self.num_rivers <= 0 or not lakes:
            return
        w, h = self.grid_width, self.grid_height

        links = []
        in_tree = {0}
        while len(in_tree) < len(lakes):
            best = None
            for i in in_tree:
                for j in range(len(lakes)):
                    if j in in_tree:
                        continue
                    d = math.hypot(lakes[i][0] - lakes[j][0], lakes[i][1] - lakes[j][1])
                    if best is None or d < best[0]:
                        best = (d, i, j)
            links.append((best[1], best[2]))
            in_tree.add(best[2])
        rng.shuffle(links)

        routes = [((lakes[i][0], lakes[i][1]), (lakes[j][0], lakes[j][1]))
                  for i, j in links[:self.num_rivers]]

        spare = list(range(len(lakes)))
        rng.shuffle(spare)
        for k in spare:
            if len(routes) >= self.num_rivers:
                break
            cx, cy = lakes[k][0], lakes[k][1]
            edge = min([(0, cy), (w - 1, cy), (cx, 0), (cx, h - 1)],
                       key=lambda p: math.hypot(p[0] - cx, p[1] - cy))
            routes.append(((cx, cy), edge))

        for n, (start, end) in enumerate(routes):
            self._draw_river(grid, start, end, offset=100 + n * 53.1)

    def _draw_river(self, grid, start, end, offset):
        w, h = self.grid_width, self.grid_height
        (x0, y0), (x1, y1) = start, end
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 1:
            return

        px, py = -(y1 - y0) / length, (x1 - x0) / length  # unit vector across the river
        steps = int(length * 2)

        for s in range(steps + 1):
            t = s / steps
            # Sway sideways with noise; the sin() envelope pins both ends so
            # the river still meets the lakes it joins.
            sway = (
                self.noise_gen.noise2(t * length / self.river_feature_size + offset, offset)
                * self.river_meander * length * math.sin(math.pi * t)
            )
            cx = min(w - 1, max(0, x0 + (x1 - x0) * t + px * sway))
            cy = min(h - 1, max(0, y0 + (y1 - y0) * t + py * sway))
            radius = max(1.0, self.river_width / 2 * (
                1 + 0.3 * self.noise_gen.noise2(t * length / 6 + offset + 5, offset + 9)))

            for x in range(int(cx - radius) - 1, int(cx + radius) + 2):
                for y in range(int(cy - radius) - 1, int(cy + radius) + 2):
                    if 0 <= x < w and 0 <= y < h and math.hypot(x - cx, y - cy) <= radius:
                        grid[x][y] = "water"

    def _connect_land(self, grid):
        """If water splits the land into several pieces, ford it: flip the
        shortest strip of water tiles joining the smallest piece to other land.
        Repeats until the land is one piece."""
        w, h = self.grid_width, self.grid_height
        while True:
            pieces = self._regions(grid, "land")
            if len(pieces) <= 1:
                return

            piece = min(pieces, key=len)
            parent = {t: None for t in piece}
            queue = deque(piece)
            found = None
            while queue and found is None:
                x, y = queue.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (x + dx, y + dy)
                    if not (0 <= n[0] < w and 0 <= n[1] < h) or n in parent:
                        continue
                    if grid[n[0]][n[1]] == "land":
                        found = (x, y)  # reached a different land piece
                        break
                    parent[n] = (x, y)
                    queue.append(n)

            if found is None:
                return
            t = found
            while t is not None:
                grid[t[0]][t[1]] = "land"
                t = parent[t]

    def _regions(self, grid, kind):
        """All 4-connected regions of `kind`, as lists of (x, y)."""
        w, h = self.grid_width, self.grid_height
        seen, regions = set(), []
        for sx in range(w):
            for sy in range(h):
                if grid[sx][sy] != kind or (sx, sy) in seen:
                    continue
                region, queue = [], deque([(sx, sy)])
                seen.add((sx, sy))
                while queue:
                    x, y = queue.popleft()
                    region.append((x, y))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < w and 0 <= ny < h
                                and (nx, ny) not in seen and grid[nx][ny] == kind):
                            seen.add((nx, ny))
                            queue.append((nx, ny))
                regions.append(region)
        return regions

    def _remove_small_regions(self, grid, kind, min_size):
        """Flip every 4-connected region of `kind` smaller than min_size to the
        other tile type (small water -> land, small land -> water)."""
        w, h = self.grid_width, self.grid_height
        other = "land" if kind == "water" else "water"
        seen = set()

        for sx in range(w):
            for sy in range(h):
                if grid[sx][sy] != kind or (sx, sy) in seen:
                    continue

                region, queue = [], deque([(sx, sy)])
                seen.add((sx, sy))
                while queue:
                    x, y = queue.popleft()
                    region.append((x, y))
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < w and 0 <= ny < h
                                and (nx, ny) not in seen and grid[nx][ny] == kind):
                            seen.add((nx, ny))
                            queue.append((nx, ny))

                if len(region) < min_size:
                    for x, y in region:
                        grid[x][y] = other

    # --------------------------------------------------
    # TILE TYPE CACHING
    # --------------------------------------------------

    def set_maptypes(self):
        self.land_tiles = [
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if self.map_grid[x][y] == "land"
        ]

        self.water_tiles = {
            (x, y)
            for x in range(self.grid_width)
            for y in range(self.grid_height)
            if self.map_grid[x][y] == "water"
        }

        self.shore_tiles = self.compute_shore_tiles()

    def compute_shore_tiles(self):
        shore = set()

        for x, y in self.land_tiles:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue

                    if (x + dx, y + dy) in self.water_tiles:
                        shore.add((x, y))
                        break
                else:
                    continue
                break

        return shore

    # --------------------------------------------------
    # UTILITIES
    # --------------------------------------------------
    def is_at(self, x, y, c):
        return (c.x, c.y) == (x, y)

    def is_walkable(self, x, y):
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            return self.map_grid[x][y] == "land"
        return False

    def get_neighbors(self, x, y):
        offsets = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        neighbors = []

        for dx, dy in offsets:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                neighbors.append((nx, ny))

        return set(neighbors)

    # --------------------------------------------------
    # SEARCH FUNCTIONS
    # --------------------------------------------------

    def find_closest_veg(self, x, y, perceived_tiles):
        target_veg = None
        min_distance = float("inf")

        perceived_set = set(perceived_tiles)

        for v in self.veg_list:
            if v.alive and (v.v_x, v.v_y) in perceived_set:
                dx = x - v.v_x
                dy = y - v.v_y
                distance = dx * dx + dy * dy

                if distance < min_distance:
                    min_distance = distance
                    target_veg = v

        print("veg:", target_veg.alive if target_veg is not None else "none")
        return target_veg

    def find_closest_shore(self, x, y, perceived_tiles):
        closest_shore = None
        min_distance = float("inf")

        for u, v in perceived_tiles:
            if (u, v) in self.shore_tiles:
                dx = x - u
                dy = y - v
                distance = dx * dx + dy * dy

                if distance < min_distance:
                    min_distance = distance
                    closest_shore = (u, v)

        return closest_shore


    def find_closest_mate(self, c):
        perceived_creatures = self.check_for_creatures_in_perspective_tiles(c)

        closest_creature = None
        min_distance = float('inf')

        for other in perceived_creatures:
            if other.genome.type != c.genome.type:
                continue  # only same-species mates
            if other.reproduction.current_mate is not None:
                continue  # already paired up
            if other.status != "wandering":
                continue  # busy (hungry, thirsty, fleeing, hunting, ...)
            if not c.reproductionmanager.check_if_mature(other):
                continue

            dx = other.x - c.x
            dy = other.y - c.y
            distance = dx * dx + dy * dy  # squared distance (faster than sqrt)

            if distance < min_distance:
                min_distance = distance
                closest_creature = other

        return closest_creature

    def find_closest_prey(self, c):
        perceived_creatures = self.check_for_creatures_in_perspective_tiles(c)

        if not perceived_creatures:
            return None

        closest_creature = None
        min_distance = float('inf')

        for other in perceived_creatures:
            if other == c:
                continue  # don't target itself 
            if other.genome.type != "prey":
                continue   # only target prey.

            dx = other.x - c.x
            dy = other.y - c.y
            distance = dx * dx + dy * dy  # squared distance (faster than sqrt)

            if distance < min_distance:
                min_distance = distance
                closest_creature = other

        return closest_creature
    
    def check_for_creatures_in_perspective_tiles(self, creature):

        visible_creatures = []

        # Ensure creature has perceived tiles

        for other in self.creature_list:

            # Skip self
            if other is creature:
                continue

            # Skip dead creatures
            if not other.alive:
                continue

            # If other creature is inside perspective
            if (other.x, other.y) in creature.targeting.perceived_tiles:
                visible_creatures.append(other)

        return set(visible_creatures)
    
    def compute_best_flee_tile(self, prey, predator):
        if predator is None:
            return None

        neighbors = self.get_neighbors(prey.x, prey.y)

        best_tile = None
        max_dist = -1

        for nx, ny in neighbors:
            if self.is_walkable(nx, ny):
                dx = nx - predator.x
                dy = ny - predator.y
                dist = dx * dx + dy * dy

                if dist > max_dist:
                    max_dist = dist
                    best_tile = (nx, ny)

        return best_tile