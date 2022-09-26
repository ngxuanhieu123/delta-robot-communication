from PyQt5.QtCore import QThread, pyqtSignal, QRect
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt
import cv2 as cv
from time import time
from ..models.center_detector import CenterDetector


class VisionThread(QThread):
    updated_img = pyqtSignal(QImage)
    size = (500, 400)
    
    def __init__(self):
        QThread.__init__(self)
        self._temp = None
        self._temp_next = None
        self._has_cutting_frame = False
        self.controller = None
        self._show_binary_frame = False
        self._limit_area = 0
        self._binary_threshold = 127

    def set_controller(self, controller):
        self.controller = controller

    def run(self):
        self.cam_on = True

        capture = cv.VideoCapture(1)

        while self.cam_on:
            start_time = time()
            ret, frame = capture.read()
            if ret: 
                img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                img = cv.resize(img, self.size)
                
                img = self._draw_current_box(img)
                cutted_img = self._cutting_img(img)
                belt, binary_img = self.controller.model.center_detector.get_center_points(cutted_img)
                drawed_img = self.controller.model.center_detector.draw_points(img)

                try:
                    drawed_img = cv.circle(drawed_img, self.controller.model.predictor.predict(time=1000)[0], 3, (0, 255, 0), -1)
                except:
                    pass

                self._imshow_binary_frame(belt, binary_img)
                img = self._get_q_image(drawed_img)
                
                pic = img.scaled(*self.size, Qt.KeepAspectRatio)
                self.updated_img.emit(pic)
                cv.waitKey(1)

    def stop(self):
        self.cam_on = False 
        cv.release()
        cv.destroyAllWindows()
        self.quit()

    def _get_q_image(self, img):
        return QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_RGB888)

    def _imshow_binary_frame(self, handled_img, binary_img):
        if self._show_binary_frame:
            try:
                cv.imshow("binary frame gaussian", handled_img)
                cv.imshow("binary frame", binary_img)
                cv.waitKey(1)
            except Exception as e:
                print(e)
        else:
            cv.destroyAllWindows()

    def _get_cutting_value(self):
        try:
            min_x = min(self._temp[0], self._temp_next[0])
            max_x = max(self._temp[0], self._temp_next[0])

            min_y = min(self._temp[1], self._temp_next[1])
            max_y = max(self._temp[1], self._temp_next[1])
            return min_x, min_y, max_x, max_y
        except:
            return 0, 0, self.size[0], self.size[1]

    def _cutting_img(self, img):
        min_x, min_y, max_x, max_y = self._get_cutting_value()
        self.controller.model.center_detector.set_shifting_frame((min_x, min_y))
        return img[min_y:max_y, min_x:max_x, :]

    def _draw_current_box(self, img):
        img = cv.rectangle(img, self._temp, self._temp_next, (0, 0, 0), 2)
        return img

    def model_is_changed(self, model):
        if isinstance(model, CenterDetector):
            return

        if model.has_min_point() and model.need_max_point():
            self._temp = model.get_min_point()
            self._temp_next = model.get_current_posistion()
        elif model.has_cutting_frame():
            self._temp, self._temp_next = model.get_cutting_frame()
            self._has_cutting_frame = True

        self._show_binary_frame = model.show_binary_frame()
        self._limit_area = model.get_values("limit_area")
        self._binary_threshold = model.get_values("binary_threshold")
