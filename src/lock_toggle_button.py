import tkinter as tk

class LockToggleButton:
    def __init__(self, parent, is_locked, lock_img, unlock_img):
        self.lock_img = lock_img
        self.unlock_img = unlock_img
        self.is_locked = is_locked

        self.button = tk.Label(parent, image=self.lock_img if is_locked else self.unlock_img)
        self.button.pack(side=tk.TOP, padx=2, pady=2)
        self.button.bind("<Button-1>", self.toggle)
        
    def toggle(self, event=None):
        self.is_locked = not self.is_locked
        new_image = self.lock_img if self.is_locked else self.unlock_img
        self.button.config(image=new_image)
        self.button.image = new_image