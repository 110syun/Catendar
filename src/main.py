import threading
import atexit
import json
import time
import os
import sys
import multiprocessing
import platform
import signal
import csv
from watcher import Watcher
from widget_manager import WidgetManager

def widget_process_entry(os_name, parent_pid, queue):
    manager = WidgetManager(os_name, parent_pid, queue)
    manager.run_widget_manager()

class AppController:
    def __init__(self):
        self.os_name = platform.system()
        self.queue = multiprocessing.Queue()
        self.watcher = None
        self.app_dir = self.get_app_dir()

    def get_app_dir(self):
        if getattr(sys, 'frozen', False):
            return os.path.dirname(sys.executable)
        else:
            return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def get_path(self, filename):
        return os.path.join(self.app_dir, filename)

    def dump_categories_json(self):
        data = [category.to_dict() for category in self.watcher.categories]
        with open(self.get_path("categories.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    
    def dump_timestamps_csv(self):
        timestamp_filename = time.strftime('log/%Y-%m-%d') + ".csv"
        with open(self.get_path(timestamp_filename), "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(self.watcher.timestamps)

    def cleanup(self):
        data = [category.to_dict() for category in self.watcher.categories]
        with open(self.get_path("categories.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        timestamp_filename = time.strftime('log/%Y-%m-%d') + ".csv"
        with open(self.get_path(timestamp_filename), "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(self.watcher.timestamps)

    def load_categories(self):
        try:
            with open(self.get_path("categories.json"), "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def load_timestamps(self):
        timestamp_filename = time.strftime('log/%Y-%m-%d') + ".csv"
        try:
            with open(self.get_path(timestamp_filename), "r", newline='', encoding="utf-8") as f:
                reader = csv.reader(f)
                return [row for row in reader]
        except FileNotFoundError:
            pass
        return None
    
    def handle_signal(self, signum, frame):
        self.cleanup()
        sys.exit(0)

    def start(self):
        os.makedirs(self.get_path('log'), exist_ok=True)
        os.makedirs(self.get_path('preset'), exist_ok=True)

        categories_data = self.load_categories()
        timestamps = self.load_timestamps()

        self.watcher = Watcher(self, self.queue, categories_data, timestamps)
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)
        atexit.register(self.cleanup)

        process = multiprocessing.Process(
            target=widget_process_entry,
            args=(self.os_name, os.getpid(), self.queue)
        )
        process.daemon = True
        process.start()

        if self.os_name == "Windows":
            threading.Thread(target=self.watcher.homescreen.openGUI, daemon=True).start()
            self.watcher.update_window_name()
        elif self.os_name == "Darwin":
            threading.Thread(target=self.watcher.update_window_name, daemon=True).start()
            self.watcher.homescreen.openGUI()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    if platform.system() in ("Windows", "Darwin"):
        multiprocessing.set_start_method("spawn", force=True)

    app = AppController()
    app.start()
