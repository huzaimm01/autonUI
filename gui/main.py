import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GL import (
    glDeleteTextures, glGenTextures, glBindTexture, glTexParameteri, glTexImage2D,
    glClearColor, glEnable, glBlendFunc, glViewport, glMatrixMode, glLoadIdentity,
    glOrtho, glClear, glBegin, glTexCoord2f, glVertex2f, glEnd, glColor4f,

    GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_TEXTURE_MAG_FILTER, GL_LINEAR,
    GL_RGBA, GL_UNSIGNED_BYTE, GL_BLEND, GL_LINES, GL_QUADS, GL_LINE_LOOP, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA,
    GL_PROJECTION, GL_MODELVIEW, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_LINES, GL_QUADS, GL_LINE_STRIP, GL_LINE_LOOP
)
from PIL import Image
from app import GameConfig, RobotConfig, PathPlanner, Utils


class OpenGLField(QGLWidget):
    def __init__(self, parent=None):
        super(OpenGLField, self).__init__(parent)
        self.path = []
        self.elements = []
        self.polygon_obstacles = []
        self.field_dims = (7.925, 16.46)  
        self.margin = 0.5 
        self.texture_id = None

    def set_data(self, field_dims, path, elements, polygon_obstacles=None):
        self.field_dims = field_dims
        self.path = path
        self.elements = elements
        self.polygon_obstacles = polygon_obstacles if polygon_obstacles else []
        self.update()

    def set_background(self, game_name):
        file = os.path.join(os.path.dirname(__file__), "assets", "field_backgrounds", f"{game_name.lower().replace(' ', '_')}.png")
        print("Loading field background from:", file)
        if os.path.exists(file):
            image = Image.open(file).convert("RGBA")
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

    def initializeGL(self):
        glClearColor(0.05, 0.07, 0.1, 1)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_TEXTURE_2D)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        
        
        field_aspect = self.field_dims[0] / self.field_dims[1]
        widget_aspect = w / h
        
        
        x_margin = self.margin
        y_margin = self.margin
        
        if widget_aspect > field_aspect:
            
            y_view = self.field_dims[1] + 2*y_margin
            x_view = y_view * widget_aspect
            x_center = self.field_dims[0] / 2
            y_center = self.field_dims[1] / 2
            glOrtho(
                x_center - x_view/2, 
                x_center + x_view/2, 
                y_center + y_view/2, 
                y_center - y_view/2, 
                -1, 1
            )
        else:
            # Widget is taller than field
            x_view = self.field_dims[0] + 2*x_margin
            y_view = x_view / widget_aspect
            x_center = self.field_dims[0] / 2
            y_center = self.field_dims[1] / 2
            glOrtho(
                x_center - x_view/2, 
                x_center + x_view/2, 
                y_center + y_view/2, 
                y_center - y_view/2, 
                -1, 1
            )
            
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Draw field background
        if self.texture_id:
            glColor4f(1.0, 1.0, 1.0, 1.0)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(0, 0)
            glTexCoord2f(1.0, 0.0); glVertex2f(self.field_dims[0], 0)
            glTexCoord2f(1.0, 1.0); glVertex2f(self.field_dims[0], self.field_dims[1])
            glTexCoord2f(0.0, 1.0); glVertex2f(0, self.field_dims[1])
            glEnd()

        # Draw grid
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

        # Draw field border
        glColor4f(0.6, 0.6, 0.6, 0.8)
        glBegin(GL_LINE_LOOP)
        glVertex2f(0, 0)
        glVertex2f(self.field_dims[0], 0)
        glVertex2f(self.field_dims[0], self.field_dims[1])
        glVertex2f(0, self.field_dims[1])
        glEnd()

        # Draw obstacles
        glColor4f(1.0, 0.5, 0.1, 0.8)
        for poly in self.polygon_obstacles:
            glBegin(GL_LINE_LOOP)
            for pt in poly:
                glVertex2f(pt["x"], pt["y"])
            glEnd()

        # Draw field elements
        try:
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
        except Exception as e:
            print(f"Error drawing elements: {e}")

        # Draw path
        if self.path:
            glColor4f(0.0, 1.0, 1.0, 1.0)
            glBegin(GL_LINE_STRIP)
            for pt in self.path:
                glVertex2f(pt[0], pt[1])
            glEnd()
            
            # Draw path points
            glColor4f(1.0, 1.0, 0.0, 1.0)
            for pt in self.path:
                glBegin(GL_QUADS)
                glVertex2f(pt[0] - 0.1, pt[1] - 0.1)
                glVertex2f(pt[0] + 0.1, pt[1] - 0.1)
                glVertex2f(pt[0] + 0.1, pt[1] + 0.1)
                glVertex2f(pt[0] - 0.1, pt[1] + 0.1)
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
        
        # Apply dark theme
        self.apply_theme("dark")
        
        # Set up OpenGL widget
        self.openGLContainer = self.findChild(QtWidgets.QWidget, "openGLContainer")
        if self.openGLContainer:
            if not self.openGLContainer.layout():
                self.openGLContainer.setLayout(QtWidgets.QVBoxLayout())
            
            self.fieldWidget = OpenGLField(self.openGLContainer)
            self.openGLContainer.layout().addWidget(self.fieldWidget)
            
            # Make OpenGL widget expand to fill available space
            self.openGLContainer.layout().setContentsMargins(0, 0, 0, 0)
            self.fieldWidget.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding,
                QtWidgets.QSizePolicy.Expanding
            )
        
        # Set up field dimensions
        self.fieldWidth = self.findChild(QtWidgets.QLineEdit, "fieldWidth")
        self.fieldLength = self.findChild(QtWidgets.QLineEdit, "fieldLength")
        self.fieldWidth.setText("7.925")
        self.fieldLength.setText("16.46")
        
        # Set up robot dimensions
        self.robotWidth = self.findChild(QtWidgets.QLineEdit, "robotWidth")
        self.robotLength = self.findChild(QtWidgets.QLineEdit, "robotLength")
        self.robotHeight = self.findChild(QtWidgets.QLineEdit, "robotHeight")
        self.robotWidth.setText("0.9")
        self.robotLength.setText("0.9")
        self.robotHeight.setText("0.9")
        
        # Set up start coordinates
        self.startX = self.findChild(QtWidgets.QLineEdit, "startX")
        self.startY = self.findChild(QtWidgets.QLineEdit, "startY")
        self.startX.setText("1.0")
        self.startY.setText("1.0")
        
        # Set up goal coordinates
        self.goalX = self.findChild(QtWidgets.QLineEdit, "goalX")
        self.goalY = self.findChild(QtWidgets.QLineEdit, "goalY")
        self.goalList = self.findChild(QtWidgets.QListWidget, "goalList")
        
        # Set up buttons
        self.officialFieldCheck = self.findChild(QtWidgets.QCheckBox, "officialFieldCheck")
        self.addGoalButton = self.findChild(QtWidgets.QPushButton, "addGoalButton")
        self.removeGoalButton = self.findChild(QtWidgets.QPushButton, "removeGoalButton")
        self.clearGoalsButton = self.findChild(QtWidgets.QPushButton, "clearGoalsButton")
        self.planButton = self.findChild(QtWidgets.QPushButton, "planButton")
        
        # Set up result box
        self.resultBox = self.findChild(QtWidgets.QTextEdit, "resultBox")
        
        # Set up game selector
        self.gameSelect = self.findChild(QtWidgets.QComboBox, "gameSelect")
        
        # Set up data
        self.games = {}
        self.populate_games()
        self.toggle_field_mode()
        
        # Connect signals
        self.planButton.clicked.connect(self.plan_path)
        self.officialFieldCheck.stateChanged.connect(self.toggle_field_mode)
        self.addGoalButton.clicked.connect(self.add_goal)
        self.removeGoalButton.clicked.connect(self.remove_selected_goal)
        self.clearGoalsButton.clicked.connect(self.clear_goals)
        self.gameSelect.currentTextChanged.connect(self.update_background)

    def apply_theme(self, theme):
        file = "style_dark.qss" if theme == "dark" else "style_light.qss"
        path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(path):
            with open(path, "r") as f:
                self.setStyleSheet(f.read())

    def populate_games(self):
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith(".json"):
                    try:
                        game = GameConfig.from_file(os.path.join(data_dir, file))
                        self.games[game.name] = game
                        self.gameSelect.addItem(game.name)
                    except Exception as e:
                        print(f"Error loading game config from {file}: {e}")
            
            # Set default field dimensions if a game is selected
            if self.gameSelect.count() > 0:
                self.update_background(self.gameSelect.currentText())
            else:
                # If no games were loaded, use default dimensions
                self.fieldWidget.set_data((7.925, 16.46), [], [])

    def update_background(self, game_name):
        self.fieldWidget.set_background(game_name)
        game = self.games.get(game_name)
        if game:
            dims = (game.field_width, game.field_length)
            self.fieldWidth.setText(str(game.field_width))
            self.fieldLength.setText(str(game.field_length))
            
            elements = []
            try:
                elements = [e.to_dict() if hasattr(e, "to_dict") else e for e in game.field_elements]
            except Exception as e:
                print(f"Error converting elements: {e}")
                
            obstacle_path = os.path.join(os.path.dirname(__file__), "..", "frc_field_grid_with_obstacles.json")
            polygons = []
            try:
                polygons = Utils.get_polygon_obstacles(game_name, obstacle_path)
            except Exception as e:
                print(f"Error loading obstacles: {e}")
                
            self.fieldWidget.set_data(dims, [], elements, polygon_obstacles=polygons)
            self.fieldWidget.update()

    def toggle_field_mode(self):
        self.fieldWidth.setDisabled(self.officialFieldCheck.isChecked())
        self.fieldLength.setDisabled(self.officialFieldCheck.isChecked())

    def add_goal(self):
        x = self.goalX.text().strip()
        y = self.goalY.text().strip()
        if x and y:
            try:
                float_x = float(x)
                float_y = float(y)
                self.goalList.addItem(f"{float_x}, {float_y}")
                self.goalX.clear()
                self.goalY.clear()
            except ValueError:
                self.resultBox.setText("Please enter valid numeric values for goal coordinates.")

    def remove_selected_goal(self):
        row = self.goalList.currentRow()
        if row >= 0:
            self.goalList.takeItem(row)

    def clear_goals(self):
        self.goalList.clear()

    def plan_path(self):
        game_name = self.gameSelect.currentText()
        if not game_name:
            self.resultBox.setText("Please select a game.")
            return
            
        game = self.games.get(game_name)
        if not game:
            self.resultBox.setText(f"Game '{game_name}' not found.")
            return
            
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
                text = self.goalList.item(i).text()
                coords = text.split(',')
                if len(coords) == 2:
                    gx, gy = float(coords[0]), float(coords[1])
                    goals.append((gx, gy))
                    
            if not goals:
                self.resultBox.setText("Please add at least one goal point.")
                return

        except ValueError as e:
            self.resultBox.setText(f"Error: {str(e)}\nPlease enter valid numeric values.")
            return
        except Exception as e:
            self.resultBox.setText(f"Error: {str(e)}")
            return

        
        try:
            planner = PathPlanner(game, robot)
            path = planner.plan_path(start, goals)
            
            if path:
                
                path = Utils.smooth_catmull_rom_path(path)
                
                
                self.resultBox.setText("\n".join([f"{p[0]:.2f}, {p[1]:.2f}" for p in path]))
                self.fieldWidget.set_data((fw, fl), path, elements, self.fieldWidget.polygon_obstacles)
                
                
                try:
                    Utils.write_path_to_json(path)
                    Utils.write_path_to_csv(path)
                    self.resultBox.append("\nPath saved to JSON and CSV files.")
                except Exception as e:
                    self.resultBox.append(f"\nError saving path: {str(e)}")
            else:
                self.resultBox.setText("No valid path found.")
                
        except Exception as e:
            self.resultBox.setText(f"Error planning path: {str(e)}")


def launch_gui():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    launch_gui()