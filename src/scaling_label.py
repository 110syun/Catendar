from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
class ScalingLabel(QLabel):
    def __init__(self, manager, image, option_number):
        super().__init__()
        self.manager = manager
        self.image = image
        self.option_number = option_number
        pixmap = QPixmap(self.image)
        self.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.option_number == 0:
                self.manager.scale_up()
            else:
                self.manager.scale_down()
        super().mousePressEvent(event)