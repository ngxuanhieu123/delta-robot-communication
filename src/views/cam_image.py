from PyQt5.QtWidgets import QLabel, QDialog, QMessageBox, QHBoxLayout, QLineEdit, QDialogButtonBox, QVBoxLayout
from PyQt5.QtGui import QPainter, QColor
from .i_observer import IObserver
from .components import LineEditWithLabel



class CurrentDialog(QDialog):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.initUi()
        self.setWindowTitle("Robot Position")

    def initUi(self):
        main_widget = QVBoxLayout(self)

        input_widget = QHBoxLayout(self)
        main_widget.addLayout(input_widget)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.add_equivalent_point)
        buttons.rejected.connect(self.remove_latest_point)
        main_widget.addWidget(buttons)

        self.x_value = LineEditWithLabel("X value")
        input_widget.addWidget(self.x_value)

        self.y_value = LineEditWithLabel("Y Value")
        input_widget.addWidget(self.y_value)

    def add_equivalent_point(self):
        x = self.x_value.get_text(return_type=int)
        self.x_value.set_text()
        y = self.y_value.get_text(return_type=int)
        self.y_value.set_text()

        self.controller.add_equivalent_point((x, y))
        self.close()

    def remove_latest_point(self):
        self.controller.remove_latest_point()
        self.close()


class CameraImage(QLabel):
    def __init__(self, controller, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setMouseTracking(True)
        self.controller = controller
        self.message_box = CurrentDialog(self.controller)
        self.is_testing = False

    def mouseMoveEvent(self, event):
        pass

    def mousePressEvent(self, event):
        if not self.is_testing:
            self.controller.add_point((event.x(), event.y()))
            self.message_box.show()
        else:
            self.controller.move_to((event.x(), event.y()))
            print("Here")

    def model_is_changed(self, model):
        self.is_testing = model.is_testing
