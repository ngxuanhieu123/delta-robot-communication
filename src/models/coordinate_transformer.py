import numpy as np
from .i_model import Model


class CoordinateTransformer(Model):
    def __init__(self):
        Model.__init__(self)
        self.__input_point_tank = []
        self.__output_point_tank = []
        self._transform_matrix = None

    def add_point(self, point) -> bool:
        if self.can_add_point():
            self.__input_point_tank.append(point)
            self.model_is_changed()

    def add_equivalent_point(self, point) -> bool:
        self.__output_point_tank.append(point)
        try:
            self._calculate_the_transform_matrix() 
            self.model_is_changed()
            return True
        except:
            return False


    def _format_sys_position(self, sys_position) -> np.ndarray:
        return np.concatenate([sys_position, np.ones(shape=(1, sys_position.shape[1]))], axis=0)

    def _get_sys_matrix(self) -> np.ndarray:
        return np.array(self.__input_point_tank).T

    def _get_robot_matrix(self) -> np.ndarray:
        return np.array(self.__output_point_tank).T

    def _calculate_the_transform_matrix(self) -> None:
        sys_matrix = self._get_sys_matrix()
        robot_matrix = self._get_robot_matrix()

        self._transform_matrix = np.dot(robot_matrix, np.linalg.inv(self._format_sys_position(sys_matrix)))

    def convert(self, point) -> tuple:
        transformed_point = np.dot(self._transform_matrix, self._format_sys_position(np.array(point).reshape(2, -1)))
        int_transformed_point = np.asarray(np.round(transformed_point), np.int32)
        return tuple(int_transformed_point.reshape(-1,))

    def get_all_points(self) -> list:
        return self.__input_point_tank

    def can_add_point(self) -> bool:
        return len(self.__input_point_tank) == len(self.__output_point_tank)

    def remove_latest_point(self) -> bool:
        if len(self.__input_point_tank) > 0:
            self.__input_point_tank = self.__input_point_tank[:-1]

    def can_convert(self) -> bool:
        return self._transform_matrix is not None

    def remove_all(self):
        self.__input_point_tank = []
        self.__output_point_tank = []
        self._transform_matrix = None
        self.model_is_changed()

    def save_weight(self, datafile="data.npy"):
        np.save(datafile, self._transform_matrix)

    def load_weight(self, datafile="data.npy"):
        self._transform_matrix = np.load(datafile)

    def set_weight(self, weight):
        self._transform_matrix = np.array(weight)

    def get_matrix(self):
        return self._transform_matrix
