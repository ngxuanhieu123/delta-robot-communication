from ..views import VisionWidget
from ..models import Model, Command, CoordinateTransformer, CenterDetector, TrajectoryPredictor
from ..models.properties import Property, DefaultParam
from .controller import Controller
from time import time, sleep



class VisionSystemModel(Model):
    def __init__(self):
        super().__init__()
        self._current_pos = (0, 0)
        self._cutting_frame_points = []
        self._points = []
        self._show_binary_frame = False
        self._values = {
            "area_threshold": 2000,
            "binary_threshold": 225,
            "radius": 3,
            "speed": 840,
            "moving_delay": 10,
            "grabbing_delay": 500, 
            "predicted_time": 42
        }
        self._grab_loop = False
        self.center_detector = CenterDetector(values=self._values)
        self.predictor = TrajectoryPredictor()

    def get_grab_loop(self):
        return self._grab_loop

    def toggle_grab_loop(self):
        self._grab_loop = not self._grab_loop

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

    def add_point(self, point):
        self._points.append(point)
        self.model_is_changed()

    def clear_points(self):
        self._points = []
        self.model_is_changed()

    def get_points(self):
        return self._points

    def show_binary_frame(self):
        return self._show_binary_frame

    def toggle_show_binary_frame(self):
        self._show_binary_frame = not self._show_binary_frame
        self.model_is_changed()

    def get_values(self, key):
        if key in self._values.keys():
            return self._values[key]
        else:
            return 0

    def set_values(self, key, value):
        if key in self._values.keys():
            self._values[key] = value

        self.model_is_changed()

    def get_point(self):
        if len(self._points) != 0:
            return True, self._points[0]
        else:
            return False, None

class VisionSystemController:
    def __init__(self, ui_dir="ui_files/vision_system.ui"):
        self.win = VisionWidget(self)
        self.model = VisionSystemModel()
        self.model.add_observer(self.win.thread)
        self.model.add_observer(self.win.limit_area_label)
        self.model.add_observer(self.win.limit_area_slider)
        self.model.add_observer(self.win.binary_threshold_label)
        self.model.add_observer(self.win.binary_threshold_slider)
        self.model.add_observer(self.win.speed_label)
        self.model.add_observer(self.win.speed_slider)
        self.model.add_observer(self.win.moving_delay_label)
        self.model.add_observer(self.win.moving_delay_slider)
        self.model.add_observer(self.win.grabbing_delay_label)
        self.model.add_observer(self.win.grabbing_delay_slider)
        self.model.add_observer(self.win.predicted_time_label)
        self.model.add_observer(self.win.predicted_time_slider)
        self.transformer = CoordinateTransformer()
        self.transformer.load_weight()

        address_property = Property()
        self.command = Command(address_property=address_property)
        self.connection_controller = Controller(command=self.command)
        self.command.reset_command()

        try:
            self.connection_controller.connect("192.168.27.16", 502)
        except Exception as e:
            print(e)

        self.grap_loop = True

    def show(self):
        self.win.show()

    def grab_product(self, point):
#        first_time = time()
#
#        for i in range(self.model.predictor.get_num_data_points()):
#            time_val = time() - first_time
#            try:
#                point = self.model.center_detector.get_current_points()[0]
#                self.model.predictor.add_point(point, time_val * 1000)
#            except:
#                pass
#
#            sleep(self.model.predictor.get_sample_time()/1000)
#
#        point = self.model.predictor.predict(time=self.model.get_values("predicted_time"))

        point = (point[0] + self.model.get_values("predicted_time"), point[1] + self.model.get_values("moving_delay"))
        point = self.transformer.convert(point)

        if point[0] > 400000:
            point = (400000, point[1])
        if point[0] < -400000:
            point = (-400000, point[1])
        if point[1] > 400000:
            point = (point[0], 400000)
        if point[1] < -400000:
            point = (point[0], -400000)

        self.connection_controller.move(int(point[0]), int(point[1]), -700000, delay=1000, speed=self.model.get_values("speed"))


        self.connection_controller.move(int(point[0]), int(point[1]), -775000, delay=self.model.get_values("grabbing_delay"), speed=self.model.get_values("speed"))
        self.connection_controller.control_out(1)

        self.connection_controller.move(int(point[0]), int(point[1]), -700000, delay=1000, speed=self.model.get_values("speed"))

        self.connection_controller.move(-166159, 342836, -650000, delay=1000, speed=self.model.get_values("speed"))

        self.connection_controller.control_out(1, is_on=False)
