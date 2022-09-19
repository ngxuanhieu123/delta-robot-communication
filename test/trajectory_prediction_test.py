import unittest
from src.models import TrajectoryPredictor


class TrajectoryPredictorTest(unittest.TestCase):
    def test_trajectory_predictor_initializes_with_the_current_position_and_the_number_of_frames_to_the_next_data_point_then_check_the_length_after_6_frames(self):
        predictor = TrajectoryPredictor(init_pos=(80, 100), min_number_sleep_frames=5)
        predictor.get_frame([(81, 103)])
