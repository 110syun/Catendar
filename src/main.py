import threading
import atexit
import json
import time
import os
from watcher import Watcher

def cleanup(watcher):
    data = [category.to_dict() for category in watcher.categories]
    with open("categories.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    timestamp_filename = time.strftime('log/%Y-%m-%d') + ".txt"
    with open(timestamp_filename, "w", encoding="utf-8") as f:
        for timestamp in watcher.timestamps:
            f.write(f"app: {timestamp['app']}, category: {timestamp['category']}, start: {timestamp['start']}, end: {timestamp['end']}\n")

def main():
    try:
        with open("categories.json", "r", encoding="utf-8") as f:
            categories_data = json.load(f)
    except FileNotFoundError:
        categories_data = None

    if not os.path.exists('log'):
        os.makedirs('log')
    
    if not os.path.exists('preset'):
        os.makedirs('preset')
    
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

    watcher = Watcher(categories_data, timestamps)
    atexit.register(cleanup, watcher)
    threading.Thread(target=watcher.homescreen.openGUI, daemon=True).start()
    watcher.update_window_name()

if __name__ == "__main__":
    main()