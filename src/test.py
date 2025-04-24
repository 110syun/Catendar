import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QRegion
from PyQt5.QtCore import QTimer, Qt
import multiprocessing
import win32gui
import win32con

class SpriteAnimator(QWidget):
    def __init__(self, sprite_path, num_frames, queue, target_hwnd):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.hwnd_target = target_hwnd
        self.target_rect = win32gui.GetWindowRect(self.hwnd_target)
        
        left, top, right, bottom = self.target_rect
        width = right - left
        height = bottom - top
        
        self.setGeometry(left, top, width, height)
        self.setMask(QRegion(0, 0, width, height))
        
        self.sprite_sheet = QPixmap(sprite_path)
        self.num_frames = num_frames
        self.current_frame = 0
        
        self.frame_width = self.sprite_sheet.width() // num_frames
        self.frame_height = self.sprite_sheet.height()
        
        self.label = QLabel(self)
        self.label.setGeometry(width - self.frame_width - 10, height - self.frame_height - 10, self.frame_width, self.frame_height)
        
        self.update_frame()

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(100)

        self.position_timer = QTimer()
        self.position_timer.timeout.connect(self.follow_window)
        self.position_timer.start(10)

        self.hwnd_animator = int(self.winId())

        self.queue = queue
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self.process_queue)
        self.queue_timer.start(50)

    def update_frame(self):
        x = self.current_frame * self.frame_width
        cropped = self.sprite_sheet.copy(x, 0, self.frame_width, self.frame_height)
        self.label.setPixmap(cropped)
        
    def next_frame(self):
        self.current_frame = (self.current_frame + 1) % self.num_frames
        self.update_frame()

    def follow_window(self):
        current_hwnd = win32gui.GetForegroundWindow()
        if self.hwnd_target:
            rect = win32gui.GetWindowRect(self.hwnd_target)
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top

            self.setGeometry(left, top, width, height)
            self.setMask(QRegion(0, 0, width, height))
            
            self.label.setGeometry(width - self.frame_width - 10, height - self.frame_height - 10, self.frame_width, self.frame_height)
        if self.hwnd_target == current_hwnd:
            win32gui.SetWindowPos(
                self.hwnd_animator,
                win32con.HWND_TOPMOST,
                self.x(),
                self.y(),
                self.width(),
                self.height(),
                win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
            )
            win32gui.SetWindowPos(
                self.hwnd_animator,
                win32con.HWND_NOTOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
            )

    def process_queue(self):
        try:
            while not self.queue.empty():
                value = self.queue.get_nowait()
        except Exception as e:
            print(f"Queue processing error: {e}")

def run_test(queue):
    app = QApplication(sys.argv)
    animator = SpriteAnimator(
        sprite_path="src/images/test.png",
        num_frames=1,
        queue=queue
    )
    animator.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    queue=multiprocessing.Queue()
    run_test(queue)