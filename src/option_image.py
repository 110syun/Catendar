from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
class OptionImage(QLabel):
    def __init__(self, manager, image):
        super().__init__()
        self.manager = manager
        self.image = image
        pixmap = QPixmap(self.image)
        self.setPixmap(pixmap)
        self.resize(pixmap.width(), pixmap.height())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.manager.change_bed_image(self.image)
        super().mousePressEvent(event)