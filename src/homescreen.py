import tkinter as tk
import threading
import pystray
import os
import sys
from pystray import MenuItem as item, Icon
from PIL import Image
from category import Category
from category_listbox import CategoryListbox
from category_label import CategoryLabel
from scheduler import Scheduler
from self_check_editor import SelfCheckEditor

class Homescreen:
    def __init__(self, app):
        self.os_name = app.os_name
        self.app = app
        self.controller = app.controller
        self.app_dir = self.controller.app_dir
        self.listboxes = []
        self.resource_path = self.check_resource_path()
        self.scheduler = Scheduler(self)
    
    def check_resource_path(self):
        if hasattr(sys, '_MEIPASS'):
            return sys._MEIPASS
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def update_listbox(self, all):
        if self.listboxes:
            if all:
                for category_index, listbox in enumerate(self.listboxes):
                    listbox.delete(0, tk.END)
                    for item in self.app.categories[category_index].items:
                        listbox.insert(tk.END, f"{item.name}")
            else:
                listbox = self.listboxes[0]
                listbox.delete(0, tk.END)
                for item in self.app.categories[0].items:
                    listbox.insert(tk.END, f"{item.name}")
        self.controller.dump_categories_json()
                    
    def get_listbox_at(self, event):
        for listbox in self.listboxes:
            x1, y1, x2, y2 = listbox.winfo_rootx(), listbox.winfo_rooty(), listbox.winfo_rootx() + listbox.winfo_width(), listbox.winfo_rooty() + listbox.winfo_height()
            if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
                return listbox
        return None
        
    def openGUI(self):
        root = tk.Tk()
        root.title("Window Management")
        
        def create_menu():
            return (item("ウィンドウを開く", show_gui), item("終了", on_closing))

        def on_closing():
            if self.os_name == "Windows":
                self.app.running = False
                icon.stop()
                root.quit()
            elif self.os_name == "Darwin":
                root.quit()
            
        def show_gui():
            root.deiconify()

        def hide_window():
            root.withdraw()
        
        root.protocol("WM_DELETE_WINDOW", hide_window)

        def rename_category(label, frame, category):
            category_index = self.app.categories.index(category)
            entry = tk.Entry(root)
            entry.insert(0, label.cget("text"))
            entry.pack()
            entry.focus_set()

            def save_name(event):
                new_name = entry.get()
                if new_name:
                    label.config(text=new_name)
                    category.name = new_name
                    entry.destroy()
                else:
                    self.app.delete_category(category_index)
                    frame.destroy()
                    del self.listboxes[category_index]
                    entry.destroy()
                    self.update_listbox(True)
                self.scheduler.update_listbox()

            entry.bind("<Return>", save_name)
            entry.bind("<FocusOut>", save_name)

        def create_category_frame(category):
            frame = tk.Frame(root, bd=2, relief=tk.SUNKEN)
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
            label = CategoryLabel(frame, self, category, text=category.name)
            label.pack()
            label.bind("<Double-Button-1>", lambda event, lbl=label: rename_category(lbl, frame, category))
            listbox = CategoryListbox(frame, self, category, width=15)
            listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.listboxes.append(listbox)
            scrollbar = tk.Scrollbar(frame, orient="vertical", command=listbox.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            listbox.config(yscrollcommand=scrollbar.set)
            self.update_listbox(all)

        def create_category():
            new_category = "名前の無いカテゴリ"
            self.app.categories.append(Category(name=new_category))
            create_category_frame(self.app.categories[-1])

        def create_widgets():
            button_frame = tk.Frame(root)
            button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
            create_category_button = tk.Button(button_frame, text="カテゴリ作成", command=create_category)
            create_category_button.pack(side=tk.LEFT, padx=5)
            open_shceduler_button = tk.Button(button_frame, text="スケジューラーを開く", command=lambda: self.scheduler.openGUI(root))
            open_shceduler_button.pack(side=tk.LEFT, padx=5)
            for category in self.app.categories:
                create_category_frame(category)
                
        def start_self_check():
            editor = SelfCheckEditor(self)
            editor.start_self_check(root)

        if self.os_name == "Windows":
            image = Image.open(os.path.join(self.resource_path, "images", "icon.png"))
            icon = Icon("schedule-app", image, menu=create_menu())
            root.iconbitmap(os.path.join(self.resource_path, "images", "icon.ico"))
            threading.Thread(target=icon.run, daemon=True).start()
        create_widgets()
        self.scheduler.openGUI(root)
        threading.Thread(target=start_self_check, daemon=True).start()
        root.mainloop()