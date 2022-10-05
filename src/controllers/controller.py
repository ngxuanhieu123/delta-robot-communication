import socket
from ..utils import create_a_socket_client
from ..models import Command, Response
from ..models.properties import Property, DefaultParam
from time import sleep, time
import numpy as np 


class Controller:
    def __init__(self, command=None):
        self.client = create_a_socket_client()
        self.command = command
        self._x_value = 0
        self._y_value = 0
        self._z_value = 0
        self._limit_x = (-400000, 400000)
        self._limit_y = (-400000, 400000)
        self._limit_z = (-800000, -600000)
        self._connected = False

    def connect(self, ip_address, port, test=False):
        if not test:
            try:
                self.client.connect((ip_address, port))
                self._connected = True
            except Exception as e:
                print(f"[ERROR] {e}")
                self._connected = False 

    def is_connected(self):
        return self._connected

    def send(self, msg):
        self.client.send(msg)
        result = self.client.recv(100)
        if self.command is not None:
            first_time = time()
            print(f"[DEBUG] Delay start for msg: {msg}")
            self.command.delay()
            print(f"[DEBUG] Delay end for msg: {msg} - Cosuming time: {time() - first_time}")
        return result

    def set_function(self, function):
        self.command.set_function(function)

    def disconnect(self):
        print("[INFO]Disconnect")
        self.client.close()

    def set_params(self, params):
        self._params = params

    def _compare_restrict(self, value, limit):
        if limit is None:
            return value 
        else:
            if value < limit[0]:
                return limit[0]
            elif value > limit[1]:
                return limit[1]
            else:
                return value

    def _convert_to_robot_value(self, controller, topic):
        return int(round(controller.model.get_value(topic) * 1000))

    def _update_param(self, controller):
        try:
            self._limit_x = [self._convert_to_robot_value(controller, 'x_min'), self._convert_to_robot_value(controller, 'x_max')]
            self._limit_y = [self._convert_to_robot_value(controller, 'y_min'), self._convert_to_robot_value(controller, 'y_max')]
            self._limit_z = [self._convert_to_robot_value(controller, 'z_min'), self._convert_to_robot_value(controller, 'z_max')]
        except AttributeError as e:
            print(f"[ERROR] {e}")

    def move(self, x_val, y_val, z_val=-700000, speed=1000, delay=0, controller=None):
        print(f"[INFO] Start moving x: {x_val} - y: {y_val} - z: {z_val} - speed: {speed} - delay: {delay}")
        self._update_param(controller)
        self.command.reset_command()
        self.set_function(3)

        x_val = self._compare_restrict(x_val, self._limit_x)
        y_val = self._compare_restrict(y_val, self._limit_y)
        z_val = self._compare_restrict(z_val, self._limit_z)

        self.command.set_param(0, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(0, x_val)
        self.command.set_param(1, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(1, y_val)
        self.command.set_param(2, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(2, z_val)
        self.command.set_param(4, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(4, speed)
        self.command.set_delay(delay)
        if self.is_connected():
            self.send(self.command.to_hex())
        else:
            print(self.command.to_hex())
            sleep(delay)

        if controller is not None:
            controller.model.set_value("current_x", x_val/1000)
            self._x_value = x_val
            controller.model.set_value("current_y", y_val/1000)
            self._y_value = y_val
            controller.model.set_value("current_z", z_val/1000)
            self._z_value = z_val
        print(f"[INFO] Finish moving")

    def control_out(self, out_num, is_on=True, delay=0, controller=None):
        self.command.reset_command()
        self.command.set_function(12)
        self.command.set_param(0, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(0, out_num * 1000)
        self.command.set_param(1, Property(num_bytes=4, reverse=True))
        self.command.set_param_value(1, 1000 if is_on == True else 0)
        self.command.set_delay(delay)
        if self.is_connected:
            self.send(self.command.to_hex())
        else:
            print(self.command.to_hex())

    def get_current_encoder_value(self):
        self.command.reset_command()
        self.command.set_function(14)
        response = self.send(self.command.to_hex())

        response_obj = Response()
        Response.from_bytes(response_obj, response)

        return response_obj.get_value()

    def reset(self):
        self.command.reset_command()
        self.command.set_function(4)
        if self.is_connected:
            self.send(self.command.to_hex())
        else:
            print(self.command.to_hex())

    def increase_x(self, step=30000, speed=1000, delay=300, controller=None):
        self.move(self._x_value + step, self._y_value, self._z_value, speed=speed, delay=delay, controller=controller)

    def decrease_x(self, step=30000, speed=1000, delay=300, controller=None):
        self.move(self._x_value - step, self._y_value, self._z_value, speed=speed, delay=delay, controller=controller)

    def increase_y(self, step=30000, speed=1000, delay=300, controller=None):
        self.move(self._x_value, self._y_value + step, self._z_value, speed=speed, delay=delay, controller=controller)

    def decrease_y(self, step=30000, speed=1000, delay=300, controller=None):
        self.move(self._x_value, self._y_value - step, self._z_value, speed=speed, delay=delay, controller=controller)

    def increase_z(self, step=10000, speed=1000, delay=300, controller=None):
        self.move(self._x_value, self._y_value, self._z_value + step, speed=speed, delay=delay, controller=controller)

    def decrease_z(self, step=10000, speed=1000, delay=300, controller=None):
        self.move(self._x_value, self._y_value, self._z_value - step, speed=speed, delay=delay, controller=controller)


    def pick_and_place(self, data, controller=None):
        x_val = data["x_val"]
        y_val = data["y_val"]
        z_val_low = data["z_val_low"]
        z_val_high = data["z_val_high"]

        x_val_target = data["x_val_target"]
        y_val_target = data["y_val_target"]
        z_val_target = data["z_val_target"]

        moving_speed = data["moving_speed"]
        grabbing_speed = data["grabbing_speed"]

        moving_delay = data["moving_delay"]
        grabbing_delay = data["grabbing_delay"]

        catch_first_speed = data["catch_first_speed"]
        catch_first_delay = data["catch_first_delay"]

        catch_second_speed = data["catch_second_speed"]
        catch_second_delay = data["catch_second_delay"]

        unit_factor = data["unit_factor"]

        encoder = data["encoder"]

        print(f"[INFO] Pick and place x: {data}")

        self.move(100000, y_val, z_val_high, speed=moving_speed, delay=moving_delay, controller=controller)

        current_encoder = self.get_current_encoder_value()
        adapt_x = int(abs(current_encoder - encoder) * unit_factor * 1000)
        print(f"[DEBUG] Adapt x: {adapt_x}")
        self.move(x_val - adapt_x, y_val, z_val_high, speed=catch_first_speed, delay=catch_first_delay, controller=controller)
        print(f"[DEBUG] Current encoder: {current_encoder}")

        current_encoder = self.get_current_encoder_value()
        adapt_x = int(abs(current_encoder - encoder) * unit_factor * 1000)
        print(f"[DEBUG] Adapt x: {adapt_x}")
        self.move(x_val - adapt_x, y_val, z_val_low, speed=catch_second_speed, delay=catch_second_delay, controller=controller)
        print(f"[DEBUG] Current encoder: {current_encoder}")

        self.control_out(1, is_on=True, delay=10)
        self.move(x_val_target, y_val_target, z_val_target, speed=moving_speed, delay=moving_delay, controller=controller)
        self.control_out(1, is_on=False, delay=50)


        print("[INFO] Pick and place finish")
        if controller is not None:
            controller.picking_stm = False
