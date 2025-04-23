import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt
import win32gui
import win32con

class SpriteAnimator(QWidget):
    def __init__(self, sprite_path, num_frames, target_window_title):
        super().__init__()
#        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.sprite_sheet = QPixmap(sprite_path)
        self.num_frames = num_frames
        self.current_frame = 0
        
        self.frame_width = self.sprite_sheet.width() // num_frames
        self.frame_height = self.sprite_sheet.height()
        
        self.label = QLabel(self)
        self.update_frame()
        self.label.resize(self.frame_width, self.frame_height)

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(100)  # ミリ秒間隔
        
        self.target_window_title = target_window_title

        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.follow_window)
        self.position_timer.start(10)
        
        self.hwnd_animator = int(self.winId())
        self.hwnd_target = win32gui.FindWindow(None, "Google Chrome")
        win32gui.SetWindowPos(
            self.hwnd_animator,
            self.hwnd_target,
            self.x(),
            self.y(),
            self.width(),
            self.height(),
            win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
        )

    def update_frame(self):
        x = self.current_frame * self.frame_width
        cropped = self.sprite_sheet.copy(x, 0, self.frame_width, self.frame_height)
        self.label.setPixmap(cropped)
        
    def next_frame(self):
        self.current_frame = (self.current_frame + 1) % self.num_frames
        self.update_frame()

    def follow_window(self):
        hwnd = win32gui.FindWindow(None, self.target_window_title)
        if hwnd:
            rect = win32gui.GetWindowRect(hwnd)
            x = rect[2] - self.frame_width - 10
            y = rect[3] - self.frame_height - 10
            self.move(x, y)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    animator = SpriteAnimator(
        sprite_path="images/rotating_arc_spritesheet2.png",
        num_frames=10,
        target_window_title="QTimer — Qt for Python - Google Chrome"
    )
    animator.show()
    sys.exit(app.exec_())