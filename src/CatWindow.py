import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QPixmap

class CatWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.label.setStyleSheet("background: transparent")

        # 画像の読み込み
        self.images = {
            "sleep": QPixmap("images/sleep.png"),
            "walk1": QPixmap("images/walk1.png"),
            "walk2": QPixmap("images/walk2.png"),
        }

        self.current_state = "sleep"
        self.walk_toggle = True
        self.move_offset = QPoint(5, 0)

        self.setFixedSize(100, 100)
        self.label.setPixmap(self.images["sleep"])
        self.label.resize(100, 100)

        # 状態監視タイマー
        self.state_timer = QTimer()
        self.state_timer.timeout.connect(self.update_state)
        self.state_timer.start(1000)  # 毎秒チェック

        # アニメーションタイマー
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(500)

    def update_state(self):
        if not os.path.exists("state.json"):
            return
        try:
            with open("state.json", "r") as f:
                data = json.load(f)
            self.current_state = data.get("state", "sleep")
        except Exception as e:
            print(f"状態ファイル読み取りエラー: {e}")

    def animate(self):
        if self.current_state == "walk":
            img = "walk1" if self.walk_toggle else "walk2"
            self.label.setPixmap(self.images[img])
            self.move(self.pos() + self.move_offset)
            self.walk_toggle = not self.walk_toggle
        else:
            self.label.setPixmap(self.images["sleep"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    cat = CatWindow()
    cat.move(300, 300)
    cat.show()
    sys.exit(app.exec_())