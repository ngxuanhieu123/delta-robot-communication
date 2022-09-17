from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from .i_observer import IObserver
from PyQt5.QtCore import Qt
import cv2 as cv


class WebcamThread(QThread):
    updated_img = pyqtSignal(QImage)
    
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

                img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)

                pic = img.scaled(352, 239, Qt.KeepAspectRatio)
                self.updated_img.emit(pic)

    def stop(self):
        self.cam_on = False 
        self.quit()

    def model_is_changed(self, model):
        self._points = model.get_all_points
