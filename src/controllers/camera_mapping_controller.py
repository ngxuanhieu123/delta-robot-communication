from ..views import CameraMapping
from ..models import CoordinateTransformer


class CameraMappingController:
    def __init__(self):
        self.win = CameraMapping(self)
        self.transformer = CoordinateTransformer()
        self.transformer.add_observer(self.win.webcam_thread)
        self.transformer.add_observer(self.win.side_bar)

    def show(self):
        self.win.show()

    def add_point(self, point_with_img_coordinate):
        self.transformer.add_point(point_with_img_coordinate)

    def add_equivalent_point(self, point_with_robot_coordinate):
        enough = self.transformer.add_equivalent_point(point_with_robot_coordinate)

    def remove_latest_point(self):
        self.transformer.remove_latest_point()
