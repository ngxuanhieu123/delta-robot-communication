from PyQt5.QtWidgets import QWidget, QComboBox, QPushButton
from PyQt5.uic import loadUi



class ChoosingCameraDialog(QWidget):
    def __init__(self, controller, ui_file="ui_files/choosing_webcam.ui"):
        super().__init__()
        loadUi(ui_file, self)
        self.controller = controller
        self.cam_id_combo = self.findChild(QComboBox, 'cam_id')
        self.cam_id_combo.config(self.controller, 'cam_id')
        self.ok_btn = self.findChild(QPushButton, 'ok_btn')
        self.ok_btn.clicked.connect(self.set_cam)

    def set_cam(self):
        self.close()
        self.controller.show()
