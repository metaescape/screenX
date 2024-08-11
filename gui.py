import tkinter as tk

TITLE = "ScreenX"


class ScreenRecorderApp:
    def __init__(self):

        # 初始化窗口
        self.init_root()
        self.recording_hook = lambda: print("Recording...")
        self.end_hook = lambda: print("Recording stopped.")

    def init_root(self):
        self.root = tk.Tk()
        self.recording = False

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        self.selection_box = {
            "top": 0,
            "left": 0,
            "width": screen_width,
            "height": screen_height,
        }
        print(f"Screen size: {screen_width}x{screen_height}")
        self.root.attributes("-topmost", True)

        self.root.attributes("-type", "dialog")
        self.root.attributes(
            "-alpha", 0.2
        )  # Set transparency level (0.0 to 1.0)
        self.root.geometry(f"{screen_width}x{screen_height}")
        self.root.title(TITLE)
        self.root.configure(bg="white")

        self.canvas = tk.Canvas(self.root, cursor="cross")

        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.buttons = []

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if self.selection_box:
            self.canvas.delete(self.selection_box)
        self.selection_box = self.canvas.create_rectangle(
            self.start_x,
            self.start_y,
            self.start_x,
            self.start_y,
            outline="black",
            width=2,
        )

    def on_mouse_drag(self, event):
        self.canvas.coords(
            self.selection_box, self.start_x, self.start_y, event.x, event.y
        )

    def on_button_release(self, event):
        self.end_x = event.x
        self.end_y = event.y

        self.bbox = {
            "top": self.start_y,
            "left": self.start_x,
            "width": self.end_x - self.start_x,
            "height": self.end_y - self.start_y,
        }

        # 调整 root 窗口的大小和位置以匹配选择框
        width = abs(self.end_x - self.start_x) - 2
        height = abs(self.end_y - self.start_y) - 2
        x = min(self.start_x, self.end_x) + 1
        y = min(self.start_y, self.end_y) + 1
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.attributes("-alpha", 0.02)

        self.create_button_window()

    def create_button_window(self):
        self.button_window = tk.Toplevel(self.root)
        self.button_window.overrideredirect(True)  # 去掉窗口边框
        self.button_window.geometry(
            f"+{self.end_x}+{self.start_y}"
        )  # 将按钮窗口放置在选择框的右侧
        self.button_window.attributes("-alpha", 1.0)  # 确保按钮窗口不透明

        confirm_button = tk.Button(
            self.button_window, text="record", command=self.toggle_recording
        )
        confirm_button.pack(side=tk.TOP, padx=5, pady=5)

        reset_button = tk.Button(
            self.button_window, text="resel", command=self.reset_selection
        )
        reset_button.pack(side=tk.BOTTOM, padx=5, pady=5)

        exit_button = tk.Button(
            self.button_window, text="exit", command=self.exit_app
        )
        exit_button.pack(side=tk.BOTTOM, padx=5, pady=5)
        self.buttons = [confirm_button, reset_button, exit_button]

    def reset_selection(self):
        self.root.destroy()
        self.init_root()

    def toggle_recording(self):
        if not self.recording:
            self.recording = True
            self.recording_hook()
            self.buttons[0].config(text="stop")
            # 在这里开始录制逻辑
        else:
            self.recording = False
            self.buttons[0].config(text="record")
            self.end_hook()
            # 在这里结束录制逻辑
            self.exit_app()

    def register_recording_hook(self, hook):
        self.recording_hook = hook

    def register_end_hook(self, hook):
        self.end_hook = hook

    def exit_app(self):
        self.root.destroy()

    def run(self):
        self.root.mainloop()


# Example of how to use this selection in your recording
if __name__ == "__main__":

    app = ScreenRecorderApp()
    app.run()

    print(app.bbox)
