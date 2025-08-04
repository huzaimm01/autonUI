"""
Data structures for AutonUI
"""
from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class FieldElement:
    """Represents a field element (obstacle, target, etc.)"""
    name: str
    x: float
    y: float
    width: float
    height: float
    type: str

@dataclass
class Waypoint:
    """Represents a waypoint in the path"""
    x: float
    y: float
    id: int

@dataclass
class GamePreset:
    """Represents a game field configuration"""
    name: str
    field_width: float
    field_length: float
    unit: str = "meters"
    point_values: Dict[str, int] = None
    field_elements: List[FieldElement] = None

    def __post_init__(self):
        if self.point_values is None:
            self.point_values = {}
        if self.field_elements is None:
            self.field_elements = []