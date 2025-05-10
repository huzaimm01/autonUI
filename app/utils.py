import math

class Utils:
    @staticmethod
    def distance(p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    @staticmethod
    def angle_between(p1, p2):
        return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

    @staticmethod
    def midpoint(p1, p2):
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    @staticmethod
    def rotate_point(point, angle, origin=(0, 0)):
        ox, oy = origin
        px, py = point
        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy

    @staticmethod
    def format_path(path):
        return [{'x': round(x, 2), 'y': round(y, 2)} for x, y in path]

    @staticmethod
    def circles_overlap(c1, r1, c2, r2):
        return Utils.distance(c1, c2) < (r1 + r2)

    @staticmethod
    def point_in_rect(point, rect_center, width, height):
        x, y = point
        cx, cy = rect_center
        return (cx - width / 2 <= x <= cx + width / 2 and
                cy - height / 2 <= y <= cy + height / 2)

    @staticmethod
    def path_intersects_obstacle(path, obstacle_center, obstacle_w, obstacle_h, robot_w, robot_l):
        for pt in path:
            if Utils.point_in_rect(pt, obstacle_center, obstacle_w + robot_w, obstacle_h + robot_l):
                return True
        return False

    @staticmethod
    def get_official_field_dimensions(game_name):
        if game_name == "Charged Up":
            return 8.01, 16.46
        elif game_name == "Crescendo":
            return 8.02, 16.45
        elif game_name == "Reefscape":
            return 8.10, 16.30
        else:
            return 8.0, 16.0

    @staticmethod
    def get_official_elements(game_name):
        if game_name == "Charged Up":
            return [
                {"name": "Charge Station", "x": 8.0, "y": 8.0, "width": 1.5, "height": 1.5, "type": "obstacle"},
                {"name": "Grid", "x": 1.0, "y": 8.0, "width": 0.5, "height": 2.0, "type": "target"}
            ]
        elif game_name == "Crescendo":
            return [
                {"name": "Speaker", "x": 15.0, "y": 4.0, "width": 1.0, "height": 1.5, "type": "target"},
                {"name": "Amp", "x": 1.0, "y": 4.0, "width": 1.0, "height": 1.5, "type": "target"},
                *[
                    {"name": f"Note {i+1}", "x": 4.5 + i * 1.1, "y": 2.0 + (i % 2) * 2,
                     "width": 0.3, "height": 0.3, "type": "note"}
                    for i in range(9)
                ]
            ]
        elif game_name == "Reefscape":
            return [
                {"name": "Reef", "x": 14.0, "y": 4.5, "width": 1.2, "height": 1.2, "type": "target"},
                {"name": "Crate", "x": 2.0, "y": 3.5, "width": 1.0, "height": 1.0, "type": "obstacle"},
                *[
                    {"name": f"Bubble {i+1}", "x": 4.0 + i * 1.2, "y": 5.0 - (i % 2),
                     "width": 0.4, "height": 0.4, "type": "note"}
                    for i in range(6)
                ]
            ]
        else:
            return []

    @staticmethod
    def group_elements_by_type(elements):
        grouped = {"obstacle": [], "note": [], "target": [], "unknown": []}
        for e in elements:
            grouped.setdefault(e.get("type", "unknown"), []).append(e)
        return grouped
