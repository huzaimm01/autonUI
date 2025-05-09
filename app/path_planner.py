import math

class PathPlanner:
    def __init__(self, game_config, robot_config):
        self.game_config = game_config
        self.robot_config = robot_config
        self.path = []

    def plan_path(self, start, goals):
        current = start
        self.path = [start]
        for goal in goals:
            segment = self._generate_segment(current, goal)
            self.path.extend(segment[1:])
            current = goal
        return self.path

    def _generate_segment(self, start, end):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.hypot(dx, dy)
        steps = max(2, int(distance / 0.1))
        return [(
            start[0] + dx * t / steps,
            start[1] + dy * t / steps
        ) for t in range(steps + 1)]

    def export_path(self):
        return [{'x': round(p[0], 2), 'y': round(p[1], 2)} for p in self.path]

    def clear_path(self):
        self.path = []
