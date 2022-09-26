from PyQt5.QtWidgets import QLabel


class Label(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None 
        self._topic = ""
        self._callback = None

    def config(self, controller, topic, callback=None):
        self.controller = controller
        self._topic = topic
        data = controller.model.get_value(topic)
        self.controller.model.add_observer(self)

    def model_is_changed(self, model):
        if self._callback is None:
            self.setText(str(model.get_value(self._topic)))
        else:
            self._callback(self, model)
