from test import SpriteAnimator
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
from PyQt5.QtGui import QPixmap, QRegion
from PyQt5.QtCore import QTimer, Qt, QPoint, QPropertyAnimation, QEasingCurve
import multiprocessing
import win32gui
import win32con

class TransparentWindow(QWidget):
    def __init__(self, target_hwnd, manager):
        super().__init__()
        self.manager = manager
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.target_hwnd = target_hwnd
        self.target_rect = win32gui.GetWindowRect(self.target_hwnd)
        
        left, top, right, bottom = self.target_rect
        left, top = left + 10, top + 10
        right, bottom = right - 10, bottom - 10
        width = right - left
        height = bottom - top
        
        self.setGeometry(left, top, width, height)
        self.setMask(QRegion(0, 0, width, height))

        self.hwnd = int(self.winId())
        ex_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)
        win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_NOACTIVATE)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def follow_window(self):
        if win32gui.IsWindow(self.target_hwnd):
            rect = win32gui.GetWindowRect(self.target_hwnd)
            left, top, right, bottom = rect
            left, top = left + 10, top + 10
            right, bottom = right - 10, bottom - 10
            width = right - left
            height = bottom - top

            self.setGeometry(left, top, width, height)
            self.setMask(QRegion(0, 0, width, height))