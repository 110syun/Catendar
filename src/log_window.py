import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class UsageLogWindow:
    def __init__(self, root, csv, os_name):
        if os_name == "Windows":
            try:
                font_path = "C:/Windows/Fonts/meiryo.ttc"
                jp_font = fm.FontProperties(fname=font_path)
                plt.rcParams["font.family"] = jp_font.get_name()
            except Exception as e:
                print("フォント設定エラー:", e)
        elif os_name == "Darwin":
            try:
                font_path = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
                jp_font = fm.FontProperties(fname=font_path)
                plt.rcParams["font.family"] = jp_font.get_name()
            except Exception as e:
                print("フォント設定エラー:", e)

        self.top = tk.Toplevel(root)
        self.top.wm_title("Usage Log")

        df = pd.read_csv(csv, parse_dates=["start_time", "end_time"])

        fig, ax = plt.subplots(figsize=(12, 2))

        colors = plt.cm.tab10.colors
        app_to_color = {app: colors[i % len(colors)] for i, app in enumerate(df["category"].unique())}

        for _, row in df.iterrows():
            ax.barh(
                y=0,
                left=row["start_time"],
                width=row["end_time"] - row["start_time"],
                height=0.3,
                color=app_to_color[row["category"]],
                label=row["category"]
            )

        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        ax.legend(by_label.values(), by_label.keys(), bbox_to_anchor=(1.05, 1), loc="upper left")

        ax.set_yticks([])
        ax.set_xlabel("Time")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.title("Application Usage Timeline")
        plt.tight_layout()
        plt.grid(True, axis='x')

        self.canvas = FigureCanvasTkAgg(fig, master=self.top)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Main Screen")
    root.geometry("300x100")

    def open_usage_log():
        UsageLogWindow(root)

    btn_show_log = ttk.Button(root, text="ログ表示", command=open_usage_log)
    btn_show_log.pack(pady=30)

    root.mainloop()