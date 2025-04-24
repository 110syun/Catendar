from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer
class SpriteAnimator(QLabel):
    def __init__(self, sprite_path, num_frames, manager):
        super().__init__()
        self.manager = manager
        
        self.sprite_sheet = QPixmap(sprite_path)
        self.num_frames = num_frames
        self.current_frame = 0
        
        self.frame_width = self.sprite_sheet.width() // num_frames
        self.frame_height = self.sprite_sheet.height()
        
        self.update_frame()

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        self.timer.start(100)

    def update_frame(self):
        x = self.current_frame * self.frame_width
        cropped = self.sprite_sheet.copy(x, 0, self.frame_width, self.frame_height)
        self.setPixmap(cropped)

    def next_frame(self):
        self.current_frame = (self.current_frame + 1) % self.num_frames
        self.update_frame()