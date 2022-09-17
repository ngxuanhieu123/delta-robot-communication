from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel
from .camera_thread import WebcamThread


class CameraMapping(QWidget):
    def __init__(self, ui_file="../../ui_files/vision_mapping.ui"):
        super().__init__()

        self.initUi(ui_file)

    def initUi(self, ui_file):
        loadUi(ui_file, self)

        self.webcam = self.findChild(QLabel, 'webcam')
        
        self.webcam_thread = WebcamThread()
        self.webcam_thread.start()
        self.webcam_thread.updated_img.connect(self.update_webcam)

    def update_webcam(self, img):
        self.webcam.setPixmap(QPixmap.fromImage(img))
