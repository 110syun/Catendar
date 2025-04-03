import tkinter as tk
from tkinter import messagebox
import re

class Scheduler:
    def __init__(self, app):
        if (app):
            self.homescreen = app
            self.watcher = self.homescreen.app

    def openGUI(self):
        root = tk.Tk()
        root.title("Time Scheduler")

        def validate_time_format(hour, minute):
            """時刻が正しい形式かどうかを検証する"""
            return hour.isdigit() and minute.isdigit() and 0 <= int(hour) <= 24 and 0 <= int(minute) <= 59

        def create_frame():
            frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            
            hour_entry = tk.Entry(frame, width=5)
            hour_entry.pack(side=tk.LEFT, padx=2, pady=2)

            colon_label = tk.Label(frame, text=":")
            colon_label.pack(side=tk.LEFT, padx=2, pady=2)

            minute_entry = tk.Entry(frame, width=5)
            minute_entry.pack(side=tk.LEFT, padx=2, pady=2)

            def on_submit(event=None):
                hour = hour_entry.get()
                minute = minute_entry.get()
                if validate_time_format(hour, minute):
                    messagebox.showinfo("成功", f"時刻 {hour}:{minute} が登録されました！")
                else:
                    messagebox.showerror("エラー", "時刻は hh:mm の形式で入力してください（例: 14:30）")

            # エントリボックスにイベントをバインド
            hour_entry.bind("<FocusOut>", on_submit)
            minute_entry.bind("<FocusOut>", on_submit)

        def create_widgets():
            create_button = tk.Button(root, text="追加", command=create_frame)
            create_button.pack(side=tk.BOTTOM)

        create_widgets()
        root.mainloop()

if __name__ == "__main__":
    scheduler = Scheduler(None)
    scheduler.openGUI()