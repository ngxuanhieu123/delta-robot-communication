from .i_command import ICommand


class Command(ICommand):
    def set_function(self, function:int) -> None:
        pass 

    def to_hex(self) -> bytearray:
        return b'\x30\x30\x00\x00\x00\x22\x01\x06\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

