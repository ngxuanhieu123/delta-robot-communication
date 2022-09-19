from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QPixmap
from .vision_camera_image import VisionCameraImage
from .vision_thread import VisionThread
from PyQt5.uic import loadUi
from .components import EditableLabel, ControllableSlider



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
        self.thread.set_controller(controller)
        self.thread.updated_img.connect(self.update_normal_image)
        self.thread.cutting_frame.connect(self.update_cutting_frame)
        self.thread.start()

        self.show_binary_frame_btn = self.findChild(QPushButton, 'show_binary_frame_btn')
        self.show_binary_frame_btn.clicked.connect(lambda x: self.controller.model.toggle_show_binary_frame())

        self.limit_area_label = self.findChild(EditableLabel, 'limit_area_label')
        self.limit_area_label.set_text("Limit Area: ")
        self.limit_area_label.set_updated_key("limit_area")

        self.limit_area_slider = self.findChild(ControllableSlider, 'limit_area_slider')
        self.limit_area_slider.set_updated_key("limit_area")
        self.limit_area_slider.set_controller(controller)

        self.run_once_btn = self.findChild(QPushButton, 'run_once_btn')
        self.run_once_btn.clicked.connect(self.grab_obj)

    def update_normal_image(self, image):
        self.normal_image.setPixmap(QPixmap.fromImage(image))

    def update_cutting_frame(self, image):
        self.cutting_frame.setPixmap(QPixmap.fromImage(image))

    def grab_obj(self):
        try:
            self.controller.grab_product(self.controller.model.get_points()[0])
        except Exception as e:
            print(e)
