import threading
import time
import random
import pyautogui
import keyboard
import cv2
import numpy as np
from PIL import ImageGrab

class MacroController:
    def __init__(self):
        self.running = False
        self.paused = False
        self.thread = None

        # ---------- FAILSAFES ----------
        pyautogui.FAILSAFE = True
        self.max_idle = 30
        self.last_action = time.time()

        # ---------- HOTKEYS ----------
        keyboard.add_hotkey("f8", self.toggle_pause)
        keyboard.add_hotkey("f9", self.stop)

        # ---------- STATS ----------
        self.start_time = None
        self.fish_caught = 0

        # ---------- KEYS (CHANGE IF NEEDED) ----------
        self.cast_key = "1"
        self.reel_key = "2"
        self.inventory_key = "i"

        # ---------- DETECTION ----------
        self.bobber_image = "assets/bobber.png"
        self.inventory_full_image = "assets/inventory_full.png"
        self.image_threshold = 0.75

        # ---------- FISHING SPOTS ----------
        self.spots = [
            (960, 540),
            (1020, 560),
            (900, 520),
        ]
        self.current_spot = 0

    # ================= CONTROL =================
    def start(self):
        if self.running:
            return
        self.running = True
        self.paused = False
        self.start_time = time.time()
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()
        print("Macro started.")

    def stop(self):
        print("Macro stopped.")
        self.running = False

    def toggle_pause(self):
        self.paused = not self.paused
        print("Paused" if self.paused else "Resumed")

    # ================= MAIN LOOP =================
    def loop(self):
        while self.running:
            if self.paused:
                time.sleep(0.2)
                continue

            if time.time() - self.last_action > self.max_idle:
                print("Failsafe: idle timeout.")
                self.stop()
                break

            if self.inventory_full():
                print("Inventory full. Stopping.")
                self.stop()
                break

            self.move_to_next_spot()
            self.cast()
            if self.wait_for_bite():
                self.reel()
                self.fish_caught += 1
                self.print_stats()

            self.anti_afk()
            self.random_delay(1.5, 3.0)

    # ================= FISHING =================
    def cast(self):
        print("Casting...")
        pyautogui.press(self.cast_key)
        self.last_action = time.time()
        self.random_delay(0.8, 1.2)

    def wait_for_bite(self):
        print("Waiting for bite...")
        start = time.time()

        while time.time() - start < 20:
            if not self.running or self.paused:
                return False

            if self.image_detect(self.bobber_image):
                print("Bite detected!")
                return True

            time.sleep(0.15)

        print("No bite.")
        return False

    def reel(self):
        print("Reeling in!")
        pyautogui.press(self.reel_key)
        self.last_action = time.time()
        self.random_delay(0.6, 1.0)

    # ================= DETECTION =================
    def image_detect(self, image_path):
        try:
            screenshot = ImageGrab.grab()
            screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
            template = cv2.imread(image_path, 0)

            res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)

            return max_val >= self.image_threshold
        except:
            return False

    def inventory_full(self):
        print("Checking inventory...")
        pyautogui.press(self.inventory_key)
        time.sleep(0.4)

        full = self.image_detect(self.inventory_full_image)

        pyautogui.press(self.inventory_key)
        time.sleep(0.2)

        return full

    # ================= MOVEMENT =================
    def move_to_next_spot(self):
        x, y = self.spots[self.current_spot]
        pyautogui.moveTo(x, y, duration=random.uniform(0.3, 0.6))
        self.current_spot = (self.current_spot + 1) % len(self.spots)

    # ================= ANTI-AFK =================
    def anti_afk(self):
        if r
