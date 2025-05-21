import threading
import tkinter as tk
import json
from datetime import datetime
from tkinter import filedialog
from tkinter import messagebox
from scheduler_listbox import SchedulerListbox
from timekeeper import Timekeeper

class Scheduler:
    def __init__(self, app):
        if (app):
            self.homescreen = app
            self.watcher = self.homescreen.app
        self.frames = []
        self.entries = []
        self.initialize = True
        self.times = []
        self.timekeeper = None

    def get_listbox_at(self, event):
        for frame in self.frames:
            listbox = frame[2]
            x1, y1, x2, y2 = listbox.winfo_rootx(), listbox.winfo_rooty(), listbox.winfo_rootx() + listbox.winfo_width(), listbox.winfo_rooty() + listbox.winfo_height()
            if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
                return listbox
        return None
    
    def update_listbox(self):
        for frame in self.frames:
            listbox = frame[2]
            listbox.delete(0, tk.END)
            for category in listbox.categories:
                listbox.insert(tk.END, f"{category.name}")

    def openGUI(self, root):
        if self.timekeeper:
            self.timekeeper.stop()
            self.timekeeper = None

        if hasattr(self, "win") and self.win.winfo_exists():
            self.win.deiconify()
            return
        
        if root:
            self.win = tk.Toplevel(root)
        else :
            self.win = tk.Tk()
        self.win.title("Time Scheduler")

        main_frame = tk.Frame(self.win, bd=2, relief=tk.SUNKEN)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        def create_listbox():
            frame = tk.Frame(main_frame, bd=2, relief=tk.SUNKEN)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=(40, 5))

            options = ["white list", "black list"]
            selected_option = tk.StringVar(value=options[0])
            dropdown = tk.OptionMenu(frame, selected_option, *options)
            dropdown.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

            listbox = SchedulerListbox(frame, self, width=5)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.frames.append([frame, selected_option, listbox])

        def create_entries():
            frame = tk.Frame(main_frame, bd=2, relief=tk.SUNKEN)

            hour_entry = tk.Entry(frame, width=5)
            hour_entry.pack(side=tk.LEFT, padx=2, pady=2)

            colon_label = tk.Label(frame, text=":")
            colon_label.pack(side=tk.LEFT, padx=2, pady=2)

            minute_entry = tk.Entry(frame, width=5)
            minute_entry.pack(side=tk.LEFT, padx=2, pady=2)

            self.entries.append([frame, hour_entry, minute_entry])

        def relocation_entries():
            equal_part = len(self.entries) + 1
            for i, frame in enumerate(self.entries):
                frame[0].place(relx=(1 / equal_part) * (i + 1), y=2.5, anchor="n")

            self.win.update_idletasks()
            min_width = self.win.winfo_reqwidth()
            min_height = self.win.winfo_reqheight()
            self.win.minsize(min_width, min_height)

        def add_schedule():
            create_listbox()
            create_entries()
            relocation_entries()
            if len(self.entries) > 1:
                delete_button.config(state="normal")

        def delete_schedule():
            frame_to_remove = self.frames.pop()
            frame_to_remove[0].destroy()

            entry_to_remove = self.entries.pop()
            entry_to_remove[0].destroy()

            relocation_entries()

            if len(self.entries) <= 1:
                delete_button.config(state="disabled")

        def validate_time_format():
            self.times.clear()
            now = datetime.now()
            for entry in self.entries:
                hour = entry[1].get()
                minute = entry[2].get()
                if hour.isdigit() and minute.isdigit() and 0 <= int(hour) <= 24 and 0 <= int(minute) <= 59:
                    dt = datetime(now.year, now.month, now.day, int(hour), int(minute))
                    if not self.times or self.times[-1] < dt:
                        self.times.append(dt)
                    else:
                        messagebox.showwarning("警告", "時間の経過に沿っていません")
                        return
                else:
                    messagebox.showwarning("エラー", "'0~24:0~59'の半角数字を入力してください")
                    return
            result = messagebox.askyesno("OK", "プリセットを保存しますか？")
            if result:
                save_file()
            on_close()

        def on_close():
            self.timekeeper = Timekeeper(self, self.watcher.queue)
            threading.Thread(target=self.timekeeper.main, daemon=True).start()
            self.win.withdraw()
        self.win.protocol("WM_DELETE_WINDOW", validate_time_format)

        def save_file():
            file_path = filedialog.asksaveasfilename(
                title="Save As",
                defaultextension=".pre",
                filetypes=[("Text files", "*.pre")],
                initialdir="./preset"
            )
            if file_path:
                data = {
                    "frames": [
                        {
                            "selected_option": frame[1].get(),
                            "listbox_items": frame[2].get(0, tk.END)
                        }
                        for frame in self.frames
                    ],
                    "entries": [
                        {
                            "hour": entry[1].get(),
                            "minute": entry[2].get()
                        }
                        for entry in self.entries
                    ]
                }
                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)

        def load_file():
            file_path = filedialog.askopenfilename(
                title="Select a preset file",
                filetypes=[("Text files", "*.pre")],
                initialdir="./preset"
            )
            if file_path:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

                for frame in self.frames:
                    frame[0].destroy()
                self.frames.clear()

                for entry in self.entries:
                    entry[0].destroy()
                self.entries.clear()

                for frame_data in data["frames"]:
                    create_listbox()
                    frame = self.frames[-1]
                    listbox = frame[2]
                    listbox.delete(0, tk.END)
                    for item in frame_data["listbox_items"]:
                        for category in self.watcher.categories:
                            if category.name == item:
                                listbox.add_category(category)
                    frame[1].set(frame_data["selected_option"])

                for entry_data in data["entries"]:
                    create_entries()
                    entry = self.entries[-1]
                    entry[1].insert(0, entry_data["hour"])
                    entry[2].insert(0, entry_data["minute"])
                    
                self.update_listbox()
                relocation_entries()

        button_frame = tk.Frame(self.win)
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)

        create_button = tk.Button(button_frame, text="追加", command=add_schedule)
        create_button.pack(side=tk.LEFT, padx=5)

        delete_button = tk.Button(button_frame, text="削除", command=delete_schedule)
        delete_button.pack(side=tk.LEFT, padx=5)
        
        Confirmed_button = tk.Button(button_frame, text="確定して閉じる", command=validate_time_format)
        Confirmed_button.pack(side=tk.LEFT, padx=5)
        
        preset_save_button = tk.Button(button_frame, text="プリセット保存", command=save_file)
        preset_save_button.pack(side=tk.LEFT, padx=5)

        preset_load_button = tk.Button(button_frame, text="プリセット読み込み", command=load_file)
        preset_load_button.pack(side=tk.LEFT, padx=5)

        if len(self.entries) <= 1:
            delete_button.config(state="disabled")

        if self.initialize:
            for i in range(2):
                create_listbox()
            create_entries()

        relocation_entries()

        self.initialize = False
        if root is None:
            self.win.mainloop()

if __name__ == "__main__":
    scheduler = Scheduler(None)
    scheduler.openGUI(None)