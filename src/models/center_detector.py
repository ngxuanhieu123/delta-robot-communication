from .i_model import Model
import cv2 as cv
import numpy as np
from .centroid_tracker import *


class CenterDetector(Model):
    def __init__(self, shifting_frame=(0, 0), values={"binary_threshold": 127, "area_threshold": 700, "radius": 3, "points": []}):
        super().__init__()
        self._shifting_frame = shifting_frame
        self._values = values
        self._bnd_boxes = []
        self.tracker = CentroidTracker()

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

            contours, belt = self._get_gaussian_contours(gray_img, img)
            binary_contours, binary_img = self._get_binary_contours(gray_img)
            self._values["points"] = []
            self._values["angles"] = []
            self._values["encoder_value"] = 0
            self._bnd_boxes = []

            if kernel == "Gaussian": 
                using_contours = contours
            elif kernel == "Binary":
                using_contours = binary_contours

#            encoder_value = controller.connection.get_current_encoder_value()
            if len(binary_contours) != 0:
                for contour in using_contours: 
                    ret, point, angle = self._get_center_point_from_contour(contour)
                    if ret:
                        self._values["points"].append(point)
                        self._values["angles"].append(angle)
#                        controller.model.set_value("encoder_value", encoder_value)

#            self.tracker.update(self._values["points"], controller=controller)
            return belt, binary_img
        except Exception as e:
            print(f"[ERROR] {e}")
            return img, img

    def _get_rect_from_contour(self, contour):
        return cv.boundingRect(contour)

    def _get_center_point_from_contour(self, contour):
        moments = cv.moments(contour)
        if moments["m00"] == 0:
            return False, None, None
        else:
            x = int(moments["m10"]/moments["m00"]) + self._shifting_frame[0]
            y = int(moments["m01"]/moments["m00"]) + self._shifting_frame[1]

            area = cv.contourArea(contour)
            min_rect = cv.minAreaRect(contour)
            print(f"[DEBUG] Min Rect: {min_rect}")
            angle = min_rect[2] if min_rect[2] < 45 else 90 - min_rect[2]

            if area > self._values["area_threshold"]:
#                print(self._get_rect_from_contour(contour))
                self._bnd_boxes.append(self._get_rect_from_contour(contour))
                return True, (x, y), angle
            else:
                return False, None, None

    def draw_points(self, frame, controller=None):
        result = frame.copy()
        try:
#            points = controller.detector.tracker.objects
            points = self._values["points"]
            angles = self._values["angles"]
            for point, angle in zip(points, angles):
                result = cv.circle(result, point, 3, (0, 0, 255), -1)
                cv.putText(result, f"Angle: {angle}", (point[0] - 10, point[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

#            for obj_id, point in points.items():
#                result = cv.circle(result, point, 3, (0, 0, 255), -1)
#                cv.putText(result, f"ID: {obj_id}", (point[0] - 10, point[1] - 10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        except Exception as e:
            print(f"[ERROR] {e}")

        return result

    def draw_bnd_boxes(self, frame):
        result = frame.copy()
        for x, y, w, h in self._bnd_boxes:
            cv.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 3)

        return result

    def _get_gaussian_contours(self, img, bgr_img=None):
        hsv = cv.cvtColor(bgr_img, cv.COLOR_BGR2HSV)

        lower_range = np.array([0, 0, 153])
        upper_range = np.array([204, 255, 255])
        mask = cv.inRange(hsv, lower_range, upper_range)

        contours, _ = cv.findContours(mask,cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        return contours, mask

    def _get_binary_contours(self, img):
        blur_img = cv.GaussianBlur(img, (5, 5), 0)
        _, binary_img = cv.threshold(blur_img, self._values["binary_threshold"], 255, cv.THRESH_BINARY)
        binary_contours, _ = cv.findContours(binary_img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        return binary_contours, binary_img
