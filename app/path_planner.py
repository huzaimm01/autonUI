from app.utils import Utils
import math

class PathPlanner:
    def __init__(self, game_config, robot_config):
        self.game = game_config
        self.robot = robot_config

    def plan_path(self, start, goals, obstacles=None):
        path = [start]
        current = start

        for goal in goals:
            segment = self._generate_path_segment(current, goal, obstacles)
            if not segment:
                return None
            path += segment[1:]
            current = goal

        return path

    def _generate_path_segment(self, start, goal, obstacles):
        if not obstacles:
            return [start, goal]

        for obstacle in obstacles:
            ox, oy = obstacle["x"], obstacle["y"]
            ow = obstacle.get("width", 1.0)
            oh = obstacle.get("height", 1.0)

            if Utils.path_intersects_obstacle([start, goal], (ox, oy), ow, oh,
                                              self.robot.width, self.robot.length):
                angle = Utils.angle_between(start, goal)
                offset_distance = max(self.robot.width, self.robot.length) + 0.5

                # Try both sides of the detour
                for offset_angle in [angle + math.pi / 2, angle - math.pi / 2]:
                    sidestep = (
                        start[0] + offset_distance * math.cos(offset_angle),
                        start[1] + offset_distance * math.sin(offset_angle)
                    )

                    if not any(Utils.path_intersects_obstacle([start, sidestep, goal],
                                                              (o["x"], o["y"]),
                                                              o.get("width", 1.0),
                                                              o.get("height", 1.0),
                                                              self.robot.width,
                                                              self.robot.length)
                               for o in obstacles):
                        return [start, sidestep, goal]

                return None

        return [start, goal]
