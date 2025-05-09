import json

class GameConfig:
    def __init__(self, name, field_width, field_length, point_values, field_elements):
        self.name = name
        self.field_width = field_width
        self.field_length = field_length
        self.point_values = point_values
        self.field_elements = field_elements

    @staticmethod
    def from_dict(data):
        return GameConfig(
            name=data['name'],
            field_width=data['field_width'],
            field_length=data['field_length'],
            point_values=data['point_values'],
            field_elements=data['field_elements']
        )

    @staticmethod
    def from_file(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            return GameConfig.from_dict(data)

class RobotConfig:
    def __init__(self, width, length, height, max_velocity, max_acceleration, drivetrain):
        self.width = width
        self.length = length
        self.height = height
        self.max_velocity = max_velocity
        self.max_acceleration = max_acceleration
        self.drivetrain = drivetrain

class FieldElement:
    def __init__(self, name, x, y):
        self.name = name
        self.x = x
        self.y = y

    def to_dict(self):
        return {
            'name': self.name,
            'x': self.x,
            'y': self.y
        }

    @staticmethod
    def from_dict(data):
        return FieldElement(
            name=data['name'],
            x=data['x'],
            y=data['y']
        )