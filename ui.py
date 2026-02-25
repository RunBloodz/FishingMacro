import sys
import threading
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFormLayout, QGroupBox, QMessageBox, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint
from PyQt6.QtGui import QPixmap, QImage, QCursor
from pynput import keyboard
import mss
import numpy as np
from config import load_config, save_config
from macro import MacroController

class CalibrationOverlay(QWidget):
    # Signal: x, y, (r, g, b)
    clicked_signal = pyqtSignal(int, int, tuple)

    def __init__(self, pixmap):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self.label = QLabel(self)
        self.label.setPixmap(pixmap)
        self.label.setGeometry(0, 0, pixmap.width(), pixmap.height())
        self.pixmap = pixmap

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position()
            x = int(pos.x())
            y = int(pos.y())

            image = self.pixmap.toImage()
            qcolor = image.pixelColor(x, y)
            color = (qcolor.red(), qcolor.green(), qcolor.blue())

            self.clicked_signal.emit(x, y, color)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

class FishingUI(QWidget):
    status_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.macro = MacroController()
        self.picking_mode = None
        self.overlay = None

        self.init_ui()

        # Hotkey listener
        self.hk_listener = keyboard.GlobalHotKeys({
            '<f2>': self.start_macro,
            '<f3>': self.stop_macro
        })
        self.hk_listener.start()

    def init_ui(self):
        self.setWindowTitle("Blox Fruits Fishing Macro ULTRA")
        self.setFixedWidth(400)
        layout = QVBoxLayout()

        # --- Status ---
        self.status_label = QLabel("Status: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(self.status_label)

        # --- Hotkeys Group ---
        hk_group = QGroupBox("Hotkeys & Keys")
        hk_layout = QFormLayout()
        self.rod_key_input = QLineEdit(self.config['rod_key'])
        self.reset_key_input = QLineEdit(self.config['reset_key'])
        hk_layout.addRow("Rod Key:", self.rod_key_input)
        hk_layout.addRow("Reset Key:", self.reset_key_input)
        hk_group.setLayout(hk_layout)
        layout.addWidget(hk_group)

        # --- Calibration Group ---
        cal_group = QGroupBox("Calibration (Screen will freeze)")
        cal_layout = QVBoxLayout()

        btn_excl = QPushButton("Set Exclamation (Pos & Color)")
        btn_excl.clicked.connect(lambda: self.start_picking("exclamation"))
        cal_layout.addWidget(btn_excl)

        btn_bar = QPushButton("Set Minigame Bar (Auto-Detect)")
        btn_bar.clicked.connect(lambda: self.start_picking("bar_auto"))
        cal_layout.addWidget(btn_bar)

        btn_fish = QPushButton("Set Fish Color")
        btn_fish.clicked.connect(lambda: self.start_picking("fish"))
        cal_layout.addWidget(btn_fish)

        btn_catcher = QPushButton("Set Catcher Color")
        btn_catcher.clicked.connect(lambda: self.start_picking("catcher"))
        cal_layout.addWidget(btn_catcher)

        btn_chest = QPushButton("Set Chest Color (Yellow)")
        btn_chest.clicked.connect(lambda: self.start_picking("chest"))
        cal_layout.addWidget(btn_chest)

        cal_group.setLayout(cal_layout)
        layout.addWidget(cal_group)

        # --- Controls ---
        ctrl_layout = QHBoxLayout()
        self.start_btn = QPushButton("START (F2)")
        self.start_btn.clicked.connect(self.start_macro)
        self.start_btn.setStyleSheet("background-color: green; color: white;")

        self.stop_btn = QPushButton("STOP (F3)")
        self.stop_btn.clicked.connect(self.stop_macro)
        self.stop_btn.setStyleSheet("background-color: red; color: white;")

        ctrl_layout.addWidget(self.start_btn)
        ctrl_layout.addWidget(self.stop_btn)
        layout.addLayout(ctrl_layout)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        self.setLayout(layout)
        self.status_signal.connect(self.update_status_label)

    def update_status_label(self, text):
        self.status_label.setText(f"Status: {text}")
        if "Running" in text:
            self.status_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.status_label.setStyleSheet("font-weight: bold; color: red;")

    def start_macro(self):
        self.save_settings()
        self.macro.start()
        self.status_signal.emit("Running")

    def stop_macro(self):
        self.macro.stop()
        self.status_signal.emit("Stopped")

    def save_settings(self):
        self.config['rod_key'] = self.rod_key_input.text()
        self.config['reset_key'] = self.reset_key_input.text()
        save_config(self.config)
        self.macro.update_config()

    def get_screenshot(self):
        with mss.mss() as sct:
            # Capture the whole primary monitor
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            # mss BGRA -> QImage ARGB32 (which is BGRA on little-endian)
            img = QImage(sct_img.raw, sct_img.width, sct_img.height, QImage.Format.Format_ARGB32)
            return QPixmap.fromImage(img)

    def start_picking(self, mode):
        self.picking_mode = mode
        self.status_signal.emit(f"Picking {mode}... Click on the frozen screen!")

        # Take a screenshot to "freeze" the screen
        pixmap = self.get_screenshot()

        # Show overlay
        self.overlay = CalibrationOverlay(pixmap)
        self.overlay.clicked_signal.connect(self.handle_picking_click)
        self.overlay.show()

    def handle_picking_click(self, x, y, color):
        if self.picking_mode == "exclamation":
            self.config['exclamation_pos'] = [x, y]
            self.config['exclamation_color'] = list(color)
            self.status_signal.emit(f"Set Exclamation: {x},{y} Color: {color}")

        elif self.picking_mode == "bar_auto":
            self.status_signal.emit("Scanning for bar edges...")
            bg_color = color
            self.config['bar_bg_color'] = list(bg_color)
            self.config['minigame_bar_y'] = y

            # Use the screenshot for scanning edges (faster than individual grabs)
            image = self.overlay.pixmap.toImage()

            # Scan left
            x_start = x
            while x_start > 0:
                qc = image.pixelColor(x_start - 1, y)
                c = (qc.red(), qc.green(), qc.blue())
                if not self.macro.is_color_match(c, bg_color, 15):
                    break
                x_start -= 1

            # Scan right
            x_end = x
            while x_end < image.width() - 1:
                qc = image.pixelColor(x_end + 1, y)
                c = (qc.red(), qc.green(), qc.blue())
                if not self.macro.is_color_match(c, bg_color, 15):
                    break
                x_end += 1

            self.config['minigame_bar_x_start'] = x_start
            self.config['minigame_bar_x_end'] = x_end
            self.status_signal.emit(f"Detected Bar: {x_start} to {x_end} at Y={y}")

        elif self.picking_mode == "fish":
            self.config['fish_color'] = list(color)
            self.status_signal.emit(f"Set Fish Color: {color}")

        elif self.picking_mode == "catcher":
            self.config['catcher_color'] = list(color)
            self.status_signal.emit(f"Set Catcher Color: {color}")

        elif self.picking_mode == "chest":
            self.config['chest_color'] = list(color)
            self.status_signal.emit(f"Set Chest Color: {color}")

        self.picking_mode = None
        save_config(self.config)
        self.macro.update_config()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FishingUI()
    window.show()
    sys.exit(app.exec())
