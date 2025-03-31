import tkinter as tk

class CategoryLabel(tk.Label):
    def __init__(self, master, app, category, **kwargs):
        super().__init__(master, **kwargs)
        self.homescreen = app
        self.scheduler = app.scheduler
        self.category = category
        self.bind("<ButtonPress-1>", self.prepare_drag)
        self.bind("<B1-Motion>", self.start_drag)
        self.bind("<B1-Motion>", self.do_drag, add=True)
        self.bind("<ButtonRelease-1>", self.drop_item)
        self.drag_data = {"text": None, "started": False}
        self.drag_label = None

    def prepare_drag(self, event):
        """ドラッグ準備（クリック時）"""
        self.drag_data["text"] = self["text"]
        self.drag_data["started"] = False

    def start_drag(self, event):
        """ドラッグ開始（マウスを動かした瞬間）"""
        if not self.drag_data["started"] and self.drag_data["text"]:
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
        if self.drag_data["started"]:
            target_listbox = self.scheduler.get_listbox_at(event)
            if target_listbox:
                target_listbox.add_category(self.category)
            self.scheduler.update_listbox()
            self.drag_data = {"index": None, "text": None, "started": False}

            if self.drag_label:
                self.drag_label.destroy()
                self.drag_label = None