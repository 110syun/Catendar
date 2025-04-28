import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QRegion
from PyQt5.QtCore import QTimer, Qt, QPoint, QPropertyAnimation, QEasingCurve, pyqtSlot, QObject
from transparent_window import TransparentWindow
from sprite_manager import SpriteManager
import time
import multiprocessing
import win32gui
import win32con
import pywintypes
import ctypes

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
        self.berore_destination_y = None
        self.visible = False
        
    def start_timers(self):
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self.process_queue)
        self.queue_timer.start(50)

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
                self.animator = SpriteManager(
                    manager = self
                )
                self.animator.setParent(self.widgets[self.current_window_hwnd])
                self.current_animator_hwnd = self.current_window_hwnd
                self.animator.change_sprite("cat_sit_f.png")
                self.animator.setGeometry(
                    -100,
                    self.widgets[self.current_window_hwnd].height() - self.animator.frame_height - 10,
                    self.animator.frame_width,
                    self.animator.frame_height
                )
                if self.visible:
                    self.animator.show()
                else:
                    self.animator.hide()
                self.animation = QPropertyAnimation(self.animator, b"pos")
                self.animation.setEasingCurve(QEasingCurve.Linear)
                self.animation.finished.connect(self.on_animation_finished)
                self.heading_bottom_left(self.widgets[self.current_window_hwnd])
            self.widgets[self.current_window_hwnd].show()
        self.widgets[self.current_window_hwnd].follow_window()
        if self.current_animator_hwnd != self.current_window_hwnd:
            self.heading_off_screen(self.widgets[self.current_animator_hwnd])
        else:
            self.animator.move(self.animator.x(), self.widgets[self.current_animator_hwnd].height() - self.animator.frame_height - 10)
            self.heading_bottom_left(self.widgets[self.current_animator_hwnd])

    def heading_bottom_left(self, widget):
        destination_x = (widget.width() - self.animator.frame_width - 10)
        if destination_x != self.before_destination_x or self.animator.y() != self.berore_destination_y:
            win32gui.SetWindowPos(
                self.widgets[self.current_animator_hwnd].hwnd_self,
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE
            )
            QTimer.singleShot(100, self.not_p_most)
            self.was_stopped = True
            self.off_screen = False
            self.animation.stop()
            destination = QPoint(destination_x, self.animator.y())
            start_pos = self.animator.pos()
            distance = abs(destination_x - self.animator.x())
            if destination_x > self.animator.x():
                self.animator.change_sprite("cat_walk_r.png")
            else:
                self.animator.change_sprite("cat_walk_l.png")
            duration = distance / self.speed_per_second * 1000
            self.animation.setStartValue(start_pos)
            self.animation.setEndValue(destination)
            self.animation.setDuration(int(duration))
            self.was_stopped = False
            self.before_destination_x = destination_x
            self.berore_destination_y = self.animator.y()
            self.animation.start()

    def heading_off_screen(self, widget):
        destination_x = (widget.width() - self.animator.frame_width + 100)
        if destination_x != self.before_destination_x or self.animator.y() != self.berore_destination_y:
            self.was_stopped = True
            self.off_screen = True
            self.animation.stop()
            destination = QPoint(destination_x, self.animator.y())
            start_pos = self.animator.pos()
            distance = abs(destination_x - self.animator.x())
            if destination_x > self.animator.x():
                self.animator.change_sprite("cat_walk_r.png")
            else:
                self.animator.change_sprite("cat_walk_l.png")
            duration = distance / self.speed_per_second * 1000
            self.animation.setStartValue(start_pos)
            self.animation.setEndValue(destination)
            self.animation.setDuration(int(duration))
            self.was_stopped = False
            self.before_destination_x = destination_x
            self.berore_destination_y = self.animator.y()
            self.animation.start()
        
    def run_widget_manager(self):
        app = QApplication(sys.argv)
        timer = QTimer()
        timer.timeout.connect(self.get_foreground_window)
        timer.start(100)
        self.start_timers()
        sys.exit(app.exec_())
    
    def not_p_most(self):
        hwnd = self.widgets[self.current_animator_hwnd].hwnd_self
        result = win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_NOTOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
        error_code = ctypes.GetLastError()
        if not result:
            print(f"SetWindowPos failed with error code: {error_code}")
        else:
            print(f"SetWindowPos succeeded for hwnd: {hwnd}")
        
    def process_queue(self):
        try:
            while not self.queue.empty():
                value = self.queue.get_nowait()
                if isinstance(value, int):
                    if value == 0:
                        self.animator.hide()
                        self.visible = False
                    elif value == 1:
                        self.animator.show()
                        self.visible = True
        except Exception as e:
            print(f"Queue processing error: {e}")
    
    @pyqtSlot()
    def on_animation_finished(self):
        self.animator.change_sprite("cat_sit_f.png")
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
            if self.visible:
                self.animator.show()
            self.heading_bottom_left(self.widgets[self.current_window_hwnd])

if __name__ == "__main__":
    queue=multiprocessing.Queue()
    manager = WidgetManager(queue)
    manager.visible = True
    manager.run_widget_manager()