# OS依存部分のリストアップ（行番号付き）

本アプリケーションの`src`ディレクトリ内で、OS依存性が高い（特にWindows固有APIや挙動に依存する）部分をファイルごと・行番号付きでまとめます。

---

## watcher.py
- 4行目: `import win32process`
- 5行目: `import win32gui`
- 6行目: `import wmi`
- 22行目: `win32process.GetWindowThreadProcessId(hwnd)`
- 23行目: `self.c.query(...)`（WMIによるプロセス情報取得）
- 44行目: `hwnd = win32gui.GetForegroundWindow()`

---

## transparent_window.py
- 5行目: `import win32gui`
- 6行目: `import win32con`
- 13行目: `self.target_rect = win32gui.GetWindowRect(self.target_hwnd)`
- 26行目: `self.hwnd = int(self.winId())`
- 27行目: `ex_style = win32gui.GetWindowLong(self.hwnd, win32con.GWL_EXSTYLE)`
- 28行目: `win32gui.SetWindowLong(self.hwnd, win32con.GWL_EXSTYLE, ex_style | win32con.WS_EX_NOACTIVATE)`
- 35行目: `if win32gui.IsWindow(self.target_hwnd):`
- 36行目: `rect = win32gui.GetWindowRect(self.target_hwnd)`

---

## widget_manager.py
- 7行目: `import win32gui`
- 8行目: `import win32con`
- 9行目: `import win32process`
- 10行目: `import pywintypes`
- 12行目: `import psutil`
- 38行目: `_, process_id = win32process.GetWindowThreadProcessId(hwnd)`
- 53行目: `hwnd = win32gui.GetForegroundWindow()`
- 58行目: `style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)`
- 63行目: `class_name = win32gui.GetClassName(hwnd)`
- 70行目: `if self.current_window_hwnd not in self.widgets: ... TransparentWindow(target_hwnd=...)`
- 83行目: `self.widgets[self.current_window_hwnd].follow_window()`
- 86行目: `self.heading_off_screen(self.widgets[self.current_animator_hwnd])`
- 89行目: `self.animator.move(...)`
- 90行目: `self.bed_image.move(...)`
- 91行目: `self.destination_check(self.widgets[self.current_animator_hwnd])`
- 94行目: `if not win32gui.IsWindow(self.widgets[self.current_animator_hwnd].target_hwnd):`
- 109, 127, 145行目: `win32gui.SetWindowPos(...)`（複数箇所）

---

## sprite_manager.py
- 8行目: `import pyautogui`
- 61行目: `pyautogui.write('A', interval=0)`

---

## operation_checker.py
- 2行目: `import multiprocessing`
- 54行目: `multiprocessing.freeze_support()`
- 55行目: `multiprocessing.set_start_method("spawn", force=True)`
- 56行目: `queue = multiprocessing.Queue()`
- 59行目: `process = multiprocessing.Process(...)`
- 61行目: `process.daemon = True`
- 62行目: `process.start()`

---

## main.py
- 7行目: `import multiprocessing`
- 74行目: `queue = multiprocessing.Queue()`
- 91行目: `process = multiprocessing.Process(...)`
- 93行目: `process.daemon = True`
- 94行目: `process.start()`
- 99行目: `multiprocessing.freeze_support()`
- 100行目: `multiprocessing.set_start_method("spawn", force=True)`

---

## その他
- `cat_bed.py`, `timekeeper.py` などは直接的なOS依存APIはありませんが、PyQt5の一部機能や`datetime`/`time`のタイムゾーン・ロケール依存に注意が必要です。

---

## 備考
- `win32gui`, `win32con`, `win32process`, `wmi`, `pywintypes` などはWindows専用APIです。
- `pyautogui`や`PyQt5`の一部機能はOSによって動作が異なる場合があります。
- `multiprocessing.set_start_method("spawn", force=True)`はWindowsで必要、UNIX系では"fork"がデフォルトです。

---