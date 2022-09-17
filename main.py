from src.controllers import Controller, XMLParser
from src.models import Command, Response
from src.models.properties import Property
from src.utils import binding_server_for
from threading import Thread
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("filename", default="process.xml")
parser.add_argument("--test", "-t", action='store_true')
parser.add_argument("--host", "-H", default="192.168.27.16")
parser.add_argument("--port", "-p", type=int, default=502)
parser.add_argument("--loops", "-l", type=int, default=1)
args = parser.parse_args()


def control_robot(parser, controller):
    for index, command in enumerate(parser.get_commands_list()):
        controller.command = command
        print(f"""
            ----------
            Command: {command.get_name()}
            Command Name: {command.get_name()}
            Command: {command.to_hex()}
            ----------
        """)
        response_hex = controller.send(controller.command.to_hex())
        Response.from_bytes(response, response_hex)

        print(f"""
            --------------
                Address: {response.get_function()}
                Value: {response.get_value()}
            --------------
        """)


if __name__ == "__main__":
    if args.test:
        host = "127.0.0.1"
        port = 8090
        thread = Thread(target=binding_server_for, args=(host, port))
        thread.start()
    else:
        host = args.host 
        port = args.port

    parser = XMLParser(filename=args.filename)
    controller = Controller(Command())
    controller.connect(host, port)
    response = Response()
    
    for i in range(args.loops):
        control_robot(parser, controller)

    if args.test:
        controller.send(b'quit')
    else:
        controller.disconnect()
