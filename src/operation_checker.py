import multiprocessing
from widget_manager import WidgetManager
import tkinter as tk

class OperationChecker:
    def __init__(self, queue):
        self.queue = queue
    
    def create_main_window(self):
        root = tk.Tk()
        root.title("動作確認アプリ")
        root.geometry("200x280")

        buttons_info = [
            ("歩き前", self.walk_front_action),
            ("歩き後ろ", self.walk_back_action),
            ("歩き正面", self.walk_advancing_action),
            ("歩き右", self.walk_right_action),
            ("歩き左", self.walk_left_action),
            ("座り正面", self.sit_action),
            ("寝る", self.sleep_action)
        ]

        for i, (text, command) in enumerate(buttons_info):
            btn = tk.Button(root, text=text, command=command)
            btn.pack(pady=5)

        root.mainloop()

    def walk_front_action(self):
        self.queue.put("cat_walk_f.png")

    def walk_back_action(self):
        self.queue.put("cat_walk_b.png")

    def walk_advancing_action(self):
        self.queue.put("cat_walk_a.png")

    def walk_right_action(self):
        self.queue.put("cat_walk_r.png")

    def walk_left_action(self):
        self.queue.put("cat_walk_l.png")

    def sit_action(self):
        self.queue.put("cat_sit_f.png")

    def sleep_action(self):
        self.queue.put("cat_sleep_r.png")

def start_test_subprocess(queue):
    manager = WidgetManager(queue)
    manager.visible = True
    manager.run_widget_manager()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    multiprocessing.set_start_method("spawn", force=True)
    queue = multiprocessing.Queue()
    operation_checker = OperationChecker(queue)
    process = multiprocessing.Process(
        target=start_test_subprocess,
        args=(queue,)
    )
    process.daemon = True
    process.start()
    operation_checker.create_main_window()