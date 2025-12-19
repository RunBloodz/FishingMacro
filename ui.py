from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from macro import MacroController

class FishingUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FishingMacro ULTRA")
        self.setFixedSize(420, 320)
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
            QPushButton {
                background-color: #1f1f1f;
                border-radius: 10px;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
            }
        """)

        self.macro = MacroController()

        layout = QVBoxLayout()

        title = QLabel("FishingMacro ULTRA")
        title.setFont(QFont("Segoe UI", 20))
        layout.addWidget(title)

        start = QPushButton("START")
        stop = QPushButton("STOP")

        start.clicked.connect(self.macro.start)
        stop.clicked.connect(self.macro.stop)

        layout.addWidget(start)
        layout.addWidget(stop)

        self.setLayout(layout)
