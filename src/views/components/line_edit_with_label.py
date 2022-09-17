from PyQt5.QtWidgets import QLabel, QLineEdit, QWidget, QVBoxLayout


class LineEditWithLabel(QWidget):
    def __init__(self, label="Label"):
        super().__init__()
        self.label = label

        self.initUi()

    def initUi(self):
        main_widget = QVBoxLayout(self)

        label = QLabel(self.label)
        main_widget.addWidget(label)

        self.line_edit = QLineEdit()
        main_widget.addWidget(self.line_edit)

    def get_text(self, return_type=str):
        try:
            return return_type(self.line_edit.text())
        except:
            if return_type == int:
                return 0
            else:
                return ''

    def set_text(self, new_text=''):
        self.line_edit.setText(new_text)
