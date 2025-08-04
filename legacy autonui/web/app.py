from flask import Flask, request, jsonify, render_template
from app import GameConfig, RobotConfig, PathPlanner, Utils
import os

app = Flask(__name__)
games = {}

@app.before_first_request
def load_game_data():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    for file in os.listdir(data_dir):
        if file.endswith(".json"):
            game = GameConfig.from_file(os.path.join(data_dir, file))
            games[game.name] = game

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/plan", methods=["POST"])
def plan():
    data = request.get_json()

    try:
        game = games[data["game"]]
        robot = RobotConfig(
            width=data["robot_width"],
            length=data["robot_length"],
            height=data["robot_height"],
            max_velocity=2.0,
            max_acceleration=1.0,
            drivetrain="swerve"
        )

        start = tuple(data["start"])
        goal = tuple(data["goal"])

        planner = PathPlanner(game, robot)
        path = planner.plan_path(start, [goal])
        return jsonify({"path": Utils.format_path(path)})

    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
