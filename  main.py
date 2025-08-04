#!/usr/bin/env python3
"""
AutonUI - Advanced FRC Autonomous Path Planning Tool
Main entry point for the application.
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import AutonUIMainWindow

class AutonUIApplication(QApplication):
    """Main application class"""
    
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application properties
        self.setApplicationName("AutonUI")
        self.setApplicationVersion("1.0")
        self.setOrganizationName("FRC Tools")
        
        # Enable high DPI scaling
        self.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        # Create main window
        self.main_window = AutonUIMainWindow()
        
    def run(self):
        """Run the application"""
        self.main_window.show()
        return self.exec_()

def main():
    """Main entry point"""
    # Create application
    app = AutonUIApplication(sys.argv)
    
    # Run application
    sys.exit(app.run())

if __name__ == "__main__":
    main()