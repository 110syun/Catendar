from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, Qt
from sprite import Sprite
import os
class SpriteManager(QLabel):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.sprites = {}
        self.sprite_data = [
            ["src/images/cat_sit_f.png", 4, 200],
            ["src/images/cat_walk_b.png", 3, 200],
            ["src/images/cat_walk_f.png", 3, 200],
            ["src/images/cat_walk_l.png", 6, 100],
            ["src/images/cat_walk_r.png", 6, 100],
            ["src/images/cat_walk2sit.png", 4, 100]]
        self.sprite_sheet = None
        self.num_frames = None
        self.current_frame = None
        self.frame_width = None
        self.frame_height = None
        
        self.next_filename = None
        
        self.single_shot = False

        self.timer = QTimer()
        self.timer.timeout.connect(self.next_frame)
        
        for sprite in self.sprite_data:
            self.create_sprite(sprite[0], sprite[1], sprite[2])

    def update_frame(self):
        x = self.current_frame * self.frame_width
        cropped = self.sprite_sheet.copy(x, 0, self.frame_width, self.frame_height)
        self.setPixmap(cropped)

    def next_frame(self):
        if self.current_frame == self.num_frames - 1 and self.single_shot:
            self.change_sprite(self.next_filename)
            self.next_filename = None
            return
        self.current_frame = (self.current_frame + 1) % self.num_frames
        self.update_frame()

    def create_sprite(self, sprite_path, num_frames, frame_time):
        filename = os.path.basename(sprite_path)
        self.sprites[filename] = Sprite(sprite_path, num_frames, frame_time)    
    
    def change_sprite(self, filename, next_filename = None):
        self.timer.stop()
        if next_filename:
            self.single_shot = True
            self.next_filename = next_filename
        else:
            self.single_shot = False
        sprite = self.sprites[filename]
        self.sprite_sheet = QPixmap(sprite.sprite_path)
        self.num_frames = sprite.num_frames
        self.current_frame = 0
        self.frame_width = self.sprite_sheet.width() // self.num_frames
        self.frame_height = self.sprite_sheet.height()
        self.update_frame()
        self.timer.start(sprite.frame_time)