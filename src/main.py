import threading
import atexit
import json
import time
import os
import multiprocessing
import platform
from watcher import Watcher
from widget_manager import WidgetManager

class AppController:
    def __init__(self):
        self.os_name = platform.system()
        self.queue = multiprocessing.Queue()
        self.watcher = None

    def cleanup(self):
        data = [category.to_dict() for category in self.watcher.categories]
        with open("categories.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        timestamp_filename = time.strftime('log/%Y-%m-%d') + ".txt"
        with open(timestamp_filename, "w", encoding="utf-8") as f:
            for timestamp in self.watcher.timestamps:
                f.write(f"app: {timestamp['app']}, category: {timestamp['category']}, start: {timestamp['start']}, end: {timestamp['end']}\n")

    def load_categories(self):
        try:
            with open("categories.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return None

    def load_timestamps(self):
        timestamps = []
        timestamp_filename = time.strftime('log/%Y-%m-%d') + ".txt"
        try:
            with open(timestamp_filename, "r", encoding="utf-8") as f:
                for line in f:
                    app, category, start, end = line.strip().split(", ")
                    timestamps.append({
                        "app": app.split(": ")[1],
                        "category": category.split(": ")[1],
                        "start": start.split(": ")[1],
                        "end": end.split(": ")[1]
                    })
        except FileNotFoundError:
            pass
        return timestamps

    def start_widget_process(self):
        manager = WidgetManager(self.os_name, self.queue)
        manager.run_widget_manager()

    def start(self):
        os.makedirs('log', exist_ok=True)
        os.makedirs('preset', exist_ok=True)

        categories_data = self.load_categories()
        timestamps = self.load_timestamps()

        self.watcher = Watcher(self, self.queue, categories_data, timestamps)
        atexit.register(self.cleanup, self.watcher)

        process = multiprocessing.Process(
            target=self.start_widget_process
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
