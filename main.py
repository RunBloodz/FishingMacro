<<<<<<< HEAD
import sys
from ui import FishingUI
from updater import check_update
from PyQt6.QtWidgets import QApplication

def resource_path(name):
    import os
    base = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base, name)

if __name__ == "__main__":
    check_update(resource_path("version.txt"))
    app = QApplication(sys.argv)
    win = FishingUI()
    win.show()
    sys.exit(app.exec())
=======
from ui import FishingMacroUI

if __name__ == "__main__":
    app = FishingMacroUI()
    app.run()
>>>>>>> 421cea7cdfa2bb317814615a282dcb5f05bed511
