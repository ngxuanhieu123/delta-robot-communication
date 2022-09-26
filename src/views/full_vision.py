from PyQt5.uic import loadUi
import cv2 as cv
from PyQt5.QtWidgets import QWidget, QPushButton, QFileDialog, QLabel, QSpinBox
from PyQt5.QtGui import QPixmap
from .components import DoubleSpinBox, ComboBox, SpinBox, Label, CameraLabel, DisplayPointSpinBox, DisplayPointDoubleSpinBox, VisionCameraLabel
from .robot_position_dialog import RobotPositionDialog
from .thread import WebcamThread
import os
from threading import Thread
from time import sleep
from functools import partial


class FullVisionWidget(QWidget):
    def __init__(self, controller, ui_file="ui_files/full_project_widget.ui"):
        super().__init__()
        loadUi(ui_file, self)
        self.controller = controller

        double_spin_boxes = ['current_x', 'current_y', 'current_z', 
                    'speed', 'x_min', 'x_max', 'y_min', 'y_max', 
                    'z_min', 'z_max', 'encoder_value',
                    'origin_x', 'origin_y', 'origin_z', "z_val_low", 
                    "z_val_high", "x_val_target", "y_val_target",
                    "z_val_target"]
        self.config(DoubleSpinBox, double_spin_boxes)

        combo_boxes = ['image_size', 'kernel', 'cam_id', 'cutting_frame_color', 'center_point_color',
                'contour_kernel', 'line_direction', 'catching_line_color']
        self.config(ComboBox, combo_boxes)

        spin_boxes = ['area_threshold', 'binary_threshold', "cutting_frame_x_min", "cutting_frame_x_max", 
                "cutting_frame_y_min", "cutting_frame_y_max", "cutting_frame_thickness", "catch_line", "adapt_x",
                "moving_speed", "moving_delay", "grabbing_delay", "grabbing_speed"]
        self.config(SpinBox, spin_boxes)

        labels = ['config_file']
        self.config(Label, labels)

        display_point_labels = ['img_0_0', 'img_0_1', 'img_0_2', 'img_0_3', 'img_0_4', 'img_0_5',
                'img_1_0', 'img_1_1', 'img_1_2', 'img_1_3', 'img_1_4', 'img_1_5']
        self.config_display_points(QSpinBox, display_point_labels)

        robot_display_point_labels = ['robot_0_0', 'robot_0_1', 'robot_0_2', 'robot_0_3', 'robot_0_4', 'robot_0_5',
                'robot_1_0', 'robot_1_1', 'robot_1_2', 'robot_1_3', 'robot_1_4', 'robot_1_5']
        self.config_display_points(DisplayPointDoubleSpinBox, robot_display_point_labels, topic="robot_mapping_points")

        weight_labels = ['w_0_0', 'w_0_1', 'w_2_0', 'w_1_0', 'w_1_1', 'w_2_1']
        self.config_display_points(DisplayPointDoubleSpinBox, weight_labels, topic="transformer_weight")

        self.config_btn('save_config_btn', self.save_config)
        self.config_btn('load_config_btn', self.load_config)
        self.config_btn('remove_latest_mapping_point_btn', self.remove_latest_mapping_point)
        self.config_btn('increase_x_btn', self.increase_x_the_latest_mapping_point)
        self.config_btn('decrease_x_btn', self.decrease_x_the_latest_mapping_point)
        self.config_btn('increase_y_btn', self.increase_y_the_latest_mapping_point)
        self.config_btn('decrease_y_btn', self.decrease_y_the_latest_mapping_point)
        self.config_btn('add_point_btn', self.open_add_point_dialog)
        self.config_btn('clear_points_btn', self.clear_points)
        self.config_btn('calculate_weight_btn', self.controller.get_transform_weight)
        self.config_btn('testing_btn', self.turn_on_testing_mode)
        self.config_btn('new_cutting_frame_btn', self.reset_cutting_frame)
        self.config_btn('show_binary_frame_btn', self.toggle_show_binary_frame)
        self.config_btn("move_robot_btn", self.move_robot)
        self.config_btn("move_home_btn", self.move_origin)
        self.config_btn("increase_x_val_btn", partial(self.controller.connection.increase_x, step=30000, controller=self.controller))
        self.config_btn("decrease_x_val_btn", partial(self.controller.connection.decrease_x, step=30000, controller=self.controller))
        self.config_btn("increase_y_val_btn", partial(self.controller.connection.increase_y, step=30000, controller=self.controller))
        self.config_btn("decrease_y_val_btn", partial(self.controller.connection.decrease_y, step=30000, controller=self.controller))
        self.config_btn("increase_z_val_btn", partial(self.controller.connection.increase_z, step=10000, controller=self.controller))
        self.config_btn("decrease_z_val_btn", partial(self.controller.connection.decrease_z, step=10000, controller=self.controller))
        self.config_btn("change_cam_btn", self.change_cam)
        self.config_btn("run_btn", self.run)
        self.config_btn("reset_btn", self.reset)
        self.config_btn("toggle_out_btn", self.control_valve)

        self.mapping_camera_label = self.findChild(CameraLabel, 'mapping_camera_label')
        self.vision_camera_label = self.findChild(VisionCameraLabel, 'vision_camera_label')

        self.webcam_thread = WebcamThread(controller)
        self.mapping_camera_label.config(controller, self.webcam_thread, self.webcam_thread.updated_img)
        self.vision_camera_label.config(controller, self.webcam_thread, self.webcam_thread.vision_img)

    def run(self):
        print("Hello")
        self.controller.picking = not self.controller.picking

    def config_display_points(self, class_name, display_point_labels, topic="mapping_points"):
        for label in display_point_labels:
            try:
                box = self.findChild(class_name, label)
                components = label.split("_")
                box.config(self.controller, topic, int(components[-1]), int(components[-2]))
            except Exception as e:
                print(f"[ERROR] {e} \n\tLabel: {label}")

    def config_btn(self, name, func):
        try:
            btn = self.findChild(QPushButton, name)
            btn.clicked.connect(func)
        except Exception as e:
            print(f"[ERROR] {e} \n\tName: {name}")

    def config(self, class_name, topics):
        for topic in topics:
            try:
                box = self.findChild(class_name, topic)
                box.config(self.controller, topic)
            except Exception as e:
                print(f"[ERROR] {e} \n\tTopic: {topic}")

    def save_config(self):
        def save_config_func(self):
            try:
                file_name, _ = QFileDialog.getSaveFileName(self, "Save config", "", "(*.json)")
                self.controller.model.save(file_name)
            except Exception as e:
                print(e)
        thread = Thread(target=save_config_func, args=(self,))
        thread.start()

    def load_config(self):
        def load_config_func(self):
            try:
                file_name, _ = QFileDialog.getOpenFileName(self, "Load config", "", "(*.json)")
                self.controller.model.load(file_name)
                self.controller.model.set_value("config_file", os.path.relpath(file_name, self.controller.path))
                self.controller.transformer.set_weight(self.controller.model.get_value("transformer_weight"))
            except Exception as e:
                print(e)

        thread = Thread(target=load_config_func, args=(self,))
        thread.start()

    def remove_latest_mapping_point(self):
        mapping_points = self.controller.model.get_value("mapping_points")
        robot_mapping_points = self.controller.model.get_value("robot_mapping_points")
        if len(mapping_points) >= 1:
            self.controller.model.set_value("mapping_points", mapping_points[:-1])
            self.controller.model.set_value("robot_mapping_points", robot_mapping_points[0:len(mapping_points) - 1])
        

    def increase_x_the_latest_mapping_point(self):
        mapping_points = self.controller.model.get_value("mapping_points")
        if len(mapping_points) >= 1:
            mapping_points[-1][0] += 1

        self.controller.model.set_value("mapping_points", mapping_points)

    def decrease_x_the_latest_mapping_point(self):
        mapping_points = self.controller.model.get_value("mapping_points")
        if len(mapping_points) >= 1:
            mapping_points[-1][0] -= 1

        self.controller.model.set_value("mapping_points", mapping_points)

    def increase_y_the_latest_mapping_point(self):
        mapping_points = self.controller.model.get_value("mapping_points")
        if len(mapping_points) >= 1:
            mapping_points[-1][1] += 1

        self.controller.model.set_value("mapping_points", mapping_points)

    def decrease_y_the_latest_mapping_point(self):
        mapping_points = self.controller.model.get_value("mapping_points")
        if len(mapping_points) >= 1:
            mapping_points[-1][1] -= 1

        self.controller.model.set_value("mapping_points", mapping_points)

    def open_add_point_dialog(self):
        mapping_points = self.controller.model.get_value("mapping_points")
        robot_mapping_points = self.controller.model.get_value("robot_mapping_points")
        if len(mapping_points) > len(robot_mapping_points):
            dialog = RobotPositionDialog(self.controller)
            dialog.show()
            dialog.exec_()

    def clear_points(self):
        self.controller.model.set_value("mapping_points", [])
        self.controller.model.set_value("robot_mapping_points", [])
        self.controller.model.set_value("transformer_weight", None)
        self.controller.transformer.remove_all()

    def turn_on_testing_mode(self):
        previous_state = self.controller.model.get_value("is_testing")
        self.controller.model.set_value("is_testing", not previous_state)

    def reset_cutting_frame(self):
        self.controller.model.set_value("has_cutting_frame", False)
        self.controller.model.set_value("cutting_frame_starting_point", None)
        self.controller.model.set_value("points", [])

    def change_cam(self):
        self.webcam_thread.stop()
        self.webcam_thread.run()

    def toggle_show_binary_frame(self):
        show_binary = self.controller.model.get_value("show_binary_frame")
        self.controller.model.set_value("show_binary_frame", not show_binary)

    def _get_send_value(self, topic):
        return int(round(self.controller.model.get_value(topic) * 1000))

    def _set_current_value(self, topic, value):
        self.controller.set_value(topic, float(value)/1000)

    def move_origin(self):
        x_value = self._get_send_value("origin_x")
        y_value = self._get_send_value("origin_y")
        z_value = self._get_send_value("origin_z")
        self.controller.connection.move(x_value, y_value, z_value, speed=1000, controller=self.controller)

    def move_robot(self):
        x_value = self._get_send_value("current_x")
        y_value = self._get_send_value("current_y")
        z_value = self._get_send_value("current_z")
        self.controller.connection.move(x_value, y_value, z_value, speed=1000, controller=self.controller)

    def control_valve(self):
        out_state = self.controller.model.get_value("out_state")
        self.controller.model.set_value("out_state", not out_state)
        self.controller.connection.control_out(1, is_on=out_state, delay=100, controller=self.controller)

    def closeEvent(self, event):
        self.controller.connection.disconnect()

    def reset(self):
        self.controller.connection.reset()
