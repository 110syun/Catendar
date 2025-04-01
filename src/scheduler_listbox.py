from base_draggable_listbox import BaseDraggableListbox

class SchedulerListbox(BaseDraggableListbox):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.scheduler = app
        self.categories = []
        
        self.bind("<Button-3>", self.on_right_click)

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
                
    def on_right_click(self, event):
        clicked_index = self.nearest(event.y)
        if clicked_index >= 0:
            category = self.categories[clicked_index]
            self.remove_category(category)

    def add_category(self, category):
        if category in self.categories:
            return
        self.categories.append(category)

    def remove_category(self, category):
        if category in self.categories:
            index = self.categories.index(category)
            self.categories.pop(index)
            self.delete(index)