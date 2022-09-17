from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from .i_observer import IObserver
from PyQt5.QtCore import Qt
import cv2 as cv


class WebcamThread(QThread):
    updated_img = pyqtSignal(QImage)
    size = (500, 400)
    
    def __init__(self):
        QThread.__init__(self)
        self._points = []

    def run(self):
        self.cam_on = True

        capture = cv.VideoCapture(0)

        while self.cam_on:
            ret, frame = capture.read()
            if ret: 
                img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                img = cv.resize(img, self.size)
                img = self._draw_points(img)

                img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)


                pic = img.scaled(*self.size, Qt.KeepAspectRatio)
                self.updated_img.emit(pic)

    def stop(self):
        self.cam_on = False 
        self.quit()

    def _draw_points(self, img):
        for point in self._points:
            cv.circle(img, point, 3, (0, 0, 0), -1)

        return img

    def model_is_changed(self, model):
        self._points = model.get_all_points()
