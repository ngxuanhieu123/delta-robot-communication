from ..views import CameraMapping
from ..models import CoordinateTransformer


class CameraMappingController:
    def __init__(self, ui_file=""):
        self.win = CameraMapping(ui_file)
        self.transformer = CoordinateTransformer()

    def add_point(self, point_with_img_coordinate, point_with_robot_coordinate):
        enough_point = self.transformer.add_points([point_with_img_coordinate, point_with_robot_coordinate])
