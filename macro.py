import threading
import time
import mss
import numpy as np
from pynput import mouse, keyboard
from config import load_config

class MacroController:
    def __init__(self):
        self.running = False
        self.paused = False
        self.config = load_config()
        self.thread = None

        self.mouse_ctrl = mouse.Controller()
        self.kb_ctrl = keyboard.Controller()

    def update_config(self):
        self.config = load_config()

    def start(self):
        if not self.running:
            self.update_config()
            self.running = True
            self.paused = False
            self.thread = threading.Thread(target=self.macro_loop, daemon=True)
            self.thread.start()
            print("Macro started")

    def stop(self):
        self.running = False
        print("Macro stopped")

    def toggle_pause(self):
        self.paused = not self.paused
        print(f"Macro {'paused' if self.paused else 'resumed'}")

    def is_color_match(self, c1, c2, tolerance):
        # c1 and c2 are (R, G, B)
        return all(abs(c1[i] - c2[i]) <= tolerance for i in range(3))

    def get_pixel_color(self, x, y):
        try:
            with mss.mss() as sct:
                monitor = {"top": int(y), "left": int(x), "width": 1, "height": 1}
                img = sct.grab(monitor)
                # mss ScreenShot.pixel returns (B, G, R)
                b, g, r = img.pixel(0, 0)
                return (r, g, b)
        except Exception as e:
            print(f"Error getting pixel color: {e}")
            return (0, 0, 0)

    def macro_loop(self):
        while self.running:
            if self.paused:
                time.sleep(0.1)
                continue

            try:
                # 1. Select Rod
                print(f"Selecting rod (Key {self.config['rod_key']})...")
                self.kb_ctrl.press(self.config['rod_key'])
                self.kb_ctrl.release(self.config['rod_key'])
                time.sleep(0.8)

                # 2. Cast
                print("Casting rod...")
                self.mouse_ctrl.click(mouse.Button.left)
                time.sleep(1.5)

                # 3. Wait for Exclamation
                print("Waiting for bite...")
                bite_detected = False
                start_wait = time.time()
                while time.time() - start_wait < 30 and self.running and not self.paused:
                    color = self.get_pixel_color(self.config['exclamation_pos'][0], self.config['exclamation_pos'][1])
                    if self.is_color_match(color, self.config['exclamation_color'], self.config['tolerance']):
                        bite_detected = True
                        break
                    time.sleep(0.05)

                if bite_detected:
                    print("Bite detected! Clicking...")
                    self.mouse_ctrl.click(mouse.Button.left)
                    time.sleep(0.6) # Wait for minigame UI

                    self.run_minigame()
                else:
                    print("No bite detected or timed out.")

                # 4. Reset
                print("Resetting rod...")
                self.kb_ctrl.press(self.config['reset_key'])
                self.kb_ctrl.release(self.config['reset_key'])
                time.sleep(0.5)
                # Back to rod is handled at the start of loop

            except Exception as e:
                print(f"Error in macro loop: {e}")
                time.sleep(1)

    def run_minigame(self):
        print("Minigame started.")
        y = int(self.config['minigame_bar_y'])
        x_start = int(self.config['minigame_bar_x_start'])
        x_end = int(self.config['minigame_bar_x_end'])
        width = x_end - x_start

        if width <= 0:
            print("Invalid minigame bar coordinates.")
            return

        with mss.mss() as sct:
            monitor = {"top": y, "left": x_start, "width": width, "height": 1}

            start_minigame = time.time()
            mouse_down = False

            while time.time() - start_minigame < 25 and self.running and not self.paused:
                img = sct.grab(monitor)
                # mss grab result is BGRA
                data = np.array(img)

                fish_x = -1
                catcher_x = -1

                # Scan for fish and catcher
                # Use numpy for faster searching if possible, or just a loop
                # data[0, x] is [B, G, R, A]

                # Optimized scan
                for x in range(0, width, 3):
                    b, g, r = data[0, x][:3]
                    rgb = (r, g, b)

                    if fish_x == -1 and self.is_color_match(rgb, self.config['fish_color'], self.config['tolerance']):
                        fish_x = x

                    if catcher_x == -1 and self.is_color_match(rgb, self.config['catcher_color'], self.config['tolerance']):
                        catcher_x = x

                    if fish_x != -1 and catcher_x != -1:
                        break

                if fish_x == -1 and catcher_x == -1:
                    # Check if game ended (no colors found at all)
                    # We look for ANY fish/catcher color in the whole bar more thoroughly
                    time.sleep(0.1)
                    img_verify = sct.grab(monitor)
                    data_v = np.array(img_verify)
                    found = False
                    for x in range(0, width, 5):
                        b, g, r = data_v[0, x][:3]
                        if self.is_color_match((r, g, b), self.config['fish_color'], self.config['tolerance']) or \
                           self.is_color_match((r, g, b), self.config['catcher_color'], self.config['tolerance']):
                            found = True
                            break
                    if not found:
                        print("Minigame ended (bars disappeared).")
                        break

                if fish_x != -1 and catcher_x != -1:
                    if fish_x > catcher_x:
                        if not mouse_down:
                            self.mouse_ctrl.press(mouse.Button.left)
                            mouse_down = True
                    else:
                        if mouse_down:
                            self.mouse_ctrl.release(mouse.Button.left)
                            mouse_down = False

                time.sleep(0.01)

            if mouse_down:
                self.mouse_ctrl.release(mouse.Button.left)
            print("Minigame loop finished.")
