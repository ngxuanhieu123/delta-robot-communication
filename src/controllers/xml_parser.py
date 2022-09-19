import xml.etree.ElementTree as ET
from ..models import Command
from ..models.properties import Property, DefaultParam
from ..utils import Delay


class XMLParser:
    def __init__(self, filename=""):
        self.filename = filename

        tree = ET.parse(filename)
        self.root = tree.getroot()

    def _get_command_from_element(self, element):
        address_property = Property()

        command = Command(address_property=address_property, 
                    params=[DefaultParam() for _ in range(Command.NUM_PARAMS)])

        if element.find("delay") is not None:
            command.set_delay(int(element.find("delay").text))

        if element.find("name") is not None:
            command.set_name(element.find("name").text)

        if element.find("address") is not None:
            command.set_function(element.find("address").text)

            params = element.find("parameters")

            for param in params:
                if param.find("index") is not None:
                    param_index = int(param.find("index").text)
                    param_value = int(param.find("value").text)
                    param_reverse = True if param.find("reverse") is not None else False

                    command.set_param(param_index, Property(num_bytes=4, reverse=param_reverse))
                    command.set_param_value(param_index, param_value)

        return command

    def get_commands_list(self):
        commands = []
        for element in self.root.findall("command"):
            commands.append(self._get_command_from_element(element))

        return commands
