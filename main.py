import updater
from PyQt6.QtWidgets import QApplication, QLabel
import sys

app = QApplication(sys.argv)
w = QLabel("FishingMacro Running")
w.resize(300, 100)
w.show()
sys.exit(app.exec())
