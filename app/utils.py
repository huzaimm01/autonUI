# app/utils.py

import math
import json
import os

class Utils:
    @staticmethod
    def distance(p1, p2):
        return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

    @staticmethod
    def midpoint(p1, p2):
        return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)

    @staticmethod
    def angle_between(p1, p2):
        return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

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
        base = os.path.join(os.path.dirname(__file__), "..", "data", f"{game_name}.json")
        if os.path.exists(base):
            with open(base) as f:
                data = json.load(f)
                return data.get("field_width", 8.0), data.get("field_length", 16.0)
        return 8.0, 16.0

    @staticmethod
    def get_official_elements(game_name):
        base = os.path.join(os.path.dirname(__file__), "..", "data", f"{game_name}.json")
        if os.path.exists(base):
            with open(base) as f:
                data = json.load(f)
                return data.get("field_elements", [])
        return []
