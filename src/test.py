import tkinter as tk

def open_window():
    # 新しいウィンドウを作成
    top = tk.Toplevel(root)
    top.title("サブウィンドウ")

    # 閉じるボタンを作成
    close_button = tk.Button(top, text="閉じる", command=top.destroy)
    close_button.pack(pady=20)

root = tk.Tk()
root.title("メインウィンドウ")

open_button = tk.Button(root, text="新しいウィンドウを開く", command=open_window)
open_button.pack(pady=20)

root.mainloop()
