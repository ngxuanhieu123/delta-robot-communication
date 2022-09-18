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
        self.controller = None
        self._show_binary_frame = False
        self._limit_area = 0

    def set_controller(self, controller):
        self.controller = controller

    def run(self):
        self.cam_on = True

        capture = cv.VideoCapture(0)

        while self.cam_on:
            ret, frame = capture.read()
            if ret: 
                img = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                img = cv.resize(img, self.size)
                gray_belt = cv.cvtColor(img, cv.COLOR_BGR2GRAY)


                if self._temp is not None:
                    self._draw_current_box(img)

                img = self._draw_points(img)

                try:
                    handled_img = self._hanlded_gray_img(gray_belt)
                    self._imshow_binary_frame(handled_img)
                except Exception as e:
                    print(e)

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

    def _imshow_binary_frame(self, handled_img):
        if self._show_binary_frame:
            try:
                cv.imshow("binary frame", handled_img)
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

    def _hanlded_gray_img(self, img):
        cutting_img = self._cutting_gray_img(img)
        blur_img = cv.GaussianBlur(cutting_img, (5, 5), 0)
        _, belt = cv.threshold(blur_img, 0, 255, cv.THRESH_BINARY+cv.THRESH_OTSU)

        contours, _ = cv.findContours(belt,cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        self.controller.model.clear_points()
        for contour in contours:
            self._get_product(contour)

        return belt

    def _get_product(self, contour):
        min_x, min_y, _, _ = self._get_cutting_value()
        moments = cv.moments(contour)
        if moments['m00'] == 0:
            return
        else:
            c_x = int(moments['m10']/moments['m00']) + min_x
            c_y = int(moments['m01']/moments['m00']) + min_y

            area = cv.contourArea(contour)

            if area > self._limit_area:
                self.controller.model.add_point((c_x, c_y))

    def _cutting_gray_img(self, img):
        min_x, min_y, max_x, max_y = self._get_cutting_value()
        return img[min_y:max_y, min_x:max_x]

    def _cutting_img(self, img):
        min_x, min_y, max_x, max_y = self._get_cutting_value()
        rect = QRect(min_x, min_y, max_x-min_x, max_y-min_y)

        return img.copy(rect)

    def _draw_current_box(self, img):
        img = cv.rectangle(img, self._temp, self._temp_next, (0, 0, 0), 2)

    def _draw_boxes(self, img):
        pass

    def _draw_points(self, img):
        for point in self._points:
            img = cv.circle(img, point, 4, (0, 0, 0), -1)

        return img

    def model_is_changed(self, model):
        if model.has_min_point() and model.need_max_point():
            self._temp = model.get_min_point()
            self._temp_next = model.get_current_posistion()
        elif model.has_cutting_frame():
            self._temp, self._temp_next = model.get_cutting_frame()
            self._has_cutting_frame = True

        self._points = model.get_points()
        self._show_binary_frame = model.show_binary_frame()
        self._limit_area = model.get_values("limit_area")
