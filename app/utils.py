import math

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