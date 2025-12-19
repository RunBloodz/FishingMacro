<<<<<<< HEAD
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
=======
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

    def stop(self):
        self.running = False

    def loop(self):
        while self.running:
            # SAFE PLACEHOLDER
            print("Macro running...")
            time.sleep(0.1)
# macro placeholder
>>>>>>> 421cea7cdfa2bb317814615a282dcb5f05bed511
