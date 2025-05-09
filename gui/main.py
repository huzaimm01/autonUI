import sys
import os
from PyQt5 import QtWidgets, uic
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
