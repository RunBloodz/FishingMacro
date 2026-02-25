import sys
import threading
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFormLayout, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from pynput import mouse, keyboard
import mss
from config import load_config, save_config
from macro import MacroController

class FishingUI(QWidget):
    # Signal to update UI from other threads
    status_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.macro = MacroController()
        self.picking_mode = None

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
        cal_group = QGroupBox("Calibration")
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

    # --- Picking Logic ---
    def start_picking(self, mode):
        self.picking_mode = mode
        self.status_signal.emit(f"Picking {mode}... Click on screen!")

        # Start mouse listener
        self.click_count = 0
        self.mouse_listener = mouse.Listener(on_click=self.on_screen_click)
        self.mouse_listener.start()

    def on_screen_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            color = self.get_color_at(x, y)

            if self.picking_mode == "exclamation":
                self.config['exclamation_pos'] = [int(x), int(y)]
                self.config['exclamation_color'] = list(color)
                self.status_signal.emit(f"Set Exclamation: {int(x)},{int(y)} Color: {color}")
                self.finish_picking()

            elif self.picking_mode == "bar_auto":
                # Auto detect bar edges based on background color
                self.status_signal.emit("Scanning for bar edges...")
                y_int = int(y)
                x_int = int(x)
                bg_color = color
                self.config['bar_bg_color'] = list(bg_color)
                self.config['minigame_bar_y'] = y_int

                # Scan left
                x_start = x_int
                while x_start > 0:
                    c = self.get_color_at(x_start - 1, y_int)
                    if not self.macro.is_color_match(c, bg_color, 15): # Strict tolerance for background
                        break
                    x_start -= 1

                # Scan right
                x_end = x_int
                # Assuming max screen width 4000
                while x_end < 4000:
                    c = self.get_color_at(x_end + 1, y_int)
                    if not self.macro.is_color_match(c, bg_color, 15):
                        break
                    x_end += 1

                self.config['minigame_bar_x_start'] = x_start
                self.config['minigame_bar_x_end'] = x_end
                self.status_signal.emit(f"Detected Bar: {x_start} to {x_end} at Y={y_int}")
                self.finish_picking()

            elif self.picking_mode == "fish":
                self.config['fish_color'] = list(color)
                self.status_signal.emit(f"Set Fish Color: {color}")
                self.finish_picking()

            elif self.picking_mode == "catcher":
                self.config['catcher_color'] = list(color)
                self.status_signal.emit(f"Set Catcher Color: {color}")
                self.finish_picking()

            elif self.picking_mode == "chest":
                self.config['chest_color'] = list(color)
                self.status_signal.emit(f"Set Chest Color: {color}")
                self.finish_picking()

    def finish_picking(self):
        self.mouse_listener.stop()
        self.picking_mode = None
        save_config(self.config)
        self.macro.update_config()

    def get_color_at(self, x, y):
        with mss.mss() as sct:
            monitor = {"top": int(y), "left": int(x), "width": 1, "height": 1}
            img = sct.grab(monitor)
            b, g, r = img.pixel(0, 0)
            return (r, g, b)

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = FishingUI()
    window.show()
    sys.exit(app.exec())
