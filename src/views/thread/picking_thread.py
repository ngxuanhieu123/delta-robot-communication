from PyQt5.QtCore import QThread


class PickingThread(QThread):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.running = False
        self.picking = False

    def stop(self):
        self.running = False
        self.picking = False 
        self.quit()
