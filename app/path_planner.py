import math
import heapq
from app.utils import Utils  # Make sure this import path is valid in your structure

class GridNode:
    def __init__(self, x, y, cost=0, parent=None):
        self.x = x
        self.y = y
        self.cost = cost
        self.parent = parent

    def __lt__(self, other):
        return self.cost < other.cost

    def pos(self):
        return (self.x, self.y)

class PathPlanner:
    def __init__(self, game_config, robot_config, resolution=0.2):
        self.game = game_config
        self.robot = robot_config
        self.resolution = resolution
        self.width = int(self.game.field_width / resolution)
        self.height = int(self.game.field_length / resolution)

    def is_obstacle(self, x, y):
        rx, ry = x * self.resolution, y * self.resolution
        for obj in self.game.field_elements:
            if abs(rx - obj.x) < (obj.width + self.robot.width) / 2 and abs(ry - obj.y) < (obj.height + self.robot.length) / 2:
                return True
        return False

    def heuristic(self, a, b):
        return math.hypot(b[0] - a[0], b[1] - a[1])

    def a_star(self, start, goal):
        sx, sy = int(start[0] / self.resolution), int(start[1] / self.resolution)
        gx, gy = int(goal[0] / self.resolution), int(goal[1] / self.resolution)

        open_set = []
        heapq.heappush(open_set, (0, GridNode(sx, sy)))
        came_from = {}
        cost_so_far = {(sx, sy): 0}

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (1, -1), (-1, 1), (1, 1)]

        while open_set:
            _, current = heapq.heappop(open_set)

            if (current.x, current.y) == (gx, gy):
                path = []
                while current:
                    path.append((current.x * self.resolution, current.y * self.resolution))
                    current = current.parent
                return path[::-1]

            for dx, dy in directions:
                nx, ny = current.x + dx, current.y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if self.is_obstacle(nx, ny):
                        continue
                    new_cost = cost_so_far[(current.x, current.y)] + math.hypot(dx, dy)
                    if (nx, ny) not in cost_so_far or new_cost < cost_so_far[(nx, ny)]:
                        cost_so_far[(nx, ny)] = new_cost
                        priority = new_cost + self.heuristic((nx, ny), (gx, gy))
                        heapq.heappush(open_set, (priority, GridNode(nx, ny, new_cost, current)))

        return []

    def smooth_path(self, path, alpha=0.1, beta=0.3, tolerance=1e-5):
        if not path or len(path) < 3:
            return path

        new_path = [list(p) for p in path]
        change = tolerance
        while change >= tolerance:
            change = 0.0
            for i in range(1, len(path) - 1):
                for j in range(2):
                    aux = new_path[i][j]
                    new_path[i][j] += alpha * (path[i][j] - new_path[i][j])
                    new_path[i][j] += beta * (new_path[i - 1][j] + new_path[i + 1][j] - 2.0 * new_path[i][j])
                    change += abs(aux - new_path[i][j])
        return [tuple(p) for p in new_path]

    def plan_path(self, start, goals):
        full_path = []
        current = start

        for goal in goals:
            segment = self.a_star(current, goal)
            if not segment:
                print(f"⚠️ No valid path from {current} to {goal}")
                return []
            full_path.extend(segment if not full_path else segment[1:])
            current = goal

        return self.smooth_path(full_path)
