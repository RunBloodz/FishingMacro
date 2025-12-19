from PyQt6.QtWidgets import QApplication, QLabel, QWidget
import sys

def run_ui():
    app = QApplication(sys.argv)
    w = QWidget()
    w.setWindowTitle("FishingMacro")
    w.resize(400, 200)
    QLabel("FishingMacro running", parent=w).move(120, 90)
    w.show()
    sys.exit(app.exec())
