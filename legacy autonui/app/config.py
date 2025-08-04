import json

class FieldElement:
    def __init__(self, name, x, y, width=1.0, height=1.0, type="obstacle"):
        self.name = name
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = type

    @staticmethod
    def from_dict(d):
        return FieldElement(
            name=d["name"],
            x=d["x"],
            y=d["y"],
            width=d.get("width", 1.0),
            height=d.get("height", 1.0),
            type=d.get("type", "obstacle")
        )

    def to_dict(self):
        return {
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "type": self.type
        }

class GameConfig:
    def __init__(self, name, field_width, field_length, point_values, field_elements):
        self.name = name
        self.field_width = field_width
        self.field_length = field_length
        self.point_values = point_values
        self.field_elements = field_elements

    @staticmethod
    def from_file(path):
        with open(path, 'r') as f:
            data = json.load(f)
            elements = [FieldElement.from_dict(e) for e in data.get("field_elements", [])]
            return GameConfig(
                name=data["name"],
                field_width=data["field_width"],
                field_length=data["field_length"],
                point_values=data["point_values"],
                field_elements=elements
            )

class RobotConfig:
    def __init__(self, width, length, height, max_velocity, max_acceleration, drivetrain):
        self.width = width
        self.length = length
        self.height = height
        self.max_velocity = max_velocity
        self.max_acceleration = max_acceleration
        self.drivetrain = drivetrain
