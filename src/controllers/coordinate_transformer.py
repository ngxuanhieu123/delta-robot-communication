class CoordinateTransformer:
    def __init__(self):
        self.__input_point_tank = []
        self.__output_point_tank = []

    def add_points(self, points) -> None:
        self.__input_point_tank.append(points[0])
        self.__output_point_tank.append(points[1])

    def predict(self, point) -> tuple:
        return point
