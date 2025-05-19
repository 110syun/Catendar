from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt, QAbstractAnimation
from sprite import Sprite
from pathlib import Path
import pyautogui
import os
class SpriteManager(QLabel):
    def __init__(self, manager):
        super().__init__()
        self.os_name = manager.os_name
        self.manager = manager
        self.sprites = {}
        self.sprite_data = [
            ["images/cat/cat_sit_f.png", 4, 200],
            ["images/cat/cat_sit_r.png", 3, 200],
            ["images/cat/cat_sit_l.png", 3, 200],
            ["images/cat/cat_walk_a.png", 3, 200],
            ["images/cat/cat_walk_b.png", 3, 200],
            ["images/cat/cat_walk_f.png", 3, 200],
            ["images/cat/cat_walk_r.png", 6, 100],
            ["images/cat/cat_walk_l.png", 6, 100],
            ["images/cat/cat_sleep_r.png", 4, 150],
            ["images/cat/cat_sleep_l.png", 4, 150],
            ["images/cat/cat_walk2sit_f.png", 4, 100],
            ["images/cat/cat_walk2sit_r.png", 6, 100],
            ["images/cat/cat_walk2sit_l.png", 6, 100],
            ["images/cat/cat_sleepstart_r.png", 3, 150],
            ["images/cat/cat_sleepstart_l.png", 3, 150],
            ["images/cat/cat_sit2sleep_r.png", 4, 200],
            ["images/cat/cat_sit2sleep_l.png", 4, 200],
            ["images/cat/cat_akubi.png", 6, 100],
            ["images/button/cat_push_r.png", 4, 100],
            ["images/button/cat_push_l.png", 4, 100]]
        self.sprite_sheet = None
        self.num_frames = None
        self.current_frame = None
        self.frame_width = None
        self.frame_height = None
        
        self.animation_queue = []

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        
        for sprite in self.sprite_data:
            self.create_sprite(sprite[0], sprite[1], sprite[2])

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.manager.animation.state() == QAbstractAnimation.Stopped:
            self.manager.show_option()
        super().mousePressEvent(event)

    def update_frame(self):
        x = self.current_frame * self.frame_width
        cropped = self.sprite_sheet.copy(x, 0, self.frame_width, self.frame_height)
        self.setPixmap(cropped)

    def next_frame(self):
        if self.current_frame == self.num_frames - 1 and self.animation_queue:
            next_filename = self.animation_queue.pop(0)
            self.change_sprite(next_filename)
            return
        is_last_frame = (self.current_frame == self.num_frames - 1)
        self.current_frame = (self.current_frame + 1) % self.num_frames
        self.update_frame()
        
        if is_last_frame and hasattr(self, "current_sprite_filename"):
            if "cat_push" in self.current_sprite_filename:
                pyautogui.write('A', interval=0)

    def create_sprite(self, sprite_path, num_frames, frame_time):
        filename = os.path.basename(sprite_path)
        self.sprites[filename] = Sprite(sprite_path, num_frames, frame_time)
    
    def change_sprite(self, filename, animation_queue = None):
        if not animation_queue is None:
            self.animation_queue = animation_queue
        self.timer.stop()
        sprite = self.sprites[filename]
        self.sprite_sheet = QPixmap(sprite.sprite_path)
        self.num_frames = sprite.num_frames
        self.current_frame = 0
        self.frame_width = self.sprite_sheet.width() // self.num_frames
        self.frame_height = self.sprite_sheet.height()
        self.current_sprite_filename = filename
        self.update_frame()
        self.timer.start(sprite.frame_time)
        
        if "sleep" in filename:
            self.manager.show_bed()
        else:
            self.manager.bed_image.fade_out()