from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QImage


class CameraLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self.thread = None 

    def config(self, controller, thread, img):
        self.controller = controller
        self.thread = thread
        img.connect(self.update_frame)
        self.controller.model.add_observer(self)

    def mousePressEvent(self, event):
        mapping_points = self.controller.model.get_value("mapping_points")
        robot_mapping_points = self.controller.model.get_value("robot_mapping_points")
        is_testing = self.controller.model.get_value("is_testing")
        point = [event.x(), event.y()]

        if is_testing:
            self.controller.model.set_value("testing_point", point)
        else:
            if len(mapping_points) == len(robot_mapping_points):
                mapping_points.append(point)
                self.controller.model.set_value("mapping_points", mapping_points)

    def update_frame(self, img):
        self.setPixmap(QPixmap.fromImage(img))

    def model_is_changed(self, model):
        pass


class VisionCameraLabel(CameraLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)

    def mouseMoveEvent(self, event):
        self.controller.model.set_value("current_pointer_on_vision_label", [event.x(), event.y()])

    def mousePressEvent(self, event):
        starting_point = self.controller.model.get_value("cutting_frame_starting_point")
        has_cutting_frame = self.controller.model.get_value("has_cutting_frame")
        current_point = [event.x(), event.y()]

        if not has_cutting_frame:
            if starting_point is None:
                self.controller.model.set_value("cutting_frame_starting_point", [event.x(), event.y()])
            else:
                self.controller.model.set_value("has_cutting_frame", True)
                self.controller.model.set_value("cutting_frame_x_min", min(current_point[0], starting_point[0]))
                self.controller.model.set_value("cutting_frame_x_max", max(current_point[0], starting_point[0]))
                self.controller.model.set_value("cutting_frame_y_min", min(current_point[1], starting_point[1]))
                self.controller.model.set_value("cutting_frame_y_max", max(current_point[1], starting_point[1]))
                self.controller.update_center_detector()

    def model_is_changed(self, model):
        pass
