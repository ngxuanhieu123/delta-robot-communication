import unittest
from unittest.mock import Mock
from src.models import CoordinateTransformer
from src.views import IObserver


class CoordinateTransformerTest(unittest.TestCase):
    def setUp(self):
        self.transformer = CoordinateTransformer()

    def test_given_the_coordinate_then_add_same_points_then_the_predited_result_must_be_the_same_as_the_input(self):
        self.transformer.add_point((30, 50))
        self.transformer.add_equivalent_point((30, 50))
        self.transformer.add_point((130, 60))
        self.transformer.add_equivalent_point((130, 60))
        self.transformer.add_point((150, 50))
        self.transformer.add_equivalent_point((150, 50))

        result = self.transformer.convert((230, 2))

        self.assertTupleEqual((230, 2), result)

    def test_given_the_coordinate_then_add_the_points_that_be_rotated_by_x_axis_then_the_output_must_be_rotated_with_the_input_point(self):
        self.transformer.add_point((30, 50))
        self.transformer.add_equivalent_point((50, -30))
        self.transformer.add_point((50, 130))
        self.transformer.add_equivalent_point((130, -50))
        self.transformer.add_point((150, 50))
        self.transformer.add_equivalent_point((50, -150))

        result = self.transformer.convert((230, 2))

        self.assertTupleEqual((2, -230), result)

    def test_given_the_coordinate_then_add_the_points_that_be_shifted_by_x_axis_then_the_output_must_be_shifted_with_the_input_point(self):
        self.transformer.add_point((30, 50))
        self.transformer.add_equivalent_point((40, 50))
        self.transformer.add_point((50, 130))
        self.transformer.add_equivalent_point((60, 130))
        self.transformer.add_point((150, 50))
        self.transformer.add_equivalent_point((160, 50))

        result = self.transformer.convert((230, 2))

        self.assertTupleEqual((240, 2), result)

    def test_given_the_coordinate_then_add_the_points_that_be_scaled_by_x_axis_then_the_output_must_be_scaled_with_the_input_point(self):
        self.transformer.add_point((30, 50))
        self.transformer.add_equivalent_point((60, 100))
        self.transformer.add_point((50, 130))
        self.transformer.add_equivalent_point((100, 260))
        self.transformer.add_point((150, 50))
        self.transformer.add_equivalent_point((300, 100))

        result = self.transformer.convert((230, 2))

        self.assertTupleEqual((460, 4), result)
