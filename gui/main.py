# gui/main.py

import sys
import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from PyQt5.QtOpenGL import QGLWidget
from app import GameConfig, RobotConfig, PathPlanner, Utils
from OpenGL.GL import *

class OpenGLField(QGLWidget):
    def __init__(self, parent=None):
        super(OpenGLField, self).__init__(parent)
        self.path = []
        self.elements = []
        self.field_dims = (8.0, 16.0)
        self.margin = 0.5
        self.scale = 1.0

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

    def draw_grid(self):
        glColor4f(0.2, 0.3, 0.4, 0.3)
        step = 1.0
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

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        self.draw_grid()

        # Draw elements by type
        grouped = Utils.group_elements_by_type(self.elements)

        # Obstacles
        glColor4f(0.7, 0.2, 0.2, 0.7)
        for e in grouped.get("obstacle", []):
            self._draw_rect(e)

        # Notes
        glColor4f(0.95, 0.8, 0.2, 0.85)
        for e in grouped.get("note", []):
            self._draw_rect(e)

        # Targets
        glColor4f(0.2, 0.9, 0.3, 0.6)
        for e in grouped.get("target", []):
            self._draw_rect(e)

        # Path
        if self.path:
            glColor4f(0.0, 1.0, 1.0, 1.0)
            glBegin(GL_LINE_STRIP)
            for pt in self.path:
                glVertex2f(pt[0], pt[1])
            glEnd()

        # Start & goal
        if self.path:
            glColor4f(0.0, 1.0, 0.0, 1.0)
            glBegin(GL_POINTS)
            glVertex2f(*self.path[0])
            glEnd()
            glColor4f(1.0, 0.0, 0.0, 1.0)
            glBegin(GL_POINTS)
            glVertex2f(*self.path[-1])
            glEnd()

    def _draw_rect(self, elem):
        x, y = elem["x"], elem["y"]
        w, h = elem.get("width", 1), elem.get("height", 1)
        glBegin(GL_QUADS)
        glVertex2f(x - w / 2, y - h / 2)
        glVertex2f(x + w / 2, y - h / 2)
        glVertex2f(x + w / 2, y + h / 2)
        glVertex2f(x - w / 2, y + h / 2)
        glEnd()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "layout.ui"), self)
        self.planButton.clicked.connect(self.plan_path)
        self.officialFieldCheck.stateChanged.connect(self.toggle_field_mode)

        self.fieldWidget = OpenGLField(self.centralwidget.findChild(QtWidgets.QWidget, "openGLContainer"))
        layout = self.centralwidget.findChild(QtWidgets.QVBoxLayout, "verticalLayout")
        layout.addWidget(self.fieldWidget)

        self.populate_games()
        self.toggle_field_mode()
        self.load_stylesheet()

    def load_stylesheet(self):
        qss_path = os.path.join(os.path.dirname(__file__), "style.qss")
        if os.path.exists(qss_path):
            with open(qss_path, "r") as f:
                self.setStyleSheet(f.read())

    def populate_games(self):
        self.games = {}
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        for file in os.listdir(data_dir):
            if file.endswith(".json"):
                path = os.path.join(data_dir, file)
                game = GameConfig.from_file(path)
                self.games[game.name] = game
                self.gameSelect.addItem(game.name)

    def toggle_field_mode(self):
        official = self.officialFieldCheck.isChecked()
        self.fieldWidth.setDisabled(official)
        self.fieldLength.setDisabled(official)

    def plan_path(self):
        game_name = self.gameSelect.currentText()
        game = self.games.get(game_name)

        try:
            if self.officialFieldCheck.isChecked():
                field_width, field_length = Utils.get_official_field_dimensions(game_name)
                elements = Utils.get_official_elements(game_name)
            else:
                field_width = float(self.fieldWidth.text())
                field_length = float(self.fieldLength.text())
                elements = [e.to_dict() for e in game.field_elements]

            robot_width = float(self.robotWidth.text())
            robot_length = float(self.robotLength.text())
            robot_height = float(self.robotHeight.text())
            start = (float(self.startX.text()), float(self.startY.text()))
            goal = (float(self.goalX.text()), float(self.goalY.text()))

        except ValueError:
            self.resultBox.setText("Error: Please enter valid numerical values.")
            return

        robot = RobotConfig(robot_width, robot_length, robot_height, 2.0, 1.0, "swerve")
        planner = PathPlanner(game, robot)
        path = planner.plan_path(start, [goal], elements)

        if path is None:
            self.resultBox.setText("No valid path found (obstacle detected).")
        else:
            formatted = Utils.format_path(path)
            self.resultBox.setText("\n".join([f"{p['x']}, {p['y']}" for p in formatted]))
            self.fieldWidget.set_data((field_width, field_length), path, elements)

def launch_gui():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
