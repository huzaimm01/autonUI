import sys
import os
from PyQt5 import QtWidgets, uic
from PyQt5.QtOpenGL import QGLWidget
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
        self.setMinimumSize(800, 600)

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
        glOrtho(0, self.field_dims[0], self.field_dims[1], 0, -1, 1)
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

        container = self.findChild(QtWidgets.QWidget, "openGLContainer")
        layout = container.layout() if container else self.centralWidget().findChild(QtWidgets.QVBoxLayout, "verticalLayout")

        self.fieldWidget = OpenGLField(container)
        if layout:
            layout.addWidget(self.fieldWidget)

        self.games = {}
        self.populate_games()
        self.toggle_field_mode()

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
        for file in os.listdir(data_dir):
            if file.endswith(".json"):
                game = GameConfig.from_file(os.path.join(data_dir, file))
                self.games[game.name] = game
                self.gameSelect.addItem(game.name)
        self.update_background(self.gameSelect.currentText())

    def update_background(self, game_name):
        self.fieldWidget.set_background(game_name)
        game = self.games.get(game_name)
        if game:
            dims = (game.field_width, game.field_length)
            elements = [e.to_dict() if hasattr(e, "to_dict") else e for e in game.field_elements]
            obstacle_path = os.path.join(os.path.dirname(__file__), "..", "frc_field_grid_with_obstacles.json")
            polygons = Utils.get_polygon_obstacles(game_name, obstacle_path)
            self.fieldWidget.set_data(dims, [], elements, polygon_obstacles=polygons)
            self.fieldWidget.repaint()

    def toggle_field_mode(self):
        self.fieldWidth.setDisabled(self.officialFieldCheck.isChecked())
        self.fieldLength.setDisabled(self.officialFieldCheck.isChecked())

    def add_goal(self):
        x = self.goalX.text().strip()
        y = self.goalY.text().strip()
        if x and y:
            self.goalList.addItem(f"{x}, {y}")
            self.goalX.clear()
            self.goalY.clear()

    def remove_selected_goal(self):
        row = self.goalList.currentRow()
        if row >= 0:
            self.goalList.takeItem(row)

    def clear_goals(self):
        self.goalList.clear()

    def plan_path(self):
        game = self.games[self.gameSelect.currentText()]
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

        except ValueError:
            self.resultBox.setText("Enter valid numeric values.")
            return

        planner = PathPlanner(game, robot)
        path = planner.plan_path(start, goals)
        path = Utils.smooth_catmull_rom_path(path) if path else []

        if not path:
            self.resultBox.setText("No valid path found.")
        else:
            self.resultBox.setText("\n".join([f"{p[0]:.2f}, {p[1]:.2f}" for p in path]))
            self.fieldWidget.set_data((fw, fl), path, elements, self.fieldWidget.polygon_obstacles)
            Utils.write_path_to_json(path)
            Utils.write_path_to_csv(path)


def launch_gui():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())