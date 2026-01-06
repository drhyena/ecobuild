import heapq

def astar(start, goal, grid, grid_width, grid_height):
    """
    A* pathfinding from start to goal.
    Avoids water tiles.
    """

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()
            return path

        x, y = current
     

        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0),(-1,1),(1,1)]:
            nx, ny = x + dx, y + dy

            if 0 <= nx < grid_width and 0 <= ny < grid_height:
                if grid[nx][ny] == "water":
                    continue

                tentative_g = g_score[current] + 1

                if tentative_g < g_score.get((nx, ny), float("inf")):
                    came_from[(nx, ny)] = current
                    g_score[(nx, ny)] = tentative_g
                    f_score[(nx, ny)] = tentative_g + heuristic((nx, ny), goal)

                    if (nx, ny) not in [n for _, n in open_set]:
                        heapq.heappush(open_set, (f_score[(nx, ny)], (nx, ny)))

    return []  # No path found
