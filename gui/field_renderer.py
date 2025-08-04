"""
Field rendering widget for AutonUI
"""
import math
from typing import List, Tuple, Optional
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal, QPointF, Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF

from logic.data_structures import GamePreset, Waypoint, FieldElement

class FieldRenderer(QWidget):
    """Custom widget for rendering the field, obstacles, and waypoints"""
    
    waypoint_added = pyqtSignal(float, float)  # x, y in field coordinates
    waypoint_moved = pyqtSignal(int, float, float)  # id, new_x, new_y
    waypoint_selected = pyqtSignal(int)  # waypoint id
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.setMouseTracking(True)
        
        # Field data
        self.game_preset: Optional[GamePreset] = None
        self.obstacles: List[List[Tuple[float, float]]] = []
        self.waypoints: List[Waypoint] = []
        self.selected_waypoint: Optional[int] = None
        
        # Rendering parameters
        self.pixels_per_unit = 30.0  # pixels per meter/foot
        self.grid_spacing = 1.0  # 1 unit grid
        self.margin = 50  # pixels
        
        # Interaction state
        self.dragging_waypoint: Optional[int] = None
        self.drag_offset = QPointF(0, 0)
        
        # Colors (dark theme)
        self.bg_color = QColor(30, 30, 30)
        self.grid_color = QColor(60, 60, 60)
        self.field_element_colors = {
            'obstacle': QColor(200, 80, 80, 100),
            'target': QColor(80, 200, 80, 100),
            'default': QColor(150, 150, 150, 100)
        }
        self.obstacle_color = QColor(255, 100, 100, 80)
        self.waypoint_color = QColor(100, 150, 255)
        self.waypoint_selected_color = QColor(255, 200, 100)
        self.path_color = QColor(100, 150, 255, 150)
        
    def set_game_preset(self, preset: GamePreset):
        """Set the current game preset"""
        self.game_preset = preset
        self.waypoints.clear()
        self.selected_waypoint = None
        self.update()
        
    def set_obstacles(self, obstacles: List[List[Tuple[float, float]]]):
        """Set obstacle polygons for the current game"""
        self.obstacles = obstacles
        self.update()
        
    def add_waypoint(self, field_x: float, field_y: float) -> int:
        """Add a waypoint at field coordinates"""
        waypoint_id = len(self.waypoints)
        waypoint = Waypoint(field_x, field_y, waypoint_id)
        self.waypoints.append(waypoint)
        self.update()
        return waypoint_id
        
    def remove_waypoint(self, waypoint_id: int):
        """Remove a waypoint by ID"""
        if 0 <= waypoint_id < len(self.waypoints):
            self.waypoints.pop(waypoint_id)
            # Update IDs
            for i, wp in enumerate(self.waypoints):
                wp.id = i
            if self.selected_waypoint == waypoint_id:
                self.selected_waypoint = None
            elif self.selected_waypoint and self.selected_waypoint > waypoint_id:
                self.selected_waypoint -= 1
            self.update()
            
    def clear_waypoints(self):
        """Clear all waypoints"""
        self.waypoints.clear()
        self.selected_waypoint = None
        self.update()
        
    def field_to_screen(self, field_x: float, field_y: float) -> QPointF:
        """Convert field coordinates to screen coordinates"""
        if not self.game_preset:
            return QPointF(0, 0)
            
        # Field origin is bottom-left, screen origin is top-left
        screen_x = self.margin + field_x * self.pixels_per_unit
        screen_y = self.height() - self.margin - field_y * self.pixels_per_unit
        return QPointF(screen_x, screen_y)
        
    def screen_to_field(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """Convert screen coordinates to field coordinates"""
        if not self.game_preset:
            return (0.0, 0.0)
            
        field_x = (screen_x - self.margin) / self.pixels_per_unit
        field_y = (self.height() - screen_y - self.margin) / self.pixels_per_unit
        return (field_x, field_y)
        
    def get_waypoint_at_screen(self, screen_pos: QPointF) -> Optional[int]:
        """Get waypoint ID at screen position, or None"""
        for waypoint in self.waypoints:
            wp_screen = self.field_to_screen(waypoint.x, waypoint.y)
            distance = (wp_screen - screen_pos).manhattanLength()
            if distance <= 15:  # 15 pixel tolerance
                return waypoint.id
        return None
        
    def paintEvent(self, event):
        """Custom paint event"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), self.bg_color)
        
        if not self.game_preset:
            painter.setPen(QColor(100, 100, 100))
            painter.drawText(self.rect(), Qt.AlignCenter, "Select a game to begin")
            return
            
        # Calculate field bounds
        field_width_px = self.game_preset.field_width * self.pixels_per_unit
        field_length_px = self.game_preset.field_length * self.pixels_per_unit
        
        field_rect = self.rect()
        field_rect = field_rect.adjusted(
            self.margin,
            self.height() - self.margin - field_length_px,
            -(self.width() - self.margin - field_width_px),
            -self.margin
        )
        
        # Draw field boundary
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.drawRect(field_rect)
        
        # Draw grid
        self._draw_grid(painter, field_rect)
        
        # Draw field elements
        self._draw_field_elements(painter)
        
        # Draw obstacles
        self._draw_obstacles(painter)
        
        # Draw path
        self._draw_path(painter)
        
        # Draw waypoints
        self._draw_waypoints(painter)
        
    def _draw_grid(self, painter: QPainter, field_rect):
        """Draw field grid"""
        painter.setPen(QPen(self.grid_color, 1))
        
        # Vertical lines
        x = self.margin
        while x <= field_rect.right():
            painter.drawLine(int(x), int(field_rect.top()), int(x), int(field_rect.bottom()))
            x += self.grid_spacing * self.pixels_per_unit
            
        # Horizontal lines
        y = field_rect.bottom()
        while y >= field_rect.top():
            painter.drawLine(int(field_rect.left()), int(y), int(field_rect.right()), int(y))
            y -= self.grid_spacing * self.pixels_per_unit
            
    def _draw_field_elements(self, painter: QPainter):
        """Draw field elements"""
        for element in self.game_preset.field_elements:
            color = self.field_element_colors.get(element.type, self.field_element_colors['default'])
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(150), 1))
            
            top_left = self.field_to_screen(element.x, element.y + element.height)
            width_px = element.width * self.pixels_per_unit
            height_px = element.height * self.pixels_per_unit
            
            rect = painter.drawRect(top_left.x(), top_left.y(), width_px, height_px)
            
            # Draw label
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(int(top_left.x()), int(top_left.y()), 
                           int(width_px), int(height_px), 
                           Qt.AlignCenter, element.name)
            
    def _draw_obstacles(self, painter: QPainter):
        """Draw obstacle polygons"""
        painter.setBrush(QBrush(self.obstacle_color))
        painter.setPen(QPen(self.obstacle_color.darker(150), 1))
        
        for obstacle_points in self.obstacles:
            if len(obstacle_points) < 3:
                continue
                
            polygon = QPolygonF()
            for point in obstacle_points:
                screen_point = self.field_to_screen(point[0], point[1])
                polygon.append(screen_point)
                
            painter.drawPolygon(polygon)
            
    def _draw_path(self, painter: QPainter):
        """Draw path between waypoints"""
        if len(self.waypoints) < 2:
            return
            
        painter.setPen(QPen(self.path_color, 3))
        
        for i in range(len(self.waypoints) - 1):
            start = self.field_to_screen(self.waypoints[i].x, self.waypoints[i].y)
            end = self.field_to_screen(self.waypoints[i + 1].x, self.waypoints[i + 1].y)
            painter.drawLine(start, end)
            
    def _draw_waypoints(self, painter: QPainter):
        """Draw waypoints"""
        for waypoint in self.waypoints:
            center = self.field_to_screen(waypoint.x, waypoint.y)
            
            # Choose color based on selection
            color = self.waypoint_selected_color if waypoint.id == self.selected_waypoint else self.waypoint_color
            
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(color.darker(150), 2))
            
            # Draw waypoint circle
            painter.drawEllipse(center, 8, 8)
            
            # Draw waypoint number
            painter.setPen(QColor(255, 255, 255))
            painter.drawText(center.x() - 10, center.y() - 15, f"{waypoint.id}")
            
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.LeftButton:
            waypoint_id = self.get_waypoint_at_screen(event.localPos())
            
            if waypoint_id is not None:
                # Start dragging waypoint
                self.selected_waypoint = waypoint_id
                self.dragging_waypoint = waypoint_id
                waypoint = self.waypoints[waypoint_id]
                waypoint_screen = self.field_to_screen(waypoint.x, waypoint.y)
                self.drag_offset = event.localPos() - waypoint_screen
                self.waypoint_selected.emit(waypoint_id)
            else:
                # Add new waypoint
                field_x, field_y = self.screen_to_field(event.x(), event.y())
                # Clamp to field bounds
                if (0 <= field_x <= self.game_preset.field_width and 
                    0 <= field_y <= self.game_preset.field_length):
                    waypoint_id = self.add_waypoint(field_x, field_y)
                    self.selected_waypoint = waypoint_id
                    self.waypoint_added.emit(field_x, field_y)
                    self.waypoint_selected.emit(waypoint_id)
                    
            self.update()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if self.dragging_waypoint is not None:
            # Update waypoint position
            new_pos = event.localPos() - self.drag_offset
            field_x, field_y = self.screen_to_field(new_pos.x(), new_pos.y())
            
            # Clamp to field bounds
            field_x = max(0, min(field_x, self.game_preset.field_width))
            field_y = max(0, min(field_y, self.game_preset.field_length))
            
            waypoint = self.waypoints[self.dragging_waypoint]
            waypoint.x = field_x
            waypoint.y = field_y
            
            self.waypoint_moved.emit(self.dragging_waypoint, field_x, field_y)
            self.update()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release events"""
        if event.button() == Qt.LeftButton:
            self.dragging_waypoint = None
            
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Delete and self.selected_waypoint is not None:
            self.remove_waypoint(self.selected_waypoint)