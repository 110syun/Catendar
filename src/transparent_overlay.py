import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QGuiApplication, QColor, QPainter
from objc import lookUpClass
from AppKit import NSApp, NSWindow, NSScreenSaverWindowLevel

class TransparentOverlay(QWidget):
    def __init__(self):
        super().__init__()

        geometry = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(geometry)

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self.show()

        self._make_mac_mouse_transparent()

    def _make_mac_mouse_transparent(self):
        ns_window = NSApp.windows()[-1]
        ns_window.setIgnoresMouseEvents_(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = TransparentOverlay()
    sys.exit(app.exec())