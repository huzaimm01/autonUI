import sys
import os
from PyQt5 import QtWidgets, uic, QtGui, QtCore
from app import GameConfig, RobotConfig, PathPlanner, Utils

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi(os.path.join(os.path.dirname(__file__), "layout.ui"), self)
        self.planButton.clicked.connect(self.plan_path)
        self.officialFieldCheck.stateChanged.connect(self.toggle_field_mode)
        self.scene = QtWidgets.QGraphicsScene()
        self.fieldView.setScene(self.scene)
        self.populate_games()
        self.toggle_field_mode()

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
                elements = game.field_elements

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
            self.draw_field(field_width, field_length, start, goal, elements, path)

    def draw_field(self, width, height, start, goal, elements, path):
        self.scene.clear()
        scale = 50  # 1 meter = 50 px
        margin = 20
        self.scene.setSceneRect(0, 0, width * scale + 2 * margin, height * scale + 2 * margin)

        def field_to_scene(x, y):
            return margin + x * scale, margin + y * scale

        # Draw field border
        self.scene.addRect(margin, margin, width * scale, height * scale, QtGui.QPen(QtCore.Qt.black))

        # Draw start/goal
        sx, sy = field_to_scene(*start)
        gx, gy = field_to_scene(*goal)
        self.scene.addEllipse(sx - 5, sy - 5, 10, 10, QtGui.QPen(QtCore.Qt.green), QtGui.QBrush(QtCore.Qt.green))
        self.scene.addEllipse(gx - 5, gy - 5, 10, 10, QtGui.QPen(QtCore.Qt.red), QtGui.QBrush(QtCore.Qt.red))

        # Draw field elements
        for elem in elements:
            ex, ey = field_to_scene(elem["x"], elem["y"])
            ew = elem.get("width", 1.0) * scale
            eh = elem.get("height", 1.0) * scale
            rect = QtCore.QRectF(ex - ew/2, ey - eh/2, ew, eh)
            self.scene.addRect(rect, QtGui.QPen(QtCore.Qt.darkBlue), QtGui.QBrush(QtCore.Qt.lightGray))
            label = QtWidgets.QGraphicsTextItem(elem["name"])
            label.setDefaultTextColor(QtCore.Qt.black)
            label.setPos(ex - ew/2, ey - eh/2 - 20)
            self.scene.addItem(label)

        # Draw path
        if path:
            for i in range(len(path) - 1):
                x1, y1 = field_to_scene(*path[i])
                x2, y2 = field_to_scene(*path[i + 1])
                self.scene.addLine(x1, y1, x2, y2, QtGui.QPen(QtCore.Qt.blue, 2))

def launch_gui():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
