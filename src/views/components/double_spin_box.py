from PyQt5.QtWidgets import QDoubleSpinBox


class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self._topic = ""

    def config(self, controller, topic):
        self.controller = controller
        self._topic = topic
        self.valueChanged.connect(self._update_value)
        self.controller.model.add_observer(self)

    def model_is_changed(self, model):
        self.setValue(model.get_value(self._topic))

    def _update_value(self):
        self.controller.model.set_value(self._topic, self.value())


class DisplayPointDoubleSpinBox(DoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._id = None
        self._index_column = None
        self.setMinimum(-500)
        self.setMaximum(500)

    def config(self, controller, topic, index, index_column):
        self._id = index
        self._index_column = index_column
        super().config(controller, topic)
        
    def model_is_changed(self, model):
        value = model.get_value(self._topic)
        if value is not None:
            if self._id < len(value):
                self.setDisabled(False)
                self.setValue(value[self._id][self._index_column])
                return

        self.setDisabled(True)
        self.setValue(0)

    def _update_value(self):
        try:
            value = self.controller.model.get_value(self._topic)
            value[self._id][self._index_column] = self.value()

            self.controller.model.set_value(self._topic, value)
        except IndexError as e:
            print("Reset the spin box")
        except TypeError as e:
            print("Weight is reset")
