import unittest
from src.models import TrajectoryPredictor


class TrajectoryPredictorTest(unittest.TestCase):
    def setUp(self):
        self.predictor = TrajectoryPredictor(sample_time=10, num_data_points=5)

    def test_add_point_with_10_times_checking_a_static_object_and_the_model_is_created(self):
        self.predictor.add_point((30, 40), 0)
        self.predictor.add_point((30, 40), 10)
        self.predictor.add_point((30, 40), 20)
        self.predictor.add_point((30, 40), 30)
        self.predictor.add_point((30, 40), 40)

        result = self.predictor.predict(time=1000)

        self.assertTupleEqual((30, 40), result)

    def test_add_point_with_not_enough_times_then_the_predicted_result_should_be_none(self):
        self.predictor.add_point((30, 40), 0)
        self.predictor.add_point((30, 40), 10)
        self.predictor.add_point((30, 40), 20)
        self.predictor.add_point((30, 40), 30)

        result = self.predictor.predict(time=1000)

        self.assertIsNone(result)


    def test_add_point_with_constant_velocity_in_x_direction(self):
        self.predictor.add_point((31, 40), 0)
        self.predictor.add_point((32, 40), 10)
        self.predictor.add_point((33, 40), 20)
        self.predictor.add_point((34, 40), 30)
        self.predictor.add_point((35, 40), 40)

        result = self.predictor.predict(time=100)

        self.assertTupleEqual((41, 40), result)
