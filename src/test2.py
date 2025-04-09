import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from pynput import mouse
from threading import Thread

class MouseSignalEmitter(QObject):
    position_changed = pyqtSignal(int, int)

class MouseListenerThread(Thread):
    def __init__(self, emitter):
        super().__init__()
        self.emitter = emitter
        self.daemon = True

    def run(self):
        def on_move(x, y):
            self.emitter.position_changed.emit(x, y)

        with mouse.Listener(on_move=on_move) as listener:
            listener.join()

class ImageFollower(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.label = QLabel(self)
        pixmap = QPixmap(image_path)
        self.label.setPixmap(pixmap)
        self.label.resize(pixmap.size())
        self.emitter = MouseSignalEmitter()
        self.emitter.position_changed.connect(self.update_goal)
        self.listener_thread = MouseListenerThread(self.emitter)
        self.listener_thread.start()

    def update_goal(self, x, y):
        self.move(x, y)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageFollower('images/black_200x200.png')
    window.show()
    sys.exit(app.exec_())
