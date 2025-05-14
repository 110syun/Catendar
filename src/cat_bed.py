from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton, QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
import sys

class CatBed(QLabel):
    def __init__ (self):
        super().__init__()
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.opacity_effect.setOpacity(0.0)

        self._state = "idle"

        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(800)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        self.anim.finished.connect(self._on_animation_finished)

    def fade_in(self):
        if self._state == "fading_in":
            return
        self.show()
        self.anim.stop()
        self.anim.setStartValue(self.opacity_effect.opacity())
        self.anim.setEndValue(1.0)
        self._state = "fading_in"
        self.anim.start()

    def fade_out(self):
        if self._state == "fading_out":
            return
        self.anim.stop()
        self.anim.setStartValue(self.opacity_effect.opacity())
        self.anim.setEndValue(0.0)
        self._state = "fading_out"
        self.anim.start()

    def _on_animation_finished(self):
        if self._state == "fading_out":
            self.hide()
        self._state = "idle"