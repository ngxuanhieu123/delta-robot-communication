from .i_model import Model
import numpy as np 


class TrajectoryPredictor(Model):
    def __init__(self, sample_time=10, num_data_points=20):
        self._num_data_points = num_data_points
        self._points = []
        self._times = []
        self._weight = None
        self._sample_time = sample_time

    def get_sample_time(self):
        return self._sample_time

    def get_num_data_points(self):
        return self._num_data_points

    def add_point(self, point, time):
        self._times.append(time)
        self._points.append(point)

        if len(self._points) == self._num_data_points:
            self._get_weight()

    def _get_weight(self):
        time = self._get_time()
        target = np.array(self._points).reshape(-1, 2)

        self._weight = np.dot(np.linalg.inv(np.dot(time.T, time)), (np.dot(time.T, target)))

    def _get_time(self):
        time = np.array(self._times).reshape(-1, 1)
        one_column_added_time = np.concatenate((np.ones_like(time), time), axis=1)
        return one_column_added_time

    def predict(self, time=500):
        if self._weight is None:
            self._get_weight()
        
        return tuple(np.round(np.dot(np.array([[1, time]]), self._weight)[0]))

    def reset(self):
        self._weight = None
        self._points = []
        self._times = []
