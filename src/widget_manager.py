import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGraphicsOpacityEffect
from PyQt5.QtGui import QPixmap, QRegion
from PyQt5.QtCore import QTimer, Qt, QPoint, QPropertyAnimation, QEasingCurve, pyqtSlot, QObject, QAbstractAnimation
from sprite_manager import SpriteManager
from option_image import OptionImage
from cat_bed import CatBed
import multiprocessing
import os
import math

class WidgetManager(QObject):
    def __init__(self, os_name, queue):
        super().__init__()
        self.os_name = os_name
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
        self.visible_bed = False
        self.topmost = False
        self.options = []
        self.cat_direction = "r"
        self.state = 0
        self.is_center = False
        
        self.resource_path = self.check_resource_path()

        bed_images = [
            "bed-blue.png",
            "bed-pink.png",
            "bed-white.png"]
        image_dir = os.path.join(self.resource_path, "images", "bed")
        self.image_data = [os.path.join(image_dir, img) for img in bed_images]

        if self.os_name == "Windows":
            import win32gui
            import win32con
            import win32process
            import pywintypes
            import psutil
            from transparent_window import TransparentWindow
            self.win32gui = win32gui
            self.win32con = win32con
            self.win32process = win32process
            self.pywintypes = pywintypes
            self.psutil = psutil
            self.TransparentWindow = TransparentWindow
        elif self.os_name == "Darwin":
            from transparent_overlay import TransparentOverlay
            self.TransparentOverlay = TransparentOverlay
    
    def check_resource_path(self):
        if hasattr(sys, '_MEIPASS'):
            return sys._MAEIPASS
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def start_timers(self):
        self.queue_timer = QTimer()
        self.queue_timer.timeout.connect(self.process_queue)
        self.queue_timer.start(50)
        
        self.sleep_timer = QTimer()
        self.sleep_timer.setSingleShot(True)
        self.sleep_timer.timeout.connect(lambda: self.animator.change_sprite("cat_sit2sleep_" + self.cat_direction + ".png", ["cat_sleepstart_" + self.cat_direction + ".png", "cat_sleep_" + self.cat_direction + ".png"]))

    def start_animation(self):
        self.animator = SpriteManager(
            manager = self
        )
        self.animator.change_sprite("cat_sit_f.png", [])
        self.animation = QPropertyAnimation(self.animator, b"pos")
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.finished.connect(self.on_animation_finished)
        
    def init_accessories(self):
        self.bed_image = CatBed()
        pixmap = QPixmap(self.image_data[0])
        self.bed_image.setPixmap(pixmap)
        self.bed_image.resize(pixmap.width(), pixmap.height())
        self.bed_image.hide()

    def is_own_or_parent_process(self, hwnd):
        try:
            _, process_id = self.win32process.GetWindowThreadProcessId(hwnd)
            current_process_id = os.getpid()
            parent_process_id = self.psutil.Process(current_process_id).ppid()
            
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
        hwnd = self.win32gui.GetForegroundWindow()
        if hwnd == 0:
            return
        if self.is_own_or_parent_process(hwnd):
            return
        style = self.win32gui.GetWindowLong(hwnd, self.win32con.GWL_STYLE)
        if style & self.win32con.WS_POPUP:
            return
        try:
            class_name = self.win32gui.GetClassName(hwnd)
        except self.pywintypes.error:
            return
        if class_name == "Shell_TrayWnd":
            return
        self.current_window_hwnd = hwnd
        if self.current_window_hwnd not in self.widgets:
            self.widgets[self.current_window_hwnd] = self.TransparentWindow(
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
                self.destination_check(self.widgets[self.current_window_hwnd])
            self.widgets[self.current_window_hwnd].show()
        self.widgets[self.current_window_hwnd].follow_window()
        if self.current_animator_hwnd != self.current_window_hwnd:
            self.heading_off_screen(self.widgets[self.current_animator_hwnd])
            if self.topmost:
                self.topmost = False
                self.not_p_most()
        else:
            if self.is_center:
                self.animator.move(self.animator.x(), int((self.widgets[self.current_animator_hwnd].height() - self.animator.frame_height - 10) / 2))
            else:
                self.animator.move(self.animator.x(), self.widgets[self.current_animator_hwnd].height() - self.animator.frame_height - 10)
            self.bed_image.move(self.bed_image.x(), self.animator.y())
            self.destination_check(self.widgets[self.current_animator_hwnd])

        if not self.win32gui.IsWindow(self.widgets[self.current_animator_hwnd].target_hwnd):
            self.off_screen
            self.on_animation_finished()

    def destination_check(self, widget):
        if self.state <= 1:
            if self.is_center:
                self.heading_off_screen(widget)
            else:
                self.heading_bottom_left(widget)
        else:
            if self.is_center:
                self.heading_center(widget)
            else:
                self.heading_off_screen(widget)

    def heading_bottom_left(self, widget):
        destination_x = (widget.width() - self.animator.frame_width - 10)
        if destination_x != self.before_destination_x or (self.animator.y() != self.before_destination_y and self.animation.state() == QAbstractAnimation.Running):
            self.sleep_timer.stop()
            self.hide_option()
            if self.os_name == "Windows":
                self.win32gui.SetWindowPos(
                    self.widgets[self.current_animator_hwnd].hwnd,
                    self.win32con.HWND_TOPMOST,
                    0, 0, 0, 0,
                    self.win32con.SWP_NOMOVE | self.win32con.SWP_NOSIZE
                )
            self.topmost = True
            self.was_stopped = True
            self.off_screen = False
            self.animation.stop()
            destination = QPoint(destination_x, self.animator.y())
            start_pos = self.animator.pos()
            distance = abs(destination_x - self.animator.x())
            if destination_x > self.animator.x():
                self.cat_direction = "r"
            else:
                self.cat_direction = "l"
            self.animator.change_sprite("cat_walk_" + self.cat_direction + ".png", [])
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
            self.sleep_timer.stop()
            self.hide_option()
            self.was_stopped = True
            self.off_screen = True
            self.animation.stop()
            destination = QPoint(destination_x, self.animator.y())
            start_pos = self.animator.pos()
            distance = abs(destination_x - self.animator.x())
            if destination_x > self.animator.x():
                self.cat_direction = "r"
            else:
                self.cat_direction = "l"
            self.animator.change_sprite("cat_walk_" + self.cat_direction + ".png", [])
            duration = distance / self.speed_per_second * 1000
            self.animation.setStartValue(start_pos)
            self.animation.setEndValue(destination)
            self.animation.setDuration(int(duration))
            self.was_stopped = False
            self.before_destination_x = destination_x
            self.before_destination_y = self.animator.y()
            self.animation.start()

    def heading_center(self, widget):
        destination_x = int((widget.width() / 2 - self.animator.frame_width - 10))
        if destination_x != self.before_destination_x or (self.animator.y() != self.before_destination_y and self.animation.state() == QAbstractAnimation.Running):
            self.sleep_timer.stop()
            self.hide_option()
            if self.os_name == "Windows":
                self.win32gui.SetWindowPos(
                    self.widgets[self.current_animator_hwnd].hwnd,
                    self.win32con.HWND_TOPMOST,
                    0, 0, 0, 0,
                    self.win32con.SWP_NOMOVE | self.win32con.SWP_NOSIZE
                )
            self.topmost = True
            self.was_stopped = True
            self.off_screen = False
            self.animation.stop()
            destination = QPoint(destination_x, self.animator.y())
            start_pos = self.animator.pos()
            distance = abs(destination_x - self.animator.x())
            if destination_x > self.animator.x():
                self.cat_direction = "r"
            else:
                self.cat_direction = "l"
            self.animator.change_sprite("cat_walk_" + self.cat_direction + ".png", [])
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
        self.win32gui.SetWindowPos(
            hwnd,
            self.win32con.HWND_NOTOPMOST,
            0, 0, 0, 0,
            self.win32con.SWP_NOMOVE | self.win32con.SWP_NOSIZE
        )
        self.win32gui.SetWindowPos(
            hwnd,
            self.current_window_hwnd,
            0, 0, 0, 0,
            self.win32con.SWP_NOMOVE | self.win32con.SWP_NOSIZE
        )
        
    def change_state(self):
        if self.state >= 7 and self.animation.state() == QAbstractAnimation.Stopped:
            self.animator.change_sprite("cat_push_" + self.cat_direction + ".png", [])
        elif self.state >= 5 and self.animation.state() == QAbstractAnimation.Stopped:
            self.animator.change_sprite("cat_sit_" + self.cat_direction + ".png", [])
        elif self.state == 1:
            self.visible = True
            if self.current_animator_hwnd:
                self.animator.show()
                if self.visible_bed:
                    self.bed_image.fade_in()
        elif self.state == 0:
            self.animator.hide()
            self.bed_image.hide()
            self.visible = False
        
    def process_queue(self):
        try:
            while not self.queue.empty():
                value = self.queue.get_nowait()
                if isinstance(value, int) and self.state != value:
                    self.state = value
                    self.change_state()
                elif isinstance(value, str) and self.animation.state() == QAbstractAnimation.Stopped:
                    self.animator.change_sprite(value, [])
        except Exception as e:
            print(f"Queue processing error: {e}")
        
    def run_widget_manager(self):
        app = QApplication(sys.argv)
        self.start_timers()
        self.init_accessories()
        self.start_animation()
        if self.os_name == "Windows":
            timer = QTimer()
            timer.timeout.connect(self.get_foreground_window)
            timer.start(10)
        elif self.os_name == "Darwin":
            self.current_animator_hwnd = 1
            self.current_window_hwnd = 1
            self.widgets[1] = self.TransparentOverlay()
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
            else:
                self.animator.hide()
            timer = QTimer()
            timer.timeout.connect(lambda: self.destination_check(self.widgets[1]))
            timer.start(100)
        sys.exit(app.exec_())
        
    def show_bed(self):
        self.bed_image.setParent(self.widgets[self.current_animator_hwnd])
        self.bed_image.move(self.animator.pos())
        self.bed_image.stackUnder(self.animator)
        self.bed_image.fade_in()
        
    def show_option(self):
        for i, image_data in enumerate(self.image_data):
            angle = (math.pi / 2) + ((math.pi / 2) * i / (len(self.image_data) - 1))
            x = self.animator.x() + 50 * math.cos(angle)
            y = self.animator.y() - 50 * math.sin(angle)
            
            label = OptionImage(self, image_data)
            label.setParent(self.widgets[self.current_animator_hwnd])
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
        if self.state >= 7:
            self.animator.change_sprite("cat_push_" + self.cat_direction + ".png", [])
        else:
            self.animator.change_sprite("cat_walk2sit_" + self.cat_direction + ".png", ["cat_sit_" + self.cat_direction + ".png"])
            if self.state < 5:
                self.sleep_timer.start(2000)
        if not self.was_stopped and self.off_screen:
            self.off_screen = False
            self.animator.setParent(self.widgets[self.current_window_hwnd])
            self.current_animator_hwnd = self.current_window_hwnd
            if self.state <= 1:
                self.animator.setGeometry(
                    -100,
                    self.widgets[self.current_window_hwnd].height() - self.animator.frame_height - 10,
                    self.animator.frame_width,
                    self.animator.frame_height
                )
                self.is_center = False
            else:
                self.animator.setGeometry(
                    -100,
                    int((self.widgets[self.current_window_hwnd].height() - self.animator.frame_height - 10) / 2),
                    self.animator.frame_width,
                    self.animator.frame_height
                )
                self.is_center = True
            if self.visible:
                self.animator.show()
            self.destination_check(self.widgets[self.current_window_hwnd])

if __name__ == "__main__":
    import platform
    os_name = platform.system()
    queue=multiprocessing.Queue()
    manager = WidgetManager(None, queue)
    manager.os_name = os_name
    manager.visible = True
    manager.state = 2
    manager.run_widget_manager()