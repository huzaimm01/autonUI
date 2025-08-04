import math
import json
import os
import csv

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

    @staticmethod
    def filter_elements_by_type(elements, type_name):
        return [e for e in elements if e.get("type") == type_name]

    @staticmethod
    def group_elements_by_type(elements):
        grouped = {"note": [], "obstacle": [], "target": []}
        for e in elements:
            t = e.get("type", "unknown")
            if t in grouped:
                grouped[t].append(e)
            else:
                grouped[t] = [e]
        return grouped

    @staticmethod
    def get_polygon_obstacles(game_name, json_path):
        feet_to_meters = 0.3048
        with open(json_path, "r") as f:
            data = json.load(f)

        polygons = []
        for obj in data.get("obstacles", []):
            if obj.get("game", "").lower() == game_name.lower():
                points = obj.get("points", [])
                polygon = [{"x": x * feet_to_meters, "y": y * feet_to_meters} for x, y in points]
                polygons.append(polygon)
        return polygons

    @staticmethod
    def smooth_catmull_rom_path(points, resolution=10):
        def interpolate(p0, p1, p2, p3, t):
            t2 = t * t
            t3 = t2 * t
            return (
                0.5 * ((2 * p1[0]) +
                       (-p0[0] + p2[0]) * t +
                       (2*p0[0] - 5*p1[0] + 4*p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3*p1[0] - 3*p2[0] + p3[0]) * t3),
                0.5 * ((2 * p1[1]) +
                       (-p0[1] + p2[1]) * t +
                       (2*p0[1] - 5*p1[1] + 4*p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3*p1[1] - 3*p2[1] + p3[1]) * t3)
            )
        if len(points) < 4:
            return points
        new_path = []
        for i in range(1, len(points) - 2):
            for t in [j / resolution for j in range(resolution)]:
                pt = interpolate(points[i - 1], points[i], points[i + 1], points[i + 2], t)
                new_path.append(pt)
        new_path.append(points[-2])
        new_path.append(points[-1])
        return new_path

    @staticmethod
    def write_path_to_json(path, filename="path.json"):
        data = [{"x": round(x, 3), "y": round(y, 3)} for x, y in path]
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def write_path_to_csv(path, filename="path.csv"):
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["x", "y"])
            for x, y in path:
                writer.writerow([round(x, 3), round(y, 3)])
