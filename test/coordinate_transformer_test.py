import unittest
from src.controllers import CoordinateTransformer



class CoordinateTransformerTest(unittest.TestCase):
    def setUp(self):
        self.transformer = CoordinateTransformer()

    def test_given_the_coordinate_then_add_same_points_then_the_predited_result_must_be_the_same_as_the_input(self):
        self.transformer.add_points([(30, 50), (30, 50)])
        self.transformer.add_points([(130, 50), (130, 50)])
        self.transformer.add_points([(150, 50), (150, 50)])

        result = self.transformer.predict((230, 2))

        self.assertTupleEqual((230, 2), result)

    def test_given_the_coordinate_then_add_the_points_that_be_rotated_by_x_axis_then_the_output_must_be_rotated_with_the_input_point(self):
        self.transformer.add_points([(30, 50), (50, -30)])
        self.transformer.add_points([(130, 50), (130, -50)])
        self.transformer.add_points([(150, 50), (50, -150)])

        result = self.transformer.predict((230, 2))

        self.assertTupleEqual((2, -240), result)
