from ..views import CameraMapping
from ..models.properties import Property, DefaultParam
from .controller import Controller

from ..models import CoordinateTransformer, Model, Command


class CameraMappingModel(Model):
    def __init__(self):
        super().__init__()
        self.transformer = CoordinateTransformer()
        self.is_testing = False

    def toggle_mode(self):
        self.is_testing = not self.is_testing
        self.model_is_changed()

    def load_weight(self):
        self.transformer.load_weight()
        print(self.transformer._transform_matrix)
        self.model_is_changed()


class CameraMappingController:
    def __init__(self):
        self.win = CameraMapping(self)
        self.model = CameraMappingModel()
        self.model.transformer.add_observer(self.win.webcam_thread)
        self.model.transformer.add_observer(self.win.side_bar)
        self.model.add_observer(self.win.webcam_thread)
        self.model.add_observer(self.win.main_page.img)

    def show(self):
        self.win.show()

    def add_point(self, point_with_img_coordinate):
        self.model.transformer.add_point(point_with_img_coordinate)

    def add_equivalent_point(self, point_with_robot_coordinate):
        enough = self.model.transformer.add_equivalent_point(point_with_robot_coordinate)

    def remove_latest_point(self):
        self.model.transformer.remove_latest_point()

    def clear_model(self):
        self.model.transformer.remove_all()

    def save_weight(self):
        self.model.transformer.save_weight()

    def change_mode(self):
        self.model.toggle_mode()

    def load_weight(self):
        self.model.load_weight()

    def move_to(self, point):
        result = self.model.transformer.convert(point)
        address_property = Property()
        command = Command(address_property=address_property, params=[DefaultParam() for _ in range(Command.NUM_PARAMS)])
        command.set_function(3)
        command.set_param(0, Property(num_bytes=4, reverse=True))
        command.set_param_value(0, int(result[0]))
        command.set_param(1, Property(num_bytes=4, reverse=True))
        command.set_param_value(1, int(result[1]))
        command.set_param(2, Property(num_bytes=4, reverse=True))
        command.set_param_value(2, -700000)
        command.set_param(4, Property(num_bytes=4, reverse=True))
        command.set_param_value(4, 1000)

        controller = Controller(command=command)

        print(controller.command.to_hex())
        controller.connect("192.168.27.16", 502)
        controller.send(controller.command.to_hex())
        controller.disconnect()
