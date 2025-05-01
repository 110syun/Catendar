import tkinter as tk
import os
from datetime import datetime
from spreadsheet_manager import GoogleSpreadsheetManager

class SelfCheckEditor:
    def __init__(self):
        if os.path.exists("client_secret.json"):
            JSON_KEYFILE = "client_secret.json"
        else:
            self.manager = None
            return
        SPREADSHEET_URL = "https://docs.google.com/spreadsheets/d/1NngcnXZGm_kWHHPRmA95seKWpKkF3pFmQT0XFGtp02k/edit?usp=drive_link"
        self.checklist = ["睡眠","食事","運動","ストレス","今の気分","不安","心穏やか","誰とでも話せる","体の動き","集中力","体調","自分を信頼","他人を信頼","他人からの信頼"]

        self.manager = GoogleSpreadsheetManager(JSON_KEYFILE, SPREADSHEET_URL)
        sheet_names = [sheet.title for sheet in self.manager.spreadsheet.worksheets()]
        self.now = datetime.now()
        self.year = self.now.year
        self.month = self.now.month
        self.day = self.now.day
        self.YM = self.now.strftime("%Y/%m")
        self.edit_row = self.day * 2 

        if self.YM not in sheet_names:
            self.init_new_worksheet()

        if self.day < 16:
            self.edit_row += 4
        else:
            self.edit_row += 7

    def init_new_worksheet(self):
        self.manager.copy_sheet("【原本】",self.YM)
        self.manager.edit_cell(self.YM, 3, 1, self.year)
        self.manager.edit_cell(self.YM, 3, 2, self.month)
        self.manager.edit_cell(self.YM, 36, 1, self.year)
        self.manager.edit_cell(self.YM, 36, 2, self.month)

    def start_self_check(self, root):
        if not self.manager:
            return
        if root:
            self.win = tk.Toplevel(root)
        else:
            self.win = tk.Tk()
        self.current_index = 0
        self.win.title("Self Check")
        self.today_label = tk.Label(self.win, text = self.now.strftime("%Y/%m/%d") + " のセルフチェック")
        self.today_label.pack(pady = 10)
        self.frame = tk.Frame(self.win, bd=2, relief=tk.SUNKEN)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.label = tk.Label(self.frame, text = self.checklist[self.current_index])
        self.label.pack(pady = 5)
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack()
        self.create_buttons()

    def next_question(self):
        self.current_index += 1
        if (self.current_index == len(self.checklist)):
            self.win.withdraw()
        else:
            self.label.config(text = self.checklist[self.current_index])
            self.create_buttons()

    def answer(self, text):
        if not text == "〇":
            self.manager.edit_cell(self.YM, self.edit_row, self.current_index + 4, text)
        self.next_question()
    
    def create_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        if self.current_index == 4:
            button_texts = ["1", "2", "3", "4", "5"]
        else:
            button_texts = ["〇", "△", "X"]
        for text in button_texts:
            button = tk.Button(self.button_frame, text=text, width=5, command=lambda t=text: self.answer(t))
            button.pack(side=tk.LEFT, padx=10)

if __name__ == "__main__":
    editor = SelfCheckEditor()
    editor.start_self_check(None)
    editor.win.mainloop()