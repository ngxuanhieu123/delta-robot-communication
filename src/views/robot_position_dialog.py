from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog, QDoubleSpinBox



class RobotPositionDialog(QDialog):
    def __init__(self, controller, ui_file="ui_files/robot_position_dialog.ui", parent=None):
        super().__init__(parent)
        loadUi(ui_file, self)
        self.controller = controller

        self.x_spin_box = self.findChild(QDoubleSpinBox, 'x_value')
        self.y_spin_box = self.findChild(QDoubleSpinBox, 'y_value')
        self.accepted.connect(self.add_point_to_robot_mapping)

    def add_point_to_robot_mapping(self):
        robot_mapping_points = self.controller.model.get_value("robot_mapping_points")
    
        robot_mapping_points.append([self.x_spin_box.value(), self.y_spin_box.value()])     
        self.controller.model.set_value("robot_mapping_points", robot_mapping_points)
