import sys
import os
from src.controllers.full_vision_controller import FullVisionController
from PyQt5.QtWidgets import QApplication
from multiprocessing import Process


def run_app_procces(win):
    win.choosing_webcam.show()

def run_calculating_process(win):
    win.picking_thread.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FullVisionController(os.path.dirname(os.path.abspath(__file__)))
    sys.exit(app.exec_())
