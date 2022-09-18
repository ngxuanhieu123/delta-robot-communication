from ..views import VisionWidget
from ..models import Model



class VisionSystemModel(Model):
    def __init__(self):
        super().__init__()
        self._boxes_min_point = []
        self._boxes_max_point = []
        self._current_pos = (0, 0)
        self._cutting_frame_points = []

    def add_cutting_frame_point(self, point):
        self._cutting_frame_points.append(point)
        self.model_is_changed()

    def need_max_point(self):
        return len(self._cutting_frame_points) < 2

    def has_min_point(self):
        return len(self._cutting_frame_points) == 1

    def get_min_point(self):
        assert self.need_max_point()
        assert self.has_min_point()
        return self._cutting_frame_points[0]

    def get_boxes(self):
        return [(min_point, max_point) for min_point, max_point in zip(self._boxes_min_point, self._boxes_max_point)]

    def change_current_pos(self, pos):
        self._current_pos = pos
        self.model_is_changed()

    def get_current_posistion(self):
        return self._current_pos

    def get_cutting_frame(self):
        return self._cutting_frame_points

    def has_cutting_frame(self):
        return len(self._cutting_frame_points) == 2


class VisionSystemController:
    def __init__(self, ui_dir="ui_files/vision_system.ui"):
        self.win = VisionWidget(self)
        self.model = VisionSystemModel()
        self.model.add_observer(self.win.thread)

    def show(self):
        self.win.show()
