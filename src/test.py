import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPixmap

class TransparentImageWidget(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # ラベルに画像を設定
        self.label = QLabel(self)
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.size())
        self.resize(pixmap.size())

        self.drag_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        print("test")

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = None
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 透過PNG画像のパスを指定
    image_path = "images/walk1.png"  # ここを透過PNG画像のパスに変更してください
    widget = TransparentImageWidget(image_path)
    widget.show()

    sys.exit(app.exec_())