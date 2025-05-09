# gui/main.py

import sys
import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from app import GameConfig, RobotConfig, PathPlanner, Utils

def launch_gui():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "layout.ui"), self)
        self.planButton.clicked.connect(self.plan_path)
        self.scene = QtWidgets.QGraphicsScene()
        self.fieldView.setScene(self.scene)
        self.populate_games()

    def populate_games(self):
        self.games = {}
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        for file in os.listdir(data_dir):
            if file.endswith(".json"):
                path = os.path.join(data_dir, file)
                game = GameConfig.from_file(path)
                self.games[game.name] = game
                self.gameSelect.addItem(game.name)

    def plan_path(self):
        game_name = self.gameSelect.currentText()
        game = self.games.get(game_name)

        try:
            field_width = float(self.fieldWidth.text())
            field_length = float(self.fieldLength.text())
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
        path = planner.plan_path(start, [goal])
        formatted = Utils.format_path(path)

        output = "\n".join([f"{p['x']}, {p['y']}" for p in formatted])
        self.resultBox.setText(output)

        self.draw_field(field_width, field_length, start, goal, path, game)

    def draw_field(self, width, height, start, goal, path, game):
        self.scene.clear()
        scale = 50
        w_px = int(width * scale)
        h_px = int(height * scale)
        self.scene.setSceneRect(0, 0, w_px, h_px)

        pen_grid = QtGui.QPen(QtGui.QColor("#cccccc"))
        for x in range(0, w_px, scale):
            self.scene.addLine(x, 0, x, h_px, pen_grid)
        for y in range(0, h_px, scale):
            self.scene.addLine(0, y, w_px, y, pen_grid)

        brush_start = QtGui.QBrush(QtGui.QColor("green"))
        brush_goal = QtGui.QBrush(QtGui.QColor("red"))
        r = 5

        self.scene.addEllipse(start[0]*scale - r, start[1]*scale - r, 2*r, 2*r, QtGui.QPen(), brush_start)
        self.scene.addEllipse(goal[0]*scale - r, goal[1]*scale - r, 2*r, 2*r, QtGui.QPen(), brush_goal)

        path_pen = QtGui.QPen(QtGui.QColor("blue"))
        path_pen.setWidth(2)
        for i in range(len(path)-1):
            x1, y1 = path[i]
            x2, y2 = path[i+1]
            self.scene.addLine(x1*scale, y1*scale, x2*scale, y2*scale, path_pen)

        element_pen = QtGui.QPen(QtGui.QColor("black"))
        element_brush = QtGui.QBrush(QtGui.QColor("orange"))
        font = QtGui.QFont("Arial", 8)
        for elem in game.field_elements:
            x = elem["x"] * scale
            y = elem["y"] * scale
            self.scene.addRect(x - 5, y - 5, 10, 10, element_pen, element_brush)
            text = self.scene.addText(elem["name"], font)
            text.setPos(x + 6, y - 6)
