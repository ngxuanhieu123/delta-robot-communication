from PyQt5.QtCore import QThread, pyqtSignal, QTimer
import cv2 as cv
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt


class WebcamThread(QThread):
    updated_img = pyqtSignal(QImage)
    vision_img = pyqtSignal(QImage)

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self._cam_id = 0
        self._cam_on = True
        self._size = None
        self.controller.model.add_observer(self)

    def _get_cam_id(self, model):
        cam_id_data = model.get_value("cam_id") 
        return cam_id_data["options"][cam_id_data["value"]]

    def _get_size(self, model):
        size_data = model.get_value("image_size")
        return size_data["options"][size_data["value"]]

    def model_is_changed(self, model):
        self._cam_id = self._get_cam_id(model)
        self._size = self._get_size(model)

    def run(self):
        capture = cv.VideoCapture(self.controller.model.get_value("cam_id", is_combo_box=True)[1])

        while self._cam_on:
            ret, frame = capture.read()
            if ret: 
                img = self._preprocess_img(frame)

                self._detect_centers(img)

                drawed_img = self._draw_on_img(img.copy())
                mapping_img = self.create_img_from_array(drawed_img)
                mapping_pic = mapping_img.scaled(*self._size, Qt.KeepAspectRatio)

                drawed_vision_img = self._draw_on_vision(img)
                vision_img = self.create_img_from_array(drawed_vision_img)
                vision_pic = vision_img.scaled(*self._size, Qt.KeepAspectRatio)

                self.updated_img.emit(mapping_pic)
                self.vision_img.emit(vision_pic)
#            if len(self.controller.detector.tracker.picking_hub) > 0:
#                print(self.controller.detector.tracker.picking_hub)

#            if len(self.controller.detector.tracker.picking_hub) > 0:
#                print(f"[DEBUG] Picking Hub: {self.controller.detector.tracker.picking_hub}get_function()")

            if self.controller.picking and not self.controller.picking_stm and len(self.controller.model.get_value("points")) > 0:
                self.controller.run()

    def _preprocess_img(self, img):
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        img = cv.resize(img, self._size)
        img = cv.flip(img, 1)

        return img

    def _detect_centers(self, img):
        if  self.controller.model.get_value("has_cutting_frame"):
            min_x, min_y, max_x, max_y = self._get_frame_box()
            cutting_img = img[min_y:max_y, min_x:max_x, :]
            belt, binary = self.controller.detector.get_center_points(cutting_img, self.controller)

            if self.controller.model.get_value("show_binary_frame"):
                cv.imshow("img", cutting_img)
                cv.imshow("binary", binary)
                cv.imshow("gaussian", belt)
            cv.waitKey(3)
        else:
            try:
                cv.destroyAllWindows()
            except Exception as e:
                print(f"[ERROR] {e}")
        

    def create_img_from_array(self, img):
        return QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)

    def _get_frame_box(self):
        min_x = self.controller.model.get_value("cutting_frame_x_min")
        max_x = self.controller.model.get_value("cutting_frame_x_max")
        min_y = self.controller.model.get_value("cutting_frame_y_min")
        max_y = self.controller.model.get_value("cutting_frame_y_max")
        return min_x, min_y, max_x, max_y

    def _draw_on_vision(self, img):
        has_cutting_frame = self.controller.model.get_value("has_cutting_frame")
        starting_point = self.controller.model.get_value("cutting_frame_starting_point")
        current_pos = self.controller.model.get_value("current_pointer_on_vision_label")
        _, color = self.controller.model.get_value("cutting_frame_color", is_combo_box=True)
        thickness = self.controller.model.get_value("cutting_frame_thickness")
        points = self.controller.model.get_value("points")
        _, point_color = self.controller.model.get_value("center_point_color", is_combo_box=True)

        if not has_cutting_frame:
            if starting_point is not None:
                try:
                    img = cv.rectangle(img, starting_point, current_pos, color, 1)
                except Exception as e:
                    print(f"[ERROR] {e}")
        else:
            min_x, min_y, max_x, max_y = self._get_frame_box()
            img = cv.rectangle(img, [min_x, min_y], [max_x, max_y], color, thickness)

        img = self.controller.detector.draw_bnd_boxes(img)
        img = self.controller.detector.draw_points(img, self.controller)

        img = self._draw_catch_line(img)

        return img

    def _draw_catch_line(self, img):
        min_x, min_y, max_x, max_y = self._get_frame_box()
        name, direction = self.controller.model.get_value("line_direction", is_combo_box=True)
        catch_line = self.controller.model.get_value("catch_line")
        _, color = self.controller.model.get_value("catching_line_color", is_combo_box=True)

        if name == "Horizontal": 
            starting_point = [min_x, catch_line]
            end_point = [max_x, catch_line]
        elif name == "Vertical":
            starting_point = [catch_line, min_y]
            end_point = [catch_line, max_y]

        return cv.line(img, starting_point, end_point, color, 1)


    def _draw_on_img(self, img):
        mapping_points = self.controller.model.get_value("mapping_points")
        is_testing = self.controller.model.get_value("is_testing")
        testing_point = self.controller.model.get_value("testing_point")
        _, color = self.controller.model.get_value("mapping_points_color", is_combo_box=True)

        if not is_testing:
            img = self._draw_points_on_img(img, mapping_points, color)
        else:
            try:
                converted_testing_point = self.controller.convert(testing_point)
                img = cv.circle(img, testing_point, 3, color, -1)
                cv.putText(img, f"{testing_point} -> {converted_testing_point}", (testing_point[0] + 10, testing_point[1] + 10), cv.FONT_ITALIC, .3, (255, 255, 255), 1, 2)

            except Exception as e:
                print(f"[ERROR] {e}")
        return img

    def _draw_points_on_img(self, img, points, color):
        for point in points:
            try:
                img = cv.circle(img, point, 3, color, -1)
            except:
                img = cv.circle(img, point[0], 3, color, -1)
        return img

    def stop(self):
        self.cam_on = False 
        self.quit()
