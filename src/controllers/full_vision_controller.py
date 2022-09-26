from ..models.full_vision_model import FullVisionModel
from ..views.full_vision import FullVisionWidget
from .controller import Controller
from ..models.properties import Property, DefaultParam
from ..models import Command
from ..models import CoordinateTransformer, CenterDetector
from ..views.choosing_camera_dialog import ChoosingCameraDialog
from ..views.thread import PickingThread
import os
from threading import Thread
from multiprocessing import Process
from copy import deepcopy



class FullVisionController:
    def __init__(self, path=""):
        self.connection = self.create_connection()
        self.transformer = CoordinateTransformer()
        self.model = FullVisionModel(self)
        self.choosing_webcam = ChoosingCameraDialog(self)
        self.choosing_webcam.show()
        self.widget = FullVisionWidget(self)
        self.detector = self.create_center_detector()
        self.path = path
        self.picking = False
        self.picking_stm = False

    def _get_params_by_keys(self, keys=[], in_dict={}, multiple_by_thousand=False):
        params = self.model.get_values()

        for key in keys:
            if not multiple_by_thousand:
                in_dict[key] = params[key]
            else:
                in_dict[key] = int(round(params[key] * 1000))
        return in_dict

    def run(self):
        if self.picking:
            name, direction = self.model.get_value("line_direction", is_combo_box=True)
            catch_line = self.model.get_value("catch_line")
            adapt_x = self.model.get_value("adapt_x")

            points = self.model.get_value("points")
            data = {}
            data = self._get_params_by_keys(["moving_speed", "moving_delay", "grabbing_speed", 
                            "grabbing_delay"], data)
            data = self._get_params_by_keys(["z_val_low", "z_val_high", "x_val_target",
                            "y_val_target", "z_val_target"], data, multiple_by_thousand=True)

            for point in points:
                if not self.picking_stm:
                    if name == "Horizontal":
                        if point[1] < catch_line:
                            x_val, y_val = self.convert([point[0], point[1] + adapt_x])
                            x_real_val = int(round(x_val * 1000))
                            y_real_val = int(round(y_val * 1000))
                            data["x_val"] = x_real_val
                            data["y_val"] = y_real_val
                            self.picking_stm = True
                            thread = Thread(target=self.connection.pick_and_place, args=(data, ), kwargs={"controller": self})
                            thread.start()
                    elif name == "Vertical":
                        if point[0] > catch_line:
                            x_val, y_val = self.transformer.convert([point[0] + adapt_x, point[1]])
                            x_real_val = int(round(x_val * 1000))
                            y_real_val = int(round(y_val * 1000))
                            data["x_val"] = x_real_val
                            data["y_val"] = y_real_val
                            self.picking_stm = True
                            thread = Thread(target=self.connection.pick_and_place, args=(data, ), kwargs={"controller": self})
                            thread.start()
            
    def create_connection(self):
        address_property = Property()
        command = Command(address_property=address_property, params=[DefaultParam() for _ in range(Command.NUM_PARAMS)])
        connection = Controller(command=command)
        connection.connect("192.168.27.16", 502)
        return connection

    def create_center_detector(self):
        return CenterDetector(values=self.model.get_values())

    def update_center_detector(self):
        cutting_frame_x_min = self.model.get_value("cutting_frame_x_min")
        cutting_frame_y_min = self.model.get_value("cutting_frame_y_min")
        self.detector.set_shifting_frame([cutting_frame_x_min, cutting_frame_y_min])
        self.detector.set_all_values(self.model.get_values())

    def get_transform_weight(self):
        mapping_points = self.model.get_value("mapping_points")
        robot_mapping_points = self.model.get_value("robot_mapping_points")

        for mapping_point, robot_mapping_point in zip(mapping_points, robot_mapping_points):
            self.transformer.add_point(mapping_point)
            self.transformer.add_equivalent_point(robot_mapping_point)

        matrix = self.transformer.get_matrix()
        self.model.set_value("transformer_weight", matrix.tolist() if matrix is not None else None)

    def convert(self, point):
        return self.transformer.convert(point)

    def show(self):
        self.widget.webcam_thread.start()
        self.widget.show()
