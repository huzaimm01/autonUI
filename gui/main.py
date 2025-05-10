import sys
import os
from PyQt5 import QtWidgets, uic
from app import GameConfig, RobotConfig, PathPlanner, Utils
from OpenGL.GL import *
from PyQt5.QtOpenGL import QGLWidget
import math

class OpenGLField(QGLWidget):
    def __init__(self, parent=None):
        super(OpenGLField, self).__init__(parent)
        self.path = []
        self.elements = []
        self.field_dims = (8.0, 16.0)
        self.margin = 0.5

    def set_data(self, field_dims, path, elements):
        self.field_dims = field_dims
        self.path = path
        self.elements = elements
        self.update()

    def initializeGL(self):
        glClearColor(0.05, 0.07, 0.1, 1)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-self.margin, self.field_dims[0] + self.margin,
                self.field_dims[1] + self.margin, -self.margin, -1, 1)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # Draw grid
        glColor4f(0.2, 0.3, 0.4, 0.3)
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

        grouped = Utils.group_elements_by_type(self.elements)

        # Obstacles
        glColor4f(0.7, 0.2, 0.2, 0.6)
        for e in grouped.get("obstacle", []):
            self._draw_rect(e)

        # Notes
        glColor4f(0.95, 0.85, 0.1, 0.85)
        for e in grouped.get("note", []):
            self._draw_rect(e)

        # Targets
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
        glVertex2f(x - w/2, y - h/2)
        glVertex2f(x + w/2, y - h/2)
        glVertex2f(x + w/2, y + h/2)
        glVertex2f(x - w/2, y + h/2)
        glEnd()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "layout.ui"), self)
        self.planButton.clicked.connect(self.plan_path)
        self.officialFieldCheck.stateChanged.connect(self.toggle_field_mode)

        self.fieldWidget = OpenGLField(self.centralwidget.findChild(QtWidgets.QWidget, "openGLContainer"))
        layout = self.centralwidget.findChild(QtWidgets.QVBoxLayout, "verticalLayout")
        layout.addWidget(self.fieldWidget)

        self.games = {}
        self.populate_games()
        self.toggle_field_mode()
        self.apply_theme("dark")

    def populate_games(self):
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        for file in os.listdir(data_dir):
            if file.endswith(".json"):
                game = GameConfig.from_file(os.path.join(data_dir, file))
                self.games[game.name] = game
                self.gameSelect.addItem(game.name)

    def toggle_field_mode(self):
        self.fieldWidth.setDisabled(self.officialFieldCheck.isChecked())
        self.fieldLength.setDisabled(self.officialFieldCheck.isChecked())

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
                elements = [e.to_dict() for e in game.field_elements]

            robot = RobotConfig(
                width=float(self.robotWidth.text()),
                length=float(self.robotLength.text()),
                height=float(self.robotHeight.text()),
                max_velocity=2.0,
                max_acceleration=1.0,
                drivetrain="swerve"
            )

            start = (float(self.startX.text()), float(self.startY.text()))
            goal = (float(self.goalX.text()), float(self.goalY.text()))

        except ValueError:
            self.resultBox.setText("Enter valid numeric values.")
            return

        planner = PathPlanner(game, robot)
        path = planner.plan_path(start, [goal], elements)

        if not path:
            self.resultBox.setText("No valid path found.")
        else:
            self.resultBox.setText("\n".join([f"{p[0]:.2f}, {p[1]:.2f}" for p in path]))
            self.fieldWidget.set_data((fw, fl), path, [e if isinstance(e, dict) else e.to_dict() for e in elements])

    def apply_theme(self, theme):
        file = "style_dark.qss" if theme == "dark" else "style_light.qss"
        path = os.path.join(os.path.dirname(__file__), file)
        if os.path.exists(path):
            with open(path, "r") as f:
                self.setStyleSheet(f.read())

def launch_gui():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
