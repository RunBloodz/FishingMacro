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
        """)

        self.macro = MacroController()

        layout = QVBoxLayout()

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
