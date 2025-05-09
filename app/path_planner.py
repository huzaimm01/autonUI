from app.utils import Utils

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
            path += segment[1:]  # avoid duplicating the point
            current = goal

        return path

    def _generate_path_segment(self, start, goal, obstacles):
        points = [start]

        if obstacles:
            for obstacle in obstacles:
                ox, oy = obstacle["x"], obstacle["y"]
                ow, oh = obstacle.get("width", 1.0), obstacle.get("height", 1.0)

                if Utils.path_intersects_obstacle([start, goal], (ox, oy), ow, oh, self.robot.width, self.robot.length):
                    # Naive avoidance: insert a side step
                    angle = Utils.angle_between(start, goal)
                    offset_angle = angle + 1.57  # roughly 90 degrees
                    side_step = (
                        start[0] + 0.8 * self.robot.width * round(math.cos(offset_angle), 2),
                        start[1] + 0.8 * self.robot.width * round(math.sin(offset_angle), 2)
                    )

                    # Validate side step isn't inside another obstacle
                    collision = any(
                        Utils.path_intersects_obstacle([start, side_step], (ob["x"], ob["y"]),
                                                       ob.get("width", 1.0), ob.get("height", 1.0),
                                                       self.robot.width, self.robot.length)
                        for ob in obstacles
                    )
                    if collision:
                        return None

                    return [start, side_step, goal]

        return [start, goal]
