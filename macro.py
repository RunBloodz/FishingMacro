import threading
import time

class MacroController:
    def __init__(self):
        self.running = False

    def start(self):
        if self.running:
            return
        self.running = True
        threading.Thread(target=self.loop, daemon=True).start()

    def stop(self):
        self.running = False

    def loop(self):
        while self.running:
            print("Fishing...")
            time.sleep(0.2)
