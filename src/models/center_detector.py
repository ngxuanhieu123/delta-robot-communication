from .i_model import Model
import cv2 as cv


class CenterDetector(Model):
    def __init__(self, shifting_frame=(0, 0), values={"binary_threshold": 127, "area_threshold": 700, "radius": 3, "points": []}):
        super().__init__()
        self._shifting_frame = shifting_frame
        self._values = values

    def set_shifting_frame(self, shifting_frame):
        self._shifting_frame = shifting_frame
        self.model_is_changed()

    def get_shifting_frame(self):
        return self._shifting_frame

    def get_current_points(self):
        return self._values["points"]

    def get_values(self, key):
        if key in self._values.keys():
            return self._values[key]
        else:
            return 0

    def set_values(self, key, value):
        if key in self._values.keys():
            self._values[key] = value
        self.model_is_changed()

    def set_all_values(self, values):
        self._values = values

    def get_center_points(self, img, controller=None):
        try:
            if controller is not None:
                kernel, name = controller.model.get_value("contour_kernel", is_combo_box=True)
            else:
                kernel = "Gaussian"

            try:
                gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
            except:
                gray_img = cv.cvtColor(img, cv.COLOR_RGB2GRAY)

            contours, belt = self._get_gaussian_contours(gray_img)
            binary_contours, binary_img = self._get_binary_contours(gray_img)
            self._values["points"] = []

            if kernel == "Gaussian": 
                using_contours = contours
            elif kernel == "Binary":
                using_contours = binary_contours

            if len(binary_contours) != 0:
                for contour in using_contours: 
                    ret, point = self._get_center_point_from_contour(contour)
                    if ret:
                        self._values["points"].append(point)

            return belt, binary_img
        except Exception as e:
            print(f"[ERROR] {e}")
            return img, img

    def _get_center_point_from_contour(self, contour):
        moments = cv.moments(contour)
        if moments["m00"] == 0:
            return False, None
        else:
            x = int(moments["m10"]/moments["m00"]) + self._shifting_frame[0]
            y = int(moments["m01"]/moments["m00"]) + self._shifting_frame[1]

            area = cv.contourArea(contour)

            if area > self._values["area_threshold"]:
                return True, (x, y)
            else:
                return False, None

    def draw_points(self, frame):
        result = frame.copy()
        for point in self._values["points"]:
            result = cv.circle(result, point, self._values["radius"], (0, 0, 255), -1)

        return result

    def _get_gaussian_contours(self, img):
        blur_img = cv.GaussianBlur(img, (5, 5), 0)
        _, belt = cv.threshold(blur_img, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)

        contours, _ = cv.findContours(belt,cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        return contours, belt

    def _get_binary_contours(self, img):
        _, binary_img = cv.threshold(img, self._values["binary_threshold"], 255, cv.THRESH_BINARY)
        binary_contours, _ = cv.findContours(binary_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        return binary_contours, binary_img
