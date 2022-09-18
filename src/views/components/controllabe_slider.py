from PyQt5.QtWidgets import QSlider


class ControllableSlider(QSlider):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self.setValue((self.maximum() + self.minimum()) // 2)
        self._updated_key = ""
        self.valueChanged.connect(self.update_value)

    def set_controller(self, controller):
        self.controller = controller

    def set_updated_key(self, new_updated_key):
        self._updated_key = new_updated_key

    def model_is_changed(self, model):
        self.setValue(model.get_values(self._updated_key))

    def update_value(self):
        self.controller.model.set_values(self._updated_key, self.value())
