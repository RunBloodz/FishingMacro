import threading
import time


class MacroController:
    def __init__(self):
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()
        print("Macro started")

    def stop(self):
        self.running = False
        print("Macro stopped")

    def loop(self):
        while self.running:
            # Placeholder logic
            time.sleep(0.02)
