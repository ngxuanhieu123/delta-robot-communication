import unittest
from src.models import Response


class ResponseTest(unittest.TestCase):
    def test_given_the_binary_response_when_response_convert_it_to_value_then_the_value_should_be_positive(self):
        response = b'\x30\x30\x00\x00\x00\x08\x01\x03\x00\x04\x00\x00\xd0\x57'

        response_obj = Response()
        Response.from_bytes(response_obj, response)

        assert response_obj.get_function() == 4
        assert response_obj.get_value() == 53335

    def test_given_the_binary_response_when_response_convert_it_to_value_then_the_value_should_be_negative(self):
        response = b'\x30\x30\x00\x00\x00\x08\x01\x03\x00\x04\xff\xff\xff\xfb'

        response_obj = Response()
        Response.from_bytes(response_obj, response)

        assert response_obj.get_function() == 4
        assert response_obj.get_value() == -5
