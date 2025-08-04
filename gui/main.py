import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QResizeEvent
from OpenGL.GL import (
    glDeleteTextures, glGenTextures, glBindTexture, glTexParameteri, glTexImage2D,
    glClearColor, glEnable, glBlendFunc, glViewport, glMatrixMode, glLoadIdentity,
    glOrtho, glClear, glBegin, glTexCoord2f, glVertex2f, glEnd, glColor4f,

    GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR,
    GL_RGBA, GL_UNSIGNED_BYTE, GL_BLEND,GL_LINES, GL_QUADS, GL_LINE_LOOP, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
    GL_PROJECTION, GL_MODELVIEW, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_LINES, GL_QUADS, GL_LINE_STRIP, GL_LINES, GL_QUADS, GL_LINE_LOOP
)
from OpenGL.GLU import gluOrtho2D
from PIL import Image
from app import GameConfig, RobotConfig, PathPlanner, Utils


class OpenGLField(QGLWidget):
    def __init__(self, parent=None):
        super(OpenGLField, self).__init__(parent)
        self.path = []
        self.elements = []
        self.polygon_obstacles = []
        self.field_dims = (7.925, 16.46)
        self.margin = 0
        self.texture_id = None
        self.setMinimumSize(400, 300)  # Set a reasonable minimum size
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)  # Make field expand
        self.pending_background = None
        self.initialized = False

    def set_data(self, field_dims, path, elements, polygon_obstacles=None):
        self.field_dims = field_dims
        self.path = path
        self.elements = elements
        self.polygon_obstacles = polygon_obstacles if polygon_obstacles else []
        self.update()

    def set_background(self, game_name):
        # Try multiple possible naming conventions for the field background
        possible_filenames = [
            f"{game_name.lower().replace(' ', '_')}.png",
            f"{game_name.lower()}.png",
            f"{game_name.replace(' ', '_')}.png",
            f"{game_name}.png"
        ]
        
        # Search in multiple possible locations
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "assets", "field_backgrounds"),
            os.path.join(os.path.dirname(__file__), "..", "assets", "field_backgrounds"),
            os.path.join(os.path.dirname(__file__), "assets"),
            os.path.join(os.path.dirname(__file__), "..", "assets")
        ]
        
        file_found = None
        for path in possible_paths:
            if os.path.exists(path):
                for filename in possible_filenames:
                    file_path = os.path.join(path, filename)
                    if os.path.exists(file_path):
                        file_found = file_path
                        break
                if file_found:
                    break
        
        if file_found:
            print(f"Loading field background from: {file_found}")
            if self.initialized:
                self._load_texture(file_found)
            else:
                # Store the file path to load after initialization
                self.pending_background = file_found
        else:
            print(f"Warning: Could not find background image for game '{game_name}'")
            print(f"Looked for: {possible_filenames}")
            print(f"In directories: {possible_paths}")

    def _load_texture(self, file_path):
        try:
            image = Image.open(file_path).convert("RGBA")
            ix, iy = image.size
            image_data = image.tobytes("raw", "RGBA", 0, -1)

            if self.texture_id:
                glDeleteTextures([self.texture_id])
                
            self.texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            self.update()
        except Exception as e:
            print(f"Error loading texture: {e}")

    def initializeGL(self):
        glClearColor(0.05, 0.07, 0.1, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)
        
        self.initialized = True
        
        # Load any pending background
        if self.pending_background:
            self._load_texture(self.pending_background)
            self.pending_background = None

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        # Calculate proper aspect ratio to prevent squishing
        aspect_ratio = w / h if h > 0 else 1
        field_aspect_ratio = self.field_dims[0] / self.field_dims[1]
        
        # Adjust the view to maintain proper aspect ratio
        if aspect_ratio > field_aspect_ratio:
            # Window is wider than field
            height = self.field_dims[1]
            width = height * aspect_ratio
            offset_x = (width - self.field_dims[0]) / 2
            glOrtho(-offset_x, self.field_dims[0] + offset_x, self.field_dims[1], 0, -1, 1)
        else:
            # Window is taller than field
            width = self.field_dims[0]
            height = width / aspect_ratio
            offset_y = (height - self.field_dims[1]) / 2
            glOrtho(0, self.field_dims[0], self.field_dims[1] + offset_y, -offset_y, -1, 1)
            
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        if self.texture_id:
            glColor4f(1.0, 1.0, 1.0, 1.0)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 1.0); glVertex2f(0, 0)
            glTexCoord2f(1.0, 1.0); glVertex2f(self.field_dims[0], 0)
            glTexCoord2f(1.0, 0.0); glVertex2f(self.field_dims[0], self.field_dims[1])
            glTexCoord2f(0.0, 0.0); glVertex2f(0, self.field_dims[1])
            glEnd()

        # Grid
        glColor4f(0.2, 0.3, 0.4, 0.4)
        for x in range(int(self.field_dims[0]) + 1):
            glBegin(GL_LINES)
            glVertex2f(x, 0)
            glVertex2f(x, self.field_dims[1])
            glEnd()
        for y in range(int(self.field_dims[1]) + 1):
            glBegin(GL_LINES)
            glVertex2f(0, y)
            glVertex2f(self.field_dims[0], y)
            glEnd()

        # Obstacles
        glColor4f(1.0, 0.5, 0.1, 0.8)
        for poly in self.polygon_obstacles:
            glBegin(GL_LINE_LOOP)
            for pt in poly:
                glVertex2f(pt["x"], pt["y"])
            glEnd()

        # Field elements
        grouped = Utils.group_elements_by_type(self.elements)
        glColor4f(0.8, 0.2, 0.2, 0.7)
        for e in grouped.get("obstacle", []):
            self._draw_rect(e)
        glColor4f(0.95, 0.85, 0.1, 0.9)
        for e in grouped.get("note", []):
            self._draw_rect(e)
        glColor4f(0.2, 1.0, 0.4, 0.5)
        for e in grouped.get("target", []):
            self._draw_rect(e)

        # Path
        if self.path:
            glColor4f(0.0, 1.0, 1.0, 1.0)
            glBegin(GL_LINE_STRIP)
            for pt in self.path:
                glVertex2f(pt[0], pt[1])
            glEnd()

    def _draw_rect(self, e):
        x, y = e["x"], e["y"]
        w, h = e.get("width", 1.0), e.get("height", 1.0)
        glBegin(GL_QUADS)
        glVertex2f(x - w / 2, y - h / 2)
        glVertex2f(x + w / 2, y - h / 2)
        glVertex2f(x + w / 2, y + h / 2)
        glVertex2f(x - w / 2, y + h / 2)
        glEnd()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "layout.ui"), self)
        self.apply_theme("dark")

        # Get the field preview container widget - with fallback if not found
        self.fieldPreviewContainer = self.findChild(QtWidgets.QWidget, "fieldPreview")
        
        # If fieldPreview widget doesn't exist in the UI, create a sensible fallback container
        if not self.fieldPreviewContainer:
            print("Warning: 'fieldPreview' widget not found in UI file! Creating fallback container.")
            # Find the right-side widget where field preview should go
            rightContainer = self.findChild(QtWidgets.QWidget, "rightPanel")
            
            if not rightContainer:
                # If no right panel exists either, use the central widget as fallback
                rightContainer = self.centralWidget()
                
            # Create a new widget to serve as our field preview container
            self.fieldPreviewContainer = QtWidgets.QWidget(rightContainer)
            self.fieldPreviewContainer.setObjectName("fieldPreview")
            
            # Add it to the layout
            if rightContainer.layout():
                rightContainer.layout().addWidget(self.fieldPreviewContainer)
            else:
                # If no layout exists, create one
                newLayout = QtWidgets.QVBoxLayout(rightContainer)
                newLayout.addWidget(self.fieldPreviewContainer)
                rightContainer.setLayout(newLayout)
        
        # Create a proper layout for the field preview if it doesn't exist
        if not self.fieldPreviewContainer.layout():
            self.fieldPreviewLayout = QtWidgets.QVBoxLayout(self.fieldPreviewContainer)
            self.fieldPreviewLayout.setContentsMargins(0, 0, 0, 0)
            self.fieldPreviewContainer.setLayout(self.fieldPreviewLayout)
        else:
            self.fieldPreviewLayout = self.fieldPreviewContainer.layout()
            
        # Create and add the OpenGL widget to the field preview area
        self.fieldWidget = OpenGLField(self.fieldPreviewContainer)
        self.fieldPreviewLayout.addWidget(self.fieldWidget)

        # Set up the splitter to give proper space to the field preview
        mainSplitter = self.findChild(QtWidgets.QSplitter, "mainSplitter")
        if mainSplitter:
            # Set reasonable initial sizes (adjust as needed)
            mainSplitter.setSizes([400, 600])  # Left panels, right field preview
            
        # Additional setup for better field display
        if hasattr(self, 'fieldWidget'):
            # Force the OpenGL widget to take as much space as possible
            sizePolicy = QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Expanding, 
                QtWidgets.QSizePolicy.Expanding
            )
            sizePolicy.setHorizontalStretch(3)
            sizePolicy.setVerticalStretch(3)
            self.fieldWidget.setSizePolicy(sizePolicy)

        # Find and connect UI controls (with fallbacks if they don't exist)
        self.findAndConnectUIControls()

        self.games = {}
        self.populate_games()
        self.toggle_field_mode()
        
        # Update the field background after the widget is shown
        QTimer.singleShot(100, lambda: self.update_background(self.gameSelect.currentText()))

    def findAndConnectUIControls(self):
        """Find all the UI controls and connect them with fallbacks if they don't exist"""
        # Find all necessary UI elements with fallbacks
        self.planButton = self.findChildWithFallback(QtWidgets.QPushButton, "planButton")
        self.officialFieldCheck = self.findChildWithFallback(QtWidgets.QCheckBox, "officialFieldCheck")
        self.addGoalButton = self.findChildWithFallback(QtWidgets.QPushButton, "addGoalButton")
        self.removeGoalButton = self.findChildWithFallback(QtWidgets.QPushButton, "removeGoalButton")
        self.clearGoalsButton = self.findChildWithFallback(QtWidgets.QPushButton, "clearGoalsButton")
        self.gameSelect = self.findChildWithFallback(QtWidgets.QComboBox, "gameSelect")
        self.goalList = self.findChildWithFallback(QtWidgets.QListWidget, "goalList")
        self.goalX = self.findChildWithFallback(QtWidgets.QLineEdit, "goalX")
        self.goalY = self.findChildWithFallback(QtWidgets.QLineEdit, "goalY")
        self.fieldWidth = self.findChildWithFallback(QtWidgets.QLineEdit, "fieldWidth")
        self.fieldLength = self.findChildWithFallback(QtWidgets.QLineEdit, "fieldLength")
        self.robotWidth = self.findChildWithFallback(QtWidgets.QLineEdit, "robotWidth")
        self.robotLength = self.findChildWithFallback(QtWidgets.QLineEdit, "robotLength")
        self.robotHeight = self.findChildWithFallback(QtWidgets.QLineEdit, "robotHeight")
        self.startX = self.findChildWithFallback(QtWidgets.QLineEdit, "startX")
        self.startY = self.findChildWithFallback(QtWidgets.QLineEdit, "startY")
        self.resultBox = self.findChildWithFallback(QtWidgets.QTextEdit, "resultBox")
        
        # Connect signals to slots if the UI elements exist
        if self.planButton:
            self.planButton.clicked.connect(self.plan_path)
        if self.officialFieldCheck:
            self.officialFieldCheck.stateChanged.connect(self.toggle_field_mode)
        if self.addGoalButton:
            self.addGoalButton.clicked.connect(self.add_goal)
        if self.removeGoalButton:
            self.removeGoalButton.clicked.connect(self.remove_selected_goal)
        if self.clearGoalsButton:
            self.clearGoalsButton.clicked.connect(self.clear_goals)
        if self.gameSelect:
            self.gameSelect.currentTextChanged.connect(self.update_background)

    def findChildWithFallback(self, widgetType, name):
        """Find a child widget by name and type with a fallback if not found"""
        widget = self.findChild(widgetType, name)
        if widget is None:
            print(f"Warning: UI element '{name}' not found! Some functionality may be limited.")
            
            # Create fallback widgets for essential controls
            if name == "gameSelect":
                widget = QtWidgets.QComboBox(self)
                widget.setObjectName(name)
            elif name == "resultBox":
                widget = QtWidgets.QTextEdit(self)
                widget.setObjectName(name)
            # Add more fallbacks for critical widgets if needed
                
        return widget

    def apply_theme(self, theme):
        file = "style_dark.qss" if theme == "dark" else "style_light.qss"
        path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(path):
            with open(path, "r") as f:
                self.setStyleSheet(f.read())

    def populate_games(self):
        if not hasattr(self, 'gameSelect') or self.gameSelect is None:
            print("Cannot populate games: gameSelect widget not found")
            return
            
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        
        # Check if data directory exists
        if not os.path.exists(data_dir):
            print(f"Warning: Data directory not found at {data_dir}")
            self.resultBox.setText(f"Error: Data directory not found at {data_dir}")
            return
            
        try:
            for file in os.listdir(data_dir):
                if file.endswith(".json"):
                    try:
                        game = GameConfig.from_file(os.path.join(data_dir, file))
                        self.games[game.name] = game
                        self.gameSelect.addItem(game.name)
                    except Exception as e:
                        print(f"Error loading game config {file}: {e}")
        except Exception as e:
            print(f"Error accessing data directory: {e}")
            self.resultBox.setText(f"Error accessing game data: {e}")

    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize events to ensure field preview gets proper space."""
        super().resizeEvent(event)
        # Make sure the OpenGL widget gets updated when window is resized
        if hasattr(self, 'fieldWidget'):
            self.fieldWidget.update()

    def update_background(self, game_name):
        if not game_name:
            print("No game selected, skipping background update")
            return
        
        print(f"Updating background for game: {game_name}")
        self.fieldWidget.set_background(game_name)
        game = self.games.get(game_name)
        if game:
            # Get field dimensions for this specific game
            dims = (game.field_width, game.field_length)
            print(f"Field dimensions: {dims}")
            
            # Get field elements
            elements = [e.to_dict() if hasattr(e, "to_dict") else e for e in game.field_elements]
            
            # Look for obstacles file in multiple locations
            obstacle_paths = [
                os.path.join(os.path.dirname(__file__), "..", "frc_field_grid_with_obstacles.json"),
                os.path.join(os.path.dirname(__file__), "frc_field_grid_with_obstacles.json"),
                os.path.join(os.path.dirname(__file__), "..", "data", "frc_field_grid_with_obstacles.json"),
                os.path.join(os.path.dirname(__file__), "data", "frc_field_grid_with_obstacles.json")
            ]
            
            polygons = []
            for obstacle_path in obstacle_paths:
                if os.path.exists(obstacle_path):
                    try:
                        polygons = Utils.get_polygon_obstacles(game_name, obstacle_path)
                        print(f"Loaded polygon obstacles from: {obstacle_path}")
                        break
                    except Exception as e:
                        print(f"Warning: Could not load polygon obstacles from {obstacle_path}: {e}")
            
            # Force a complete reset of the field data
            self.fieldWidget.set_data(dims, [], elements, polygon_obstacles=polygons)
            
            # Force OpenGL field to update
            self.fieldWidget.update()
            self.fieldWidget.repaint()
            
            # Print status to help debug
            print(f"Updated field data with {len(elements)} elements and {len(polygons)} obstacles")
            
            # Update UI elements based on game
            if hasattr(self, 'fieldWidth') and hasattr(self, 'fieldLength'):
                self.fieldWidth.setText(str(game.field_width))
                self.fieldLength.setText(str(game.field_length))

    def toggle_field_mode(self):
        if not hasattr(self, 'fieldWidth') or not hasattr(self, 'fieldLength') or \
           not hasattr(self, 'officialFieldCheck'):
            print("Missing UI elements for toggle_field_mode")
            return
            
        self.fieldWidth.setDisabled(self.officialFieldCheck.isChecked())
        self.fieldLength.setDisabled(self.officialFieldCheck.isChecked())

    def add_goal(self):
        if not hasattr(self, 'goalX') or not hasattr(self, 'goalY') or not hasattr(self, 'goalList'):
            print("Missing UI elements for add_goal")
            return
            
        x = self.goalX.text().strip()
        y = self.goalY.text().strip()
        if x and y:
            self.goalList.addItem(f"{x}, {y}")
            self.goalX.clear()
            self.goalY.clear()

    def remove_selected_goal(self):
        if not hasattr(self, 'goalList'):
            print("Missing UI elements for remove_selected_goal")
            return
            
        row = self.goalList.currentRow()
        if row >= 0:
            self.goalList.takeItem(row)

    def clear_goals(self):
        if not hasattr(self, 'goalList'):
            print("Missing UI elements for clear_goals")
            return
            
        self.goalList.clear()

    def plan_path(self):
        # Check if all required UI elements are available
        required_widgets = ['gameSelect', 'officialFieldCheck', 'fieldWidth', 'fieldLength',
                           'robotWidth', 'robotLength', 'robotHeight', 'startX', 'startY', 
                           'goalList', 'resultBox', 'fieldWidget']
                           
        for widget_name in required_widgets:
            if not hasattr(self, widget_name) or getattr(self, widget_name) is None:
                error_msg = f"Missing UI element: {widget_name}. Cannot plan path."
                print(error_msg)
                if hasattr(self, 'resultBox') and self.resultBox:
                    self.resultBox.setText(error_msg)
                return
                
        try:    
            game_name = self.gameSelect.currentText()
            if not game_name or game_name not in self.games:
                self.resultBox.setText("No game selected or game not found.")
                return
                
            game = self.games[game_name]
            official = self.officialFieldCheck.isChecked()

            try:
                if official:
                    fw, fl = Utils.get_official_field_dimensions(game.name)
                    elements = Utils.get_official_elements(game.name)
                else:
                    fw = float(self.fieldWidth.text())
                    fl = float(self.fieldLength.text())
                    elements = [e.to_dict() if hasattr(e, 'to_dict') else e for e in game.field_elements]

                robot = RobotConfig(
                    width=float(self.robotWidth.text()),
                    length=float(self.robotLength.text()),
                    height=float(self.robotHeight.text()),
                    max_velocity=2.0,
                    max_acceleration=1.0,
                    drivetrain="swerve"
                )

                start = (float(self.startX.text()), float(self.startY.text()))
                goals = []
                for i in range(self.goalList.count()):
                    gx, gy = map(float, self.goalList.item(i).text().split(','))
                    goals.append((gx, gy))

            except ValueError as e:
                self.resultBox.setText(f"Enter valid numeric values: {str(e)}")
                return

            planner = PathPlanner(game, robot)
            path = planner.plan_path(start, goals)
            path = Utils.smooth_catmull_rom_path(path) if path else []

            if not path:
                self.resultBox.setText("No valid path found.")
            else:
                self.resultBox.setText("\n".join([f"{p[0]:.2f}, {p[1]:.2f}" for p in path]))
                self.fieldWidget.set_data((fw, fl), path, elements, self.fieldWidget.polygon_obstacles)
                try:
                    Utils.write_path_to_json(path)
                    Utils.write_path_to_csv(path)
                except Exception as e:
                    print(f"Warning: Could not write path to files: {e}")
                    
        except Exception as e:
            error_msg = f"Error planning path: {str(e)}"
            print(error_msg)
            self.resultBox.setText(error_msg)


def launch_gui():
    app = QtWidgets.QApplication(sys.argv)
    try:
        window = MainWindow()
        window.showMaximized()
        sys.exit(app.exec_())
    except Exception as e:
        error_dialog = QtWidgets.QMessageBox()
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setText(f"Error launching application: {str(e)}")
        error_dialog.setWindowTitle("Application Error")
        error_dialog.setDetailedText(f"Details:\n{str(e)}")
        error_dialog.exec_()
        sys.exit(1)