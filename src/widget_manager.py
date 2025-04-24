from test import SpriteAnimator
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QRegion
from PyQt5.QtCore import QTimer, Qt, QPoint, QPropertyAnimation, QEasingCurve, pyqtSlot, QObject
from transparent_window import TransparentWindow
from sprite_animator import SpriteAnimator
import time
import multiprocessing
import win32gui
import win32con
import pywintypes

class WidgetManager(QObject):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.widgets = {}
        self.animator = None
        self.off_screen = False
        self.speed_per_second = 100
        self.was_stopped = False
        self.current_window_hwnd = None
        self.current_animator_hwnd = None
        self.before_destination_x = None

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
        self.current_window_hwnd = hwnd
        if self.current_window_hwnd not in self.widgets:
            self.widgets[self.current_window_hwnd] = TransparentWindow(
            target_hwnd=self.current_window_hwnd,
            manager = self
            )
            if not self.animator:   
                self.animator = SpriteAnimator(
                    sprite_path="src/images/test.png",
                    num_frames=1,
                    manager = self
                )
                self.animator.setParent(self.widgets[self.current_window_hwnd])
                self.current_animator_hwnd = self.current_window_hwnd
                self.animator.setGeometry(
                    -100,
                    self.widgets[self.current_window_hwnd].height() - self.animator.frame_height - 10,
                    self.animator.frame_width,
                    self.animator.frame_height
                )
                self.animator.show()
                self.animation = QPropertyAnimation(self.animator, b"pos")
                self.animation.setEasingCurve(QEasingCurve.Linear)
                self.animation.finished.connect(self.on_animation_finished)
                self.heading_bottom_left(self.widgets[self.current_window_hwnd])
            self.widgets[self.current_window_hwnd].show()
        self.widgets[self.current_window_hwnd].follow_window()
        if self.current_animator_hwnd != self.current_window_hwnd:
            self.heading_off_screen(self.widgets[self.current_animator_hwnd])
        else:
            self.heading_bottom_left(self.widgets[self.current_animator_hwnd])
            

    def heading_bottom_left(self, widget):
        destination_x = (widget.width() - self.animator.frame_width - 10)
        if destination_x != self.before_destination_x:
            win32gui.SetWindowPos(
                self.widgets[self.current_animator_hwnd].hwnd_self,
                win32con.HWND_TOPMOST,
                self.widgets[self.current_animator_hwnd].x(),
                self.widgets[self.current_animator_hwnd].y(),
                self.widgets[self.current_animator_hwnd].width(),
                self.widgets[self.current_animator_hwnd].height(),
                win32con.SWP_NOACTIVATE | win32con.SWP_SHOWWINDOW
            )
            QTimer.singleShot(100, self.not_p_most)
            print("go!")
            self.was_stopped = True
            self.off_screen = False
            self.animation.stop()
            destination = QPoint(destination_x, self.animator.y())
            start_pos = self.animator.pos()
            distance = abs(destination_x - self.animator.x())
            duration = distance / self.speed_per_second * 1000
            self.animation.setStartValue(start_pos)
            self.animation.setEndValue(destination)
            self.animation.setDuration(int(duration))
            self.was_stopped = False
            self.before_destination_x = destination_x
            self.animation.start()

    def heading_off_screen(self, widget):
        destination_x = (widget.width() - self.animator.frame_width + 100)
        if destination_x != self.before_destination_x:
            print("good by!")
            self.was_stopped = True
            self.off_screen = True
            self.animation.stop()
            destination = QPoint(destination_x, self.animator.y())
            start_pos = self.animator.pos()
            distance = abs(destination_x - self.animator.x())
            duration = distance / self.speed_per_second * 1000
            self.animation.setStartValue(start_pos)
            self.animation.setEndValue(destination)
            self.animation.setDuration(int(duration))
            self.was_stopped = False
            self.before_destination_x = destination_x
            self.animation.start()
        
    def run_test(self):
        app = QApplication(sys.argv)
        timer = QTimer()
        timer.timeout.connect(self.get_foreground_window)
        timer.start(10)
        sys.exit(app.exec_())
    
    def not_p_most(self):
        win32gui.SetWindowPos(
            self.widgets[self.current_animator_hwnd].hwnd_self,
            win32con.HWND_NOTOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
        )
    
    @pyqtSlot()
    def on_animation_finished(self):
        if not self.was_stopped and self.off_screen:
            self.off_screen = False
            self.animator.setParent(self.widgets[self.current_window_hwnd])
            self.current_animator_hwnd = self.current_window_hwnd
            self.animator.setGeometry(
                -100,
                self.widgets[self.current_window_hwnd].height() - self.animator.frame_height - 10,
                self.animator.frame_width,
                self.animator.frame_height
            )
            self.animator.show()
            self.heading_bottom_left(self.widgets[self.current_window_hwnd])

if __name__ == "__main__":
    queue=multiprocessing.Queue()
    manager = WidgetManager(queue)
    manager.run_test()