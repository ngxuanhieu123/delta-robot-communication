from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap
from .vision_camera_image import VisionCameraImage
from .vision_thread import VisionThread
from PyQt5.uic import loadUi



class VisionWidget(QWidget):
    def __init__(self, controller, ui_dir="ui_files/vision_system.ui"):
        super().__init__()
        loadUi(ui_dir, self)
        self.controller = controller

        self.normal_image = self.findChild(VisionCameraImage, 'normal_image')
        self.normal_image.set_controller(controller)
        self.normal_image.set_can_add_frame_point(True)

        self.cutting_frame = self.findChild(VisionCameraImage, 'cutting_frame')
        self.cutting_frame.set_controller(controller)

        self.thread = VisionThread()
        self.thread.updated_img.connect(self.update_normal_image)
        self.thread.cutting_frame.connect(self.update_cutting_frame)
        self.thread.start()

    def update_normal_image(self, image):
        self.normal_image.setPixmap(QPixmap.fromImage(image))

    def update_cutting_frame(self, image):
        self.cutting_frame.setPixmap(QPixmap.fromImage(image))
