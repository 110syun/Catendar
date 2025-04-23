from test import SpriteAnimator
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QRegion
from PyQt5.QtCore import QTimer, Qt, QPoint, QPropertyAnimation, QEasingCurve
import multiprocessing
import win32gui
import win32con

class SpriteAnimator(QWidget):
    def __init__(self, sprite_path, num_frames, queue, target_hwnd, manager):
        super().__init__()
        self.manager = manager
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
        
        self.speed_per_second = 100
        self.animation = QPropertyAnimation(self.label, b"pos")
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.update_animation()

    def update_frame(self):
        x = self.current_frame * self.frame_width
        cropped = self.sprite_sheet.copy(x, 0, self.frame_width, self.frame_height)
        self.label.setPixmap(cropped)
        
    def next_frame(self):
        self.current_frame = (self.current_frame + 1) % self.num_frames
        self.update_frame()

    def follow_window(self):
        current_hwnd = win32gui.GetForegroundWindow()
        if win32gui.IsWindow(self.hwnd_target):
            rect = win32gui.GetWindowRect(self.hwnd_target)
            left, top, right, bottom = rect
            width = right - left
            height = bottom - top

            self.setGeometry(left, top, width, height)
            self.setMask(QRegion(0, 0, width, height))
            
            self.label.move(self.label.x(), height - self.frame_height - 10)
            self.update_animation()
        else:
            del self.manager.widgets[self.hwnd_target]
            self.deleteLater()
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
            
    def update_animation(self):
        destination_x = (self.width - self.frame_width - 10)
        destination = QPoint(destination_x, self.label.x())
        start_pos = self.label.pos()
        distance = abs(destination_x - self.label.x())
        duration = distance / self.speed_per_second * 1000
        self.animation.setStartValue(start_pos)
        self.animation.setEndValue(destination)
        self.animation.setDuration(int(duration))
        
        self.animation.start()

    def process_queue(self):
        try:
            while not self.queue.empty():
                value = self.queue.get_nowait()
        except Exception as e:
            print(f"Queue processing error: {e}")

class WidgetManager:
    def __init__(self, queue):
        self.queue = queue
        self.widgets = {}

    def get_foreground_window(self):
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return
        try:
            class_name = win32gui.GetClassName(hwnd)
        except pywintypes.error:
            return
        if class_name == "Shell_TrayWnd":
            return
        if hwnd not in self.widgets:
            self.widgets[hwnd] = SpriteAnimator(
            sprite_path="src/images/test.png",
            num_frames=1,
            queue=self.queue,
            target_hwnd=hwnd,
            manager = self
        )
            self.widgets[hwnd].show()

    def run_test(self):
        app = QApplication(sys.argv)
        timer = QTimer()
        timer.timeout.connect(self.get_foreground_window)
        timer.start(10)
        sys.exit(app.exec_())
    
if __name__ == "__main__":
    queue=multiprocessing.Queue()
    manager = WidgetManager(queue)
    manager.run_test()