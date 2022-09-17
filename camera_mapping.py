import sys
from src.views import CameraMapping
from src.controllers import CameraMappingController
from PyQt5.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    controller = CameraMappingController()
    controller.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
