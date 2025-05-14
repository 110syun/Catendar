import time
from datetime import datetime

class Timekeeper:
    def __init__(self, app, queue):
        if (app):
            self.scheduler = app
            self.watcher = app.watcher
        self.current_phase = 0
        self.previous_time = datetime.now()
        self.last = False
        self.running = True
        self.queue = queue
        self.excess_time
        for time in self.scheduler.times:
            if self.previous_time > time:
                self.current_phase += 1
            else:
                break
            self.last = True

    def main(self):
        self.queue.put(1)
        while self.running:
            now = datetime.now()
            current_category = self.watcher.previous_category
            frame = self.scheduler.frames[self.current_phase]
            current_option = frame[1].get()
            current_listbox = frame[2]
            if current_option == "white list" and current_category not in current_listbox.categories and current_listbox.categories:
                self.unscheduled_activities()
            elif current_option == "black list" and current_category in current_listbox.categories or not current_listbox.categories:
                self.unscheduled_activities()
            else:
                self.queue.put(2)
            if not self.last and now > self.scheduler.times[self.current_phase]:
                self.excess_time = 0
                self.current_phase += 1
                if len(self.scheduler.times) <= self.current_phase:
                    self.last = True
            self.previous_time = now
            time.sleep(1)
            
    def stop(self):
        self.running = False
        self.queue.put(0)
        
    def unscheduled_activities(self):
        self.excess_time += 1
        if self.excess_time >= 60:
            self.queue.put(3)
        elif self.excess_time >= 180:
            self.queue.put(4)
        elif self.excess_time >= 300:
            self.queue.put(5)