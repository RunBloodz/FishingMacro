from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QVBoxLayout, QHBoxLayout
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sys

from macro import MacroController
from updater import check_update


class FishingMacroUI:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.setWindowTitle("FishingMacro ULTRA")
        self.window.resize(900, 500)

        self.window.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #eaeaea;
                font-family: Segoe UI;
            }
            QPushButton {
                background-color: #1f1f1f;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2c2c2c;
            }
        """)

        self.macro = MacroController()

        layout = QVBoxLayout()

        title = QLabel("FishingMacro ULTRA")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        start = QPushButton("START")
        stop = QPushButton("STOP")
        update = QPushButton("CHECK UPDATE")

        start.clicked.connect(self.macro.start)
        stop.clicked.connect(self.macro.stop)
        update.clicked.connect(check_update)

        layout.addWidget(title)
        layout.addStretch()
        layout.addWidget(start)
        layout.addWidget(stop)
        layout.addWidget(update)
        layout.addStretch()

        self.window.setLayout(layout)

    def run(self):
        self.window.show()
        sys.exit(self.app.exec())
