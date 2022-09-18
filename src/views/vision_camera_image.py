from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPainter


class VisionCameraImage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("")
        self.controller = None
        self.setMouseTracking(True)
        self._can_add_frame_point = False

    def set_can_add_frame_point(self, can_add):
        self._can_add_frame_point = can_add

    def set_controller(self, controller):
        self.controller = controller

    def mousePressEvent(self, event):
        if self._can_add_frame_point:
            self.controller.model.add_cutting_frame_point((event.x(), event.y()))

    def mouseMoveEvent(self, event):
        if self._can_add_frame_point:
            self.controller.model.change_current_pos((event.x(), event.y()))
