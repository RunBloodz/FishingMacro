# Main entry point
import sys
from PyQt6.QtWidgets import QApplication
from ui import FishingUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FishingUI()
    window.show()
    sys.exit(app.exec())
