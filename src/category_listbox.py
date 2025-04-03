from base_draggable_listbox import BaseDraggableListbox

class CategoryListbox(BaseDraggableListbox):
    def __init__(self, master, app, category, **kwargs):
        super().__init__(master, **kwargs)
        self.homescreen = app
        self.category = category

    def drop_item(self, event):
        """ドロップ処理"""
        if self.drag_data["started"]:
            with self.homescreen.app.lock:
                target_listbox = self.homescreen.get_listbox_at(event)
                if target_listbox:
                    item = self.category.items.pop(self.drag_data["index"])
                    target_listbox.category.add_item(item)
                self.homescreen.update_listbox(True)
                self.drag_data = {"index": None, "text": None, "started": False}

                if self.drag_label:
                    self.drag_label.destroy()
                    self.drag_label = None