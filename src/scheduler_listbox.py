import tkinter as tk

class SchedulerListbox(tk.Listbox):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.scheduler = app
        self.categories = []
        self.bind("<ButtonPress-1>", self.prepare_drag)
        self.bind("<B1-Motion>", self.start_drag)
        self.bind("<B1-Motion>", self.do_drag, add=True)
        self.bind("<ButtonRelease-1>", self.drop_item)
        self.drag_data = {"index": None, "text": None, "started": False}
        self.drag_label = None

    def prepare_drag(self, event):
        """ドラッグ準備（クリック時）"""
        index = self.nearest(event.y)
        if index >= 0:
            self.drag_data["index"] = index
            self.drag_data["text"] = self.get(index)
            self.drag_data["started"] = False

    def start_drag(self, event):
        """ドラッグ開始（マウスを動かした瞬間）"""
        if not self.drag_data["started"] and self.drag_data["text"]:
            self.delete(self.drag_data["index"])
            self.drag_data["started"] = True

            self.drag_label = tk.Toplevel(self)
            self.drag_label.overrideredirect(True)
            self.drag_label.attributes("-alpha", 0.7)
            label = tk.Label(self.drag_label, text=self.drag_data["text"], bg="lightgray", relief=tk.SOLID)
            label.pack()
            self.update_drag_label(event)

    def do_drag(self, event):
        """ドラッグ中の処理（マウス追従）"""
        if self.drag_label:
            self.update_drag_label(event)
        self.event_generate("<<ListboxSelect>>")

    def update_drag_label(self, event):
        """ドラッグ中のラベルの位置を更新"""
        x = self.winfo_rootx() + event.x + 10
        y = self.winfo_rooty() + event.y + 10
        self.drag_label.geometry(f"+{x}+{y}")

    def drop_item(self, event):
        """ドロップ処理"""
        if self.drag_data["started"]:
            target_listbox = self.scheduler.get_listbox_at(event)
            if target_listbox:
                category = self.categories.pop(self.drag_data["index"])
                target_listbox.add_category(category)
            self.scheduler.update_listbox()
            self.drag_data = {"index": None, "text": None, "started": False}

            if self.drag_label:
                self.drag_label.destroy()
                self.drag_label = None
                
    def add_category(self, category):
        if category in self.categories:
            return
        self.categories.append(category)
        
    def remove_category(self, category):
        if category in self.categories:
            index = self.categories.index(category)
            self.categories.pop(index)
            self.delete(index)