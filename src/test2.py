import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QTimer
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
    def __init__(self, sprite_sheet_path, sprite_count):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # スプライトシートの読み込み
        self.sprite_sheet = QPixmap(sprite_sheet_path)
        self.sprite_count = sprite_count
        self.current_sprite_index = 0

        # スプライトのサイズを計算
        self.sprite_width = self.sprite_sheet.width() // sprite_count
        self.sprite_height = self.sprite_sheet.height()

        # QLabelの設定
        self.label = QLabel(self)
        self.update_sprite()
        self.label.resize(self.sprite_width, self.sprite_height)

        # マウス追従の設定
        self.emitter = MouseSignalEmitter()
        self.emitter.position_changed.connect(self.update_goal)
        self.listener_thread = MouseListenerThread(self.emitter)
        self.listener_thread.start()

        # スプライト切り替え用のタイマー
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_sprite)
        self.timer.start(100)  # 100msごとにスプライトを切り替え

    def update_sprite(self):
        # 現在のスプライトを切り出して表示
        x = self.current_sprite_index * self.sprite_width
        sprite = self.sprite_sheet.copy(x, 0, self.sprite_width, self.sprite_height)
        self.label.setPixmap(sprite)

    def next_sprite(self):
        # 次のスプライトに切り替え
        self.current_sprite_index = (self.current_sprite_index + 1) % self.sprite_count
        self.update_sprite()

    def update_goal(self, x, y):
        self.move(x, y)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # スプライトシートのパスとスプライト数を指定
    window = ImageFollower('images//rotating_arc_spritesheet2.png', 10)
    window.show()
    sys.exit(app.exec_())
