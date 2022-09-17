import sys
from src.views import CameraMapping
from PyQt5.QtWidgets import QApplication
from 


def main():
    app = QApplication(sys.argv)
    win = CameraMapping("ui_files/vision_mapping.ui")
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
