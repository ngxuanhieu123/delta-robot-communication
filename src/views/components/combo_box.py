from PyQt5.QtWidgets import QComboBox


class ComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self._topic = ""

    def config(self, controller, topic):
        self.controller = controller
        self._topic = topic

        data = controller.model.get_value(topic)
        self.addItems(data["options"].keys())

        self.currentTextChanged.connect(self._update_value)
        self.controller.model.add_observer(self)

    def model_is_changed(self, model):
        data = model.get_value(self._topic)
        self.setCurrentText(data["value"])

    def _update_value(self):
        data = self.controller.model.get_value(self._topic)
        data["value"] = self.currentText()
        self.controller.model.set_value(self._topic, data)
