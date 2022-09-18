from src.controllers import VisionSystemController
from PyQt5.QtWidgets import QApplication
import sys


def main():
    app = QApplication(sys.argv)
    controller = VisionSystemController()
    controller.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
