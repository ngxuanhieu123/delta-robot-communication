from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QComboBox, QPushButton
from .camera_thread import WebcamThread
from .cam_image import CameraImage
from .components import LineEditWithLabel


class CameraMappingSideBar(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.initUi()
        self.controller = controller

    def initUi(self):
        sidebar_widget = QVBoxLayout(self)

        test_point = QHBoxLayout()
        sidebar_widget.addLayout(test_point)
        
        self.x_sys_value = LineEditWithLabel("X's on camera system")
        self.y_sys_value = LineEditWithLabel("Y's on camera system")

        test_point.addWidget(self.x_sys_value)
        test_point.addWidget(self.y_sys_value)

        result_point = QHBoxLayout()
        sidebar_widget.addLayout(result_point)

        self.x_robot_value = LineEditWithLabel("X's on robot system")
        self.y_robot_value = LineEditWithLabel("Y's on robot system")

        result_point.addWidget(self.x_robot_value)
        result_point.addWidget(self.y_robot_value)

        self.convert_btn = QPushButton("Convert")
        self.convert_btn.setEnabled(False)
        self.convert_btn.clicked.connect(self.convert)
        sidebar_widget.addWidget(self.convert_btn)

        self.testing_btn = QPushButton("Testing")
        sidebar_widget.addWidget(self.testing_btn)
        self.testing_btn.clicked.connect(self.convert_mode)
        self.testing_btn.setEnabled(False)

        self.save_weight_btn = QPushButton("Save Weight")
        sidebar_widget.addWidget(self.save_weight_btn)
        self.save_weight_btn.clicked.connect(self.save_weight)
        self.save_weight_btn.setEnabled(False)

    def save_weight(self):
        self.controller.model.transformer.save_weight()

    def convert_mode(self):
        print("Here")
        self.controller.change_mode()

    def convert(self):
        x = self.x_sys_value.get_text(return_type=int)
        y = self.y_sys_value.get_text(return_type=int)

        result = self.controller.model.transformer.convert((x, y))
        self.x_robot_value.set_text(str(result[0]))
        self.y_robot_value.set_text(str(result[1]))

    def model_is_changed(self, model):
        if model.can_convert():
            self.convert_btn.setEnabled(True)
            self.testing_btn.setEnabled(True)
            self.save_weight_btn.setEnabled(True)
        else:
            self.convert_btn.setEnabled(False)
            self.testing_btn.setEnabled(False)
            self.save_weight_btn.setEnabled(False)


class CameraMappingMain(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.initUi()

    def initUi(self):
        main_widget = QVBoxLayout(self)

        self.combo_box = QComboBox()
        main_widget.addWidget(self.combo_box)

        self.img = CameraImage(self.controller)
        main_widget.addWidget(self.img)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.controller.clear_model)
        main_widget.addWidget(clear_btn)
    
    def update_image(self, img):
        self.img.setPixmap(img)


class CameraMapping(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.initUi()

    def initUi(self):
        main_layout = QHBoxLayout(self)

        self.side_bar = CameraMappingSideBar(self.controller)
        main_layout.addWidget(self.side_bar)

        self.main_page = CameraMappingMain(self.controller)
        main_layout.addWidget(self.main_page)
        
        self.webcam_thread = WebcamThread()
        self.webcam_thread.start()
        self.webcam_thread.updated_img.connect(self.update_webcam)

    def update_webcam(self, img):
        self.main_page.update_image(QPixmap.fromImage(img))
