from PyQt5.QtWidgets import QLabel


class EditableLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.controller = None
        self._text = ""
        self._updated_key = ""
        self.setText(self._text + "0")

    def set_controller(self, controller):
        self.controller = controller

    def set_text(self, new_text):
        self._text = new_text

    def set_updated_key(self, new_updated_key):
        self._updated_key = new_updated_key

    def model_is_changed(self, model):
        self.setText(str(self._text) + str(model.get_values(self._updated_key)))
