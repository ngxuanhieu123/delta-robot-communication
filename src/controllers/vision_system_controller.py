from ..views import VisionWidget
from ..models import Model, Command, CoordinateTransformer
from ..models.properties import Property, DefaultParam
from .controller import Controller



class VisionSystemModel(Model):
    def __init__(self):
        super().__init__()
        self._boxes_min_point = []
        self._boxes_max_point = []
        self._current_pos = (0, 0)
        self._cutting_frame_points = []
        self._points = []
        self._show_binary_frame = False
        self._values = {
            "limit_area": 700
        }
        self._grab_loop = False

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
        self.transformer = CoordinateTransformer()
        self.transformer.load_weight()

        address_property = Property()
        self.command = Command(address_property=address_property)
        self.connection_controller = Controller(command=self.command)
        self.command.reset_command()

        self.connection_controller.connect("192.168.27.16", 502)

        self.grap_loop = True

    def show(self):
        self.win.show()

    def _command_to_move_command(self, x_val, y_val, z_val=-700000, speed=1000, delay=0):
        self.command.reset_command()
        self.command.set_function(3)

        self.command.set_param(0, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(0, x_val)
        self.command.set_param(1, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(1, y_val)
        self.command.set_param(2, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(2, z_val)
        self.command.set_param(4, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(4, speed)
        self.command.set_delay(delay)

    def _command_to_control_out(self, out_num, is_on=True):
        self.command.reset_command()
        self.command.set_function(12)
        self.command.set_param(0, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(0, out_num * 1000)
        self.command.set_param(1, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(1, 1000 if is_on == True else 0)


    def grab_product(self, point):
        print(point)
        point = self.transformer.convert(point)
        print(point)

        self._command_to_move_command(int(point[0]), int(point[1]), -650000, delay=1000)
        print(self.command.to_hex())
        self.connection_controller.send(self.command.to_hex())

        self._command_to_move_command(int(point[0]), int(point[1]), -750000, delay=1000)
        print(self.command.to_hex())
        self.connection_controller.send(self.command.to_hex())

        self._command_to_control_out(1)
        print(self.command.to_hex())
        self.connection_controller.send(self.command.to_hex())

        self._command_to_move_command(int(point[0]), int(point[1]), -650000, delay=500)
        print(self.command.to_hex())
        self.connection_controller.send(self.command.to_hex())

        self._command_to_move_command(0, 0, -650000, delay=1000)
        print(self.command.to_hex())
        self.connection_controller.send(self.command.to_hex())

        self._command_to_control_out(1, is_on=False)
        print(self.command.to_hex())
        self.connection_controller.send(self.command.to_hex())

    def grab(self):
        remain, point = self.model.get_point()
        self.grab_product(point)
