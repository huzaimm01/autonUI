import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "gui"))
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from main import launch_gui

if __name__ == "__main__":
    launch_gui()