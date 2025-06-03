import threading
import time
from item import Item
from category import Category
from homescreen import Homescreen

class Watcher:
    def __init__(self, app, queue, categories_data=None, timestamps=None):
        self.controller = app
        self.os_name = app.os_name

        if self.os_name == "Windows":
            import win32process
            import win32gui
            import wmi
            self.win32process = win32process
            self.win32gui = win32gui
            self.c = wmi.WMI()
        elif self.os_name == "Darwin":
            from AppKit import NSWorkspace
            from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID
            self.NSWorkspace = NSWorkspace
            self.CGWindowListCopyWindowInfo = CGWindowListCopyWindowInfo
            self.kCGWindowListOptionOnScreenOnly = kCGWindowListOptionOnScreenOnly
            self.kCGNullWindowID = kCGNullWindowID

  
        self.categories = []
        self.previous_window = None
        self.previous_category = None
        self.lock = threading.Lock()
        self.running = True
        self.timestamps = timestamps if timestamps else [['app', 'category', 'start_time', 'end_time']]
        self.homescreen = Homescreen(self)
        self.queue = queue

        if categories_data:
            for category_data in categories_data:
                category = Category(name=category_data["name"])
                for item_data in category_data["items"]:
                    item = Item(name=item_data["name"], active_time=item_data["active_time"])
                    category.add_item(item)
                self.categories.append(category)
        else:
            self.categories.append(Category(name="未分類"))

    def get_app_name(self, hwnd):
        exe = None
        try:
            _, pid = self.win32process.GetWindowThreadProcessId(hwnd)
            for p in self.c.query(f'SELECT Name FROM Win32_Process WHERE ProcessId = {str(pid)}'):
                exe = p.Name
                break
        except Exception as e:
            print(f"Exception: {e}")
        return exe

    def item_exists(self, elapsed_time):
        with self.lock:
            for category in self.categories:
                for item in category.items:
                    if self.previous_window == item.name:
                        item.active_time += elapsed_time
                        return
            self.categories[0].add_item(Item(name=self.previous_window, active_time=elapsed_time))
            self.homescreen.update_listbox(False)
            return

    def update_window_name(self):
        previous_time = time.time()
        while self.running:
            current_time = time.time()
            elapsed_time = current_time - previous_time

            if self.os_name == "Windows":
                hwnd = self.win32gui.GetForegroundWindow()
                window_name = self.get_app_name(hwnd)
            elif self.os_name == "Darwin":
                active_app = self.NSWorkspace.sharedWorkspace().frontmostApplication()
                window_name = active_app.localizedName()

            if window_name:
                if self.previous_window:
                    self.item_exists(elapsed_time)
                    if self.previous_window == window_name:
                        if self.timestamps:
                            self.timestamps[-1][-1] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
                    else:
                        with self.lock:
                            self.previous_window = window_name
                            for category in self.categories:
                                for item in category.items:
                                    if item.name == self.previous_window:
                                        self.previous_category = category
                            self.timestamps.append([
                                self.previous_window,
                                self.previous_category.name if self.previous_category else "未分類",
                                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(previous_time)),
                                time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
                            ])
                else:
                    with self.lock:
                        self.previous_window = window_name
                        for category in self.categories:
                            for item in category.items:
                                if item.name == self.previous_window:
                                    self.previous_category = category
                        self.timestamps.append([
                            self.previous_window,
                            self.previous_category.name if self.previous_category else "未分類",
                            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(previous_time)),
                            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_time))
                    ])
                previous_time = current_time
            time.sleep(1)

    def delete_category(self, category_index):
        for item in self.categories[category_index].items:
            self.categories[0].add_item(item)
        for frame in self.homescreen.scheduler.frames:
            listbox = frame[2]
            listbox.remove_category(self.categories[category_index])
        del self.categories[category_index]

if __name__ == "__main__":
    import platform
    os_name = platform.system()
    watcher = Watcher(os_name, None, None, None)
    threading.Thread(target=watcher.update_window_name, daemon=True).start()
    watcher.homescreen.openGUI()