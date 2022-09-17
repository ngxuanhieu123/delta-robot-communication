import numpy as np


class CoordinateTransformer:
    def __init__(self):
        self.__input_point_tank = []
        self.__output_point_tank = []
        self._transform_matrix = None

    def add_points(self, points) -> None:
        self.__input_point_tank.append(points[0])
        self.__output_point_tank.append(points[1])

    def convert(self, point) -> tuple:
        sys_matrix = np.array(self.__input_point_tank).T
        robot_matrix = np.array(self.__output_point_tank).T

        complete_sys_matrix = np.concatenate((sys_matrix, np.ones(shape=(1, 3))), axis=0)

        self._transform_matrix = np.dot(robot_matrix, np.linalg.inv(complete_sys_matrix))

        filled_point = np.concatenate([np.array(point).reshape(2, -1), np.ones(shape=(1, 1))], axis=0)

        transformed_point = np.dot(self._transform_matrix, filled_point)
        int_transformed_point = np.asarray(np.round(transformed_point), np.int32)
        return tuple(int_transformed_point.reshape(-1,))
