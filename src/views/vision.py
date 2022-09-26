from PyQt5.QtWidgets import QWidget, QPushButton
from PyQt5.QtGui import QPixmap
from .vision_camera_image import VisionCameraImage
from .vision_thread import VisionThread
from PyQt5.uic import loadUi
from .components import EditableLabel, ControllableSlider
from threading import Thread
from multiprocessing import Process



class VisionWidget(QWidget):
    def __init__(self, controller, ui_dir="ui_files/vision_system.ui"):
        super().__init__()
        loadUi(ui_dir, self)
        self.controller = controller
        self._run_continuously = False
        self.command_thread = None

        self.normal_image = self.findChild(VisionCameraImage, 'normal_image')
        self.normal_image.set_controller(controller)
        self.normal_image.set_can_add_frame_point(True)

        self.thread = VisionThread()
        self.thread.set_controller(controller)
        self.thread.updated_img.connect(self.update_normal_image)
        self.thread.start()

        self.show_binary_frame_btn = self.findChild(QPushButton, 'show_binary_frame_btn')
        self.show_binary_frame_btn.clicked.connect(lambda x: self.controller.model.toggle_show_binary_frame())

        self.limit_area_label = self.findChild(EditableLabel, 'limit_area_label')
        self.limit_area_label.set_text("Limit Area: ")
        self.limit_area_label.set_updated_key("area_threshold")

        self.limit_area_slider = self.findChild(ControllableSlider, 'limit_area_slider')
        self.limit_area_slider.set_updated_key("area_threshold")
        self.limit_area_slider.set_controller(controller)

        self.binary_threshold_label = self.findChild(EditableLabel, "binary_threshold_label")
        self.binary_threshold_label.set_text("Binary Threshold: ")
        self.binary_threshold_label.set_updated_key("binary_threshold")

        self.binary_threshold_slider = self.findChild(ControllableSlider, "binary_threshold_slider")
        self.binary_threshold_slider.set_updated_key("binary_threshold")
        self.binary_threshold_slider.set_controller(controller)

        self.speed_label = self.findChild(EditableLabel, "speed_label")
        self.speed_label.set_text("Speed: ")
        self.speed_label.set_updated_key("speed")

        self.speed_slider = self.findChild(ControllableSlider, "speed_slider")
        self.speed_slider.set_updated_key("speed")
        self.speed_slider.set_controller(controller)

        self.moving_delay_label = self.findChild(EditableLabel, "moving_delay_label")
        self.moving_delay_label.set_text("Y adaptie: ")
        self.moving_delay_label.set_updated_key("moving_delay")

        self.moving_delay_slider = self.findChild(ControllableSlider, "moving_delay_slider")
        self.moving_delay_slider.set_updated_key("moving_delay")
        self.moving_delay_slider.set_controller(controller)

        self.grabbing_delay_label = self.findChild(EditableLabel, "grabbing_delay_label")
        self.grabbing_delay_label.set_text("Grabbing Delay: ")
        self.grabbing_delay_label.set_updated_key("grabbing_delay")

        self.grabbing_delay_slider = self.findChild(ControllableSlider, "grabbing_delay_slider")
        self.grabbing_delay_slider.set_updated_key("grabbing_delay")
        self.grabbing_delay_slider.set_controller(controller)

        self.predicted_time_label = self.findChild(EditableLabel, "predicted_time_label")
        self.predicted_time_label.set_text("X adapt: ")
        self.predicted_time_label.set_updated_key("predicted_time")

        self.predicted_time_slider = self.findChild(ControllableSlider, "predicted_time_slider")
        self.predicted_time_slider.set_updated_key("predicted_time")
        self.predicted_time_slider.set_controller(controller)

        self.run_continuously_btn = self.findChild(QPushButton, "run_continuously_btn")
        self.run_continuously_btn.clicked.connect(self.grab_continuously)

        self.stop_btn = self.findChild(QPushButton, "stop_btn")
        self.stop_btn.clicked.connect(self.stop_run_continuously)

    def update_normal_image(self, image):
        self.normal_image.setPixmap(QPixmap.fromImage(image))

    def update_cutting_frame(self, image):
        self.cutting_frame.setPixmap(QPixmap.fromImage(image))

    def _grab_product(self):
        while self._run_continuously:
            if len(self.controller.model.center_detector.get_current_points()) != 0:
                try:
                    self.controller.grab_product(self.controller.model.center_detector.get_current_points()[0])
                except Exception as e:
                    print(e)

    def grab_obj(self):
        try:
            self.command_thread = Thread(target=self.controller.grab_product)
            self.command_thread.start()
        except Exception as e:
            print(e)

    def grab_continuously(self):
        self._run_continuously = True
        try:
            self.command_thread = Thread(target=self._grab_product)
            self.command_thread.start()
        except Exception as e:
            print(e)

    def stop_run_continuously(self):
        self._run_continuously = False
        try:
            self.command_thread.join()
        except Exception as e:
            print(e)

