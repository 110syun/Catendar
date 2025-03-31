import tkinter as tk
from category import Category
from category_listbox import CategoryListbox
from category_label import CategoryLabel
from scheduler import Scheduler

class Homescreen:
    def __init__(self, app):
        self.app = app
        self.listboxes = []
        self.scheduler = Scheduler(self)
        
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
                    
    def get_listbox_at(self, event):
        for listbox in self.listboxes:
            x1, y1, x2, y2 = listbox.winfo_rootx(), listbox.winfo_rooty(), listbox.winfo_rootx() + listbox.winfo_width(), listbox.winfo_rooty() + listbox.winfo_height()
            if x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2:
                return listbox
        return None
        
    def openGUI(self):
        root = tk.Tk()
        root.title("Window Management")

        def on_closing():
            self.app.running = False
            root.quit()

        root.protocol("WM_DELETE_WINDOW", on_closing)

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
            create_category_button = tk.Button(root, text="カテゴリ作成", command=create_category)
            create_category_button.pack(side=tk.BOTTOM)
            open_shceduler_button = tk.Button(root, text="スケジューラーを開く", command=lambda: self.scheduler.openGUI(root))
            open_shceduler_button.pack(side=tk.BOTTOM)
            for category in self.app.categories:
                create_category_frame(category)

        create_widgets()
        root.mainloop()