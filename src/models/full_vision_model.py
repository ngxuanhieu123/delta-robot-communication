from .i_model import Model
import json
import cv2 as cv


COLORS = {
        "Red": (255, 0, 0),
        "Green": (0, 255, 0),
        "Blue": (0, 0, 255),
        "White": (255, 255, 255),
        "Black": (0, 0, 0)
        }


class FullVisionModel(Model):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._params = {
            "current_x": 1.00,
            "current_y": 0.00,
            "current_z": -700.0,
            "speed": 1.0,
            "x_min": -400.0,
            "x_max": 400.0,
            "y_min": -400.0,
            "y_max": 400.0,
            "z_min": -800.0,
            "z_max": -600.0,
            "z_val_low": -775.000,
            "z_val_high": -750.000,
            "x_val_target": 200.000,
            "y_val_target": 400.000,
            "z_val_target": -700.000,
            "catch_first_speed": 300,
            "catch_first_delay": 1500,
            "catch_second_speed": 300,
            "catch_second_delay": 100,
            "unit_factor": 0.125,
            "moving_speed": 1000,
            "grabbing_speed": 1000,
            "moving_delay": 500,
            "grabbing_delay": 1000,
            "adapt_x": -30,
            "encoder_value": 0.0,
            "config_file": "Empty",
            "image_size": {"options": {"180x180":(180, 180), "200x200": (200, 200), "300x300": (300, 300), "500x400":(500, 400)}, "value": "500x400"},
            "binary_threshold": 125,
            "contour_kernel": {"options": {"Binary": "binary", "Gaussian": "gaussian"}, "value": "Gaussian"},
            "area_threshold": 700,
            "point_radius": 3,
            "kernel": {"options": {"5x5": (5, 5), "4x4": (4, 4), "3x3": (3, 3)}, "value": "5x5"},
            "catch_line": 354,
            "line_direction": {"options": {"Vertical": 0, "Horizontal": 1}, "value": "Vertical"},
            "catching_line_color": {"options": COLORS, "value": "Blue"},
            "out_state": False,
            "origin_x": 0.,
            "origin_y": 1.,
            "origin_z": -700.,
            "cam_id": {"options": {"Default Webcam": 0}, "value": "Default Webcam"}, 
            "mapping_points": [],
            "mapping_points_color": {"options": COLORS, "value": "Green"},
            "robot_mapping_points": [], 
            "transformer_weight": None,
            "is_testing": False,
            "testing_point": [0, 0],
            "has_cutting_frame": False,
            "cutting_frame_x_min": 0,
            "cutting_frame_x_max": 500,
            "cutting_frame_y_min": 0,
            "cutting_frame_y_max": 500,
            "cutting_frame_starting_point": None,
            "current_pointer_on_vision_label": [0, 0],
            "cutting_frame_color": {"options": COLORS, "value": "White"},
            "cutting_frame_thickness": 1,
            "points": [],
            "encoder_value": 0,
            "angles": [],
            "show_binary_frame": False,
            "center_point_color": {"options": COLORS, "value": "Red"}
        }

#        self.load("test.json")
        self.get_camera_id()

    def get_camera_id(self):
        available_camera_id = []
        result = {}
        for i in range(10):
            cam_test = cv.VideoCapture(i)
            ret, _ = cam_test.read()
            if ret:
                available_camera_id.append(i)

        for camera_id in available_camera_id:
            if camera_id == 0:
                result["Default Webcam"] = camera_id
            else:
                result[f"Webcam {camera_id}"] = camera_id

        self._params["cam_id"] = {"options": result, "value": list(result.keys())[0]}

    def get_value(self, key, is_combo_box=False):
        if not is_combo_box:
            if key in self._params.keys():
                return self._params[key]
            else:
                return 0.0
        else:
            if key in self._params.keys():
                value = self._params[key]["value"]
                return value, self._params[key]["options"][value]

    def set_value(self, key, new_value):
        if key in self._params.keys():
            self._params[key] = new_value
            self.model_is_changed()

    def save(self, file_name):
        with open(file_name, "w") as json_file:
            json.dump(self._params, json_file, separators=(',\n', ':'))

    def load(self, file_name):
        with open(file_name, "r") as json_file:
            self._params = json.load(json_file)

        self.controller.transformer.set_weight(self._params["transformer_weight"])
        self.controller.update_center_detector()
        self.model_is_changed()

    def get_values(self):
        return self._params
