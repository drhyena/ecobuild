import heapq
import math

# Cost of a diagonal step relative to a straight one. A diagonal really is ~1.41x as far to
# walk (creatures move in pixels), so paths prefer straight lines when it costs nothing extra.
# Set this to 1.0 for "every step costs the same": the heuristic below adapts automatically.
DIAGONAL_COST = math.sqrt(2)

# every neighbour, straight and diagonal: (dx, dy, cost)
DIRECTIONS = [
    (0, 1, 1.0), (1, 0, 1.0), (0, -1, 1.0), (-1, 0, 1.0),
    (-1, 1, DIAGONAL_COST), (1, 1, DIAGONAL_COST),
    (-1, -1, DIAGONAL_COST), (1, -1, DIAGONAL_COST),
]


def heuristic(a, b):
    """Octile distance: the exact cost to get from a to b on an empty map with these moves.
    (With DIAGONAL_COST = 1 this is Chebyshev distance.) It never overestimates, so A* is
    guaranteed to return the cheapest path."""
    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])
    return (dx + dy) + (DIAGONAL_COST - 2) * min(dx, dy)


def astar(start, goal, grid, grid_width, grid_height, allow_corner_cutting=True):
    """
    A* pathfinding from start to goal over 8 directions. Avoids water tiles.

    Returns the tiles to walk, in order. The start tile is NOT included and the goal tile is.
    Returns [] if the goal can't be reached, and also if start == goal (already there): callers
    use that empty result to clear a target once the creature has arrived.

    allow_corner_cutting: if False, a diagonal step is refused when either of the two straight
    tiles it passes between is water, so nothing squeezes through a gap where water touches at a
    corner. Creatures that move without A* (wandering, fleeing, hunting) can still cut corners.
    """
    start, goal = tuple(start), tuple(goal)
    if start == goal:
        return []

    gx, gy = goal
    if not (0 <= gx < grid_width and 0 <= gy < grid_height) or grid[gx][gy] == "water":
        return []  # can never get there, so don't search for it

    # heap entries are (f, g, tile). A tile may be pushed more than once when a cheaper route to
    # it turns up; the older entries are skipped when they come off the heap (closed set).
    open_set = [(heuristic(start, goal), 0.0, start)]
    came_from = {}
    g_score = {start: 0.0}
    closed = set()

    while open_set:
        _, g, current = heapq.heappop(open_set)

        if current in closed:
            continue
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path
        closed.add(current)

        x, y = current
        for dx, dy, cost in DIRECTIONS:
            nx, ny = x + dx, y + dy

            if not (0 <= nx < grid_width and 0 <= ny < grid_height):
                continue
            if grid[nx][ny] == "water" or (nx, ny) in closed:
                continue
            if (not allow_corner_cutting and dx and dy
                    and (grid[x + dx][y] == "water" or grid[x][y + dy] == "water")):
                continue

            tentative_g = g + cost
            if tentative_g < g_score.get((nx, ny), float("inf")):
                g_score[(nx, ny)] = tentative_g
                came_from[(nx, ny)] = current
                heapq.heappush(open_set, (tentative_g + heuristic((nx, ny), goal), tentative_g, (nx, ny)))

    return []  # No path found