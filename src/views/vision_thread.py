from PyQt5.QtCore import QThread, pyqtSignal, QRect
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt
import cv2 as cv


class VisionThread(QThread):
    updated_img = pyqtSignal(QImage)
    cutting_frame = pyqtSignal(QImage)
    size = (500, 400)
    
    def __init__(self):
        QThread.__init__(self)
        self._points = []
        self._boxes = []
        self._points = []
        self._temp = None
        self._temp_next = None
        self._has_cutting_frame = False

    def run(self):
        self.cam_on = True

        capture = cv.VideoCapture(0)

        while self.cam_on:
            ret, frame = capture.read()
            if ret: 
                img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                img = cv.resize(img, self.size)


                if self._temp is not None:
                    self._draw_current_box(img)

                img = self._get_q_image(img)
                cutting_img = self._cutting_img(img)

                pic = img.scaled(*self.size, Qt.KeepAspectRatio)
                self.updated_img.emit(pic)

                self.cutting_frame.emit(cutting_img)
                
    def stop(self):
        self.cam_on = False 
        cv.release()
        cv.destroyAllWindows()
        self.quit()

    def _get_q_image(self, img):
        return QImage(img.data.tobytes(), img.shape[1], img.shape[0], QImage.Format_RGB888)

    def _cutting_img(self, img):
        try:
            min_x = min(self._temp[0], self._temp_next[0])
            max_x = max(self._temp[0], self._temp_next[0])

            min_y = min(self._temp[1], self._temp_next[1])
            max_y = max(self._temp[1], self._temp_next[1])
            
            rect = QRect(min_x, min_y, max_x-min_x, max_y-min_y)

            return img.copy(rect)
        except Exception as e:
            return img.copy()

    def _draw_current_box(self, img):
        img = cv.rectangle(img, self._temp, self._temp_next, (0, 0, 0), 2)

    def _draw_boxes(self, img):
        pass

    def _draw_points(self, img):
        pass

    def model_is_changed(self, model):
        if model.has_min_point() and model.need_max_point():
            self._temp = model.get_min_point()
            self._temp_next = model.get_current_posistion()
        elif model.has_cutting_frame():
            self._temp, self._temp_next = model.get_cutting_frame()
            self._has_cutting_frame = True
