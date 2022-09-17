import numpy as np
from .i_model import Model


class CoordinateTransformer(Model):
    def __init__(self):
        Model.__init__(self)
        self.__input_point_tank = []
        self.__output_point_tank = []
        self._transform_matrix = None

    def add_points(self, points) -> bool:
        self.__input_point_tank.append(points[0])
        self.__output_point_tank.append(points[1])

        try:
            self._calculate_the_transform_matrix() 
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
