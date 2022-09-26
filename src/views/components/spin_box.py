from PyQt5.QtWidgets import QSpinBox


class SpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None 
        self.topic = ""
        self.setMaximum(500)

    def config(self, controller, topic):
        self.controller = controller
        self._topic = topic
        self.valueChanged.connect(self._update_value)
        self.controller.model.add_observer(self)

    def model_is_changed(self, model):
        self.setValue(model.get_value(self._topic))

    def _update_value(self):
        self.controller.model.set_value(self._topic, self.value())


class DisplayPointSpinBox(SpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._id = None
        self._index_column = None

    def config(self, controller, topic, index, index_column):
        self._id = index
        self._index_column = index_column
        super().config(controller, topic)
        
    def model_is_changed(self, model):
        value = model.get_value(self._topic)
        if self._id < len(value):
            self.setDisabled(False)
            self.setValue(value[self._id][self._index_column])
        else:
            self.setDisabled(True)
            self.setValue(0)

    def _update_value(self):
        try:
            value = self.controller.model.get_value(self._topic)
            value[self._id][self._index_column] = self.value()

            self.controller.model.set_value(self._topic, value)
        except IndexError as e:
            print("Reset the spin box")

class CuttingFrameSpinBox(SpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    def model_is_changed(self, model):
        is_active = model.get_value("has_cutting_frame")
        self.setEnabled(is_active)

        if is_active:
            value = model.get_value(self._topic)
            self.setValue(value)
        else:
            self.setValue(0)

    def _update_value(self):
        self.controller.model.set_value(self._topic, self.value())
