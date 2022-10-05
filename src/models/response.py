class Response:
    def __init__(self):
        self.value = None
        self.function = None

    def get_function(self):
        return self.function

    def get_value(self):
        return self.value

    @staticmethod
    def from_bytes(obj, response):
        obj.function = response[8:10]
        obj.value = response[10:]

        obj.function = int.from_bytes(obj.function, 'big')
        obj.value = int.from_bytes(obj.value, 'big')
        if obj.value > 2 ** (4 * 8 - 1):
            obj.value = - (2 ** (4 * 8) - obj.value)


if __name__ == "__main__":
    response_obj = Response()
    Response.from_bytes(response_obj, b'00\x00\x00\x00\x08\x01\x03\x01\x3f\x00\x24\x00\x00')
    value = response_obj.get_value()
    function = response_obj.get_function()

    print(str(value) + '\t' + str(function))
