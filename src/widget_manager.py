import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap, QRegion
from PyQt5.QtCore import QTimer, Qt, QPoint, QPropertyAnimation, QEasingCurve, pyqtSlot, QObject, QAbstractAnimation
from transparent_window import TransparentWindow
from sprite_manager import SpriteManager
from option_image import OptionImage
import multiprocessing
import win32gui
import win32con
import win32process
import pywintypes
import os
import psutil
import math

class WidgetManager(QObject):
    def __init__(self, queue):
        super().__init__()
        self.queue = queue
        self.widgets = {}
        self.off_screen = False
        self.speed_per_second = 100
        self.was_stopped = False
        self.current_window_hwnd = None
        self.current_animator_hwnd = None
        self.before_destination_x = None
        self.before_destination_y = None
        self.visible = False
        self.topmost = False
        self.image_data = [
            "images/bed-blue.png",
            "images/bed-pink.png",
            "images/bed-white.png"]
        self.options = []

    def start_timers(self):
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self.process_queue)
        self.queue_timer.start(50)
    
    def start_animation(self):
        self.animator = SpriteManager(
            manager = self
        )
        self.bed_image = QLabel()
        pixmap = QPixmap("images/bed-blue.png")
        self.bed_image.setPixmap(pixmap)
        self.bed_image.resize(pixmap.width(), pixmap.height())
        self.bed_image.hide()
        self.animator.change_sprite("cat_sit_f.png")
        self.animation = QPropertyAnimation(self.animator, b"pos")
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.finished.connect(self.on_animation_finished)
    
    def is_own_or_parent_process(self, hwnd):
        try:
            _, process_id = win32process.GetWindowThreadProcessId(hwnd)
            current_process_id = os.getpid()
            parent_process_id = psutil.Process(current_process_id).ppid()
            
            if process_id == current_process_id:
                return True
            elif process_id == parent_process_id:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error: {e}")
            return True
        
    def get_foreground_window(self):
        hwnd = win32gui.GetForegroundWindow()
        if hwnd == 0:
            return
        if self.is_own_or_parent_process(hwnd):
            return
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        if style & win32con.WS_POPUP:
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
            if not self.current_animator_hwnd:
                if self.visible:
                    self.animator.show()
                else:
                    self.animator.hide()
                self.animator.setParent(self.widgets[self.current_window_hwnd])
                self.current_animator_hwnd = self.current_window_hwnd
                self.animator.setGeometry(
                    -100,
                    self.widgets[self.current_window_hwnd].height() - self.animator.frame_height - 10,
                    self.animator.frame_width,
                    self.animator.frame_height
                )
                self.heading_bottom_left(self.widgets[self.current_window_hwnd])
            self.widgets[self.current_window_hwnd].show()
        self.widgets[self.current_window_hwnd].follow_window()
        if self.current_animator_hwnd != self.current_window_hwnd:
            self.heading_off_screen(self.widgets[self.current_animator_hwnd])
            if self.topmost:
                self.topmost = False
                self.not_p_most()
        else:
            self.animator.move(self.animator.x(), self.widgets[self.current_animator_hwnd].height() - self.animator.frame_height - 10)
            self.bed_image.move(self.animator.x(), self.animator.y())
            self.heading_bottom_left(self.widgets[self.current_animator_hwnd])

        if not win32gui.IsWindow(self.widgets[self.current_animator_hwnd].target_hwnd):
            self.off_screen
            self.on_animation_finished()

    def heading_bottom_left(self, widget):
        destination_x = (widget.width() - self.animator.frame_width - 10)
        if destination_x != self.before_destination_x or (self.animator.y() != self.before_destination_y and self.animation.state() == QAbstractAnimation.Running):
            self.hide_option()
            win32gui.SetWindowPos(
                self.widgets[self.current_animator_hwnd].hwnd,
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )
            self.topmost = True
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
            self.before_destination_y = self.animator.y()
            self.animation.start()

    def heading_off_screen(self, widget):
        destination_x = (widget.width() - self.animator.frame_width + 100)
        if destination_x != self.before_destination_x or (self.animator.y() != self.before_destination_y and self.animation.state() == QAbstractAnimation.Running):
            self.hide_option()
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
            self.before_destination_y = self.animator.y()
            self.animation.start()
    
    def not_p_most(self):
        hwnd = self.widgets[self.current_animator_hwnd].hwnd
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_NOTOPMOST,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
        win32gui.SetWindowPos(
            hwnd,
            self.current_window_hwnd,
            0, 0, 0, 0,
            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
        )
        
    def process_queue(self):
        try:
            while not self.queue.empty():
                value = self.queue.get_nowait()
                if isinstance(value, int):
                    if value == 0:
                        self.animator.hide()
                        self.visible = False
                    elif value == 1:
                        self.visible = True
                        if self.current_animator_hwnd:
                            self.animator.show()
                elif isinstance(value, str):
                    if self.animation.state() == QAbstractAnimation.Stopped:
                        self.animator.change_sprite(value)
        except Exception as e:
            print(f"Queue processing error: {e}")
        
    def run_widget_manager(self):
        app = QApplication(sys.argv)
        timer = QTimer()
        timer.timeout.connect(self.get_foreground_window)
        timer.start(10)
        self.start_timers()
        self.start_animation()
        sys.exit(app.exec_())
        
    def show_bed(self):
        self.bed_image.setParent(self.widgets[self.current_window_hwnd])
        self.bed_image.move(self.animator.pos())
        self.bed_image.stackUnder(self.animator)
        self.bed_image.show()
        
    def show_option(self):
        for i, image_data in enumerate(self.image_data):
            angle = (math.pi / 2) + ((math.pi / 2) * i / (len(self.image_data) - 1))
            x = self.animator.x() + 50 * math.cos(angle)
            y = self.animator.y() - 50 * math.sin(angle)
            
            label = OptionImage(self, image_data)
            label.setParent(self.widgets[self.current_window_hwnd])
            label.move(int(x), int(y))
            label.show()
            self.options.append(label)
            
    def hide_option(self):
        for label in self.options:
            label.deleteLater()
        self.options.clear()
            
    def change_bed_image(self, image):
        pixmap = QPixmap(image)
        self.bed_image.setPixmap(pixmap)
        self.hide_option()

    @pyqtSlot()
    def on_animation_finished(self):
        self.animator.change_sprite("cat_walk2sit.png", "cat_sit_f.png")
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