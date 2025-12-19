<<<<<<< HEAD
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
=======
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from macro import MacroController
from updater import check_for_update
import sys

class FishingMacroUI:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.win = QWidget()
        self.win.setWindowTitle("FishingMacro ULTRA")
        self.win.resize(900, 500)

        self.win.setStyleSheet("""
            QWidget { background:#0f1117; color:#e5e7eb; }
            QPushButton {
                background:#1f2937;
                border-radius:10px;
                padding:12px;
                font-size:14px;
            }
            QPushButton:hover { background:#374151; }
            QLabel { font-size:16px; }
>>>>>>> 421cea7cdfa2bb317814615a282dcb5f05bed511
        """)

        self.macro = MacroController()

        layout = QVBoxLayout()

<<<<<<< HEAD
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
=======
        title = QLabel("🎣 FishingMacro ULTRA")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size:26px;")
        layout.addWidget(title)

        btns = QHBoxLayout()

        start = QPushButton("START (F2)")
        stop = QPushButton("STOP (F3)")
        update = QPushButton("CHECK UPDATE")

        start.clicked.connect(self.macro.start)
        stop.clicked.connect(self.macro.stop)
        update.clicked.connect(check_for_update)

        btns.addWidget(start)
        btns.addWidget(stop)
        btns.addWidget(update)

        layout.addLayout(btns)
        self.win.setLayout(layout)

    def run(self):
        self.win.show()
        sys.exit(self.app.exec())
>>>>>>> 421cea7cdfa2bb317814615a282dcb5f05bed511
