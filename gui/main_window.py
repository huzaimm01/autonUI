"""
Main window for AutonUI
"""
import os
import json
import math
import csv
from typing import Dict, List, Tuple, Optional
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from logic.data_structures import GamePreset, FieldElement
from gui.field_renderer import FieldRenderer

class AutonUIMainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AutonUI - FRC Autonomous Path Planner")
        self.setMinimumSize(1200, 800)
        
        # Data
        self.game_presets: Dict[str, GamePreset] = {}
        self.obstacle_data: Dict[str, List[List[Tuple[float, float]]]] = {}
        self.current_game: Optional[str] = None
        
        # Load data
        self._load_game_presets()
        self._load_obstacle_data()
        
        # Setup UI
        self._setup_ui()
        self._setup_style()
        
    def _setup_ui(self):
        """Setup the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        
        # Left panel
        left_panel = self._create_left_panel()
        main_layout.addWidget(left_panel)
        
        # Field renderer
        self.field_renderer = FieldRenderer()
        self.field_renderer.waypoint_added.connect(self._on_waypoint_added)
        self.field_renderer.waypoint_moved.connect(self._on_waypoint_moved)
        self.field_renderer.waypoint_selected.connect(self._on_waypoint_selected)
        main_layout.addWidget(self.field_renderer, 1)
        
        # Right panel
        right_panel = self._create_right_panel()
        main_layout.addWidget(right_panel)
        
        # Menu bar
        self._create_menu_bar()
        
    def _create_left_panel(self) -> QWidget:
        """Create the left control panel"""
        panel = QWidget()
        panel.setFixedWidth(250)
        layout = QVBoxLayout(panel)
        
        # Game selection
        game_group = QGroupBox("Game Selection")
        game_layout = QVBoxLayout(game_group)
        
        self.game_combo = QComboBox()
        self.game_combo.addItem("Select Game...")
        for game_name in self.game_presets.keys():
            self.game_combo.addItem(game_name)
        self.game_combo.currentTextChanged.connect(self._on_game_changed)
        game_layout.addWidget(self.game_combo)
        
        # Game info
        self.game_info_label = QLabel("No game selected")
        self.game_info_label.setWordWrap(True)
        game_layout.addWidget(self.game_info_label)
        
        layout.addWidget(game_group)
        
        # Path controls
        path_group = QGroupBox("Path Controls")
        path_layout = QVBoxLayout(path_group)
        
        self.clear_path_btn = QPushButton("Clear Path")
        self.clear_path_btn.clicked.connect(self._clear_path)
        path_layout.addWidget(self.clear_path_btn)
        
        self.export_btn = QPushButton("Export Path")
        self.export_btn.clicked.connect(self._export_path)
        path_layout.addWidget(self.export_btn)
        
        self.import_btn = QPushButton("Import Path")
        self.import_btn.clicked.connect(self._import_path)
        path_layout.addWidget(self.import_btn)
        
        layout.addWidget(path_group)
        
        layout.addStretch()
        return panel
        
    def _create_right_panel(self) -> QWidget:
        """Create the right info panel"""
        panel = QWidget()
        panel.setFixedWidth(250)
        layout = QVBoxLayout(panel)
        
        # Waypoint info
        waypoint_group = QGroupBox("Waypoint Info")
        waypoint_layout = QFormLayout(waypoint_group)
        
        self.waypoint_id_label = QLabel("None")
        waypoint_layout.addRow("Selected:", self.waypoint_id_label)
        
        self.waypoint_x_spin = QDoubleSpinBox()
        self.waypoint_x_spin.setRange(0, 100)
        self.waypoint_x_spin.setDecimals(2)
        self.waypoint_x_spin.valueChanged.connect(self._on_waypoint_x_changed)
        waypoint_layout.addRow("X:", self.waypoint_x_spin)
        
        self.waypoint_y_spin = QDoubleSpinBox()
        self.waypoint_y_spin.setRange(0, 100)
        self.waypoint_y_spin.setDecimals(2)
        self.waypoint_y_spin.valueChanged.connect(self._on_waypoint_y_changed)
        waypoint_layout.addRow("Y:", self.waypoint_y_spin)
        
        self.delete_waypoint_btn = QPushButton("Delete Waypoint")
        self.delete_waypoint_btn.clicked.connect(self._delete_selected_waypoint)
        waypoint_layout.addWidget(self.delete_waypoint_btn)
        
        layout.addWidget(waypoint_group)
        
        # Statistics
        stats_group = QGroupBox("Path Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("No path created")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        layout.addWidget(stats_group)
        
        layout.addStretch()
        return panel
        
    def _create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Path", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._clear_path)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Export Path...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_path)
        file_menu.addAction(export_action)
        
        import_action = QAction("Import Path...", self)
        import_action.setShortcut("Ctrl+O")
        import_action.triggered.connect(self._import_path)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    def _setup_style(self):
        """Setup dark theme styling"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 5px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #4a4a4a;
            }
            QPushButton:pressed {
                background-color: #2a2a2a;
            }
            QComboBox, QDoubleSpinBox {
                background-color: #3a3a3a;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 3px;
                min-height: 20px;
            }
            QLabel {
                color: #ffffff;
            }
        """)
        
    def _load_game_presets(self):
        """Load game presets from JSON files"""
        presets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "presets")
        if not os.path.exists(presets_dir):
            os.makedirs(presets_dir)
            # Create sample Charged Up preset
            self._create_sample_preset(presets_dir)
            
        for filename in os.listdir(presets_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(presets_dir, filename), 'r') as f:
                        data = json.load(f)
                    
                    elements = []
                    for elem_data in data.get('field_elements', []):
                        elements.append(FieldElement(**elem_data))
                    
                    preset = GamePreset(
                        name=data['name'],
                        field_width=data['field_width'],
                        field_length=data['field_length'],
                        unit=data.get('unit', 'meters'),
                        point_values=data.get('point_values', {}),
                        field_elements=elements
                    )
                    
                    self.game_presets[preset.name] = preset
                    
                except Exception as e:
                    print(f"Error loading preset {filename}: {e}")
                    
    def _create_sample_preset(self, presets_dir: str):
        """Create sample Charged Up preset"""
        sample_data = {
            "name": "Charged Up",
            "field_width": 8.01,
            "field_length": 16.46,
            "unit": "meters",
            "point_values": {
                "grid": 5,
                "station": 10
            },
            "field_elements": [
                {"name": "Charge Station", "x": 6.5, "y": 6.0, "width": 2.5, "height": 1.2, "type": "obstacle"},
                {"name": "Grid Left", "x": 0.5, "y": 7.0, "width": 0.6, "height": 2.4, "type": "target"},
                {"name": "Grid Right", "x": 15.4, "y": 7.0, "width": 0.6, "height": 2.4, "type": "target"},
                {"name": "Loading Zone", "x": 1.2, "y": 0.5, "width": 3.0, "height": 1.0, "type": "target"}
            ]
        }
        
        with open(os.path.join(presets_dir, "charged_up.json"), 'w') as f:
            json.dump(sample_data, f, indent=2)
            
    def _load_obstacle_data(self):
        """Load obstacle data from JSON files"""
        fieldmaps_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fieldmaps")
        if not os.path.exists(fieldmaps_dir):
            os.makedirs(fieldmaps_dir)
            # Create sample obstacle data
            self._create_sample_obstacles(fieldmaps_dir)
            
        for filename in os.listdir(fieldmaps_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(fieldmaps_dir, filename), 'r') as f:
                        data = json.load(f)
                    
                    for obstacle_set in data.get('obstacles', []):
                        game_name = obstacle_set['game']
                        points = obstacle_set['points']
                        
                        # Convert to tuples
                        polygon = [(float(p[0]), float(p[1])) for p in points]
                        
                        if game_name not in self.obstacle_data:
                            self.obstacle_data[game_name] = []
                        self.obstacle_data[game_name].append(polygon)
                        
                except Exception as e:
                    print(f"Error loading obstacles {filename}: {e}")
                    
    def _create_sample_obstacles(self, fieldmaps_dir: str):
        """Create sample obstacle data"""
        sample_data = {
            "unit": "meters",
            "origin": {"x": 0, "y": 0},
            "dimensions": {"length": 16.46, "width": 8.01},
            "obstacles": [
                {
                    "game": "Charged Up",
                    "points": [[6.0, 5.5], [9.0, 5.5], [9.0, 7.7], [6.0, 7.7]]
                }
            ]
        }
        
        with open(os.path.join(fieldmaps_dir, "obstacles.json"), 'w') as f:
            json.dump(sample_data, f, indent=2)
    
    # Event handlers and other methods continue...
    # (Include all the remaining methods from the original implementation)
    
    def _on_game_changed(self, game_name: str):
        """Handle game selection change"""
        if game_name == "Select Game..." or game_name not in self.game_presets:
            self.current_game = None
            self.field_renderer.set_game_preset(None)
            self.game_info_label.setText("No game selected")
            return
            
        self.current_game = game_name
        preset = self.game_presets[game_name]
        
        # Set field renderer
        self.field_renderer.set_game_preset(preset)
        
        # Load obstacles for this game
        obstacles = self.obstacle_data.get(game_name, [])
        self.field_renderer.set_obstacles(obstacles)
        
        # Update info
        info_text = f"Field: {preset.field_width}×{preset.field_length} {preset.unit}\n"
        info_text += f"Elements: {len(preset.field_elements)}\n"
        info_text += f"Obstacles: {len(obstacles)}"
        self.game_info_label.setText(info_text)
        
        # Update spinbox ranges
        self.waypoint_x_spin.setRange(0, preset.field_width)
        self.waypoint_y_spin.setRange(0, preset.field_length)
        
    def _on_waypoint_added(self, x: float, y: float):
        """Handle waypoint added"""
        self._update_stats()
        
    def _on_waypoint_moved(self, waypoint_id: int, x: float, y: float):
        """Handle waypoint moved"""
        if waypoint_id == self.field_renderer.selected_waypoint:
            self.waypoint_x_spin.blockSignals(True)
            self.waypoint_y_spin.blockSignals(True)
            self.waypoint_x_spin.setValue(x)
            self.waypoint_y_spin.setValue(y)
            self.waypoint_x_spin.blockSignals(False)
            self.waypoint_y_spin.blockSignals(False)
        self._update_stats()
        
    def _on_waypoint_selected(self, waypoint_id: int):
        """Handle waypoint selection"""
        if 0 <= waypoint_id < len(self.field_renderer.waypoints):
            waypoint = self.field_renderer.waypoints[waypoint_id]
            self.waypoint_id_label.setText(f"Waypoint {waypoint_id}")
            
            self.waypoint_x_spin.blockSignals(True)
            self.waypoint_y_spin.blockSignals(True)
            self.waypoint_x_spin.setValue(waypoint.x)
            self.waypoint_y_spin.setValue(waypoint.y)
            self.waypoint_x_spin.blockSignals(False)
            self.waypoint_y_spin.blockSignals(False)
            
            self.waypoint_x_spin.setEnabled(True)
            self.waypoint_y_spin.setEnabled(True)
            self.delete_waypoint_btn.setEnabled(True)
        else:
            self.waypoint_id_label.setText("None")
            self.waypoint_x_spin.setEnabled(False)
            self.waypoint_y_spin.setEnabled(False)
            self.delete_waypoint_btn.setEnabled(False)
        
    def _on_waypoint_x_changed(self, value: float):
        """Handle waypoint X coordinate change"""
        if self.field_renderer.selected_waypoint is not None:
            waypoint = self.field_renderer.waypoints[self.field_renderer.selected_waypoint]
            waypoint.x = value
            self.field_renderer.update()
            self._update_stats()
            
    def _on_waypoint_y_changed(self, value: float):
        """Handle waypoint Y coordinate change"""
        if self.field_renderer.selected_waypoint is not None:
            waypoint = self.field_renderer.waypoints[self.field_renderer.selected_waypoint]
            waypoint.y = value
            self.field_renderer.update()
            self._update_stats()
            
    def _delete_selected_waypoint(self):
        """Delete the currently selected waypoint"""
        if self.field_renderer.selected_waypoint is not None:
            self.field_renderer.remove_waypoint(self.field_renderer.selected_waypoint)
            self.waypoint_id_label.setText("None")
            self.waypoint_x_spin.setEnabled(False)
            self.waypoint_y_spin.setEnabled(False)
            self.delete_waypoint_btn.setEnabled(False)
            self._update_stats()
            
    def _clear_path(self):
        """Clear all waypoints"""
        self.field_renderer.clear_waypoints()
        self.waypoint_id_label.setText("None")
        self.waypoint_x_spin.setEnabled(False)
        self.waypoint_y_spin.setEnabled(False)
        self.delete_waypoint_btn.setEnabled(False)
        self._update_stats()
        
    def _update_stats(self):
        """Update path statistics"""
        waypoints = self.field_renderer.waypoints
        
        if len(waypoints) == 0:
            self.stats_label.setText("No path created")
            return
            
        if len(waypoints) == 1:
            self.stats_label.setText(f"Path: 1 waypoint\n"
                                   f"Position: ({waypoints[0].x:.2f}, {waypoints[0].y:.2f})")
            return
            
        # Calculate total path length
        total_length = 0.0
        for i in range(len(waypoints) - 1):
            dx = waypoints[i+1].x - waypoints[i].x
            dy = waypoints[i+1].y - waypoints[i].y
            total_length += math.sqrt(dx*dx + dy*dy)
            
        unit = self.game_presets[self.current_game].unit if self.current_game else "units"
        
        stats_text = f"Path: {len(waypoints)} waypoints\n"
        stats_text += f"Total length: {total_length:.2f} {unit}\n"
        stats_text += f"Start: ({waypoints[0].x:.2f}, {waypoints[0].y:.2f})\n"
        stats_text += f"End: ({waypoints[-1].x:.2f}, {waypoints[-1].y:.2f})"
        
        self.stats_label.setText(stats_text)
        
    def _export_path(self):
        """Export path to JSON file"""
        if not self.field_renderer.waypoints:
            QMessageBox.information(self, "Export Path", "No path to export!")
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Path", "path.json", "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if not filename:
            return
            
        try:
            export_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "export")
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
                
            waypoints_data = []
            for wp in self.field_renderer.waypoints:
                waypoints_data.append({
                    "id": wp.id,
                    "x": wp.x,
                    "y": wp.y
                })
                
            if filename.endswith('.json'):
                export_data = {
                    "game": self.current_game,
                    "unit": self.game_presets[self.current_game].unit if self.current_game else "meters",
                    "waypoints": waypoints_data,
                    "created": QDateTime.currentDateTime().toString(Qt.ISODate)
                }
                
                with open(filename, 'w') as f:
                    json.dump(export_data, f, indent=2)
                    
            elif filename.endswith('.csv'):
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'X', 'Y'])
                    for wp in self.field_renderer.waypoints:
                        writer.writerow([wp.id, wp.x, wp.y])
                        
            QMessageBox.information(self, "Export Path", f"Path exported successfully to:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export path:\n{str(e)}")
            
    def _import_path(self):
        """Import path from JSON file"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Import Path", "", "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if not filename:
            return
            
        try:
            self.field_renderer.clear_waypoints()
            
            if filename.endswith('.json'):
                with open(filename, 'r') as f:
                    data = json.load(f)
                    
                # Check if game matches
                if 'game' in data and data['game'] != self.current_game:
                    reply = QMessageBox.question(
                        self, "Game Mismatch",
                        f"Path was created for '{data['game']}' but current game is '{self.current_game}'.\n"
                        "Continue importing?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        return
                        
                for wp_data in data.get('waypoints', []):
                    self.field_renderer.add_waypoint(wp_data['x'], wp_data['y'])
                    
            elif filename.endswith('.csv'):
                with open(filename, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        x = float(row['X'])
                        y = float(row['Y'])
                        self.field_renderer.add_waypoint(x, y)
                        
            self._update_stats()
            QMessageBox.information(self, "Import Path", f"Path imported successfully from:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Import Error", f"Failed to import path:\n{str(e)}")
            
    def _show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About AutonUI", 
                         "AutonUI v1.0\n\n"
                         "Advanced FRC Autonomous Path Planning Tool\n\n"
                         "Features:\n"
                         "• Visual field representation\n"
                         "• Drag-and-drop waypoint editing\n"
                         "• Multiple game support\n"
                         "• Obstacle visualization\n"
                         "• Path export/import\n\n"
                         "Click to add waypoints, drag to move them.\n"
                         "Use Delete key to remove selected waypoint.")