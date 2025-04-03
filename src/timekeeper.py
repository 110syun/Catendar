import time
from datetime import datetime
from tkinter import messagebox

class Timekeeper:
    def __init__(self, app):
        print("initialize")
        if (app):
            self.scheduler = app
            self.watcher = app.watcher
        self.current_phase = 0
        self.previous_time = datetime.now()
        self.last = False
        self.running = True
        for time in self.scheduler.times:
            if self.previous_time > time:
                self.current_phase += 1
            else:
                break
            self.last = True

    def main(self):
        stress = 0
        while self.running:
            now = datetime.now()
            current_category = self.watcher.previous_category
            frame = self.scheduler.frames[self.current_phase]
            current_option = frame[1].get()
            current_listbox = frame[2]
            if current_option == "white list":
                if current_category not in current_listbox.categories and current_listbox.categories:
                    stress += 1
            else:
                if current_category in current_listbox.categories or not current_listbox.categories:
                    stress += 1
            if stress == 10:
                stress = 0
            if not self.last and now > self.scheduler.times[self.current_phase]:
                stress = 0
                self.current_phase += 1
                if len(self.scheduler.times) <= self.current_phase:
                    self.last = True
            self.previous_time = now
            time.sleep(1)
            
    def stop(self):
        self.running = False