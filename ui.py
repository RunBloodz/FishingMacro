import sys
import threading
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFormLayout, QGroupBox, QMessageBox, QApplication, QSizeGrip)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint, QRect
from PyQt6.QtGui import QPixmap, QImage, QCursor, QColor
from pynput import keyboard
import mss
import numpy as np
from config import load_config, save_config
from macro import MacroController

class ResizableFrame(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 255, 0, 40); border: 2px solid #00FF00;")
        self.setGeometry(QRect(200, 200, 150, 50))
        self.old_pos = None

        # Grip for resizing
        self.grip = QSizeGrip(self)
        self.grip.setFixedSize(20, 20)
        self.grip.setStyleSheet("background-color: #00FF00;")

    def resizeEvent(self, event):
        self.grip.move(self.width() - self.grip.width(), self.height() - self.grip.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

class CalibrationOverlay(QWidget):
    # Signal: x_center, y_center, (r, g, b), rect
    confirmed_signal = pyqtSignal(int, int, tuple, QRect)

    def __init__(self, pixmap, initial_rect=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setWindowState(Qt.WindowState.WindowFullScreen)

        # Background screenshot
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(pixmap)
        self.bg_label.setGeometry(0, 0, pixmap.width(), pixmap.height())
        self.pixmap = pixmap

        # Resizable Frame
        self.frame = ResizableFrame(self)
        if initial_rect:
            self.frame.setGeometry(initial_rect)

        # Confirm Button
        self.btn_confirm = QPushButton("CONFIRM (Enter)", self)
        self.btn_confirm.setStyleSheet("""
            QPushButton {
                background-color: #00AA00;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #00CC00;
            }
        """)
        self.btn_confirm.setFixedSize(150, 40)
        self.btn_confirm.clicked.connect(self.on_confirm)

        # Cancel Button
        self.btn_cancel = QPushButton("CANCEL (Esc)", self)
        self.btn_cancel.setStyleSheet("background-color: #AA0000; color: white; padding: 10px; border-radius: 5px;")
        self.btn_cancel.setFixedSize(150, 40)
        self.btn_cancel.clicked.connect(self.close)

        # Position buttons at the bottom
        self.update_button_positions()

    def update_button_positions(self):
        screen_geo = QApplication.primaryScreen().geometry()
        self.btn_confirm.move(screen_geo.width() // 2 - 160, screen_geo.height() - 60)
        self.btn_cancel.move(screen_geo.width() // 2 + 10, screen_geo.height() - 60)

    def on_confirm(self):
        rect = self.frame.geometry()
        center_x = rect.center().x()
        center_y = rect.center().y()

        image = self.pixmap.toImage()
        # Ensure coordinates are within image bounds
        safe_x = max(0, min(center_x, image.width() - 1))
        safe_y = max(0, min(center_y, image.height() - 1))

        qcolor = image.pixelColor(safe_x, safe_y)
        color = (qcolor.red(), qcolor.green(), qcolor.blue())

        self.confirmed_signal.emit(center_x, center_y, color, rect)
        self.close()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            self.on_confirm()
        elif event.key() == Qt.Key.Key_Escape:
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

        self.hk_listener = keyboard.GlobalHotKeys({
            '<f2>': self.start_macro,
            '<f3>': self.stop_macro
        })
        self.hk_listener.start()

    def init_ui(self):
        self.setWindowTitle("Blox Fruits Fishing Macro ULTRA")
        self.setFixedWidth(400)
        layout = QVBoxLayout()

        self.status_label = QLabel("Status: Stopped")
        self.status_label.setStyleSheet("font-weight: bold; color: red;")
        layout.addWidget(self.status_label)

        hk_group = QGroupBox("Hotkeys & Keys")
        hk_layout = QFormLayout()
        self.rod_key_input = QLineEdit(self.config['rod_key'])
        self.reset_key_input = QLineEdit(self.config['reset_key'])
        hk_layout.addRow("Rod Key:", self.rod_key_input)
        hk_layout.addRow("Reset Key:", self.reset_key_input)
        hk_group.setLayout(hk_layout)
        layout.addWidget(hk_group)

        cal_group = QGroupBox("Calibration (Frozen screen + Frames)")
        cal_layout = QVBoxLayout()

        buttons = [
            ("Set Exclamation", "exclamation"),
            ("Set Minigame Bar (Auto)", "bar_auto"),
            ("Set Fish Color", "fish"),
            ("Set Catcher Color", "catcher"),
            ("Set Chest Color", "chest")
        ]
        for text, mode in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, m=mode: self.start_picking(m))
            cal_layout.addWidget(btn)

        cal_group.setLayout(cal_layout)
        layout.addWidget(cal_group)

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
        self.status_label.setStyleSheet(f"font-weight: bold; color: {'green' if 'Running' in text else 'red'};")

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
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = QImage(sct_img.raw, sct_img.width, sct_img.height, QImage.Format.Format_ARGB32)
            return QPixmap.fromImage(img)

    def start_picking(self, mode):
        self.picking_mode = mode
        self.status_signal.emit(f"Adjust frame for {mode}...")

        pixmap = self.get_screenshot()

        initial_rect = QRect(200, 200, 100, 100)
        if mode == "bar_auto":
            initial_rect = QRect(200, 400, 400, 40)
        elif mode == "exclamation":
            initial_rect = QRect(pixmap.width()//2 - 25, pixmap.height()//2 - 100, 50, 50)

        self.overlay = CalibrationOverlay(pixmap, initial_rect)
        self.overlay.confirmed_signal.connect(self.handle_confirmed_calibration)
        self.overlay.show()

    def handle_confirmed_calibration(self, x, y, color, rect):
        if self.picking_mode == "exclamation":
            self.config['exclamation_pos'] = [x, y]
            self.config['exclamation_color'] = list(color)
            self.status_signal.emit(f"Set Exclamation: {x},{y} Color: {color}")

        elif self.picking_mode == "bar_auto":
            self.status_signal.emit("Scanning for bar edges...")
            bg_color = color
            self.config['bar_bg_color'] = list(bg_color)
            self.config['minigame_bar_y'] = y

            image = self.overlay.pixmap.toImage()
            # Scan from frame boundaries first, then continue if color matches
            x_start = rect.left()
            while x_start > 0:
                qc = image.pixelColor(x_start - 1, y)
                c = (qc.red(), qc.green(), qc.blue())
                if not self.macro.is_color_match(c, bg_color, 15):
                    break
                x_start -= 1

            x_end = rect.right()
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
